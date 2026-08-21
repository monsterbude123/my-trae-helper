# 关键帧抽取 + Vision 分析协议

> 配套主 SKILL.md §3。本文件给出从视频提取关键帧 + 送 vision 模型分析的完整协议。

---

## §1 采样规则

```
视频时长              帧数    采样位置
≤ 6s                  5       0% / 25% / 50% / 75% / 100%
6 ~ 10s               7       0% / 16% / 33% / 50% / 67% / 84% / 100%
> 10s                 9       每 11% 一帧
```

抽帧实现:

```
ffmpeg:$FFMPEG -i input.mp4 -vf "select='eq(n\,0)+eq(n\,N)+...'" -vsync vfr frame_%03d.png
or Python(imageio):reader.get_data(int(ts * fps))
```

抽帧时机(必须在写 prompt 前完成):
- extend:抽末段(最近 4-6 秒)
- first-last-frame:抽首段/尾段各 3 帧
- edit:全段均匀抽帧

## §2 Vision 分析任务

### §2.1 输入

```json
{
  "task": "video_continuity_analysis",
  "frames": ["frame_001.png", "frame_002.png", ..., "frame_005.png"],
  "video_duration": 5.0,
  "context": "V2V prompt 输入准备,需要主体/镜头/调色连续性摘要"
}
```

### §2.2 Vision Prompt 模板

```
你是一位视频连续性分析专家。分析以下 N 帧图片,
输出每帧的特征摘要(主体/动作/镜头/调色),并指出帧间连续性。

输出格式(JSON):
{
  "frames": [{
    "index": 0, "timestamp": 0.0,
    "subject": {"face_id": "high/medium/low", "clothing": "...", "pose": "...", "expression": "..."},
    "motion": {"body_action": "...", "head_direction": "...", "eye_focus": "..."},
    "camera": {"shot_type": "...", "movement": "static/push_in/...", "angle": "eye_level/low/high/..."},
    "color": {"temperature": "4500K/5500K/...", "saturation": "0-100%", "brightness": "0-100%", "shadow_direction": "left/right/..."}
  }],
  "continuity_check": {
    "subject_identity": "consistent/drift_detected",
    "subject_pose_progression": "logical/unclear",
    "camera_motion_consistency": "consistent/jump_detected",
    "color_palette_stability": "consistent/shift_detected",
    "issues": ["..."]
  }
}
```

### §2.3 输出落地

```
保存路径:logs/keyframe_report.json
主代理读取作为 prompt 输入的"原型证据"
```

## §3 失败回退

```
情况 1:vision API 不可用
  → ffmpeg + 自动化 PHash 对比主体一致性
  → FFprobe 提取元数据(duration/fps/codec)
  → 返回"无 vision 摘要"标记,人工标注
情况 2:视频损坏/无法解码
  → 尝试 ffmpeg remux 修复
  → 失败则报告"无法抽帧,需用户提供末帧/起始帧截图"
情况 3:帧间差异巨大(拼接视频)
  → 自动切分多子段,各段独立分析
  → 输出"分段连续性子报告"
```

## §4 三子模式关键帧用法差异

```
extend:用末段分析确认续写段起点(姿态/构图/调色);prompt 引用这些摘要
first-last-frame:首尾帧已给,不要 vision;仅在用户给过渡意图时辅助分析
edit:全段分析 → 锁定原视频元素 → 输出"保留元素清单" + "可修改元素清单"
```

## §5 跨平台与依赖

```
依赖:ffmpeg + 选其一(OpenAI GPT-4V / Claude vision / Qwen-VL)+ Python 3.10+
跨平台:ffmpeg 跨平台二进制 + vision API 跨平台
落地脚本:
  - 复用 skill-markets/aigc-smart-kit/scripts/i2v_vision_call.py
  - 新增 v2v_keyframe_extract.py(主代理后续 task 落地)
```

## §6 来源

- 主 SKILL.md §3(同目录父文件)
- ffmpeg 选帧:https://ffmpeg.org/ffmpeg-filters.html#select
- vision 调用复用:i2v_vision_call.py(本仓内脚本)
