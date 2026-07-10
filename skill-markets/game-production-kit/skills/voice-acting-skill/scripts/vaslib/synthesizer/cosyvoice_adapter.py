from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from typing import Callable

import httpx

COSYVOICE_MODE_INSTRUCT = "自然语言控制"
COSYVOICE_MODE_PRETRAINED = "预训练音色"
COSYVOICE_MODE_CLONE_3S = "3s极速复刻"
COSYVOICE_MODE_CROSS_LINGUAL = "跨语言复刻"

GRADIO_FILE_URL_PREFIX = "/gradio_api/file="
GRADIO_STREAM_URL_PREFIX = "/gradio_api/stream/"

# CosyVoice3 zero_shot 端点要求 prompt_text 含 <|endofprompt|> 标记（token id 151646）。
# 这里给出 v3 支持的方言/情感指令模板，与 cosyvoice/utils/common.py::instruct_list 对齐。
# 模板必须以 "You are a helpful assistant. " 开头并以 "<|endofprompt|>" 结尾。
DEFAULT_DIALECT_INSTRUCT: str = "You are a helpful assistant.<|endofprompt|>"

# 中文方言/情感关键词 → v3 instruct 模板
DIALECT_INSTRUCT_MAP: dict[str, str] = {
    "川渝": "You are a helpful assistant. 请用四川话表达。<|endofprompt|>",
    "渝普": "You are a helpful assistant. 请用四川话表达。<|endofprompt|>",
    "四川话": "You are a helpful assistant. 请用四川话表达。<|endofprompt|>",
    "广东": "You are a helpful assistant. 请用广东话表达。<|endofprompt|>",
    "粤语": "You are a helpful assistant. 请用广东话表达。<|endofprompt|>",
    "东北": "You are a helpful assistant. 请用东北话表达。<|endofprompt|>",
    "甘肃": "You are a helpful assistant. 请用甘肃话表达。<|endofprompt|>",
    "贵州": "You are a helpful assistant. 请用贵州话表达。<|endofprompt|>",
    "河南": "You are a helpful assistant. 请用河南话表达。<|endofprompt|>",
    "湖北": "You are a helpful assistant. 请用湖北话表达。<|endofprompt|>",
    "湖南": "You are a helpful assistant. 请用湖南话表达。<|endofprompt|>",
    "江西": "You are a helpful assistant. 请用江西话表达。<|endofprompt|>",
    "闽南": "You are a helpful assistant. 请用闽南话表达。<|endofprompt|>",
    "宁夏": "You are a helpful assistant. 请用宁夏话表达。<|endofprompt|>",
    "山西": "You are a helpful assistant. 请用山西话表达。<|endofprompt|>",
    "陕西": "You are a helpful assistant. 请用陕西话表达。<|endofprompt|>",
    "山东": "You are a helpful assistant. 请用山东话表达。<|endofprompt|>",
    "上海": "You are a helpful assistant. 请用上海话表达。<|endofprompt|>",
    "天津": "You are a helpful assistant. 请用天津话表达。<|endofprompt|>",
    "云南": "You are a helpful assistant. 请用云南话表达。<|endofprompt|>",
    "北京": "You are a helpful assistant. 请用北京话表达。<|endofprompt|>",
    "快": "You are a helpful assistant. 请用尽可能快地语速说一句话。<|endofprompt|>",
    "慢": "You are a helpful assistant. 请用尽可能慢地语速说一句话。<|endofprompt|>",
    "大声": "You are a helpful assistant. Please say a sentence as loudly as possible.<|endofprompt|>",
    "小声": "You are a helpful assistant. Please say a sentence in a very soft voice.<|endofprompt|>",
    "开心": "You are a helpful assistant. 请非常开心地说一句话。<|endofprompt|>",
    "悲伤": "You are a helpful assistant. 请非常伤心地说一句话。<|endofprompt|>",
    "生气": "You are a helpful assistant. 请非常生气地说一句话。<|endofprompt|>",
}


def _pick_dialect_instruct(instruct_text: str, ref_text: str = "") -> str:
    """根据行 instruct_text / ref_text 关键词挑选 v3 方言 prompt 模板。

    优先级：DIALECT_INSTRUCT_MAP 关键词命中 > 默认模板。
    命中多个时取第一个出现的方言。
    """
    haystack = (instruct_text or "") + " " + (ref_text or "")
    for key, tmpl in DIALECT_INSTRUCT_MAP.items():
        if key in haystack:
            return tmpl
    return DEFAULT_DIALECT_INSTRUCT


class CosyVoiceAdapter:
    def __init__(self, url: str, default_prompt_wav: str | None = None):
        self.url = url.rstrip("/")
        self.default_prompt_wav = default_prompt_wav
        self.gradio_tmp_dir = os.path.join(
            os.environ.get("TMPDIR", os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))),
            "gradio",
        )

    def connect(self) -> None:
        """No persistent connection needed for HTTP API approach."""
        pass

    # ------------------------------------------------------------------
    # 1. prompt wav 上传
    # ------------------------------------------------------------------
    def _upload_prompt_wav(self, client: httpx.Client, wav_path: str) -> str:
        """把本地 wav 上传到 Gradio，返回 server 端路径。"""
        with open(wav_path, "rb") as f:
            r = client.post(
                f"{self.url}/gradio_api/upload",
                files={"files": (os.path.basename(wav_path), f, "audio/wav")},
                timeout=30.0,
            )
        r.raise_for_status()
        paths = r.json()
        if not paths:
            raise RuntimeError(f"Gradio upload returned empty: {r.text[:200]}")
        return paths[0]

    # ------------------------------------------------------------------
    # 2. SSE 事件流 → 提取 m3u8 URL
    # ------------------------------------------------------------------
    def _extract_m3u8_url_from_sse(self, client: httpx.Client, event_id: str) -> tuple[str, str]:
        """读取 Gradio SSE 流，找到 'complete' 事件并返回 m3u8 URL 与最终事件名。

        注意 Gradio SSE 顺序为 event:complete → data:[...]，因此 break 在 data 行之后。
        """
        sse_url = f"{self.url}/gradio_api/call/generate_audio/{event_id}"
        last_event = ""
        m3u8_url = ""

        with client.stream("GET", sse_url, timeout=300.0) as resp:
            resp.raise_for_status()
            done = False
            for line in resp.iter_lines():
                line = line.strip()
                if done:
                    break
                if line.startswith("event: "):
                    last_event = line[len("event: "):].strip()
                    if last_event in ("complete", "error"):
                        done = True
                elif line.startswith("data: "):
                    try:
                        data = json.loads(line[len("data: "):].strip())
                    except (json.JSONDecodeError, ValueError):
                        continue
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                if item.get("is_stream") and item.get("url"):
                                    m3u8_url = item["url"]
                                elif item.get("path", "").endswith(".wav") and item.get("url"):
                                    m3u8_url = item["url"]
                    # style A: data 在 complete 前，读到 data 可能就够了
                    # style B: data 在 complete 后，done 标记后读 data 就 break
                    if done:
                        break

        return m3u8_url, last_event

    # ------------------------------------------------------------------
    # 3. m3u8 解析 + aac 分片下载
    # ------------------------------------------------------------------
    def _download_m3u8_audio(self, client: httpx.Client, m3u8_url: str, out_path: str) -> int:
        """下载 m3u8 playlist 中所有分片并 ffmpeg 合成 wav (24kHz mono s16)。

        返回写入字节数。"""
        r = client.get(m3u8_url, timeout=30.0)
        r.raise_for_status()
        playlist = r.text
        # m3u8 中分片相对路径：解析为绝对 URL
        base = m3u8_url.rsplit("/", 1)[0] + "/"
        segment_urls: list[str] = []
        for raw in playlist.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("http://") or line.startswith("https://"):
                segment_urls.append(line)
            else:
                segment_urls.append(base + line)

        if not segment_urls:
            raise RuntimeError(f"m3u8 has no segments: {playlist[:200]}")

        # 拼接到临时 aac 文件
        tmp_dir = tempfile.mkdtemp(prefix="cosyvoice_aac_")
        try:
            concat_path = os.path.join(tmp_dir, "concat.aac")
            with open(concat_path, "wb") as out_f:
                for seg_url in segment_urls:
                    seg = client.get(seg_url, timeout=60.0)
                    seg.raise_for_status()
                    out_f.write(seg.content)

            # ffmpeg 转 wav (24kHz mono s16 PCM, 与 CosyVoice3 输出一致)
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            cmd = [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", concat_path,
                "-ar", "24000", "-ac", "1", "-acodec", "pcm_s16le",
                out_path,
            ]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode('utf-8', errors='ignore')[:300]}")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        return os.path.getsize(out_path) if os.path.isfile(out_path) else 0

    # ------------------------------------------------------------------
    # 4. 端到端单句合成
    # ------------------------------------------------------------------
    def call_gradio_api(
        self,
        tts_text: str,
        mode: str,
        sft_dropdown: str,
        prompt_text: str,
        prompt_wav_path: str,
        instruct_text: str,
        speed: float,
        output_wav_path: str,
    ) -> dict:
        """POST 到 Gradio /generate_audio，等待 SSE complete，下载 aac 分片，ffmpeg 转 wav。

        Returns:
            {"success": bool, "error": str | None, "audio_path": str | None, "size": int}
        """
        # 上传 prompt wav（3s极速复刻 / 跨语言复刻 / 预训练音色三种 mode 都可能需要）
        try:
            with httpx.Client(timeout=60.0) as client:
                server_path = self._upload_prompt_wav(client, prompt_wav_path)
        except Exception as exc:
            return {"success": False, "error": f"upload prompt wav: {exc}", "audio_path": None, "size": 0}

        # 构造 Gradio payload（参数顺序与 webui.py generate_audio 一致）
        file_data = {"path": server_path, "meta": {"_type": "gradio.FileData"}}
        payload = {
            "data": [
                tts_text,           # 0 tts_text
                mode,               # 1 mode
                sft_dropdown,       # 2 sft_dropdown
                prompt_text,        # 3 prompt_text
                file_data,          # 4 prompt_wav_upload (FileData dict)
                None,               # 5 prompt_wav_record
                instruct_text,      # 6 instruct_text
                0,                  # 7 seed
                False,              # 8 stream
                speed,              # 9 speed
            ]
        }

        # 提交 + SSE
        try:
            with httpx.Client(timeout=300.0) as client:
                submit = client.post(
                    f"{self.url}/gradio_api/call/generate_audio", json=payload
                )
                submit.raise_for_status()
                event_id = submit.json().get("event_id")
                if not event_id:
                    return {"success": False, "error": f"no event_id: {submit.text[:200]}", "audio_path": None, "size": 0}

                m3u8_url, last_event = self._extract_m3u8_url_from_sse(client, event_id)
                if last_event == "error" or not m3u8_url:
                    return {"success": False, "error": f"SSE ended with {last_event}, m3u8={m3u8_url[:100]}", "audio_path": None, "size": 0}

                # m3u8 URL 可能是 http(s)://... 也可能是 gradio 相对路径。
                # 注意：Gradio 在 SSE payload 里给的 url 经常含 "gradio_a/gradio_api/stream/" 前缀，
                # 但实际文件在 "gradio_api/stream/"（gradio_a 是 Gradio 反代的 app mount 路径前缀，
                # 浏览器/客户端访问静态资源时不需要这层），所以要去掉 gradio_a/ 前缀。
                if m3u8_url.startswith("http://") or m3u8_url.startswith("https://"):
                    stream_root = m3u8_url
                else:
                    stream_root = f"{self.url}{m3u8_url}"
                stream_root = stream_root.replace("/gradio_a/gradio_api/stream/", "/gradio_api/stream/")
                size = self._download_m3u8_audio(client, stream_root, output_wav_path)
        except Exception as exc:
            return {"success": False, "error": str(exc)[:300], "audio_path": None, "size": 0}

        if size < 1000:
            return {"success": False, "error": f"output too small ({size}B)", "audio_path": output_wav_path, "size": size}

        return {"success": True, "error": None, "audio_path": output_wav_path, "size": size}

    # ------------------------------------------------------------------
    # 5. 高级 API：接收 CosyVoiceLine 字典，返回合成结果
    # ------------------------------------------------------------------
    def build_gradio_params(self, line: dict) -> dict:
        """从 CosyVoiceLine 字典生成 Gradio 端点参数。

        v3 优先走 "3s极速复刻" 端点（webui.py 唯一能跨方言/情感控制的模式）：
        - prompt_text 必须是 v3 dialect instruct 模板（带 <|endofprompt|>）
        - prompt_wav 从 ref_audio_path / default_prompt_wav 取
        - spk_id (SFT 音色) 仅在 v3 SFT 列表非空时使用
        """
        instruct_text = line.get("instruct_text", line.get("instructText", "")) or ""
        ref_text = line.get("ref_text", line.get("refText", "")) or ""
        ref_audio_path = line.get("ref_audio_path", line.get("refAudioPath")) or self.default_prompt_wav
        spk_id = line.get("spk_id", line.get("spkId", "")) or ""

        # 方言 prompt_text：必须以 "You are a helpful assistant." 开头、以 <|endofprompt|> 结尾
        dialect_prompt = _pick_dialect_instruct(instruct_text, ref_text)

        # 默认走 3s极速复刻（webui.py 唯一支持 v3 跨方言的端点）
        return {
            "mode": COSYVOICE_MODE_CLONE_3S,
            "sft_dropdown": "",
            "prompt_text": dialect_prompt,
            "prompt_wav_path": ref_audio_path,
            "instruct_text": "",
        }

    def synthesize_line(self, line: dict, output_dir: str) -> dict:
        """合成单条台词并保存 wav 文件。"""
        params = self.build_gradio_params(line)

        line_id = line.get("line_id", line.get("lineId", ""))
        tts_text = line.get("tts_text", line.get("ttsText", "")) or ""
        speed = float(line.get("speed", 1.0) or 1.0)

        prompt_wav_path = params.get("prompt_wav_path")
        if not prompt_wav_path or not os.path.isfile(prompt_wav_path):
            return {
                "line_id": line_id,
                "status": "failed",
                "audio_path": "",
                "duration_seconds": 0.0,
                "error": f"prompt_wav not found: {prompt_wav_path}",
            }

        os.makedirs(output_dir, exist_ok=True)
        audio_path = os.path.join(output_dir, f"{line_id}.wav")

        try:
            result = self.call_gradio_api(
                tts_text=tts_text,
                mode=params["mode"],
                sft_dropdown=params["sft_dropdown"],
                prompt_text=params["prompt_text"],
                prompt_wav_path=prompt_wav_path,
                instruct_text=params["instruct_text"],
                speed=speed,
                output_wav_path=audio_path,
            )
        except Exception as exc:
            return {
                "line_id": line_id,
                "status": "failed",
                "audio_path": "",
                "duration_seconds": 0.0,
                "error": str(exc)[:200],
            }

        if not result["success"]:
            return {
                "line_id": line_id,
                "status": "failed",
                "audio_path": "",
                "duration_seconds": 0.0,
                "error": result.get("error") or "unknown",
            }

        return {
            "line_id": line_id,
            "status": "success",
            "audio_path": audio_path,
            "duration_seconds": self.estimate_duration_from_size(result["size"]),
            "error": None,
        }

    def synthesize_batch(
        self,
        lines: list[dict],
        output_dir: str,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> dict:
        """顺序合成一个 batch。"""
        if on_progress is None:
            on_progress = lambda completed, total: None

        results = []
        success_count = 0
        failure_count = 0
        total = len(lines)

        for i, line in enumerate(lines):
            result = self.synthesize_line(line, output_dir)
            results.append(result)
            if result["status"] == "success":
                success_count += 1
            else:
                failure_count += 1
                line_id = line.get("line_id", line.get("lineId", ""))
                err = (result.get("error") or "")[:80]
                print(f"    ⚠ {line_id}: {err}")
            on_progress(i + 1, total)

        return {
            "results": results,
            "success_count": success_count,
            "failure_count": failure_count,
        }

    @staticmethod
    def estimate_duration_from_size(file_size: int) -> float:
        """从 wav 文件大小估算时长（24000 Hz / 16-bit / mono）。"""
        wav_header_size = 44
        bytes_per_sample = 2
        sample_rate = 24000
        channels = 1
        data_size = max(file_size - wav_header_size, 0)
        samples = data_size / (bytes_per_sample * channels)
        return round(samples / sample_rate * 100) / 100

    def health_check(self) -> bool:
        """检查 Gradio API 是否可达。"""
        try:
            resp = httpx.get(f"{self.url}/gradio_api/info", timeout=10.0)
            return resp.is_success
        except httpx.HTTPError:
            return False
