"""
Qwen-TTS adapter — 支持本地 Gradio 模式 + 云端 DashScope 模式。

本地模式:
  调 `http://<host>:<port>/gradio_api/call/run_instruct` (SSE)，
  读取本地文件路径后拷贝 wav。

云端模式:
  调 `https://dashscope.aliyuncs.com/api/v1/services/audio/tts/generation`，
  需要 DASHSCOPE_API_KEY。
"""

from __future__ import annotations

import json
import os
import shutil
import time
from typing import Callable

import httpx

DASHSCOPE_BASE = "https://dashscope.aliyuncs.com/api/v1"
QWEN_TTS_DEFAULT_MODEL = "qwen3-tts-flash"


class QwenTtsAdapter:
    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        model: str = QWEN_TTS_DEFAULT_MODEL,
    ):
        """若 url 给出 → 本地 Gradio 模式；否则 → DashScope 云端模式。"""
        self.local_url = url.rstrip("/") if url else None
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_TTS_API_KEY")
        self.model = model
        self.base = DASHSCOPE_BASE

    # ------------------------------------------------------------------
    # 连接 / 健康检查
    # ------------------------------------------------------------------

    def connect(self) -> None:
        if self.local_url:
            # 本地模式：health_check 会验证
            return
        if not self.api_key:
            raise RuntimeError("DASHSCOPE_API_KEY not set (local url also not set)")

    def health_check(self) -> bool:
        if self.local_url:
            try:
                resp = httpx.get(f"{self.local_url}/gradio_api/info", timeout=10.0)
                return resp.is_success
            except httpx.HTTPError:
                return False
        return bool(self.api_key)

    # ------------------------------------------------------------------
    # 本地 Gradio 模式
    # ------------------------------------------------------------------

    def _local_synthesize(self, line: dict, output_dir: str) -> dict:
        """本地 Gradio /run_instruct 合成。"""
        line_id = line.get("line_id", "")
        text = line.get("annotated_text") or line.get("text") or ""
        voice = line.get("voice", "Vivian")
        instruct = line.get("instruct") or ""

        url = self.local_url
        out_path = os.path.join(output_dir, f"{line_id}.wav")
        t0 = time.time()

        payload = {"data": [text, "Auto", voice, instruct]}
        try:
            with httpx.Client(timeout=300.0) as c:
                # 提交任务
                r = c.post(f"{url}/gradio_api/call/run_instruct", json=payload)
                r.raise_for_status()
                eid = r.json()["event_id"]

                # 读 SSE
                sse = c.get(f"{url}/gradio_api/call/run_instruct/{eid}", timeout=300.0)
                sse.raise_for_status()
                audio_data = None
                got_complete = False
                for ln in sse.iter_lines():
                    ln = ln.strip()
                    if ln.startswith("event: complete") or ln.startswith("event: error"):
                        got_complete = True
                    elif ln.startswith("data: ") and got_complete:
                        try:
                            d = json.loads(ln[6:])
                        except json.JSONDecodeError:
                            continue
                        if isinstance(d, list) and d and isinstance(d[0], dict):
                            audio_data = d[0]
                        break

            if not audio_data:
                return self._failed(line_id, "no audio in SSE response", t0)

            src = audio_data.get("path", "")
            if not src or not os.path.isfile(src):
                return self._failed(line_id, f"audio file not found: {src[:100]}", t0)

            os.makedirs(output_dir, exist_ok=True)
            shutil.copy2(src, out_path)

        except Exception as exc:
            return self._failed(line_id, str(exc)[:200], t0)

        size = os.path.getsize(out_path) if os.path.isfile(out_path) else 0
        if size < 1000:
            return self._failed(line_id, f"output too small ({size}B)", t0)

        elapsed = time.time() - t0
        return {
            "line_id": line_id,
            "status": "success",
            "audio_path": out_path,
            "size": size,
            "duration_seconds": round(size / (24000 * 2), 2),
            "elapsed": round(elapsed, 2),
            "error": None,
        }

    # ------------------------------------------------------------------
    # 云端 DashScope 模式
    # ------------------------------------------------------------------

    def _cloud_synthesize(self, line: dict, output_dir: str) -> dict:
        """DashScope REST API 合成。"""
        line_id = line.get("line_id", "")
        text = line.get("annotated_text") or line.get("text") or ""
        voice = line.get("voice", "Cherry")
        speed = float(line.get("speed", 1.0) or 1.0)
        language_type = line.get("language_type", "Chinese")

        api_url = f"{self.base}/services/audio/tts/generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": {"text": text, "voice": voice, "language_type": language_type, "speed": speed},
            "parameters": {"format": "wav"},
        }

        t0 = time.time()
        try:
            with httpx.Client(timeout=120.0) as c:
                r = c.post(api_url, headers=headers, json=payload)
                r.raise_for_status()
                body = r.json()
        except Exception as exc:
            return self._failed(line_id, f"submit: {exc}", t0)

        if "output" not in body:
            return self._failed(line_id, f"no output: {json.dumps(body)[:200]}", t0)

        audio_url = (body.get("output") or {}).get("audio", {}).get("url")
        if not audio_url:
            return self._failed(line_id, f"no audio url: {json.dumps(body)[:200]}", t0)

        try:
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, f"{line_id}.wav")
            with httpx.Client(timeout=120.0) as c:
                with c.stream("GET", audio_url) as resp:
                    resp.raise_for_status()
                    with open(out_path, "wb") as f:
                        for chunk in resp.iter_bytes():
                            f.write(chunk)
        except Exception as exc:
            return self._failed(line_id, f"download: {exc}", t0)

        size = os.path.getsize(out_path) if os.path.isfile(out_path) else 0
        if size < 1000:
            return self._failed(line_id, f"output too small ({size}B)", t0)

        elapsed = time.time() - t0
        return {
            "line_id": line_id,
            "status": "success",
            "audio_path": out_path,
            "size": size,
            "duration_seconds": round(size / (24000 * 2), 2),
            "elapsed": round(elapsed, 2),
            "error": None,
        }

    # ------------------------------------------------------------------
    # 统一接口
    # ------------------------------------------------------------------

    def synthesize_line(self, line: dict, output_dir: str) -> dict:
        """合成单条台词。自动选本地/云端模式。"""
        if self.local_url:
            return self._local_synthesize(line, output_dir)
        return self._cloud_synthesize(line, output_dir)

    def synthesize_batch(
        self,
        lines: list[dict],
        output_dir: str,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> dict:
        if on_progress is None:
            on_progress = lambda c, t: None

        results = []
        success = 0
        failure = 0
        t0 = time.time()
        for i, line in enumerate(lines):
            r = self.synthesize_line(line, output_dir)
            results.append(r)
            if r["status"] == "success":
                success += 1
            else:
                failure += 1
                err = (r.get("error") or "")[:80]
                print(f"    ⚠ {r.get('line_id', '')}: {err}")
            on_progress(i + 1, len(lines))
        total = time.time() - t0

        return {
            "results": results,
            "success_count": success,
            "failure_count": failure,
            "total_elapsed": round(total, 2),
            "avg_per_line": round(total / len(lines), 2) if lines else 0,
        }

    @staticmethod
    def _failed(line_id: str, error: str, t0: float | None = None) -> dict:
        return {
            "line_id": line_id,
            "status": "failed",
            "audio_path": "",
            "size": 0,
            "duration_seconds": 0.0,
            "elapsed": round((time.time() - t0), 2) if t0 else 0.0,
            "error": error[:200],
        }
