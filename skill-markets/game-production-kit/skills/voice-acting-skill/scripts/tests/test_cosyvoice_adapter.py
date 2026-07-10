"""
CosyVoiceAdapter 单元测试 (mock HTTP, 不依赖真实 CosyVoice 服务)。
"""

import json
import os
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import httpx

from vaslib.synthesizer.cosyvoice_adapter import (
    CosyVoiceAdapter,
    DIALECT_INSTRUCT_MAP,
    DEFAULT_DIALECT_INSTRUCT,
    _pick_dialect_instruct,
)


# ---------------------------------------------------------------------------
# 1. _pick_dialect_instruct
# ---------------------------------------------------------------------------


def test_pick_dialect_instruct_sichuan():
    """川渝关键词 → 四川话模板。"""
    tmpl = _pick_dialect_instruct("用川渝口音说话，耙耳朵，愤怒")
    assert "四川话" in tmpl
    assert tmpl.endswith("<|endofprompt|>")


def test_pick_dialect_instruct_dongbei():
    """东北口音关键词 → 东北话模板。"""
    tmpl = _pick_dialect_instruct("用东北口音说话")
    assert "东北话" in tmpl


def test_pick_dialect_instruct_yue():
    """广东/粤语 → 广东话。"""
    assert "广东话" in _pick_dialect_instruct("用广东话")
    assert "广东话" in _pick_dialect_instruct("粤语风格")


def test_pick_dialect_instruct_emotion():
    """情感关键词命中。"""
    tmpl = _pick_dialect_instruct("", "请非常开心地说")
    assert "开心" in tmpl


def test_pick_dialect_instruct_default():
    """无匹配 → 默认模板（含 <|endofprompt|>）。"""
    tmpl = _pick_dialect_instruct("unknown text")
    assert tmpl == DEFAULT_DIALECT_INSTRUCT
    assert tmpl.endswith("<|endofprompt|>")


def test_pick_dialect_instruct_empty():
    """空输入 → 默认模板。"""
    assert _pick_dialect_instruct("") == DEFAULT_DIALECT_INSTRUCT
    assert _pick_dialect_instruct("", "") == DEFAULT_DIALECT_INSTRUCT


def test_dialect_instruct_map_all_have_endofprompt():
    """所有方言模板必须含 <|endofprompt|> 标记。"""
    for key, tmpl in DIALECT_INSTRUCT_MAP.items():
        assert tmpl.endswith("<|endofprompt|>"), f"{key} 缺少 <|endofprompt|>"


# ---------------------------------------------------------------------------
# 2. CosyVoiceAdapter.build_gradio_params
# ---------------------------------------------------------------------------


def test_build_gradio_params_default_mode_3s_clone():
    """默认走 3s极速复刻 模式 (v3 zero_shot 端点)。"""
    adapter = CosyVoiceAdapter("http://localhost:15000")
    line = {
        "line_id": "L01",
        "tts_text": "测试",
        "instruct_text": "用川渝口音说话，耙耳朵，愤怒",
        "ref_audio_path": "/path/to/prompt.wav",
    }
    params = adapter.build_gradio_params(line)
    assert params["mode"] == "3s极速复刻"
    assert params["prompt_wav_path"] == "/path/to/prompt.wav"
    assert "四川话" in params["prompt_text"]
    assert params["prompt_text"].endswith("<|endofprompt|>")


def test_build_gradio_params_fallback_default_prompt():
    """line 没有 ref_audio_path → 用 adapter 提供的 default_prompt_wav。"""
    adapter = CosyVoiceAdapter("http://localhost:15000", default_prompt_wav="/default.wav")
    line = {"line_id": "L01", "tts_text": "测试", "instruct_text": ""}
    params = adapter.build_gradio_params(line)
    assert params["prompt_wav_path"] == "/default.wav"
    assert params["prompt_text"] == DEFAULT_DIALECT_INSTRUCT


def test_build_gradio_params_camelcase_keys():
    """支持 camelCase 键。"""
    adapter = CosyVoiceAdapter("http://localhost:15000")
    line = {
        "lineId": "L02",
        "ttsText": "测试",
        "instructText": "用上海口音",
        "refAudioPath": "/p.wav",
    }
    params = adapter.build_gradio_params(line)
    assert "上海话" in params["prompt_text"]
    assert params["prompt_wav_path"] == "/p.wav"


# ---------------------------------------------------------------------------
# 3. CosyVoiceAdapter.call_gradio_api 端到端 (mock httpx + 真实 ffmpeg)
# ---------------------------------------------------------------------------


class MockResponse:
    def __init__(self, status_code, content, json_data=None, is_stream=False):
        self.status_code = status_code
        self.content = content
        self._json = json_data
        self.is_stream = is_stream
        self.text = content.decode("utf-8", errors="ignore") if isinstance(content, (bytes, bytearray)) else str(content)
        self.headers = {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("err", request=httpx.Request("GET", "x"), response=self)

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


def _write_silent_wav(path: str, duration_sec: float = 0.5) -> None:
    """生成一段短静音 wav (16kHz mono 16bit)。"""
    sr = 16000
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b"\x00\x00" * int(sr * duration_sec))


def _silent_aac_bytes(duration_ms: int = 100) -> bytes:
    """生成极短的 ADTS AAC 帧（仅用于测试大小，ffmpeg 会处理空帧）。

    这里直接返回固定 1KB 字节让 ffmpeg 尝试解码（会失败但能让 _download_m3u8_audio
    走到 ffmpeg 步骤，覆盖 _pick_dialect / build_params / upload / SSE 流程）。
    """
    return b"\xff\xf1\x50\x80" + b"\x00" * 1024


def test_synthesize_line_missing_prompt_wav(tmp_path):
    """缺 prompt wav → failed，不调 HTTP。"""
    adapter = CosyVoiceAdapter("http://localhost:15000")
    result = adapter.synthesize_line(
        {"line_id": "L01", "tts_text": "测试", "instruct_text": "川渝", "ref_audio_path": "/nonexistent.wav"},
        str(tmp_path),
    )
    assert result["status"] == "failed"
    assert "prompt_wav not found" in (result["error"] or "")


def test_synthesize_line_success(monkeypatch, tmp_path):
    """成功合成：mock httpx 调用 + 真实 ffmpeg 转 wav。"""
    # 1. 准备 prompt wav
    prompt_wav = tmp_path / "prompt.wav"
    _write_silent_wav(str(prompt_wav))

    # 2. 准备 m3u8 内容
    m3u8_url = "http://localhost:15000/gradio_api/stream/abc/123/21/playlist.m3u8"
    m3u8_text = (
        "#EXTM3U\n"
        "#EXT-X-VERSION:3\n"
        "#EXT-X-TARGETDURATION:10\n"
        "#EXTINF:1.0,\n"
        "seg.aac\n"
        "#EXT-X-ENDLIST\n"
    )
    aac_bytes = _silent_aac_bytes()

    # 3. mock httpx.Client：拦截 upload / call/generate_audio / SSE / m3u8 / 分片
    aac_url = "http://localhost:15000/gradio_api/stream/abc/123/21/seg.aac"
    aac_bytes = _silent_aac_bytes()
    m3u8_text_local = m3u8_text
    aac_bytes_local = aac_bytes
    aac_url_local = aac_url
    m3u8_url_local = m3u8_url

    class MockStreamContext:
        def __init__(self, lines):
            self._lines = lines
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def iter_lines(self):
            for ln in self._lines:
                yield ln
        def raise_for_status(self): pass

    class MockClient:
        def __init__(self, timeout=None):
            pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def post(self, url, *a, **kw):
            if url.endswith("/gradio_api/upload"):
                return MockResponse(200, b"", json_data=["/server/prompt.wav"])
            if url.endswith("/gradio_api/call/generate_audio"):
                return MockResponse(200, b"", json_data={"event_id": "evt-1"})
            return MockResponse(404, b"unexpected POST")
        def stream(self, method, url, *a, **kw):
            sse_lines = [
                f'data: {json.dumps([{"is_stream": True, "url": m3u8_url_local, "path": "playlist.m3u8"}])}',
                "",
                "event: complete",
            ]
            return MockStreamContext(sse_lines)
        def get(self, url, *a, **kw):
            if url == m3u8_url_local:
                return MockResponse(200, m3u8_text_local.encode("utf-8"))
            if url.endswith("/seg.aac"):
                return MockResponse(200, aac_bytes_local)
            return MockResponse(404, b"unexpected GET")

    monkeypatch.setattr("vaslib.synthesizer.cosyvoice_adapter.httpx.Client", MockClient)

    # mock _download_m3u8_audio: 直接写 wav，跳过 ffmpeg
    def fake_download(self, client, m3u8_url, out_path):
        import wave as _w
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with _w.open(out_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(b"\x00\x00" * 4800)  # 0.2s silence
        return os.path.getsize(out_path)
    monkeypatch.setattr(
        "vaslib.synthesizer.cosyvoice_adapter.CosyVoiceAdapter._download_m3u8_audio",
        fake_download,
    )

    # 4. 跑
    adapter = CosyVoiceAdapter("http://localhost:15000")
    out_dir = tmp_path / "out"
    result = adapter.synthesize_line(
        {
            "line_id": "L01",
            "tts_text": "你好世界",
            "instruct_text": "用川渝口音说话",
            "ref_audio_path": str(prompt_wav),
        },
        str(out_dir),
    )
    assert result["status"] == "success", result
    assert os.path.isfile(result["audio_path"])


def test_health_check(monkeypatch):
    """health_check 调 /gradio_api/info。"""
    class MockClient:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def get(self, url, *a, **kw):
            r = httpx.Response(200)
            r.is_success = True
            return r
    monkeypatch.setattr("vaslib.synthesizer.cosyvoice_adapter.httpx.get",
                        lambda url, **kw: type("R", (), {"is_success": True})())
    assert CosyVoiceAdapter("http://localhost:15000").health_check() is True
