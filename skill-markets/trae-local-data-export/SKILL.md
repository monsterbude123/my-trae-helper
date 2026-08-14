---
name: trae-local-data-export
description: Trae IDE 本地数据导出工具箱。整合 ZedeX/trae-chat-decrypt（Windows 进程内存 → SQLCipher 密钥 → AES-256-CBC 解密）与 cgint/ai-data-extraction（跨平台解密库解析），产出三大产物：结构化 JSON 会话文件 / 合并 TXT / 完整 SQLite 离线备份。Invoke when user wants to export / decrypt / backup Trae local chat history, or migrate ModularData/ai-agent/database.db.
requires:
intent: Trae IDE 本地数据导出工具箱
category: other
audience: [agent, devops]
---
# Trae Local Data Export

> 端到端导出 Trae IDE 本地加密聊天数据库的技能包。整合两个开源工具，串联"加密库 → 密钥 → 明文库 → 三大产物"完整管线。

---

## §0 何时加载本技能

```
MUST: 用户要求"导出/解密/备份 Trae 本地聊天/对话/会话"时加载
MUST: 用户想从 ModularData/ai-agent/database.db 取出 AI 对话记录时加载
MUST: 用户想批量拿到自己用过的 token 用量 / 模型分布 / 会话历史时加载
NEVER: 用户只想问"Trae 怎么用" — 这是 trae-professional 的领域
NEVER: 用户的数据不是自己的 — 本工具仅限个人数据恢复
```

---

## §1 核心铁律（≤ 10 条）

```
1. ONLY 自己的数据：所有解密/提取操作限本机 ModularData/ai-agent/database.db
2. MUST 先关 Trae：解密前必须先完全关闭 Trae 进程（Windows 任务管理器 + 等待 5s），
   防止 SQLCipher 持有文件锁；否则解密输出会读到旧快照或失败
3. MUST Trae 至少运行过一次：首次密钥生成需要 ai-agent 进程活着，
   关闭后再开依然有效（密钥持久在 ModularData 之外的位置——见 references/decryption-principles.md）
4. MUST 管理员权限：Windows API 读进程内存需管理员终端（PowerShell "以管理员身份运行"）
5. MUST 三选一交付：每次运行至少产出 ①结构化 JSON 会话 ②合并 TXT ③SQLite 离线备份
6. NEVER 硬编码密钥到脚本：decrypted_key.json 必须用户所有，存 .gitignore，
   禁止 commit / 禁止 echo 完整 hex
7. NEVER 联网外发：解密产物仅写本地 output/，禁止 HTTP 上传
8. NEVER 覆盖源库：解密后的 database_decrypted.db 写到 output/，
   绝不动 ModularData/ai-agent/database.db
9. PII 脱敏默认开启：导出 JSON 前自动 mask 绝对路径 / 邮箱 / 32+ 字符 hex
   （与 trae-chat-decrypt 默认 sanitization 对齐）
10. MUST 标注 .history.md：每次成功/失败的关键发现写到 output/.history.md，
    便于后续会话回溯
```

---

## §2 三阶段骨架流程

### 阶段 1 — 定位与密钥提取

```
输入: Windows 10/11 + 管理员 PowerShell + Trae 至少运行过一次
执行:
  python scripts/extract_key.py
      → 扫描 ai-agent.exe 进程内存
      → 搜索 64 字符 hex 模式
      → 用 HMAC-SHA512 验证候选密钥
      → 写入 output/decrypted_key.json
失败回退:
  ├─ 找不到 ai-agent 进程 → 启动 Trae 并保持至少一个 AI 聊天窗口活跃
  ├─ 内存扫描无候选 → 改用 Frida 模式 scripts/extract_key_frida.py
  └─ HMAC 验证失败 → 切换 KDF 推导 candidates（罕见，参考 references/decryption-principles.md §3）
```

### 阶段 2 — 数据库解密

```
输入: output/decrypted_key.json + ModularData/ai-agent/database.db
执行:
  python scripts/decrypt_db.py
      → 读 enc_key + salt
      → PBKDF2-HMAC-SHA512 派生 encryption key + HMAC key
      → 按 4096 字节分页 AES-256-CBC 解密
      → 写入 output/database_decrypted.db
验证:
  python scripts/verify_decrypted_db.py
      → 测试 PRAGMA integrity_check
      → 列出 39 个表 + 行数
      → 输出 table_summary.json
```

### 阶段 3 — 三大产物导出

```
输入: output/database_decrypted.db
执行:
  python scripts/export_sessions.py
      → 产物 1: output/chat_export/sessions/*.json  （结构化 JSON 会话）
      → 产物 2: output/chat_export/all_chats.txt   （合并 TXT）
      → 产物 3: output/database_decrypted.db         （完整 SQLite 备份 — 阶段 2 已产出）
跨平台备选（仅在阶段 1-2 失败 / Linux-macOS 环境）:
  python scripts/extract_trae_jsonl.py
      → 直接扫描已解密的 ModularData（无 SQLCipher 也能跑）
      → 输出 output/trae_conversations_*.jsonl
```

### 阶段 4 — PII 脱敏（可选但默认）

```
python scripts/sanitize_export.py
  → 替换绝对路径为 <PATH>
  → 替换 email 为 <EMAIL>
  → 替换 32+ 字符 hex 为 <HEX_32>
  → 替换 64 字符 hex 为 <HEX_64>
  → 替换 IPv4 为 <IP>
  → 写到 output/chat_export/sanitized/
```

---

## §3 三产物输出契约

| 产物 | 路径 | 格式 | 用途 |
|------|------|------|------|
| 结构化 JSON | `output/chat_export/sessions/NNN_标题_ID.json` | JSON | 二次开发 / 训练数据 / API 集成 |
| 合并 TXT | `output/chat_export/all_chats.txt` | UTF-8 纯文本 | 全文搜索 / diff / 人读 |
| SQLite 备份 | `output/database_decrypted.db` | SQLite 3 | 离线查询 / 第三方工具 / 长期归档 |

每个 JSON 会话文件结构：

```json
{
  "session_id": "abc12345",
  "title": "...",
  "type": "side_chat | inline_chat | background_chat | proactive_chat",
  "project": "<PROJECT_NAME>",
  "created_at": "2026-08-01T10:30:22Z",
  "messages": [
    {"role": "user",      "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "...", "model": "kimi-k2.5"}
  ],
  "token_usage": {
    "prompt_tokens": 15012,
    "completion_tokens": 487,
    "cache_read_tokens": 13802
  }
}
```

---

## §4 决策树（platform × state → 入口脚本）

```
                          ┌─ 已是明文 SQLite ───────────→ extract_trae_jsonl.py
                          │
用户有 database.db  ──────┤  仍是 SQLCipher 加密 ──┬─ Windows + 管理员 ──→ 阶段 1-3 全套
                          │                       └─ macOS / Linux       ──→ extract_trae_jsonl.py
                          │                                                  (说明: 需先在 Windows 端解出明文库)
                          │
                          └─ 找不到 db 文件 ──────────→ 先定位（见 references/db-location.md）
```

---

## §5 输入/输出骨架

### 输入
- `ModularData/ai-agent/database.db`（SQLCipher 4 加密，~400MB）
- `output/decrypted_key.json`（密钥提取阶段产出，跨阶段共享）

### 输出
```
output/
├── .history.md                  # 阶段日志 + 关键发现
├── decrypted_key.json           # 密钥（.gitignore 必加）
├── database_decrypted.db        # 产物 3：完整 SQLite 备份
├── table_summary.json           # 39 表 × 行数统计
└── chat_export/
    ├── sessions.json            # 会话摘要索引
    ├── all_chats.txt            # 产物 2：合并 TXT
    ├── schema.sql               # 表结构
    ├── sessions/                # 产物 1：结构化 JSON 会话
    │   ├── 001_标题1_abc12345.json
    │   ├── 002_标题2_def67890.json
    │   └── ...
    └── sanitized/               # 阶段 4 脱敏后副本
```

---

## §6 异常速查表

| 症状 | 根因 | 处置 |
|------|------|------|
| 找不到 ai-agent 进程 | Trae 未启动 / 进程名变化 | 启动 Trae 并保持 AI 聊天窗口活跃；用 TaskList 确认 `ai-agent.exe` |
| 内存扫描无候选 | 静态链接 sqlcipher / 加密方式变更 | 切 Frida 模式；查 references/decryption-principles.md §3 |
| `PRAGMA key` rejected | enc_key 错误 | 重新执行 extract_key.py；确认 HMAC 验证通过 |
| 解密后 integrity_check 失败 | 密钥不对 / 分页逻辑错 | 检查 page_size=4096 / iv 偏移 / salt 16 字节；参考 references/decryption-principles.md §2 |
| `chat_message` 0 行 | 用户从未发过消息 | 正常 — 写出空 sessions.json，提示用户 |
| 导出 JSON 字段大量 null | Trae 版本 schema 变更 | 查 references/schema-map.md 当前表结构；调整 SELECT 字段 |

---

## §7 安全审查合规

```
MUST: 密钥文件 decrypted_key.json → output/.gitignore
MUST: 任何包含 enc_key hex 的日志 → mask 后再写 .history.md
MUST: 脚本不调用任何 HTTP endpoint（除本地 file:// / 用户指定 export 路径外）
MUST: 提交前跑 trae-security-review/scripts/scan_skills_dir.py skill-markets/trae-local-data-export
NEVER: 把任何用户的真实 chat 内容 / 密钥 / 路径写进 SKILL.md / references/
```

---

## §8 关联资源

| 资源 | 路径 | 用途 |
|------|------|------|
| 解密原理详解 | [references/decryption-principles.md](references/decryption-principles.md) | SQLCipher 4 + AES-256-CBC + KDF 链 |
| 数据库定位 | [references/db-location.md](references/db-location.md) | ModularData 路径跨平台查找 |
| 表结构映射 | [references/schema-map.md](references/schema-map.md) | 39 个表 × 关键字段 × 导出字段 |
| 命令速查 | [references/quickstart.md](references/quickstart.md) | Windows / macOS / Linux 三平台命令 |
| 来源项目 | github.com/ZedeX/trae-chat-decrypt | Windows 密钥提取 + 加密库解密 |
| 来源项目 | github.com/cgint/ai-data-extraction | 跨平台解密库解析 |
