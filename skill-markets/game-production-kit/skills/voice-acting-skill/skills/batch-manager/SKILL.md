---
name: batch-manager
description: 批次切分子技能。把整段剧本的台词按 15 秒视频窗口切分为可配音的小批次，并做语速倾斜修正。触发词：批次、15秒、切分、批次大小、tilt、倾斜、batch plan、duration estimate。
---

# Batch Manager 批次切分子技能

## 职责

把 `parsed/script.json` 的所有台词行按 **13 秒上限**（保守于 15 秒视频窗口）贪心切分为批次，输出 `analyzed/batch-plan.json`，供 `annotation-generator` 消费。

## 关键函数

| 函数 | 位置 | 作用 |
|------|------|------|
| `create_batch_plan(parsed, target=13.0)` | `scripts/vaslib/batcher/batch_manager.py` | 入口：生成批次计划 |
| `estimate_line_duration(line, voice)` | 同上 | 估算单行台词朗读时长（秒） |
| `correct_tilt(line, voice, target)` | 同上 | 倾斜修正：调 speed / 改停顿让时长靠近目标 |

## 语速假设速查

基础语速：**4 字符 / 秒**（含标点）。

| 元素 | 时长 |
|------|------|
| 汉字（每字） | 0.25s（=1/4） |
| 标点 `。！？`（句末） | +0.5s |
| 标点 `，；：`（句中停顿） | +0.2s |
| 旁白停顿（`pauseBefore`） | 按 Line.pauseBefore 累加 |

> 语速分支（旁白 5 字符/秒、长难句 3 字符/秒、儿歌 6 字符/秒）→ `references/modules/batch-manager.md`

## 倾斜修正

```
tilt = target / estimate
0.8 ≤ tilt ≤ 1.2 → 无需修正
tilt < 0.8       → 加 [breath] 标签 / 降低 voice.speed
tilt > 1.2       → 删减冗余标点 / 提高 voice.speed（上限 1.3x）/ 强制切批
```

> 铁律约束（>20% 偏差必须修正）、速度上限、边界情况处理 → `references/modules/batch-manager.md`

## 批次切分算法

```
1. 按 Scene 时间段分组，不跨场景合并
2. 在每个 Scene 内，从头开始贪心累加 Line.duration
3. 当前批累计 ≤ 13s 时继续添加；超出则封批，开启下一批
4. 单行超 13s → 强制单独成批（标记 oversized=true）
5. 批次编号格式：{sceneId}-B{n}，如 S03-B02
```

## 输入 / 输出

- **输入**：
  - `output/parsed/script.json`（台词行）
  - `output/analyzed/script-analysis.json`（voice.speed，用于更精准估算）
- **输出**：`output/analyzed/batch-plan.json`

```json
{
  "batches": [
    {
      "id": "S01-B01",
      "sceneId": "S01",
      "lineIds": ["L001", "L002"],
      "estimatedDuration": 8.4,
      "targetDuration": 13.0,
      "tilt": 1.55,
      "corrected": false,
      "oversized": false
    }
  ]
}
```

## 关联技能

- 上游：`script-parser`、`voice-assigner`
- 下游：`annotation-generator`（每批一行注音）

## 详细参考

- 模块详解（含完整算法、边界情况、测试用例）→ `references/modules/batch-manager.md`
- 类型定义：`scripts/vaslib/types/batch.py`（`Batch`, `BatchPlan`）
- 铁律：`references/CONSTRAINTS.md` 第 5 节"配音业务铁律"
