"""minimax-multimodal 单元测试 — 不依赖真实 API Key。

覆盖:
  - _client.mask_key 脱敏
  - _client.get_credentials 双区域 + 优先级
  - _client.auth_headers
  - _client.file_to_base64 data URI
  - verify_all._minimal_png
  - text_chat._check_business_error
  - image_generate URL 解析
  - music_generate 响应解析
  - video_generate V1 / H3 端点 + 字段
"""
import os
import sys
import tempfile
from pathlib import Path

# 把 scripts/ 加入 path,所有模态脚本都依赖 _client
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _client  # noqa: E402
import text_chat  # noqa: E402
import image_generate  # noqa: E402
import music_generate  # noqa: E402
import speech_synthesize  # noqa: E402
import video_generate  # noqa: E402
import verify_all  # noqa: E402


def clear_env():
    """清掉所有 Key 相关环境变量。"""
    for k in ("MINIMAX_API_KEY", "MINIMAX_GLOBAL_API_KEY", "MINIMAX_BASE_URL"):
        os.environ.pop(k, None)


# ===== mask_key =====

def test_mask_key_long():
    assert _client.mask_key("sk-12345678") == "*******5678"


def test_mask_key_short():
    # 长度<=4 时全部隐藏
    assert _client.mask_key("ab") == "**"


def test_mask_key_empty():
    assert _client.mask_key("") == "<empty>"


def test_mask_key_none():
    assert _client.mask_key(None) == "<empty>"


# ===== get_credentials =====

def test_get_credentials_no_key_raises():
    clear_env()
    try:
        _client.get_credentials()
    except RuntimeError as e:
        assert "未找到 API Key" in str(e)
        return
    raise AssertionError("Should have raised")


def test_get_credentials_cn():
    clear_env()
    os.environ["MINIMAX_API_KEY"] = "cn-test-key-12345"
    cred = _client.get_credentials()
    assert cred["region"] == "cn"
    assert cred["base_url"] == "https://api.minimaxi.com"
    assert cred["api_key"] == "cn-test-key-12345"


def test_get_credentials_global():
    clear_env()
    os.environ["MINIMAX_GLOBAL_API_KEY"] = "gl-test-key-12345"
    cred = _client.get_credentials()
    assert cred["region"] == "global"
    assert cred["base_url"] == "https://api.minimax.io"
    assert cred["api_key"] == "gl-test-key-12345"


def test_get_credentials_explicit_base_url():
    clear_env()
    os.environ["MINIMAX_GLOBAL_API_KEY"] = "gl-key"
    os.environ["MINIMAX_BASE_URL"] = "https://api.minimax.io/"
    cred = _client.get_credentials()
    assert cred["region"] == "global"
    # 末尾 / 应该被 strip
    assert cred["base_url"] == "https://api.minimax.io"


def test_get_credentials_explicit_cn_url():
    clear_env()
    os.environ["MINIMAX_API_KEY"] = "cn-key"
    os.environ["MINIMAX_BASE_URL"] = "https://api.minimaxi.com/v1"
    cred = _client.get_credentials()
    assert cred["region"] == "cn"


# ===== auth_headers =====

def test_auth_headers_has_both():
    h = _client.auth_headers("test-key")
    assert h["Authorization"] == "Bearer test-key"
    assert h["api-key"] == "test-key"
    assert h["Content-Type"] == "application/json"


def test_auth_headers_no_json():
    h = _client.auth_headers("test-key", json_body=False)
    assert "Content-Type" not in h


# ===== file_to_base64 =====

def test_file_to_base64_png():
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "test.png"
        f.write_bytes(bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000d49444154789c63000100000005000100"
            "0d0a2db40000000049454e44ae426082"
        ))
        uri = _client.file_to_base64(f)
        assert uri.startswith("data:image/png;base64,")
        assert len(uri) > 50


def test_file_to_base64_jpg():
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "test.jpg"
        f.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        uri = _client.file_to_base64(f)
        assert uri.startswith("data:image/jpeg;base64,")


def test_file_to_base64_missing():
    try:
        _client.file_to_base64(Path("/nonexistent/file.png"))
    except FileNotFoundError:
        return
    raise AssertionError("Should have raised")


# ===== verify_all._minimal_png =====

def test_minimal_png():
    png = verify_all._minimal_png()
    assert png.exists()
    assert png.stat().st_size > 0
    # PNG 头部 magic number
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


# ===== text_chat._check_business_error =====

def test_check_business_error_success():
    text_chat._check_business_error({"choices": [], "base_resp": {"status_code": 0}})


def test_check_business_error_no_base_resp():
    text_chat._check_business_error({"choices": []})


def test_check_business_error_login_fail():
    try:
        text_chat._check_business_error({
            "base_resp": {"status_code": 1004, "status_msg": "login fail"}
        })
    except RuntimeError as e:
        assert "1004" in str(e)
        assert "login fail" in str(e)
        return
    raise AssertionError("Should have raised")


# ===== text_chat._extract_content =====

def test_extract_content_direct():
    """正常情况:content 直接含答案。"""
    data = {"choices": [{"message": {"content": "你好"}}]}
    assert text_chat._extract_content(data) == "你好"


def test_extract_content_with_reasoning():
    """M 系列 CoT:有 reasoning 但 content 也有答案 → 返回 content。"""
    data = {
        "choices": [{
            "message": {
                "content": "答案是 2",
                "reasoning_content": "用户问 1+1,我算出来是 2。",
                "reasoning_details": [{"text": "..."}],
            }
        }]
    }
    # 优先取 content
    assert text_chat._extract_content(data) == "答案是 2"


def test_extract_content_empty():
    """content 为空 → 返回空串(CoT 被 max_tokens 截断的信号)。"""
    data = {"choices": [{"message": {"content": ""}}]}
    assert text_chat._extract_content(data) == ""


# ===== image_generate URL parsing =====

def test_image_generate_url_nested():
    """响应格式:{data: {image_urls: [...]}}"""
    captured = {}

    def fake_request(method, url, **kwargs):
        captured["url"] = url
        captured["body"] = kwargs.get("json_body")
        return {"data": {"image_urls": ["https://x.com/a.png", "https://x.com/b.png"]}, "base_resp": {"status_code": 0}}

    orig = _client.request
    _client.request = fake_request
    try:
        urls = image_generate.generate(
            "test", model="image-01", aspect_ratio="1:1", n=2,
            api_key="k", base_url="https://api.minimaxi.com", timeout=30,
        )
        assert urls == ["https://x.com/a.png", "https://x.com/b.png"]
        assert "/v1/image_generation" in captured["url"]
    finally:
        _client.request = orig


def test_image_generate_url_flat():
    """响应格式:{image_urls: [...]}"""
    def fake_request(method, url, **kwargs):
        return {"image_urls": ["https://x.com/a.png"]}

    orig = _client.request
    _client.request = fake_request
    try:
        urls = image_generate.generate(
            "test", api_key="k", base_url="https://x", timeout=30,
        )
        assert urls == ["https://x.com/a.png"]
    finally:
        _client.request = orig


# ===== music_generate 响应解析 =====

def test_music_generate_hex():
    """响应格式:{data: {audio: hex}}"""
    test_hex = "deadbeef"

    def fake_request(method, url, **kwargs):
        return {
            "data": {"audio": test_hex, "status": 2},
            "base_resp": {"status_code": 0},
        }

    orig = _client.request
    _client.request = fake_request
    try:
        audio, mime = music_generate.generate(
            "test prompt", is_instrumental=True,
            output_format="hex",  # 默认 url,必须显式
            api_key="k", base_url="https://x", timeout=30,
        )
        assert audio.hex() == test_hex
        assert mime == "audio/mpeg"
    finally:
        _client.request = orig


def test_music_generate_error_raises():
    def fake_request(method, url, **kwargs):
        return {"base_resp": {"status_code": 1004, "status_msg": "login fail"}}

    orig = _client.request
    _client.request = fake_request
    try:
        try:
            music_generate.generate(
                "test", api_key="k", base_url="https://x", timeout=30,
            )
        except RuntimeError as e:
            assert "1004" in str(e)
            return
        raise AssertionError("Should have raised")
    finally:
        _client.request = orig


# ===== speech_synthesize =====

def test_speech_synthesize_hex():
    test_hex = "00112233"

    def fake_request(method, url, **kwargs):
        return {"data": {"audio": test_hex, "status": 2}, "base_resp": {"status_code": 0}}

    orig = _client.request
    _client.request = fake_request
    try:
        audio = speech_synthesize.synthesize(
            "test", model="speech-2.8-turbo", voice="male-qn-qingse", fmt="mp3",
            api_key="k", base_url="https://x", timeout=30,
        )
        assert audio.hex() == test_hex
    finally:
        _client.request = orig


# ===== video_generate 端点 =====

def test_video_v1_endpoint():
    """V1 走 /v1/video_generation,轮询 /v1/query/.../task_id 拿 URL。"""
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url))
        if method == "POST":
            return {"task_id": "abc123"}
        # GET 轮询 + 文件检索
        if "/v1/files/retrieve" in url:
            # 真实 MiniMax 响应:{file: {file_id, ..., download_url}, base_resp}
            return {
                "file": {
                    "file_id": "f1",
                    "download_url": "https://x.com/video.mp4",
                },
                "base_resp": {"status_code": 0},
            }
        # 轮询 GET → 立即返回 Success(避免测试 hang)
        return {
            "status": "Success",
            "file_id": "f1",
            "base_resp": {"status_code": 0},
        }

    orig_req = _client.request
    orig_download = _client.download_file

    def fake_download(url, out_path, **kwargs):
        out_path.write_bytes(b"fake video")
        return out_path

    _client.request = fake_request
    _client.download_file = fake_download
    try:
        url = video_generate.generate_hailuo(
            "test prompt",
            api_key="k", base_url="https://api.minimaxi.com", timeout=30,
        )
        # POST 必须是 V1 create
        post_urls = [c[1] for c in calls if c[0] == "POST"]
        assert any("/v1/video_generation" in u for u in post_urls)
        # GET 必须是 V1 query
        get_urls = [c[1] for c in calls if c[0] == "GET"]
        assert any("/v1/query/video_generation" in u for u in get_urls)
        # 最终 URL 是 video.mp4
        assert url == "https://x.com/video.mp4"
    finally:
        _client.request = orig_req
        _client.download_file = orig_download


def test_video_h3_endpoint_and_fields():
    """H3 必须走 /v2/ 且字段是 ratio/content 用 image_url。"""
    captured = {}

    def fake_request(method, url, **kwargs):
        if method == "POST":
            captured["post_url"] = url
            captured["post_body"] = kwargs.get("json_body")
            return {"task_id": "h3-task-001"}
        # GET 轮询
        captured["get_url"] = url
        return {
            "task": {
                "status": "succeeded",
                "content": {"url": "https://x.com/h3.mp4"},
            }
        }

    orig = _client.request
    _client.request = fake_request
    try:
        url = video_generate.generate_h3(
            "h3 prompt", duration=5, resolution="2K", aspect_ratio="16:9",
            api_key="k", base_url="https://api.minimaxi.com", timeout=30,
        )
        assert captured["post_url"] == "https://api.minimaxi.com/v2/video_generation"
        assert "/v2/query/video_generation" in captured["get_url"]
        body = captured["post_body"]
        assert body["model"] == "MiniMax-H3"
        assert body["ratio"] == "16:9"  # 不是 aspect_ratio
        assert body["resolution"] == "2K"
        assert body["duration"] == 5
        types = [c["type"] for c in body["content"]]
        assert "text" in types
        assert types[-1] == "text"
        assert url == "https://x.com/h3.mp4"
    finally:
        _client.request = orig


def test_video_h3_with_reference_image():
    captured = {}

    def fake_request(method, url, **kwargs):
        if method == "POST":
            captured["body"] = kwargs.get("json_body")
            return {"task_id": "x"}
        return {
            "task": {"status": "succeeded", "content": {"url": "https://x.com/x.mp4"}}
        }

    orig = _client.request
    _client.request = fake_request
    try:
        png = verify_all._minimal_png()
        video_generate.generate_h3(
            "test", reference_image=png, duration=5, resolution="768P", aspect_ratio="1:1",
            api_key="k", base_url="https://api.minimaxi.com", timeout=30,
        )
        body = captured["body"]
        image_items = [c for c in body["content"] if c.get("role") == "reference_image"]
        assert len(image_items) == 1
        assert image_items[0]["type"] == "image_url"  # 不是 image
        assert image_items[0]["image_url"].startswith("data:image/png;base64,")
    finally:
        _client.request = orig


# ===== output_path =====

def test_output_path_default():
    p = _client.output_path("image", "png")
    assert p.name.startswith("image_")
    assert p.suffix == ".png"
    assert "output" in str(p)


def test_output_path_explicit():
    p = _client.output_path("video", "mp4", "/tmp/my_video.mp4")
    assert str(p).endswith("my_video.mp4")


if __name__ == "__main__":
    # 简易运行(也可 `pytest tests/`)
    import traceback
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS  {t.__name__}")
        except Exception:
            failed += 1
            print(f"  FAIL  {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)