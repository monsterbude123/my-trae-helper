# 输入分析 JSON Schema v2.0(input-report.json)

> **定位**:`video-input-analyzer` 的核心输出契约。下游各 video prompt 儿子 skill 必须按此 schema 读取字段。
>
> **v2.0 vs v1.0 关系**:v2.0 是 v1.0 的多模态扩展版。v1.0 字段(`subject` / `scene` / `cinematography` / `aesthetic` / `dynamic` / `constraints` / `user_overrides`)全部保留,新增 `input_mode` / `input_inventory` / `reference_assignments` / `video_metadata`。
>
> **不重复**:v1.0 字段语义详细见 [../i2v-image-analyzer/references/image-schema.md](../../i2v-image-analyzer/references/image-schema.md) §1-§7(本文只引,不复述)。

## §0 顶层结构 v2.0

```json
{
  "version": "2.0",
  "input_mode": "i2v | t2v | v2v | ref2v | mm2v",
  "analyzed_at": "<ISO 8601>",
  "input_inventory": { ... },
  "subject": { ... },
  "scene": { ... },
  "cinematography": { ... },
  "aesthetic": { ... },
  "dynamic": { ... },
  "constraints": { ... },
  "reference_assignments": [ ... ],
  "video_metadata": { ... },
  "user_overrides": { ... },
  "analyzer_status": "ok | partial: <原因>"
}
```

| 字段 | 必填 | 类型 | 含义 |
|------|------|------|------|
| `version` | ✅ | string | 锁 `"2.0"` |
| `input_mode` | ✅ | enum | `i2v` / `t2v` / `v2v` / `ref2v` / `mm2v` |
| `analyzed_at` | ✅ | string | ISO 8601 时间戳 |
| `input_inventory` | ✅ | object | 全部输入清单(§1) |
| `subject` | ⚠️ 必填(若 vision 可见) | object | 主体识别(沿用 v1.0) |
| `scene` | ⚠️ 必填(若 vision 可见) | object | 场景识别(沿用 v1.0) |
| `cinematography` | ⚠️ 必填(若 vision 可见) | object | 镜头识别(沿用 v1.0) |
| `aesthetic` | ⚠️ 必填(若 vision 可见) | object | 美学风格(沿用 v1.0) |
| `dynamic` | ⚠️ 必填(若 vision 可见) | object | 动态潜能(沿用 v1.0) |
| `constraints` | ⚠️ 选填 | object | 不可变 + 高风险元素(沿用 v1.0) |
| `reference_assignments` | ⚠️ ref2v 模式必填 | array | 参考素材角色分配(§3) |
| `video_metadata` | ⚠️ v2v 模式必填 | object | 视频元信息(§4) |
| `user_overrides` | ⚠️ 选填 | object | 用户关键词 + 文本注入(§5) |
| `analyzer_status` | ✅ | string | `ok` / `partial: <原因>` |

> **沿用 v1.0 字段**:`subject` / `scene` / `cinematography` / `aesthetic` / `dynamic` / `constraints` 字段语义详见 v1.0 schema §1-§6。v2.0 不改变这些字段含义,只增加多模态上下文。

## §1 input_inventory(输入清单)

```json
"input_inventory": {
  "images": [
    {
      "id": "img-1",
      "source": "<url or path>",
      "sha1": "abc123...",
      "size_bytes": 524288,
      "width": 1920,
      "height": 1080
    }
  ],
  "videos": [
    {
      "id": "vid-1",
      "source": "<url or path>",
      "sha1": "def456...",
      "duration_s": 5.0,
      "fps": 24,
      "width": 1920,
      "height": 1080,
      "key_frames": [
        { "time_s": 0.0, "description": "首帧描述" },
        { "time_s": 2.5, "description": "中帧描述" },
        { "time_s": 5.0, "description": "末帧描述" }
      ]
    }
  ],
  "audios": [
    {
      "id": "aud-1",
      "source": "<url or path>",
      "sha1": "ghi789...",
      "duration_s": 10.0,
      "transcript": "<可选,若可用>"
    }
  ],
  "user_text": "<原始用户文本>"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `images[].id` | ✅ | 本地唯一 ID(`img-1`, `img-2` ...) |
| `images[].source` | ✅ | URL 或本地路径 |
| `images[].sha1` | ✅ | 内容指纹(供下游引用) |
| `videos[].key_frames` | ✅ v2v 必填 | 至少含首 / 中 / 末 3 帧 |
| `audios[].transcript` | ⚠️ | 语音转写(若有) |
| `user_text` | ⚠️ | 用户的原始文本输入 |

## §2 input_mode(输入模式判定)

```json
"input_mode": "i2v"
```

| 值 | 含义 | 路由目标 |
|----|------|----------|
| `i2v` | 单图 + 文本(图生视频) | `i2v-h3-prompt`(默认)/ `i2v-seedance-prompt` / `i2v-kling-prompt` |
| `t2v` | 纯文本(文生视频) | `t2v-h3-prompt`(待创建)/ `t2v-seedance-prompt`(待创建) |
| `v2v` | 视频 + 文本(视频续写 / 风格化) | `v2v-h3-prompt`(待创建) |
| `ref2v` | 多模态 + 文本(参考生视频) | `ref2v-h3-prompt`(待创建) |
| `mm2v` | 输入不明确(主 Agent 询问用户) | 由用户决定 |

判定算法详见 [references/input-mode-detection.md](input-mode-detection.md)。

## §3 reference_assignments(ref2v 模式专属)

```json
"reference_assignments": [
  {
    "media_id": "img-1",
    "role": "character_identity",
    "rationale": "主体脸部特写,用于锁定身份一致性"
  },
  {
    "media_id": "img-2",
    "role": "scene_aesthetic",
    "rationale": "场景色调 / 灯光 / 美学锚"
  },
  {
    "media_id": "vid-1",
    "role": "motion_reference",
    "rationale": "镜头运动节奏参考"
  },
  {
    "media_id": "aud-1",
    "role": "rhythm_ambient",
    "rationale": "节奏 / 氛围参考"
  }
]
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `media_id` | ✅ | 引用 `input_inventory.images[].id` 或 `videos[].id` 或 `audios[].id` |
| `role` | ✅ | 见 §3.1 候选值 |
| `rationale` | ✅ | 为什么分配这个角色(供下游 prompt 解释) |

### §3.1 role 候选值

| role | 含义 | 典型对应素材 |
|------|------|------------|
| `character_identity` | 主体身份(脸部 / 产品) | 高清人脸特写 |
| `scene_aesthetic` | 场景色调 / 美学 | 风景 / 场景参考图 |
| `motion_reference` | 镜头运动参考 | 视频 / 多角度照片 |
| `rhythm_ambient` | 节奏 / 氛围参考 | 音频 |
| `first_last_frame` | 首尾帧补帧(i2v 模式) | 2 张图(首帧 + 尾帧) |
| `style_transfer` | 风格化参考(v2v 风格化) | 单图(目标风格) |
| `extension_prior` | 续写前序(v2v 续写) | 单视频 |

### §3.2 分配原则

```
MUST:
  - 每个参考素材 MUST 分配唯一角色(不重叠)
  - rationale MUST 解释"为什么是这个角色"(1 句话)

SHOULD:
  - character_identity 优先分配给"主体脸部清晰"的图
  - scene_aesthetic 分配给"场景主导"的图
  - motion_reference 分配给"镜头运动明确"的视频
  - rhythm_ambient 分配给"节奏感清晰"的音频
```

## §4 video_metadata(v2v 模式专属)

```json
"video_metadata": {
  "source_video": "prev.mp4",
  "duration_s": 5.0,
  "fps": 24,
  "resolution": "1920x1080",
  "key_frames": [
    { "time_s": 0.0, "description": "首帧:主角中近景站立" },
    { "time_s": 2.5, "description": "中帧:主角转身" },
    { "time_s": 5.0, "description": "末帧:主角背对镜头" }
  ],
  "last_frame_description": "主角背对镜头,中近景",
  "continuation_intent": "extend | restyle | loop",
  "style_anchor": "Same Art Deco as source"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `source_video` | ✅ | 原视频文件名 / URL |
| `duration_s` | ✅ | 时长(秒) |
| `fps` | ⚠️ | 帧率 |
| `resolution` | ⚠️ | 分辨率(如 `1920x1080`) |
| `key_frames` | ✅ | 至少首 / 中 / 末 3 帧 |
| `last_frame_description` | ✅ | 末帧详细描述(供续写衔接) |
| `continuation_intent` | ✅ | `extend`(续写)/ `restyle`(风格化)/ `loop`(循环) |
| `style_anchor` | ⚠️ | 风格锚(SAME ART STYLE) |

## §5 user_overrides(关键词 + 文本注入)

```json
"user_overrides": {
  "raw_keywords": ["电影感", "温暖", "镜头推近"],
  "user_text": "20 岁东方少女在金色走廊里转圈",
  "classified": {
    "camera": ["镜头推近"],
    "style": ["电影感"],
    "mood": ["温暖"]
  },
  "merged_into": {
    "aesthetic.style": "cinematic, live-action (用户强化)",
    "aesthetic.mood": "warm, contemplative",
    "cinematography.recommended_motion": "push in (用户强化)"
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `raw_keywords` | ⚠️ | 用户原始关键词(留痕) |
| `user_text` | ⚠️ | 用户原始文本(供下游 prompt 引用) |
| `classified` | ⚠️ | 按类别分桶(§5.1) |
| `merged_into` | ⚠️ | 实际注入到哪些字段(优先级高于 vision) |

### §5.1 分类(多模态版,扩展 v1.0)

| 类别 | 关键词示例 | 注入字段 |
|------|-----------|---------|
| `camera` | 推近 / 拉远 / 环绕 / 固定 | `cinematography.recommended_motion` |
| `style` | 电影感 / 胶片 / 写实 | `aesthetic.style` |
| `mood` | 温暖 / 紧张 / 平静 | `aesthetic.mood` |
| `action` | 转头 / 跑步 / 风吹 | `dynamic.suggested_action` |
| `audio` | 安静 / 城市喧嚣 / 海浪 | `audio.ambient` |
| `duration` | 5s / 10s / 30s | `dynamic.duration` |
| `role`(ref2v) | 主体身份 / 场景色调 / 镜头参考 | `reference_assignments[*].role` |
| `continuation`(v2v) | 续写 / 风格化 / 同风格 | `video_metadata.continuation_intent` |

## §6 最小可用骨架(降级态)

vision 完全失败 / 输入解析失败时:

```json
{
  "version": "2.0",
  "input_mode": "mm2v",
  "analyzed_at": "<iso>",
  "input_inventory": {
    "images": [],
    "videos": [],
    "audios": [],
    "user_text": "<user_text 字段>"
  },
  "subject": { "name": "unknown", "count": 0, "position": "unknown", "pose": "unknown" },
  "scene": { "type": "unknown", "key_elements": [] },
  "cinematography": { "framing": "unknown", "angle": "unknown", "composition": "unknown" },
  "aesthetic": { "style": "unknown", "lighting": "unknown", "mood": "neutral" },
  "dynamic": {
    "movable_subjects": [],
    "recommended_camera_motion": { "type": "static", "amplitude": "medium", "speed": "normal", "rationale": "无法识别主体" },
    "recommended_duration": 5,
    "recommended_rhythm": "normal"
  },
  "constraints": { "must_not_change": [], "high_risk_motion": [] },
  "user_overrides": { "raw_keywords": [], "classified": {}, "merged_into": {} },
  "analyzer_status": "partial: vision 无法识别主体,使用保守默认值"
}
```

下游包装 prompt 时,**`unknown` 字段不写入 prompt**,留 vision 不确定的留白。

## §7 校验清单

下游包装 prompt 前必须自检:

- [ ] 顶层 `version` = `"2.0"`
- [ ] `input_mode` ∈ `{i2v, t2v, v2v, ref2v, mm2v}`
- [ ] `input_inventory` 至少含一类输入(images / videos / audios / user_text)
- [ ] ref2v 模式时 `reference_assignments` 已分配(每个素材有 role + rationale)
- [ ] v2v 模式时 `video_metadata.key_frames` 至少 3 帧
- [ ] `recommended_camera_motion` 含 type + amplitude + speed + rationale 四件套
- [ ] `must_not_change` 至少含"主体身份"(若有人物主体)
- [ ] `user_overrides` 已合并(若有用户关键词)
- [ ] `unknown` 字段不写入 prompt

## §8 v1.0 → v2.0 迁移矩阵

| v1.0 字段 | v2.0 字段 | 兼容说明 |
|----------|----------|----------|
| `version: "1.0"` | `version: "2.0"` | MUST 升级 |
| `image_id` | `input_inventory.images[0].sha1` | i2v 模式时兼容 |
| (无) | `input_mode` | 新增必填 |
| (无) | `input_inventory` | 新增必填 |
| (无) | `reference_assignments` | ref2v 模式时新增 |
| (无) | `video_metadata` | v2v 模式时新增 |
| `subject` / `scene` / ... | (沿用) | 语义不变 |

### §8.1 v1.0 → v2.0 兼容矩阵

| 下游 skill | 接受 v1.0? | 接受 v2.0? | 迁移要求 |
|-----------|------------|------------|----------|
| i2v-h3-prompt | ✅ | ✅ | v2.0 字段忽略即可 |
| i2v-seedance-prompt | ✅ | ✅ | v2.0 字段忽略即可 |
| i2v-kling-prompt | ✅ | ✅ | v2.0 字段忽略即可 |
| t2v-h3-prompt | ⚠️ 需 subject/scene=unknown | ✅ | v2.0 跳过 vision 部分 |
| v2v-h3-prompt | ❌ | ✅ | MUST 升级 v2.0 |
| ref2v-h3-prompt | ❌ | ✅ | MUST 升级 v2.0 |

> **回退策略**:旧 skill 暂未升级 v2.0 时,vision 脚本可生成 v1.0 报告(仅 i2v 模式)。
> 新 skill 一律接收 v2.0。

## §9 来源

- 蒸馏自 `i2v-image-analyzer/references/image-schema.md`(v1.0)
- 多模态扩展:支持 images / videos / audios + 文本
- 创建日期:2026-08-20
