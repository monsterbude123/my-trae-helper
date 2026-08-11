# Trae SQLCipher 4 解密原理

> 来源: ZedeX/trae-chat-decrypt README + .history.md
> 适用: Trae CN（ByteDance VS Code fork）加密聊天数据库

---

## §1 加密参数

| 参数 | 值 | 来源 |
|------|----|------|
| SQLCipher 版本 | 4 | DLL 静态分析 |
| 加密算法 | AES-256-CBC | DLL 字符串 + 行为验证 |
| KDF | PBKDF2-HMAC-SHA512, 256000 迭代 | DLL bootstrap.rs |
| HMAC | HMAC-SHA512 per-page | 标准 SQLCipher 4 |
| Page Size | 4096 字节 | 标准 |
| Salt | 文件前 16 字节 | 每库唯一 |
| Key 格式 | Raw 32-byte hex | `PRAGMA key = "x'...'"` 注入 |

---

## §2 密钥派生链

```
┌──────────────────────────────────┐
│ DLL 硬编码 passphrase            │   "YOUR_DLL_KEY_STRING"
│ (在 ai_agent.dll bootstrap.rs)   │
└──────────────┬───────────────────┘
               │ runtime key generation
               ▼
┌──────────────────────────────────┐
│ Raw 32-byte encryption key       │   ← 64 字符 hex，存在 ai-agent 进程内存
│ (本工具要提取的目标)             │     address 在 process memory 中
└──────┬───────────────────┬───────┘
       │                   │
       │ salt = db[0:16]   │ mac_salt = salt XOR 0x3A
       │ iter = 256000     │ iter = 2
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ Encrypt key  │    │ HMAC key     │
│ (解 page)    │    │ (验 page)    │
└──────────────┘    └──────────────┘
```

> 关键洞察: 密钥是运行时随机生成的，**不**可从机器 ID / 用户 ID 推导。
> 必须从 ai-agent 进程内存中读取（首次启动后持久有效）。

---

## §3 页面解密算法

```python
from Crypto.Cipher import AES
import hashlib, hmac, struct

PAGE_SZ = 4096
SALT_SZ = 16
IV_SZ = 16
HMAC_SZ = 64
RESERVE_SZ = IV_SZ + HMAC_SZ  # 80 字节

def verify_key(enc_key, db_page1):
    """验证候选密钥：用 page 1 的 HMAC 反推"""
    salt = db_page1[:16]
    mac_salt = bytes(b ^ 0x3A for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=32)
    hmac_data = db_page1[16: PAGE_SZ - RESERVE_SZ + 16]
    stored_hmac = db_page1[PAGE_SZ - 64:]
    hm = hmac.new(mac_key, hmac_data, hashlib.sha512)
    hm.update(struct.pack("<I", 1))  # page number
    return hm.digest() == stored_hmac


def decrypt_page(enc_key, page_data, pgno):
    """分页解密，page 1 特殊处理（重建 SQLite header）"""
    iv = page_data[PAGE_SZ - RESERVE_SZ : PAGE_SZ - RESERVE_SZ + IV_SZ]
    if pgno == 1:
        encrypted = page_data[SALT_SZ : PAGE_SZ - RESERVE_SZ]
        cipher = AES.new(enc_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted)
        # 重建 SQLite 头: "SQLite format 3\x00" + 16 字节零
        return b"SQLite format 3\x00" + decrypted + b"\x00" * RESERVE_SZ
    else:
        encrypted = page_data[:PAGE_SZ - RESERVE_SZ]
        cipher = AES.new(enc_key, AES.MODE_CBC, iv)
        return cipher.decrypt(encrypted) + b"\x00" * RESERVE_SZ
```

---

## §4 进程内存扫描策略

### 4.1 进程识别

```
进程名: ai-agent.exe
命令行: 含 --vscode-crash-reporter-process-type=ai
         或 --type=aiAgent
```

### 4.2 内存扫描（Windows API）

```python
# 用 VirtualQueryEx + ReadProcessMemory 扫描可读页
# 搜索 64 字符 hex 模式: [0-9a-f]{64}
# 排除页首/页尾（对齐噪音）
# 对每个候选用 verify_key() 验证
```

### 4.3 Frida 模式（备选）

```python
# 当静态链接 sqlcipher 干扰内存扫描时
import frida
session = frida.attach("ai-agent.exe")
script = session.create_script(open("_frida_hook5.js").read())
script.load()
# hook sqlite3_key_v2 → 捕获传入的 raw key
```

---

## §5 失败模式与回退

| 现象 | 原因 | 回退方案 |
|------|------|---------|
| 找不到 ai-agent 进程 | Trae 关闭 / 进程名变更 | 检查 `%APPDATA%\Trae CN` 是否存在；用 tasklist 找 *ai* |
| 内存扫描 0 候选 | 静态链接 + 加密散布 | 切 Frida 模式 |
| HMAC 验证全失败 | enc_key 是 passphrase 而非 raw key | DLL 字符串搜索 `<YOUR_DDL_KEY_STRING>` 附近找转换逻辑 |
| decrypt 后 integrity 失败 | page_size 错误 / iv 偏移错 | dump page 1 hexdiff 标准 SQLite header 比对 |

---

## §6 法律与伦理边界

> 本工具仅用于**个人数据恢复**——从你自己机器上的 Trae 取出你自己的对话。
> 不要用于：他人数据、绕过公司审计、批量爬取、规避 Trae TOS。

---

## §7 参考链接

- [ZedeX/trae-chat-decrypt](https://github.com/ZedeX/trae-chat-decrypt) — 完整方法学
- [SQLCipher 4 文档](https://www.zetetic.net/sqlcipher/sqlcipher-api/) — 加密原语
- [AES-256-CBC](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_block_chaining_(CBC)) — 分组密码模式
- [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) — 密钥派生
