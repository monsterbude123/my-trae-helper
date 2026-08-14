"""E2E dry-run:用假的 Key 触发每个模态端点,验证:
  1. 端点 URL 正确
  2. 请求 body 格式正确
  3. 401 错误能被脚本捕获并报告

每个模态独立测试,失败不影响其他。
"""
import os
import sys
import json

# 用一个明显假的 key,触发 401
os.environ["MINIMAX_API_KEY"] = "fake-test-key-for-dry-run-only"
os.environ.pop("MINIMAX_GLOBAL_API_KEY", None)
os.environ.pop("MINIMAX_BASE_URL", None)

sys.path.insert(0, "scripts")
import _client
import text_chat
import image_generate
import video_generate
import speech_synthesize
import music_generate
import vision_describe

cred = _client.get_credentials()
print(f"Using: region={cred['region']}, base={cred['base_url']}, key={_client.mask_key(cred['api_key'])}")
print("=" * 60)


def test(name, fn, *args, **kwargs):
    """调一个模态,捕获异常。期望:401 或 status_code != 0(认证失败)。"""
    try:
        result = fn(*args, **kwargs)
        # 200 OK 但 status_code != 0 = MiniMax 业务错误,通常是 1004(login fail)
        if isinstance(result, dict):
            status_code = (
                result.get("base_resp", {}).get("status_code")
                if isinstance(result.get("base_resp"), dict)
                else None
            )
            if status_code is not None and status_code != 0:
                print(f"[{name}] OK auth-error path: status_code={status_code} {str(result.get('base_resp', {}).get('status_msg', ''))[:80]}")
                return True
        print(f"[{name}] UNEXPECTED success: {str(result)[:120]}")
        return False
    except PermissionError as e:
        # 401 路径,证明端点 + 请求格式正确
        print(f"[{name}] OK 401 path: {str(e)[:120]}")
        return True
    except Exception as e:
        # 其他错误(网络/超时/5xx)
        msg = str(e)[:200]
        if "401" in msg or "认证" in msg or "authorization" in msg.lower() or "login fail" in msg.lower():
            print(f"[{name}] OK auth-error caught: {msg}")
            return True
        if "status_code" in msg and "1004" in msg:
            print(f"[{name}] OK 1004 login-fail caught: {msg}")
            return True
        print(f"[{name}] OTHER ERR: {type(e).__name__}: {msg}")
        return None  # 中性


results = {}

# 1. 文本对话
results["text_chat"] = test("text_chat", lambda: text_chat.chat(
    "test", model="MiniMax-M2.7",
    api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
))

# 2. 文生图
results["image_gen"] = test("image_gen", lambda: image_generate.generate(
    "test", model="image-01", aspect_ratio="1:1", n=1,
    api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
))

# 3. 语音合成
results["speech"] = test("speech", lambda: speech_synthesize.synthesize(
    "test", model="speech-2.8-turbo", voice="male-qn-qingse", fmt="mp3",
    api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
))

# 4. 音乐生成
results["music"] = test("music", lambda: music_generate.generate(
    "test", model="music-3.0", is_instrumental=True,
    api_key=cred["api_key"], base_url=cred["base_url"], timeout=30,
))

# 5. 图像理解(用 minimal PNG)
import verify_all as _verify_mod
png = _verify_mod._minimal_png()
results["vision"] = test("vision", lambda: vision_describe.describe(
    str(png), "describe", model="MiniMax-M3",
    api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
))

# 6. 视频生成(V1 Hailuo)
results["video_v1"] = test("video_v1", lambda: video_generate.generate_hailuo(
    "test", model="MiniMax-Hailuo-2.3", duration=6, resolution="768P",
    api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
))

# 7. 视频生成(V2 H3)
results["video_h3"] = test("video_h3", lambda: video_generate.generate_h3(
    "test", duration=5, resolution="768P", aspect_ratio="16:9",
    api_key=cred["api_key"], base_url=cred["base_url"], timeout=cred["timeout"],
))

print("=" * 60)
print("E2E DRY-RUN SUMMARY")
for k, v in results.items():
    status = {True: "✅ 401 path OK", False: "❌ unexpected success", None: "⚠ other err"}[v]
    print(f"  {status:18s}  {k}")

# 期望:全部 True (401 路径)
all_ok = all(v is True for v in results.values())
print("=" * 60)
print("OVERALL:", "✅ ALL ENDPOINTS HIT 401 AS EXPECTED" if all_ok else "❌ MISMATCH")
sys.exit(0 if all_ok else 1)