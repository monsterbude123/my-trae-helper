# batch-manager 模块

**对应源码**: `scripts/vaslib/batcher/batch_manager.py`

## 职责

将 `ScriptAnalysis` 中的台词切分为 15 秒内的批次，用于 TTS 合成。

## 常量

```python
CHARS_PER_SECOND = 4              # 语速假设
TARGET_BATCH_SECONDS = 15         # 目标时长
BATCH_MARGIN_SECONDS = 2          # 安全 margin
MAX_BATCH_SECONDS = 13            # 实际上限 (15 - 2)
TILT_TOLERANCE = 0.2              # 倾斜修正窗口 0.2
```

## 关键函数

### estimate_line_duration(line: Line) -> float

估算单句时长。

```
duration = (中文字符 + 字母数字) / 4
        + 句末标点(。！？) × 0.5s
        + 句中标点(，、；) × 0.2s
        + line.pause_before
        + line.pause_after
```

### correct_tilt(estimated: float, target: float) -> TiltCorrection | None

倾斜修正。

| ratio (估计/目标) | 返回 |
|---|---|
| < 0.8 | TiltCorrection(speed_adjustment = target/estimated, reason="内容过短，需减速") |
| 0.8 ~ 1.2 | None（不需要修正） |
| > 1.2 | TiltCorrection(speed_adjustment = target/estimated, reason="内容过长，需加速") |

### create_batch_plan(analysis: ScriptAnalysis) -> BatchPlan

**主入口**。贪心算法：

```
for scene in analysis.scenes:
    for line in scene.lines:
        if line.type == "action": continue
        if current_batch.estimated + line.duration > MAX_BATCH_SECONDS:
            commit current_batch
            start new batch
        add line to current_batch
```

## 输入输出

```
ScriptAnalysis
  ├── scenes[i].lines  (list[Line])
  └── voice_assignments
       ↓
[create_batch_plan]
       ↓
BatchPlan
  ├── batches: list[Batch]
  │     ├── id="batch-1"
  │     ├── scene_id
  │     ├── lines (filter action)
  │     ├── estimated_duration_seconds
  │     ├── target_duration_seconds = scene.duration
  │     └── tilt_correction
  ├── total_batches
  ├── average_lines_per_batch
  └── overflow_strategy = "split_line"
```

## 业务铁律

- **MAX_BATCH_SECONDS = 13 不能改**（业务铁律 #3）
- 单 batch 内禁止混合多个 scene（保持 scene 内聚性）
- 倾斜修正的 speed_adjustment 范围 [0.5, 2.0]（极端情况 TTS 可能失真）

## 测试

`scripts/tests/test_core.py::TestBatchPlan` - 3 个测试用例。
