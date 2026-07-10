import os
import shutil
import time
from typing import Any

from gradio_client import Client

MIN_VALID_AUDIO_SIZE = 1000

DIALECT_MAP: dict[str, str] = {
    "河南话": "Henan Dialect / 河南话",
    "陕西话": "Shaanxi Dialect / 陕西话",
    "四川话": "Sichuan Dialect / 四川话",
    "贵州话": "Guizhou Dialect / 贵州话",
    "云南话": "Yunnan Dialect / 云南话",
    "桂林话": "Guilin Dialect / 桂林话",
    "济南话": "Jinan Dialect / 济南话",
    "石家庄话": "Shijiazhuang Dialect / 石家庄话",
    "甘肃话": "Gansu Dialect / 甘肃话",
    "宁夏话": "Ningxia Dialect / 宁夏话",
    "青岛话": "Qingdao Dialect / 青岛话",
    "东北话": "Northeast Dialect / 东北话",
    "北京话": "Northeast Dialect / 东北话",
    "天津话": "Northeast Dialect / 东北话",
    "渝普": "Sichuan Dialect / 四川话",
    "川渝": "Sichuan Dialect / 四川话",
    "沪普": "Auto",
    "上海": "Auto",
}

GENDER_MAP: dict[str, str] = {
    "male": "Male / 男",
    "female": "Female / 女",
    "男": "Male / 男",
    "女": "Female / 女",
}

AGE_MAP: dict[str, str] = {
    "child": "Child / 儿童",
    "teen": "Teenager / 少年",
    "young": "Young Adult / 青年",
    "middle-aged": "Middle-aged / 中年",
    "elderly": "Elderly / 老年",
    "儿童": "Child / 儿童",
    "少年": "Teenager / 少年",
    "青年": "Young Adult / 青年",
    "中年": "Middle-aged / 中年",
    "老年": "Elderly / 老年",
}


def _match_preset(char: dict, available_voices: list[str]) -> str | None:
    """Find best matching voice preset for a character."""
    name = char.get("name", "")
    for v in available_voices:
        if v == name or v.startswith(name):
            return v
    dialect = char.get("dialectHint") or char.get("dialect_hint", "") or ""
    for keyword, mapped in DIALECT_MAP.items():
        if keyword in dialect:
            for v in available_voices:
                if mapped.split(" / ")[0].lower() in v.lower():
                    return v
            return None
    gender = char.get("gender", "")
    if gender in GENDER_MAP:
        for v in available_voices:
            if GENDER_MAP[gender].split(" / ")[0].lower() in v.lower():
                return v
    return None


class OmniVoiceAdapter:
    """OmniVoice adapter — calls deployed Gradio service via gradio_client.

    API endpoints (discovered from the forked demo):
      fn_index=11  /add_design_task     — single voice design
      fn_index=13  /add_dialogue_tasks  — batch dialogue (up to 8 speakers)
      fn_index=14  /_process_queue       — execute queue, returns (Dataframe, Audio)
    """

    def __init__(self, url: str = "http://localhost:7860/"):
        self.url = url.rstrip("/")
        self._client: Client | None = None
        self.available_voices: list[str] = []

    def connect(self) -> None:
        self._client = Client(self.url)
        # Discover available voice presets from the Voice Clone tab
        try:
            ep = self._client.endpoints[7]
            param = ep.parameters_info[3]
            if "enum" in param.get("type", {}):
                raw = param["type"]["enum"]
                self.available_voices = [v for v in raw if v]
        except Exception:
            self.available_voices = []

    def health_check(self) -> bool:
        try:
            self._client.predict("ping")
            return True
        except Exception:
            return False

    @staticmethod
    def build_dialogue_script(batch_plan: dict, analysis: dict) -> str:
        """Build 'role: text' script from batch plan."""
        char_name_map: dict[str, str] = {}
        meta = analysis.get("meta") or analysis.get("script_analysis", {})
        for char in meta.get("characters", []):
            char_name_map[char["id"]] = char.get("name", char["id"])
        lines: list[str] = []
        for batch in batch_plan.get("batches", []):
            for line in batch.get("lines", []):
                if line.get("type") == "action":
                    continue
                char_id = line.get("characterId") or line.get("character_id")
                char_name = char_name_map.get(char_id, "旁白") if char_id else "旁白"
                clean_text = (line.get("text", "") or "").strip()
                if clean_text:
                    lines.append(f"{char_name}: {clean_text}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    #  Single-line generation — fn_index=11 (add_design_task)
    # ------------------------------------------------------------------

    def design_one(
        self,
        text: str,
        lang: str = "Chinese",
        gender: str = "Auto",
        age: str = "Auto",
        pitch: str = "Auto",
        style: str = "Auto",
        accent: str = "Auto",
        dialect: str = "Auto",
        num_step: int = 32,
        speed: float = 1.0,
    ) -> tuple[str | None, str]:
        """Submit a single design task, wait for completion, return audio path."""
        assert self._client is not None, "Call connect() first"

        # Submit design task (fn_index=11)
        r1 = self._client.submit(
            text, gender, age, pitch, style, accent, dialect,
            lang, num_step, 2.0, True, speed, 0, True, True,
            fn_index=11,
        ).result()
        _log_status(r1, "design task submitted")

        # Poll queue until done (fn_index=14)
        t0 = time.time()
        max_wait = 300
        while time.time() - t0 < max_wait:
            r2 = self._client.submit(fn_index=14).result()
            df, af = (r2[0], r2[1]) if isinstance(r2, (tuple, list)) and len(r2) > 1 else (r2, None)

            if isinstance(df, dict) and df.get("data"):
                rows = df["data"]
                statuses = [row[2] if len(row) > 2 else "" for row in rows]
                if all("完成" in s or "✅" in s for s in statuses):
                    audio_path = _extract_audio_path(af)
                    if audio_path and os.path.isfile(audio_path):
                        return audio_path, "completed"
                    return None, "completed"
            time.sleep(5)

        return None, "timeout"

    # ------------------------------------------------------------------
    #  Batch dialogue — fn_index=13 (add_dialogue_tasks)
    # ------------------------------------------------------------------

    def submit_dialogue_tasks(
        self,
        script: str,
        characters: list[dict],
        lang: str = "Chinese",
        output_dir: str = "output",
        options: dict | None = None,
    ) -> dict[str, Any]:
        """Submit batch dialogue tasks and wait for completion."""
        assert self._client is not None, "Call connect() first"
        opts = options or {}
        os.makedirs(output_dir, exist_ok=True)

        # Build speaker names and voice presets (max 8)
        sp_names: list[str] = []
        sp_voices: list[str | None] = []
        char_name_map: dict[str, str] = {}
        for char in characters:
            char_name_map[char["id"]] = char.get("name", char["id"])

        default_voice = self.available_voices[0] if self.available_voices else None
        speaker_names = opts.get("speaker_names", [])
        for i in range(8):
            if i < len(speaker_names):
                sn = speaker_names[i]
                sp_names.append(sn)
                matched = _match_preset({"name": sn, "gender": "male", "age": "young_adult"}, self.available_voices)
                sp_voices.append(matched or default_voice)
            else:
                sp_names.append("")
                sp_voices.append(default_voice)

        # Record pre-existing queue row count
        existing_count = 0
        try:
            pre = self._client.submit(fn_index=14).result()
            df_pre = pre[0] if isinstance(pre, (tuple, list)) else pre
            if isinstance(df_pre, dict) and df_pre.get("data"):
                existing_count = len(df_pre["data"])
        except Exception:
            pass

        # Submit dialogue tasks (fn_index=13)
        merge_output = opts.get("merge_output", False)
        r1 = self._client.submit(
            script,
            *sp_names,      # 8 textboxes
            *sp_voices,     # 8 dropdowns
            lang,
            opts.get("instruct", ""),
            opts.get("num_step", 32),
            opts.get("guidance_scale", 2.0),
            opts.get("denoise", True),
            opts.get("speed", 1.0),
            0,              # duration (auto)
            True,           # preprocess
            True,           # postprocess
            opts.get("line_pause_ms", 300),
            merge_output,
            fn_index=13,
        ).result()
        _log_status(r1, "dialogue submitted")

        # Poll queue
        t0 = time.time()
        max_wait = 600
        src = None
        new_rows: list[list] = []
        while time.time() - t0 < max_wait:
            r2 = self._client.submit(fn_index=14).result()
            df, af = (r2[0], r2[1]) if isinstance(r2, (tuple, list)) and len(r2) > 1 else (r2, None)

            if isinstance(df, dict) and df.get("data"):
                rows = df["data"]
                new_rows = rows[existing_count:]
                statuses = [row[2] if len(row) > 2 else "" for row in new_rows]
                if new_rows and all("完成" in s or "✅" in s for s in statuses):
                    audio_path = _extract_audio_path(af)
                    if audio_path and os.path.isfile(audio_path):
                        src = audio_path
                    break
            time.sleep(5)

        # Copy audio if found
        merged_audio_path: str | None = None
        if src and os.path.isfile(src) and os.path.getsize(src) > MIN_VALID_AUDIO_SIZE:
            dst = os.path.join(output_dir, "merged_dialogue.wav")
            shutil.copy2(src, dst)
            merged_audio_path = dst

        # Parse results
        results: list[dict[str, Any]] = []
        success_count = 0
        failure_count = 0
        individual_audio_paths: list[str] = []
        for row in new_rows:
            lid = row[0]
            status = row[2] if len(row) > 2 else ""
            fname = row[4] if len(row) > 4 else ""
            if "完成" in status or "✅" in status:
                success_count += 1
                results.append({
                    "line_id": f"omnivoice-{lid}",
                    "status": "success",
                    "audio_path": fname,
                    "duration_seconds": 0,
                    "error": None,
                })
                if fname:
                    individual_audio_paths.append(fname)
            else:
                failure_count += 1
                results.append({
                    "line_id": f"omnivoice-{lid}",
                    "status": "failed",
                    "audio_path": "",
                    "duration_seconds": 0,
                    "error": status,
                })

        return {
            "results": results,
            "success_count": success_count,
            "failure_count": failure_count,
            "merged_audio_path": merged_audio_path,
            "individual_audio_paths": individual_audio_paths,
        }

    def __getattr__(self, name: str) -> Any:
        """Forward unknown attribute access to gradio_client.Client for backward compat."""
        if self._client and hasattr(self._client, name):
            return getattr(self._client, name)
        raise AttributeError(f"OmniVoiceAdapter has no attribute {name!r}")


# ------------------------------------------------------------------
#  Helpers
# ------------------------------------------------------------------


def _extract_audio_path(audio_val: Any) -> str | None:
    """Extract file path from Gradio Audio component return value."""
    if not audio_val:
        return None
    if isinstance(audio_val, dict):
        return audio_val.get("path") or audio_val.get("value") or None
    if isinstance(audio_val, str):
        return audio_val
    return None


def _log_status(result: Any, label: str = "") -> None:
    """Print a one-liner status from a Gradio multi-output result."""
    if isinstance(result, (tuple, list)):
        if result and isinstance(result[0], dict) and result[0].get("data"):
            rows = result[0]["data"]
            if rows:
                print(f"    {label}: {rows[-1][2] if len(rows[-1]) > 2 else 'ok'}")
                return
        if len(result) > 1 and isinstance(result[1], str):
            print(f"    {label}: {result[1]}")
            return
    print(f"    {label}: {result}")
