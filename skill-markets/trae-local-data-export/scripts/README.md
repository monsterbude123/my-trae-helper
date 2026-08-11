# Trae Local Data Export — Scripts

> 6 个 Python 脚本，覆盖 §2 三阶段 + 跨平台备选 + PII 脱敏。

---

## 快速调用顺序

```powershell
# 阶段 1 — 密钥提取（Windows + 管理员）
python scripts\extract_key.py --db "%APPDATA%\Trae CN\ModularData\ai-agent\database.db"

# 阶段 1 失败 → Frida 备选
python scripts\extract_key_frida.py --db "%APPDATA%\Trae CN\ModularData\ai-agent\database.db"

# 阶段 2 — 解密数据库
python scripts\decrypt_db.py

# 阶段 2.5 — 校验
python scripts\verify_decrypted_db.py

# 阶段 3 — 三大产物导出
python scripts\export_sessions.py

# 阶段 3 跨平台备选（macOS / Linux + 已解密库）
python scripts\extract_trae_jsonl.py

# 阶段 4 — PII 脱敏（默认开启）
python scripts\sanitize_export.py
```

---

## 脚本清单

| 脚本 | 阶段 | 平台 | 依赖 |
|------|------|------|------|
| [extract_key.py](extract_key.py) | 1 | Windows | pycryptodome |
| [extract_key_frida.py](extract_key_frida.py) | 1 备选 | Windows | frida, frida-tools |
| [decrypt_db.py](decrypt_db.py) | 2 | 全平台 | pycryptodome |
| [verify_decrypted_db.py](verify_decrypted_db.py) | 2.5 | 全平台 | stdlib |
| [export_sessions.py](export_sessions.py) | 3 | 全平台 | stdlib |
| [extract_trae_jsonl.py](extract_trae_jsonl.py) | 3 备选 | 全平台 | stdlib |
| [sanitize_export.py](sanitize_export.py) | 4 | 全平台 | stdlib |

---

## 设计原则

1. **零外部依赖优先**：除 pycryptodome / frida 外，全部 stdlib
2. **跨版本容错**：用 `PRAGMA table_info` 探测列名，不写死 `idx` 或 `index`
3. **失败显式化**：所有 `STUB:` 前缀错误是引导用户到正确回退路径，不是静默
4. **密钥安全**：decrypted_key.json 永不被脚本读取后写回日志
5. **不修改源库**：只读 `database.db`，写到 `output/`
