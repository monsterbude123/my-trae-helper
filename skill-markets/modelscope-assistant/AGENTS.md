# modelscope-assistant 使用说明

## 何时加载

| 中文 | 英文 |
|------|------|
| 魔搭、ModelScope | modelscope |
| 模型管理、模型识别、模型下载 | model management, identify model |
| 模型推荐、找模型 | recommend model, find model |
| 磁盘上的模型是什么 | what model is this file |
| 模型去重、模型整理 | model dedup, organize models |
| HuggingFace / CivitAI 模型 | huggingface, civitai |
| 模型部署、模型使用 | model deployment |

## 加载方式

```
Skill(name="modelscope-assistant")
```

## 核心架构

```
modelscope-assistant/
├── SKILL.md                            # 顶层编排器（所有工作流入口）
├── AGENTS.md                           # 本文件
├── .mymodelscope.env                   # 配置文件（仓库根目录或用户家目录）
├── scripts/
│   ├── mymodelscope.py                 # CLI 入口（10 个子命令）
│   ├── mymodelscope/                   # Python 包
│   │   ├── __init__.py
│   │   ├── config.py                   # .env 配置加载
│   │   ├── db.py                       # SQLite 7 表 + CRUD
│   │   ├── scanner.py                  # 本地仓库扫描器
│   │   ├── query.py                    # 多维度查询引擎
│   │   ├── dedup.py                    # SHA256 去重检测
│   │   ├── metadata.py                 # 元数据解析器（文件/URL/SHA256 识别）
│   │   ├── downloader.py              # 跨平台模型下载
│   │   ├── known.py                    # 种子数据导入
│   │   ├── kb.py                       # 知识库管理
│   │   └── registry/                   # 外部 API 客户端
│   │       ├── __init__.py
│   │       ├── base.py                 # RegistryClient 抽象基类
│   │       ├── huggingface.py          # HuggingFace Hub API
│   │       ├── civitai.py              # CivitAI API
│   │       └── modelscope.py           # ModelScope SDK/API
│   └── scan-models.ps1                 # [旧] PowerShell 扫描器
└── references/
    ├── known-models.yaml               # 9 个精品模型种子数据（人工维护）
    ├── known-models.md                 # [旧] Markdown 版本
    ├── model-metadata-schema.md        # 元数据 Schema 定义
    ├── registry-generator.md           # [旧] PS 扫描器说明
    ├── model-search.md                 # 魔搭线上模型搜索
    ├── sdk-usage.md                    # Pipeline API 代码示例
    ├── training.md                     # ms-swift 微调
    ├── api-inference.md                # API 调用指南
    ├── aigc-workflow.md                # AIGC 创作
    ├── mcp-market.md                   # MCP 服务广场
    ├── free-resources.md               # 免费额度
    └── studios.md                      # 创空间部署
```

## 数据库表结构

SQLite 单文件 `.mymodelscope.db`，7 张表：

| 表 | 用途 |
|---|------|
| models | 模型主记录（id, name, type, family, task, sha256, ...） |
| capabilities | 能力标签（model_id → capability） |
| quality_scores | 质量评分（model_id → dimension, score 1-10） |
| recommendations | 推荐用途（model_id → recommendation） |
| tags | 自由标签（model_id → tag） |
| dependencies | 依赖关系（model_id → dep_type, dep_family） |
| scan_history | 扫描记录 |
| knowledge_base | 知识库（部署指南/使用指南/模型信息） |
| schema_version | Schema 版本号 |

## CLI 工作流

```
用户意图 → SKILL.md 路由到对应场景
         → AI 执行 CLI 命令（python scripts/mymodelscope.py ...）
         → 读取 JSON 输出
         → 用自然语言回答用户
```

所有数据查询命令支持 `--format json`。
