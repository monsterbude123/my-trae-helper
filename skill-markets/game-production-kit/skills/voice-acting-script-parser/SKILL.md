---
name: script-parser
description: 剧本解析子技能。将 Markdown 格式的中文影视/动画剧本（含角色元信息、场景表格、台词行）解析为结构化 ParsedScript JSON。触发词：解析剧本、剧本格式、Markdown、表格、分镜、ParsedScript、extract_characters。
---

# Script Parser 剧本解析子技能

## 职责

把 `raw/*.md` 格式的中文剧本解析为 `parsed/script.json`，包含三块结构：

- `meta` — 剧本元信息（标题、角色清单、总时长）
- `scenes` — 场景列表（场景号、时间段、地点、台词行）
- `lines` — 每条台词行（对话 / 旁白 / 动作 / 情感提示）

## 关键函数

| 函数 | 位置 | 作用 |
|------|------|------|
| `parse_script(md_path)` | `scripts/vaslib/parser/script_parser.py` | 入口：读 .md → 返回 `ParsedScript` |
| `parse_time_range(t: str)` | 同上 | 解析 `MM:SS~MM:SS` 时间段为秒数 |
| `parse_dialogue(cell: str)` | 同上 | 把台词单元格拆为多行 `Line`（多角色对话拆分） |
| `extract_characters(meta_block: str)` | 同上 | 从"角色介绍"块提取 `Character[]` |
| `extract_emotion_hint(note: str, action: str)` | 同上 | 从备注列和动作描述里抽取情感提示 |

## 剧本格式约定

输入文件须为 Markdown，结构：

```markdown
# 剧本标题

## 角色介绍
- 角色A（男 / 青年 / 川渝口音 / 性格：机智）
- 角色B（女 / 少年 / 沪普 / 性格：傲娇）

## 场景
| 场景号 | 时间 | 地点 | 描述 |
|--------|------|------|------|
| 1 | 00:00~00:15 | 街头 | 雨夜追逐 |

## 分镜
| 镜号 | 时间线 | 描述 | 动作 | 台词 | 备注 |
|------|--------|------|------|------|------|
| 1-1 | 00:00~00:05 | 雨中特写 | 角色A奔跑 | 站住！ | 反差萌 |
| 1-2 | 00:05~00:10 | 街角 | 角色B拦路 | 我等你很久了 | 冷笑 |
```

**必备列**：`时间线`、`台词`、`动作`、`备注`（含方言 / 情感线索）。

**台词类型识别**：

- `角色名：台词` → `dialogue`
- `OS / 旁白 / 字幕` → `narration`
- `[动作描述]` 方括号内容 → `action`
- `备注`列中的情感关键词 → `emotion_hint`

## 输入 / 输出

- **输入**：`raw/*.md`（UTF-8 编码）
- **输出**：`output/parsed/script.json`

## 使用建议

- 解析前用 `detect_format` 检查格式（`markdown-table` / `fountain` / `plain-text`）
- 多角色对话需逐行拆分，确保后续音色分配按角色一对一
- 旁白（OS）单独归类，不要混入 dialogue

## 关联技能

- 上游：无需
- 下游：`voice-assigner`（消费 ParsedScript 分配音色）、`batch-manager`（消费 ParsedScript 切分批次）

## 详细参考

- 模块详解（含完整代码示例、解析失败处理、测试覆盖）→ `references/modules/script-parser.md`
- 类型定义：`scripts/vaslib/types/script.py`（`ParsedScript`, `Scene`, `Line`, `Character`）
- 实施计划：`references/superpowers/plans/2026-05-05-phase1-script-annotation.md`
