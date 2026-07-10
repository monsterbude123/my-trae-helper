---
name: doc-map-manager
description: >
  文档地图管理器 — 为 docs/ 目录构建结构化索引（.docmap/docmap.db SQLite），
  支持精确匹配、模糊搜索、ChromaDB / Zvec 语义向量检索。当用户需要 "文档索引"、"搜索文档"、
  "文档地图"、"docmap"、"查找某篇文档的章节"、"更新文档索引"、"build index"、
  "查询文档"、"模糊搜索文档标题"、"语义搜索文档" 时自动加载。
  也支持为文档提问直接定位到具体文件的精确行号。
---

# 文档地图管理器

> ⚠️ **索引存储在 SQLite（.docmap/docmap.db），禁止直接 Read！**
> 必须通过 `python query-index.py` 查询——这是唯一入口。

## 概述

SQLite 存储，支持增量更新与并行解析：

| 存储 | 格式 | 说明 |
|------|------|------|
| `.docmap/docmap.db` | SQLite | 文件 mtime+size 追踪 + 标题行索引 |
| `.docmap/chroma/` | ChromaDB | 语义搜索向量库（可选，`--chroma`） |
| `.docmap/zvec/` | Zvec | 语义搜索向量库（可选，`--zvec`，CPU+API 多源动态队列） |

查询工具 `query-index.py` 支持五种检索模式 + ChromaDB / Zvec 语义向量增强。

---

## Agent 使用指南（必读）

> 当用户提到文档相关内容时，按以下决策树执行。**禁止跳过索引直接用 grep/glob/read_file 瞎找。**

### 决策树：用户问文档问题 → 我该调哪个？

```
用户问的是...
│
├── "XXX怎么实现的？""XXX是什么？""XXX流程？"
│   └── 🎯 query-index.py --grab "XXX"           ← P0 首选，一步到位
│       ├── 有结果 → 直接输出给用户（正文+行号）
│       └── 无结果 → 降级 --fuzzy "XXX"，拿到行号后 read_file
│
├── "哪些文档提到了gRPC/websocket/某个技术名词？"
│   └── 🎯 query-index.py --lookup "技术名词"     ← SQLite LIKE 查找
│
├── "ARCHITECTURE.md 里有哪些章节？"
│   └── 🎯 query-index.py --file ARCHITECTURE.md
│
├── 会话刚开始 / 不确定文档有没有更新
│   └── 🎯 build-index.py --diff                 ← 对比 SQLite 中的 mtime
│       ├── 无变化 → 直接用已有索引
│       └── 有变化 → build-index.py --incremental --zvec 或 --chroma
│
├── "更新文档索引" / "build index"
│   └── 🎯 build-index.py --incremental --zvec  ← 默认启用 Zvec 语义搜索
│       或 build-index.py --incremental --chroma  ← ChromaDB 模式
│       或 build-index.py --incremental --no-zvec --no-chroma  ← 跳过向量化
│
└── "搜索XX相关文档"（不知道关键词）
    └── 🎯 query-index.py --semantic "自然语言描述"  ← Zvec → ChromaDB → TF-IDF 降级
        或 query-index.py --fuzzy "近似词"           ← fallback
```

### 脚本路径

两个脚本相对技能目录的路径，调用时使用绝对路径：

```
{skill_root}/scripts/build-index.py
{skill_root}/scripts/query-index.py
```

实际路径为 `d:\workspace\my-trae-helper\skill-markets\doc-map-manager\scripts\{脚本名}.py`。

#### docs/ 路径自动解析

脚本按以下优先级自动查找 `docs/` 目录：

| 优先级 | 策略 | 适用场景 |
|--------|------|---------|
| P0 | `--docs-dir ./path` 显式指定 | 非 my-trae-helper 项目，推荐 |
| P1 | 脚本路径 `../../docs` | 本仓库内 |
| P2 | CWD 下的 `./docs` | 全局安装（`.codebuddy/skills/`） |
| P3 | CWD 递归父级找 `docs/` | 子在子目录执行 |
| P4 | CWD 兜底 | 以上全失败 |

**AI 推荐**：遇到非本仓库项目时，始终用 `--docs-dir` 显式指定。

### 优先级铁律

| 优先级 | 工具 | 适用场景 | 预期耗时 |
|--------|------|---------|---------|
| **P0** | `query-index.py --grab "问题"` | 用户问文档里某件事怎么做的 | **0.3s** |
| **P1** | `query-index.py --lookup "关键词"` | 知道精确技术名词 | **0.2s** |
| **P2** | `query-index.py --fuzzy "近似描述"` | grab 无结果时的降级 | **0.5s** |
| **P3** | `query-index.py --semantic "自然语言"` | 完全不知道关键词 | **3s（慢）** |
| **P4** | `query-index.py --file xxx.md` | 浏览某文件结构 | **0.3s** |
| **P5** | `read_file(...)` 手动读文件 | 仅当上面都不可用 | 高 token 消耗 |

### ⚠️ 语义搜索查询原则

语义搜索（`--semantic`）在 Zvec 或 ChromaDB 同步后可用，适合用自然语言描述模糊意图时使用。
**仍优先用 `--grab` / `--lookup`**（速度快、精度高），语义搜索在关键词不确定时作为补充。
使用精确的领域术语作为查询词，避免短泛词。

### 反模式（禁止行为）

| 禁止 | 原因 | 正确做法 |
|------|------|---------|
| ❌ 用户问文档问题，直接用 `grep` 搜 | 不知道章节结构，盲搜低效 | ✅ 先 `--grab` |
| ❌ 先 `read_file` 手动翻找 | token 黑洞 | ✅ 用 `--grab` 精确定位 |
| ❌ 拿到 `--fuzzy` 行号后用 `read_file` 读整个文件 | 浪费 token | ✅ 用 `read_file(offset=line, limit=range)` |
| ❌ 每次都 `build-index.py` 全量重建 | 慢，token 多 | ✅ `--incremental` 或先 `--diff` 看是否需要 |
| ❌ 有 `--grab` 却仍用 `--fuzzy` + 手动 `read_file` | 多一步 | ✅ `--grab` 一步到位 |

### 典型对话处理模板

**用户**: "Agent 通信怎么设计的？"

```
1. RunCommand: python ...scripts/query-index.py --grab "Agent 通信"
2. 拿到 → 原文 + 行号
3. 回复用户（用 grab 的正文内容直接回答）
```

**用户**: "这个项目文档里有没有提到 Redis？"

```
1. RunCommand: python ...scripts/query-index.py --lookup "Redis"
2. 拿到 → 匹配的标题列表
3. 告诉用户哪些文件提到 Redis，让用户选具体哪个
4. 用户选了 → --grab "那个章节"
```

---

## 使用方式

### 构建索引

```bash
# 全量构建（自动同步 Zvec 语义搜索）
python build-index.py --zvec

# 全量构建（自动同步 ChromaDB 语义搜索）
python build-index.py --chroma

# 指定文档目录
python build-index.py --docs-dir ./docs --zvec

# 跳过向量同步（加速，仅用关键词搜索）
python build-index.py --no-zvec --no-chroma

# 增量构建（只处理变更文件，基于 mtime+size）
python build-index.py --incremental --zvec

# 变更检测（对比 SQLite 中的 mtime）
python build-index.py --diff
```

### 查询索引

```bash
# 浏览某个文件的所有章节
python query-index.py --file ARCHITECTURE.md

# 精确匹配标题
python query-index.py "Agent 层"

# 模糊匹配（容忍错字、近似词）
python query-index.py --fuzzy "agent通信"

# ⭐ GRAB 模式：搜索后直接输出正文（省去一次 read_file）
python query-index.py --grab "Agent 通信"
python query-index.py --grab "gRPC" --context 5

# ⭐ 关键词查询（SQLite LIKE）
python query-index.py --lookup "gRPC"
python query-index.py --lookup "websocket" --json

# 语义搜索（需先 build --zvec 或 --chroma）
python query-index.py --semantic "多Agent之间怎么发消息"

# 限制返回条数
python query-index.py --semantic "资源上传" --top 5
```

### 增量维护

```bash
# 变更检测 — Git diff
python build-index.py --git-diff                    # 与 HEAD 对比
python build-index.py --git-diff --git-ref HEAD~3   # 与 N 个提交前对比

# 变更检测 — SQLite mtime 对比
python build-index.py --diff

# 增量构建（自动同步 Zvec）
python build-index.py --incremental --zvec
python build-index.py --incremental --chroma        # 或 ChromaDB
python build-index.py --incremental --no-zvec --no-chroma  # 仅 SQLite
```

---

## 脚本依赖

| 依赖 | 何时需要 | 安装方式 |
|------|---------|---------|
| Python 3.9+ | 必需 | 系统自带 |
| `sqlite3` | 必需 | Python 标准库，零安装 |
| `rapidfuzz` | `--fuzzy` | `pip install rapidfuzz` |
| `chromadb` | `--chroma` / `--semantic`（ChromaDB） | `pip install chromadb` |
| `zvec` | `--zvec` / `--semantic`（Zvec） | `pip install zvec` |
| `sentence_transformers` | `--zvec` 本地 Embedding | `pip install sentence_transformers` |
| `tqdm` | 进度条（推荐） | `pip install tqdm` |
| `jieba` | `--fuzzy` 中文增强 | `pip install jieba` |

**零外部依赖核心路径**：`sqlite3`（stdlib）即可运行基本的索引构建和精确/模糊/LOOKUP 查询。

向量数据位置：
- ChromaDB：`.docmap/chroma/`
- Zvec：`.docmap/zvec/`

建议加入 `.gitignore`。

---

## 降级策略

```
query 请求
  │
  ├── --semantic
  │     ├── Zvec 可用 → 向量检索（最佳）
  │     ├── ChromaDB 可用 → 次选
  │     ├── SQLite 存在 → TF-IDF 降级
  │     └── 都没有 → 报错，提示先 build
  │
  ├── --fuzzy
  │     ├── rapidfuzz 可用 → rapidfuzz partial_ratio
  │     └── rapidfuzz 不可用 → difflib.SequenceMatcher（标准库降级）
  │
  └── 精确匹配 / LOOKUP
        └── SQLite SELECT + LIKE（索引查询，瞬间返回）
```

---

## 输出格式说明

### 人类可读输出

```
  docs/ARCHITECTURE.md                               L164-L205             95%  ## 2.3 Agent 通信层设计
  docs/ARCHITECTURE.md                               L525-L538             82%  ## 4.5 跨模块通信方式
  docs/adr.md                                        L121-L137             76%  ## ADR-007: 通信协议选型
```

列：文件 | 行范围 | 匹配度 | 标题（面包屑）

### JSON 输出

```json
[
  {
    "file": "ARCHITECTURE.md",
    "line": 164,
    "end_line": 205,
    "score": 0.95,
    "title": "2.3 Agent 通信层设计",
    "breadcrumb": "2. Agent 层 > 2.3 Agent 通信层设计",
    "level": 3
  }
]
```

---

## 维护约定

1. `.docmap/docmap.db` 是 SQLite 数据库，**禁止手动编辑**
2. `.docindex.json` / `.docmap.json` / `DOCSMAP.md` 已废弃，由 SQLite 替代
3. 新增文档后运行 `build-index.py --incremental --zvec` 更新索引
4. `.docmap/chroma/` 和 `.docmap/zvec/` 建议加入 `.gitignore`（二进制向量数据不宜进仓库）
5. `.docmap/docmap.db` 建议 git track（便携，无需向量库即可使用）

---

## Embedding 配置（.env）

项目根目录 `.env` 文件可配置向量化后端和额外文档目录：

```bash
# ── Embedding 后端 ──

# 方案 1：本地 CPU 模型（默认，中文优化，需 pip install sentence_transformers）
DOCMAP_EMBEDDING_PROVIDER=sentence_transformers
DOCMAP_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 方案 2：OpenAI 兼容端点（local llm / vllm / openai，需 pip install openai）
# DOCMAP_EMBEDDING_PROVIDER=openai
# DOCMAP_EMBEDDING_API_BASE=http://localhost:11434/v1
# DOCMAP_EMBEDDING_API_KEY=local llm
# DOCMAP_EMBEDDING_MODEL=nomic-embed-text

# 方案 3：Chromadb 自带轻量模型（仅 --chroma）
# DOCMAP_EMBEDDING_PROVIDER=chroma_default

# ── Zvec 多源嵌入（CPU + 多个 OpenAI 端点负载均衡）──

# 本地 CPU 权重（0=关闭，默认 1）
# DOCMAP_EMBEDDING_LOCAL_WEIGHT=1

# API 端点权重（默认 3，仅用于单端点旧式配置）
# DOCMAP_EMBEDDING_API_WEIGHT=3

# 多端点 JSON 数组（同时连接多个 API 做负载均衡）
# DOCMAP_EMBEDDING_ENDPOINTS=[
#   {"base":"http://172.18.0.1:1234/v1","key":"sk-xxx","model":"bge-small-zh-v1.5","weight":3,"batch_size":200},
#   {"base":"http://192.168.1.100:8080/v1","key":"sk-yyy","model":"bge-small-zh-v1.5","weight":2,"batch_size":200}
# ]

# 每个 batch 的文本数量（默认 200）
# DOCMAP_EMBEDDING_BATCH=200

# ── 额外文档目录 ──

# 分号或逗号分隔的路径列表，用于引入外部技能市场、参考文档等作为文档检索源
# DOCMAP_EXTRA_DOCS_DIRS=./skill-markets/other-pkg/docs;D:\shared-docs
```

> `DOCMAP_EXTRA_DOCS_DIRS` 影响 build-index.py 的扫描范围和 query-index.py 的搜索范围。
> 所有列出的目录会被统一建索引，query 时跨所有目录检索。

不配置 `.env` 时默认使用 `BAAI/bge-small-zh-v1.5`（100MB，中文优化）。

### Zvec 性能调优

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `DOCMAP_EMBEDDING_LOCAL_WEIGHT` | `1` | CPU 源权重，设为 `0` 关闭 CPU 嵌入 |
| `DOCMAP_EMBEDDING_API_WEIGHT` | `3` | API 源权重 |
| `DOCMAP_EMBEDDING_BATCH` | `200` | OpenAI 每批次文本数 |

Zvec 模式自动支持 CPU + API 混合嵌入，按权重分配文本块，动态队列消费（谁快谁多拿）。

---

## 自排除规则（AI 必须遵守）

doc-map-manager 自动排除自身运行产物，AI 不得重新索引或修改：

| 排除对象 | 原因 | 操作规则 |
|---------|------|---------|
| `.docmap/docmap.db` | SQLite 索引数据库 | 禁止直接 SQL 修改，用脚本查询 |
| `.docmap/chroma/` | ChromaDB 向量库 | 不进入检索范围，不 git track |
| `.docmap/zvec/` | Zvec 向量库 | 不进入检索范围，不 git track |

`build-index.py` 在扫描阶段已静默排除上述文件。
