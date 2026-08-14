---
name: doc-map-manager
description: "文档知识图谱管理器 — 为 docs/ 目录构建结构化索引（.docmap/docmap.db SQLite + 链接图谱 + 新鲜度评分），
支持精确匹配、模糊搜索、ChromaDB / Zvec 语义向量检索、文档间链接查询（context）、影响面分析（impact）、
新鲜度反幻觉验证。当用户需要 \"文档索引\"、\"搜索文档\"、\"文档地图\"、\"docmap\"、\"查找某篇文档的章节\"、
\"更新文档索引\"、\"build index\"、\"查询文档\"、\"模糊搜索文档标题\"、\"语义搜索文档\"、\"文档影响面\"、
\"文档关联查询\"、\"知识图谱\" 时自动加载。"
intent: 文档知识图谱管理器 — 为 docs/ 目录构建结构化索引（
category: other
audience: [designer]
---
# 文档知识图谱管理器

> ⚠️ **索引存储在 SQLite（.docmap/docmap.db），禁止直接 Read！**
> 必须通过 `python query-index.py` 查询——这是唯一入口。

## 五层架构

```
L5 验证层 — 新鲜度评分 + 反幻觉尾注
L4 变更层 — detect-changes / impact（概念级变更检测）
L3 查询层 — grab / lookup / fuzzy / semantic / context
L2 关系层 — 链接图谱（入站/出站）+ 标签 + frontmatter 元数据
L1 索引层 — 标题 / 章节行号 / 面包屑
```

## 知识生命周期协议（Agent 必读）

> 这是确保文档检索不被 AI 幻觉污染的 4 步强制协议。

```
Agent 从文档知识库获取知识 →
  Step 1: 检查新鲜度
    🟢 ≥ 0.7 → 高置信，可直接引用
    🟡 0.3~0.7 → 中置信，标注 "文档可能不是最新的"
    🔴 < 0.3 → 低置信，必须交叉验证！

  Step 2: 涉及代码实现（API、函数名、配置）时
    → 必须用 GitNexus context() 验证
    → 文档说 Redis，代码是 Memcached → 🛑 报告不一致，不盲信文档

  Step 3: 返回结果时附带来源置信度
    → "根据 docs/xxx.md（🟢 新鲜度 0.95）..."
    → "根据 docs/yyy.md（🔴 新鲜度 0.12，可能过时）..."

  Step 4: 同一概念多点召回时
    → 输出包含 "该概念在 N 篇文档中出现" 元信息
    → Agent 应全部读完再归纳，不基于单篇下结论
```

## Agent 决策树（v2 增强版）

```
用户问的是...
│
├── "XXX怎么实现的？""XXX是什么？""XXX流程？"
│   └── 🎯 query-index.py --grab "XXX"           ← P0 首选
│       ├── 有结果 → 检查新鲜度 → 涉及代码? → GitNexus 验证 → 回复
│       └── 无结果 → 降级 --fuzzy，拿到行号后 read_file
│
├── "哪些文档提到了gRPC/websocket/某个技术名词？"
│   └── 🎯 query-index.py --lookup "技术名词"
│
├── "ARCHITECTURE.md 引用了哪些文档？被哪些文档引用？"
│   └── 🎯 query-index.py --context-mode ARCHITECTURE.md  ← v2 新增
│
├── "修改 ARCHITECTURE.md 会影响哪些文档？"
│   └── 🎯 build-index.py --impact ARCHITECTURE.md       ← v2 新增
│       或 query-index.py --impact ARCHITECTURE.md
│
├── "刚才改了文档，有哪些文档引用了它需要同步更新？"
│   └── 🎯 build-index.py --detect-changes              ← v2 新增
│
├── 会话刚开始 / 不确定文档有没有更新
│   └── 🎯 build-index.py --diff
│       ├── 无变化 → 直接用已有索引
│       └── 有变化 → build-index.py --incremental
│
├── "更新文档索引" / "build index"
│   └── 🎯 build-index.py --incremental --zvec
│
└── "搜索XX相关文档"（不知道关键词）
    └── 🎯 query-index.py --semantic "自然语言描述"
```

## 优先级铁律（v2）

| 优先级 | 工具 | 适用场景 | 耗时 | 置信度 |
|--------|------|---------|------|-------|
| **P0** | `--grab "问题"` | 用户问文档里某件事 | 0.3s | 含新鲜度 |
| **P0.5** | `--context-mode FILE` | 查看文档关联关系 | 0.3s | 链接图谱 |
| **P1** | `--lookup "关键词"` | 知道精确技术名词 | 0.2s | 含新鲜度 |
| **P1.5** | `--impact FILE` | 修改前影响评估 | 0.3s | 链接+标签 |
| **P2** | `--fuzzy "描述"` | grab 无结果降级 | 0.5s | 含新鲜度 |
| **P3** | `--semantic "自然语言"` | 完全不知道关键词 | 3s | 依赖模型 |
| **P4** | `--file xxx.md` | 浏览文件结构 | 0.3s | — |
| **P5** | `read_file(...)` | 仅当上面都不可用 | 高token | — |

## 反模式（禁止行为）

| 禁止 | 原因 | 正确做法 |
|------|------|---------|
| ❌ 用户问文档问题，直接用 `grep` 搜 | 不知道章节结构，盲搜低效 | ✅ 先 `--grab` |
| ❌ 先 `read_file` 手动翻找 | token 黑洞 | ✅ `--grab` 精确定位 |
| ❌ 拿到结果不理新鲜度直接引用 | 🔴 文档可能过时 | ✅ 检查新鲜度，🟡🔴标注 |
| ❌ 文档提到 API/配置/类名不验证代码 | 文档可能落后代码 | ✅ GitNexus context() 验证 |
| ❌ 每次都全量重建 | 慢 | ✅ `--incremental` 或先 `--diff` |
| ❌ 修改文档前不跑 `--impact` | 不知道会影响哪些关联文档 | ✅ `build-index.py --impact FILE` |
| ❌ 拿到 `--fuzzy` 行号后读整个文件 | 浪费 token | ✅ `read_file(offset=line, limit=range)` |

## 典型对话模板

**用户**: "Agent 通信怎么设计的？"

```
1. RunCommand: python ...scripts/query-index.py --grab "Agent 通信"
2. 拿到 → 原文 + 新鲜度（🟢/🟡/🔴）
3. 涉及代码实现 → GitNexus context("agent_communicate") 验证
4. 回复用户（标注新鲜度 + 交叉验证结果）
```

**用户**: "修改架构文档前，帮我看看影响面"

```
1. RunCommand: python ...scripts/query-index.py --impact ARCHITECTURE.md
2. 输出：入站链接 5 篇 + 出站链接 3 篇 + 风险等级
3. 告知用户影响范围，再动手修改
```

**用户**: "刚才改了 adr-007.md，哪些文档需要同步？"

```
1. RunCommand: python ...scripts/build-index.py --detect-changes
2. 输出：变更文件列表 + 入站链接文档（需要同步更新）
```

## 使用方式

### 构建索引

```bash
python build-index.py                          # 全量（自动计算新鲜度 + 链接图谱）
python build-index.py --incremental            # 增量（基于 mtime+size）
python build-index.py --detect-changes          # 概念级变更检测
python build-index.py --impact ARCHITECTURE.md # 影响面分析
python build-index.py --zvec                   # 全量 + Zvec 语义搜索
```

### 查询索引

```bash
# 搜索 + 正文输出
python query-index.py --grab "Agent 通信"

# 文档上下文（v2）：入站/出站链接 + 新鲜度 + 标签
python query-index.py --context-mode ARCHITECTURE.md

# 影响面分析（v2）：修改影响 + 风险等级
python query-index.py --impact adr-007.md

# 精确/模糊/语义搜索
python query-index.py --lookup "gRPC"
python query-index.py --fuzzy "agent通信"
python query-index.py --semantic "多Agent之间怎么发消息"

# 文件浏览
python query-index.py --file ARCHITECTURE.md
```

## 脚本路径

> **脚本位于本 Skill 目录的 `scripts/` 子目录下，不要凭空猜测路径。**

| 环境 | 脚本路径 |
|------|---------|
| Windows 安装 | `C:\Users\<用户名>\.trae-cn\skills\doc-map-manager\scripts\` |
| 开发源 | `{workspace}\skill-markets\doc-map-manager\scripts\` |

调用示例（Windows）：
```bash
python "C:\Users\septe\.trae-cn\skills\doc-map-manager\scripts\build-index.py" --incremental
python "C:\Users\septe\.trae-cn\skills\doc-map-manager\scripts\query-index.py" --grab "搜索关键词"
```

> **注意**: 如果上述路径不存在，用 `Get-ChildItem "$env:USERPROFILE\.trae-cn\skills\doc-map-manager\scripts\"` 确认安装位置。

## 排除目录配置

构建索引时默认排除的目录通过 `.docmap/config.json` 配置（按项目独立配置）：

```json
{
  "exclude_dirs": ["bak_v8doc", "references"]
}
```

- 文件位置：`{项目docs目录}/.docmap/config.json`
- 首次运行 `build-index.py` 时自动创建（含默认值）
- 修改后下次构建自动生效，无需改脚本代码

## 新鲜度评分规则

| 距离上次修改 | 评分 | 图标 | 含义 |
|------------|------|------|------|
| 0~7 天 | 1.0 → 0.7 | 🟢 | 新，可信任 |
| 7~30 天 | 0.7 → 0.3 | 🟡 | 注意检查 |
| 30~90 天 | 0.3 → 0.1 | 🔴 | 可能过时 |
| 90+ 天 | ≤ 0.1 | 🔴 | 过时，必须验证 |

## 降级策略

```
--semantic: Zvec → ChromaDB → TF-IDF 降级
--fuzzy: rapidfuzz → difflib 降级
精确/LOOKUP: SQLite SELECT + LIKE（毫秒级）
```

## 脚本依赖

| 依赖 | 用途 | 安装 |
|------|------|------|
| `sqlite3` | 必需 | Python 标准库 |
| `rapidfuzz` | --fuzzy | `pip install rapidfuzz` |
| `chromadb` | --chroma / --semantic(ChromaDB) | `pip install chromadb` |
| `zvec` | --zvec / --semantic(Zvec) | `pip install zvec` |
| `sentence_transformers` | 本地 Embedding | `pip install sentence_transformers` |

## 维护约定

1. `.docmap/docmap.db` 是 SQLite，禁止手动编辑
2. `.docmap/chroma/` 和 `.docmap/zvec/` 加入 `.gitignore`
3. `.docmap/docmap.db` 建议 git track（便携）
4. 新增文档后运行 `build-index.py --incremental` 更新
5. 构建会自动计算新鲜度 + 提取链接图谱 + 标签
