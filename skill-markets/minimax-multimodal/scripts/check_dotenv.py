"""测试 .env 自动加载 — 用 fake key 验证逻辑,不打印 key 内容。"""
import os
import sys
from pathlib import Path

# 模拟:在 skill 目录写一个临时 .env(不提交)
ENV = Path(__file__).resolve().parent.parent / ".env"
ENV.write_text(
    "# auto-generated for test\n"
    "MINIMAX_API_KEY=eyJFAKE_KEY_FOR_TEST_ONLY_do_not_use_in_production\n"
    "MINIMAX_TIMEOUT=42\n",
    encoding="utf-8",
)

# 清掉 shell 已设的环境变量,确保 .env 起作用
os.environ.pop("MINIMAX_API_KEY", None)
os.environ.pop("MINIMAX_TIMEOUT", None)

# 重新加载模块,触发 _load_dotenv
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import importlib
import _client
importlib.reload(_client)

# 检查:Key 已加载,但任何打印/日志只显示脱敏末 4 位
key = os.environ.get("MINIMAX_API_KEY", "")
assert key.startswith("eyJ"), "Key 加载失败"
masked = _client.mask_key(key)
# 脱敏后:以原 key 末 4 位结尾,且前面的全是 *
assert masked.endswith(key[-4:])
assert set(masked[:-4]) == {"*"}
print(f"Key loaded: length={len(key)}, masked={masked}")

timeout = os.environ.get("MINIMAX_TIMEOUT")
assert timeout == "42", f"TIMEOUT 加载失败,got {timeout!r}"
print(f"TIMEOUT loaded: {timeout}")

# 验证:cred 也正确
cred = _client.get_credentials()
print(f"region={cred['region']}, masked_key={_client.mask_key(cred['api_key'])}")
assert cred["region"] == "cn"
assert cred["timeout"] == 42

# 清理
ENV.unlink()
print("ALL DOTENV TESTS PASS")