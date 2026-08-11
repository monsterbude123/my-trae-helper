# Trae Local Data Export — Quickstart

> 三平台命令速查。详细原理见 references/decryption-principles.md。

---

## §0 前置依赖

```bash
pip install pycryptodome cryptography
# Windows 专用（Frida 备选）:
pip install frida frida-tools
```

---

## §1 Windows（端到端）

### 1.1 准备

```powershell
# 1. 以管理员身份运行 PowerShell
# 2. 启动 Trae，保持至少一个 AI 聊天窗口活跃
# 3. 切到本技能目录
cd d:\workspace\my-trae-helper\skill-markets\trae-local-data-export
```

### 1.2 阶段 1 — 密钥提取

```powershell
python scripts\extract_key.py
# 输出: output\decrypted_key.json
#       ├ enc_key: 64 字符 hex
#       └ salt: 32 字符 hex (16 字节)
```

### 1.3 阶段 2 — 数据库解密

```powershell
# 先关闭 Trae（防止文件锁）
Stop-Process -Name "Trae" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "ai-agent" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

python scripts\decrypt_db.py
# 输出: output\database_decrypted.db (约 400MB-3GB)
```

### 1.4 阶段 3 — 三大产物导出

```powershell
python scripts\export_sessions.py
# 产出:
#   output\chat_export\sessions\*.json  (结构化 JSON)
#   output\chat_export\all_chats.txt     (合并 TXT)
#   output\database_decrypted.db          (SQLite 备份, 阶段 2 已有)
```

### 1.5 阶段 4 — PII 脱敏

```powershell
python scripts\sanitize_export.py
# 产出: output\chat_export\sanitized\
```

---

## §2 macOS / Linux（仅解析已解密库）

> Linux/macOS 端无法直接读 Windows 进程内存，**必须**先在 Windows 端拿到 `output\database_decrypted.db` 再跨平台处理。

### 2.1 传输解密库

```bash
# 从 Windows 拷贝（用 U 盘 / 局域网 / scp）
scp user@windows-host:output/database_decrypted.db ./output/
```

### 2.2 解析导出

```bash
python3 scripts/export_sessions.py \
    --db ./output/database_decrypted.db \
    --out ./output/chat_export

# 跨平台备选: 直接 JSONL 模式
python3 scripts/extract_trae_jsonl.py \
    --source ~/Library/Application\ Support/Trae\ CN/ModularData/ai-agent/ \
    --out ./output/trae_conversations_$(date +%Y%m%d_%H%M%S).jsonl
```

---

## §3 失败快速回退

| 命令失败 | 回退命令 |
|---------|---------|
| `extract_key.py` 找不到 ai-agent | `scripts/extract_key_frida.py` |
| `decrypt_db.py` OOM | 加 `--page-batch 100`（默认 500） |
| `export_sessions.py` 卡住 | 改用 `extract_trae_jsonl.py` 增量导出 |
| Python import 错 | `pip install --upgrade pycryptodome cryptography` |

---

## §4 输出目录速查

```
output/
├── .history.md                    ← 阶段日志（成功/失败都写）
├── decrypted_key.json             ← 密钥（.gitignore）
├── database_decrypted.db          ← 产物 3: 完整 SQLite 备份
├── table_summary.json             ← 39 表 × 行数
└── chat_export/
    ├── sessions.json              ← 会话摘要索引
    ├── all_chats.txt              ← 产物 2: 合并 TXT
    ├── schema.sql                 ← 完整表结构
    ├── sessions/                  ← 产物 1: 结构化 JSON 会话
    │   ├── 001_标题1_abc12345.json
    │   └── ...
    └── sanitized/                 ← 阶段 4 脱敏后
```

---

## §5 与其他工具的串联

```
[本技能]                            [下游]
output/chat_export/all_chats.txt → 文档知识库: doc-map-manager
output/chat_export/sessions/*.json → 训练数据微调
output/database_decrypted.db     → 任意 SQLite 客户端（DB Browser / DBeaver）
```
