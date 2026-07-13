# 文档索引集成（doc-map-manager）

> 可选依赖 [doc-map-manager](../../doc-map-manager/SKILL.md)。为 `docs/` 目录提供结构化索引和快速查询能力。

## 集成触发点（完整生命周期）

```
流水线阶段                  doc-map-manager 动作              生命周期阶段
─────────────────────────────────────────────────────────────────────────────
[00-cockpit] 新会话自检  →  --git-diff + 文档索引存在检查   验证/诞生
                            无索引 → 引导初始化
[00-intake]  去重检查    →  --lookup + --semantic 查已有概念      消费
[00-proposal] 提案撰写   →  --grab 快速理解模块文档现有状态        消费
[00-product]  规格撰写   →  --grab 读模块文档 + 已有 spec           消费
[01-contract] 契约撰写   →  --grab 读已有 contracts/               消费
[01.5-docsync] DOC SYNC  →  --git-diff 检测 docs/ 变更             验证
                          →  --incremental (同步完成后)             维护
[10-design]  规划       →  --grab 读模块文档                       消费
[20-dev]     实现       →  --grab 需要时读模块文档                 消费
[20.5-docsync] DOC SYNC  →  --git-diff 二次确认变更                验证
                          →  --incremental (同步完成后)             维护
[40-review]  审查       →  --git-diff 验证 DOC SYNC 真实性         验证
[反馈回流]  漂移修复     →  --incremental (文档变更后)              维护
[归档]      archive     →  --incremental (文件移动后)              维护
[任意阶段]  查文档      →  --grab 一步定位内容                     消费
```

## 使用规则

| 场景 | 命令 | 说明 |
|------|------|------|
| 检测文档变更（推荐） | `python build-index.py --git-diff` | Git diff 精确检测，自动提示 DOC SYNC 缺口 |
| 与历史对比 | `python build-index.py --git-diff --git-ref HEAD~3` | 对比 N 个提交前 |
| 轻量变更检测 | `python build-index.py --diff` | mtime 检测，不需要 Git |
| 增量重建索引 | `python build-index.py --incremental` | 只索引变化的文件，自动排除 specs/changes/ |
| 全量重建索引 | `python build-index.py --chroma` | 含 ChromaDB 语义搜索支持，自动排除 specs/changes/ |
| 查文档内容 | `python query-index.py --grab "关键词"` | 搜索+输出正文，一步到位 |
| 精确查概念 | `python query-index.py --lookup "技术名词"` | 倒排索引，毫秒级 |

> ⚠️ **绝对禁止直接读写文档索引文件**。这些是机器索引文件，动辄数万行 JSON，一次 Read 直接击穿上下文窗口。查询文档始终通过 `doc-map-manager` 技能。

> 文档索引默认排除 `docs/specs/changes/` 路径（铁律 6），始终包含完整索引供查询使用。

## 集成到关键流程

- **Cockpit 起航**：通过 `doc-map-manager` 技能自检文档索引是否存在。不存在 → 提示初始化。存在 → 检测新鲜度。
- **Proposal / Spec / Contract / Planner / Implementer**：所有需要读 `docs/modules/` 理解现有系统的阶段，优先用 `--grab "概念"` 而非盲读整份文档。
- **DOC SYNC GATE**：`--git-diff` 自动检测 `specs/changes/` vs `modules/` 覆盖缺口。同步范围永远由 planner 的「文档影响清单」决定，`--git-diff` 是交叉验证的安全网。
- **Review DOC SYNC VERIFY**：reviewer 必须跑 `--git-diff` 验证 DOC SYNC 是否真正修改了模块文档（不是假性完成）。
- **doc-updater 收尾**：所有同步场景完成后跑 `--incremental`。
- **feedback-loop 回流后**：spec/文档变更后跑 `--incremental`，确保下次查询不拿过期数据。
- **archive 归档后**：文件从 `specs/changes/` 移到 `archive/out/` 或 `archive/done/` 后跑 `--incremental`。
- **intake 去重增强**：在 30% 重叠检查的 Grep 步骤后，追加 `--lookup` 精确匹配 + `--semantic` 语义相似度判定已有概念。

## ⚠️ `--diff` 召回风险须知

| 能检测 | 不能检测（召回盲区） |
|--------|---------------------|
| 磁盘上已经被修改过的 .md 文件 | 需要修改但还没被改的文件（DOC SYNC 最常见场景） |
| 新增/删除的 .md 文件 | `docs/specs/changes/` 中新增的知识点 |
| `docs/` 目录下的文件变更 | `docs/` 之外的文档目录 |

**原则**：`--diff` 检测的是"已发生的变更"，DOC SYNC 关注的是"将要执行的变更"。两者方向不同，不能互相替代。永远先看 planner 的文档影响清单。
