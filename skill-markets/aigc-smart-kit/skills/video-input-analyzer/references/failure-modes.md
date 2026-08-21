# 多模态输入分析失败的 7 类坑 + 修复

> **定位**:`video-input-analyzer` 的反例库。涵盖 v1.0 7 类 + 多模态扩展 5 类。
>
> **不重复**:v1.0 单图反例 → [../../i2v-image-analyzer/references/failure-modes.md](../../i2v-image-analyzer/references/failure-modes.md);本文聚焦多模态特有反例。

## §0 反例分类

| 类别 | 数量 | 章节 |
|------|------|------|
| 多模态识别 | 3 类 | §1-§3 |
| 角色分配 | 2 类 | §4-§5 |
| 视频关键帧 | 2 类 | §6-§7 |

## §1 vision 把多图主体混淆(角色识别错)

**现象**:ref2v 模式下,vision 把"风格参考图"的主体识别成"主角",导致后续 prompt 锁定错误。

**根因**:vision 默认按"画面中心 + 最大物体"判主体,但角色分配需看"信息主导"。

**修复**:
```
1. vision prompt 显式说:"先识别每张图的核心信息(主体 / 场景 / 风格 / 镜头),
    然后匹配到角色候选,不要默认选主体"
2. 强制要求 vision 输出 reference_assignments.role 字段
3. 主 Agent 二次校验:如果 role=character_identity 但图是远景风景,
    → 重新识别
```

## §2 video_metadata 关键帧不全(v2v)

**现象**:v2v 模式下,vision 只输出首帧描述,中帧 / 末帧缺失,导致续写衔接断。

**根因**:vision prompt 没强制"至少 3 帧"。

**修复**:
```
1. video_metadata.key_frames 必填项校验(脚本层强制):
   - 至少 3 帧(首 / 中 / 末)
   - 末帧描述必须含"机位 + 主体状态"
2. 关键帧描述模板:"time_s + 一句话描述(主体 + 动作 + 镜头)"
3. 续写前序的 last_frame_description 必填
```

## §3 audio 字段缺失(节奏参考失效)

**现象**:ref2v 模式下,音频输入存在但 audio 字段全空,vision 没识别节奏 / 情绪。

**根因**:vision 对音频的理解能力有限,需要显式 prompt 引导。

**修复**:
```
1. 音频分析子流程:
   a. 先尝试 whisper / 语音转文字(若可用)
   b. 抽取音频 BPM / 主旋律 / 情绪(vision 模型不一定擅长)
   c. 若完全失败,user_overrides.audio 字段空,标 unknown
2. vision prompt 显式说:"若音频存在,提取节奏关键词 / 情绪关键词"
3. 降级:音频字段缺失不影响主流程,只损失节奏参考
```

## §4 reference_assignments.role 冲突

**现象**:多张图都被分配 character_identity 角色,导致下游 prompt 锁定冲突。

**根因**:vision 没做去重,默认给最显眼的图分配 character_identity。

**修复**:
```
1. schema 校验:role 唯一性(同一类型只能分配 1 次)
2. 优先级规则:
   - 脸部最清晰的图 → character_identity
   - 场景主导的图 → scene_aesthetic
   - 动态的视频 → motion_reference
3. 冲突时主 Agent 二次分配
```

## §5 reference_assignments.rationale 为空

**现象**:vision 输出 role 但 rationale 缺失,下游 prompt 不知道"为什么是这个角色"。

**根因**:vision 简写,只输出 role 不输出 rationale。

**修复**:
```
1. vision prompt 强制要求 rationale(1 句话)
2. schema 校验:rationale 非空
3. 降级:rationale 缺失时,主 Agent 用 role 默认描述补充
   - character_identity: "主体脸部特写,用于锁定身份一致性"
   - scene_aesthetic: "场景色调 / 美学锚"
   - 等
```

## §6 input_mode 误判(mm2v 强制询问)

**现象**:实际是 i2v 但 vision 判定为 mm2v(因为用户文本为空,vision 不知道主体意图)。

**根因**:vision 不理解"用户意图",只看"输入完整性"。

**修复**:
```
1. mm2v 状态 MUST 询问用户,不要强行路由
2. 询问协议 → references/input-mode-detection.md §3
3. 询问时给具体选项 + 实际输入摘要,用户易选
```

## §7 v2v 续写意图错(continuation_intent 误判)

**现象**:v2v 模式下,vision 输出 continuation_intent=extend,但用户实际想 restyle(风格化)。

**根因**:vision 不知道用户意图,默认按"延续"判定。

**修复**:
```
1. user_overrides.continuation 关键词优先(用户在 keywords 里说"风格化" → restyle)
2. 关键词 → continuation_intent 映射:
   - "续写 / 接着 / 继续" → extend
   - "风格化 / 换风格 / restyle" → restyle
   - "循环 / loop" → loop
3. 主 Agent 询问(若关键词不明确)
```

## §8 速查表

| 现象 | 关键修复 |
|------|---------|
| 多图主体混淆 | vision prompt 显式匹配角色 |
| v2v 关键帧不全 | 脚本强制至少 3 帧 + 末帧描述 |
| audio 字段缺失 | 显式 vision prompt + 降级 |
| role 冲突 | schema 唯一性 + 主 Agent 二次分配 |
| rationale 为空 | vision prompt 强制 + 默认描述补充 |
| mm2v 误判 | 询问用户(不要强行路由) |
| continuation_intent 错 | 关键词优先 + 询问兜底 |

## §9 与 v1.0 反例的衔接

```
v1.0 反例(单图场景):
  §1 vision 误识别主体
  §2 风格词过度细化
  §3 时间 / 天气过度推测
  §4 漏掉图中的文字 / Logo
  §5 推荐运镜违反画面构图
  §6 关键词与 vision 冲突未解决
  §7 analyzer 输出后忘了给改造钩子
  §10 vision API 调用失败(实现层兜底)

v2.0 反例(本文新增,多模态特有):
  §1 多图主体混淆
  §2 video_metadata 关键帧不全
  §3 audio 字段缺失
  §4 role 冲突
  §5 rationale 为空
  §6 input_mode 误判
  §7 continuation_intent 错

复用:v1.0 §2-§6 仍适用于 v2.0(单图 / 单视频内的内容)。
```

## §10 来源

- 蒸馏自 `i2v-image-analyzer/references/failure-modes.md`(v1.0 反例)
- 扩展:多模态特有反例 7 类
- 跨平台实战:MiniMax H3 / Seedance 2.5 / 可灵 3.0
- 创建日期:2026-08-20
