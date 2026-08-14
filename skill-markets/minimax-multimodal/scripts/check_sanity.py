"""临时 sanity check — 验证所有脚本可导入 + mask_key 函数正确。"""
import sys
sys.path.insert(0, 'scripts')

import _client
import text_chat
import image_generate
import video_generate
import speech_synthesize
import music_generate
import vision_describe
import verify_all
import run_all

print("All scripts importable.")

print("_client.mask_key('sk-12345678'):", _client.mask_key('sk-12345678'))
print("_client.mask_key('short'):", _client.mask_key('short'))
print("_client.mask_key(''):", _client.mask_key(''))

# 验证 minimal_png
png = verify_all._minimal_png()
print("_minimal_png:", png.exists(), png.stat().st_size, "bytes")

# 验证无 Key 时报错
import os
for k in ("MINIMAX_API_KEY", "MINIMAX_GLOBAL_API_KEY", "MINIMAX_BASE_URL"):
    os.environ.pop(k, None)
try:
    _client.get_credentials()
    print("ERROR: should have raised")
except RuntimeError as e:
    print("OK: no key errored as expected:", str(e)[:60])

# 验证设了国内 Key 后能读
os.environ["MINIMAX_API_KEY"] = "test-cn-key-1234567890"
cred = _client.get_credentials()
print("CN cred:", cred["region"], cred["base_url"][:30], _client.mask_key(cred["api_key"]))
del os.environ["MINIMAX_API_KEY"]

# 国际 Key
os.environ["MINIMAX_GLOBAL_API_KEY"] = "test-global-key-1234567890"
cred = _client.get_credentials()
print("GLOBAL cred:", cred["region"], cred["base_url"][:30], _client.mask_key(cred["api_key"]))

# 显式 base_url
os.environ["MINIMAX_BASE_URL"] = "https://api.minimax.io/"
cred = _client.get_credentials()
print("Explicit global:", cred["region"], cred["base_url"])
print("ALL SANITY PASS")