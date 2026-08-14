"""诊断 vision 为什么返回空字符串。"""
import os, sys, json
os.environ["MINIMAX_API_KEY"] = "fake-test-key"
sys.path.insert(0, "scripts")
import _client, vision_describe, verify_all

cred = _client.get_credentials()
png = verify_all._minimal_png()
print("PNG path:", png, png.stat().st_size, "bytes")

# 直接调用看完整响应
import requests
url = cred["base_url"] + "/v1/text/chatcompletion_v2"
body = {
    "model": "MiniMax-M3",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "describe"},
            {"type": "image_url", "image_url": {"url": _client.file_to_base64(png)}},
        ],
    }],
    "max_tokens": 64,
}
headers = _client.auth_headers(cred["api_key"])
print("\nRequest body model:", body["model"])
print("Image data URI length:", len(body["messages"][0]["content"][1]["image_url"]["url"]))

resp = requests.post(url, json=body, headers=headers, timeout=cred["timeout"])
print(f"\nHTTP {resp.status_code}")
print("Raw body:", resp.text[:500])
try:
    j = resp.json()
    print("JSON:", json.dumps(j, ensure_ascii=False)[:500])
except Exception as e:
    print("JSON parse err:", e)