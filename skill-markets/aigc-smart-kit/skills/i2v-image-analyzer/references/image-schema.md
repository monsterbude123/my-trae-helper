# 图理解 JSON Schema(image-report.json)

> `i2v-image-analyzer` 的核心输出契约。下游 `i2v-h3-prompt` / `i2v-seedance-prompt` 必须按此 schema 读取字段,不允许自行推测未声明字段。

## §0 顶层结构

```json
{
  "version": "1.0",
  "image_id": "<hash 或 URL>",
  "analyzed_at": "<ISO 8601>",
  "subject": { ... },
  "scene": { ... },
  "cinematography": { ... },
  "aesthetic": { ... },
  "dynamic": { ... },
  "constraints": { ... },
  "user_overrides": { ... }
}
```

| 字段 | 必填 | 类型 | 含义 |
|------|------|------|------|
| `version` | ✅ | string | schema 版本(锁 1.0) |
| `image_id` | ✅ | string | 图标识(URL / hash) |
| `analyzed_at` | ✅ | string | ISO 8601 时间戳 |
| `subject` | ✅ | object | 主体识别(见 §1) |
| `scene` | ✅ | object | 场景识别(见 §2) |
| `cinematography` | ✅ | object | 镜头识别(见 §3) |
| `aesthetic` | ✅ | object | 美学风格(见 §4) |
| `dynamic` | ✅ | object | 动态潜能(见 §5) |
| `constraints` | ⚠️ 选填 | object | 不可变 + 高风险元素(见 §6) |
| `user_overrides` | ⚠️ 选填 | object | 用户关键词注入(见 §7) |

## §1 subject(主体)

```json
{
  "subject": {
    "name": "young woman",
    "count": 1,
    "position": "center-frame, mid-ground",
    "pose": "standing, slight smile, looking at camera",
    "expression": "calm, contemplative",
    "identity_cues": [
      "short black hair",
      "red jacket",
      "freckles",
      "no glasses"
    ],
    "secondary_subjects": [
      { "name": "small dog", "position": "lower-left", "size": "small" }
    ]
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 主体名(英文,供 prompt 使用) |
| `count` | ✅ | 数量 |
| `position` | ✅ | 位置描述(center / left-third / foreground ...) |
| `pose` | ✅ | 姿态(standing / sitting / running ...) |
| `expression` | ⚠️ | 表情(neutral / happy / tense ...) |
| `identity_cues` | ⚠️ | 身份线索(供锁定身份 — 防漂移) |
| `secondary_subjects` | ⚠️ | 次要主体(背景人物 / 宠物) |

## §2 scene(场景)

```json
{
  "scene": {
    "type": "outdoor",
    "subtype": "urban street / forest / cafe interior / studio / abstract",
    "time_of_day": "golden hour / midday / night / overcast",
    "weather": "clear / rainy / snowy / foggy",
    "depth_layers": [
      "foreground: blurred autumn leaves",
      "mid-ground: subject standing",
      "background: sunset skyline"
    ],
    "key_elements": [
      "autumn tree",
      "warm backlight",
      "long shadow",
      "cobblestone ground"
    ]
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | indoor / outdoor / studio / abstract |
| `subtype` | ⚠️ | 细分类 |
| `time_of_day` | ⚠️ | 时段 |
| `weather` | ⚠️ | 天气 |
| `depth_layers` | ⚠️ | 前景/中景/背景(供运镜决策) |
| `key_elements` | ✅ | 3-5 个关键元素(供 prompt 引用) |

## §3 cinematography(镜头)

```json
{
  "cinematography": {
    "framing": "medium shot",
    "angle": "eye level",
    "composition": "rule-of-thirds, subject on right-third",
    "depth_of_field": "shallow / deep / bokeh",
    "current_camera_implication": "static / suggests motion"
  }
}
```

| 字段 | 必填 | 候选值 |
|------|------|--------|
| `framing` | ✅ | extreme-wide / wide / medium / close-up / extreme-close-up |
| `angle` | ✅ | eye level / low angle / high angle / bird's eye / dutch angle |
| `composition` | ✅ | rule-of-thirds / centered / symmetric / diagonal / minimal |
| `depth_of_field` | ⚠️ | shallow / deep / bokeh |
| `current_camera_implication` | ⚠️ | 静态 / 已暗示某种运动方向 |

## §4 aesthetic(美学)

```json
{
  "aesthetic": {
    "style": "cinematic, live-action, photographic",
    "art_style": "realistic / anime / 3D-render / oil-painting / minimal",
    "lighting": "golden hour, natural backlight, soft",
    "color_grade": "warm teal-and-orange, high contrast",
    "texture": "film grain, soft halation",
    "mood": "contemplative, warm, nostalgic"
  }
}
```

| 字段 | 必填 | 候选值 |
|------|------|--------|
| `style` | ✅ | cinematic / photographic / illustration / anime / 3D |
| `art_style` | ⚠️ | realistic / anime / 3D-render / oil-painting / minimal |
| `lighting` | ✅ | 自然光 / 棚拍光 / 体积光 / 霓虹 / 烛光 |
| `color_grade` | ⚠️ | 暖 / 冷 / 高对比 / 低饱 / 复古 / 现代 / 黑白 |
| `texture` | ⚠️ | 胶片 / 数码 / 高清 / 颗粒 / 干净 |
| `mood` | ✅ | 情绪关键词(2-3 个) |

## §5 dynamic(动态潜能)

```json
{
  "dynamic": {
    "movable_subjects": [
      "hair (风吹)",
      "leaves (飘落)",
      "subject facial expression (微笑)",
      "shadow (拉长)"
    ],
    "locked_subjects": [
      "background skyline (构图锚点)",
      "subject identity (身份锁定)"
    ],
    "recommended_camera_motion": {
      "type": "push in",
      "amplitude": "small",
      "speed": "slow",
      "rationale": "强调主体,符合画面中心构图"
    },
    "recommended_duration": 5,
    "recommended_rhythm": "slow, contemplative",
    "multi_shot_potential": "low (单场景即可)/ high (建议切镜)"
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `movable_subjects` | ✅ | 可动元素 + 推荐动作 |
| `locked_subjects` | ⚠️ | 不能动的(锚点) |
| `recommended_camera_motion` | ✅ | 推荐运镜(类型 + 振幅 + 速度 + 理由) |
| `recommended_duration` | ✅ | 推荐时长(秒) |
| `recommended_rhythm` | ✅ | 推荐节奏(慢 / 中 / 快 + 情绪) |
| `multi_shot_potential` | ⚠️ | 是否建议多镜头 |

## §6 constraints(约束)

```json
{
  "constraints": {
    "must_not_change": [
      "subject face identity",
      "red jacket color",
      "background skyline",
      "any on-screen text"
    ],
    "high_risk_motion": [
      "fast rotation (face will distort)",
      "camera shake on close-up (will jitter)",
      "zooming past subject (will lose identity)"
    ],
    "text_in_image": [
      { "location": "lower-right corner", "content": "OPEN 24H" }
    ]
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `must_not_change` | ⚠️ | 必须保持不变的(供 prompt 显式约束) |
| `high_risk_motion` | ⚠️ | 高风险动作(prompt 要避免) |
| `text_in_image` | ⚠️ | 图中文字(verbatim 渲染用) |

## §7 user_overrides(关键词注入)

```json
{
  "user_overrides": {
    "raw_keywords": ["电影感", "温暖", "镜头推近"],
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
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `raw_keywords` | ✅ | 用户原始关键词(留痕) |
| `classified` | ✅ | 按类别分桶 |
| `merged_into` | ✅ | 实际注入到哪些字段(优先级高于 vision 默认) |

## §8 最小可用骨架

vision 调用失败 / 图太模糊时,使用最小骨架:

```json
{
  "version": "1.0",
  "image_id": "<hash>",
  "analyzed_at": "<iso>",
  "subject": { "name": "unknown", "count": 0, "position": "unknown", "pose": "unknown" },
  "scene": { "type": "unknown", "key_elements": [] },
  "cinematography": { "framing": "unknown", "angle": "unknown", "composition": "unknown" },
  "aesthetic": { "style": "unknown", "lighting": "unknown", "mood": "neutral" },
  "dynamic": {
    "movable_subjects": [],
    "recommended_camera_motion": { "type": "static", "amplitude": "medium", "speed": "normal", "rationale": "无法识别主体,默认保守" },
    "recommended_duration": 5,
    "recommended_rhythm": "normal"
  },
  "constraints": { "must_not_change": [], "high_risk_motion": [] },
  "analyzer_status": "partial: vision 模型无法识别主体,使用保守默认值"
}
```

下游包装 prompt 时,**`unknown` 字段不写入 prompt**,留 vision 不确定的留白。

## §9 校验清单

下游包装 prompt 前必须自检:

- [ ] 5 个必填顶层字段(subject / scene / cinematography / aesthetic / dynamic)
- [ ] `recommended_camera_motion` 含 type + amplitude + speed 三件套
- [ ] `must_not_change` 至少含"主体身份"(若有人物主体)
- [ ] `user_overrides` 已合并(若有用户关键词)
- [ ] `unknown` 字段不写入 prompt