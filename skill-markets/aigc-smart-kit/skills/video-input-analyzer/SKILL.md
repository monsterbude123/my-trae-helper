---
name: video-input-analyzer
description: 视频生成输入理解 — 接受 0~N 张图 / 0~M 个视频 / 0~K 段音频 + 文本,产出统一多模态分析报告(input-report.json)。覆盖 5 种 input_mode: i2v / t2v / v2v / ref2v / mm2v。这是 aigc-smart-kit 视频工作流的"输入理解"环节,替代单图版的 i2v-image-analyzer(v0.9)。Use when the user provides any combination of image / video / audio / text inputs for video generation and wants the AI to analyze and route to the correct video prompt skill.
version: 1.0.0
license: MIT
metadata:
  parent-skill: aigc-smart-kit
  role: input-understanding
  extends: video-prompt-method  (方法学父级)
  replaces: i2v-image-analyzer(v0.9-deprecated)
  input: [images (0..N, URL or local path), videos (0..M), audios (0..K), user-text (string), user-keywords (zero or more)]
  output: structured-input-report.json v2.0
  created: 2026-08-20
---

# video-input-analyzer — 视频输入多模态理解

> **定位**:视频生成工作流的**上游环节**。输入 0~N 张图 + 0~M 个视频 + 0~K 段音频 + 文本,产出统一 schema 的输入分析报告,自动判定 `input_mode`,路由到对应下游 prompt skill。
>
> **替代关系**:本 skill 是 `i2v-image-analyzer/v0.9` 的多模态升级版。老 skill 保留作向后兼容包装(见 ../i2v-image-analyzer/SKILL.md),新调用走本 skill。
>
> **方法学继承**:`extends: video-prompt-method` — 时间切片 / 主角锁定 / 留白等方法学来自父级 skill。本 skill 只聚焦"输入理解"层,不写 prompt 公式。

## §0 何时加载

```
MUST 加载: 用户给任意输入(0~N 张图 / 0~M 视频 / 0~K 音频)+ 让 skill 生成视频 prompt;多模态场景;v2v 续写/风格化;用户希望 AI 自动判断走哪种模式
MUST NOT:  用户已给完整 prompt 只想微调 → 对应儿子 skill;T2I → comfyui-prompt-engineer / minimax-multimodal(image);单图且老 skill 熟悉 → i2v-image-analyzer(向后兼容)
```

## §1 5 步流程(支持多模态输入)

```
Step 1 加载本 skill
Step 2 主 Agent 调用 vision 模型分析多模态输入(见 §2)
Step 3 合并 user-keywords + user-text(见 §3)
Step 4 判定 input_mode(见 §4 + references/input-mode-detection.md)
Step 5 输出 input-report.json v2.0(见 §4)
Step 6 默认路由到对应下游 prompt skill(见 §5)
```

### §1.1 输入识别

```
MUST: 主 Agent 先识别用户给了什么输入:
  图片张数: 0..N | 视频个数: 0..M | 音频段数: 0..K | 用户文本: 空 / 一句话 / 一段描述 / 关键词列表

判定 input_mode 后:
  单图 + 文本    → i2v
  纯文本         → t2v
  单视频 + 文本  → v2v
  多模态 + 文本  → ref2v
  输入不明确     → mm2v(主 Agent 询问用户)
```

## §2 Vision 调用协议(支持三种触发)

> **统一入口** — 主 Agent 调用 `scripts/i2v_vision_call.py`(向后兼容别名)+ 新增多模态参数。脚本内置 system prompt(input-schema v2.0 + multi-modal-vocabulary 标准词)、强制 JSON 输出、降级 partial schema。

### §2.1 三种 vision 触发

| 触发 | 调用参数 | 适用场景 |
|------|---------|----------|
| **图片** | `--image <path/url>` | 单图分析 |
| **视频关键帧** | `--video <path/url> --frame-time <s>` | 视频首帧 / 中间帧 / 末帧分析 |
| **纯文本** | (无 image/video,只传 `--keywords` + `--text`) | T2V 模式(无视觉输入) |

### §2.2 调用示例

```bash
# 向后兼容(单图 + 关键词)
python scripts/i2v_vision_call.py --image photo.jpg --keywords "电影感 温暖 镜头推近" --out image-report.json
# 多图(ref2v 角色分配)
python scripts/i2v_vision_call.py --reference-images "ref1.jpg" "ref2.jpg" --out ref-report.json
# 视频续写(v2v)
python scripts/i2v_vision_call.py --video prev.mp4 --frame-time 2.0 --out v2v-report.json
# 纯文本(t2v)
python scripts/i2v_vision_call.py --text "20 岁东方少女在金色走廊里转圈" --out t2v-report.json
# 多模态(ref2v)
python scripts/i2v_vision_call.py --reference-images "character.jpg" "style.jpg" --video reference-motion.mp4 --out mm-report.json
```

### §2.3 自动 input_mode 检测

```
MUST: --input-mode {auto,i2v,t2v,v2v,ref2v} (默认 auto)

auto 模式判定逻辑(优先级):
  1. 显式 --input-mode 优先
  2. 有视频输入 → v2v(视频续写)
  3. 多模态(>=2 类输入)→ ref2v
  4. 单图 + 文本 → i2v
  5. 纯文本 → t2v
  6. 输入不明确 → mm2v(标记,主 Agent 询问用户)
```

### §2.4 Vision 调用细节(脚本已封装)

- **端点**:`/v1/text/chatcompletion_v2`(复用 `minimax-multimodal/scripts/_client.py` 的共享 HTTP 客户端 + .env 自动加载 + 双区域 + 指数退避 + Key 脱敏)
- **模型**:默认 `MiniMax-M3`(中文场景优);可用 `--model` 切换
- **降级**:vision 调用失败 / 输出非 JSON → 返回 partial schema,`analyzer_status="partial: <原因>"`,CLI exit code = 2

## §3 用户关键词合并(多模态版本)

| 类别 | 关键词示例 | 注入字段 |
|------|-----------|---------|
| **镜头类** | 推近 / 拉远 / 环绕 / 固定 | `recommended_camera.motion` |
| **风格类** | 电影感 / 胶片 / 写实 / 二次元 | `aesthetic.style` |
| **情绪类** | 温暖 / 紧张 / 平静 / 史诗 | `aesthetic.mood` |
| **动作类** | 转头 / 跑步 / 风吹 / 微笑 | `dynamic.suggested_action` |
| **声音类** | 安静 / 城市喧嚣 / 海浪 | `audio.ambient` |
| **时长类** | 5s / 10s / 30s | `dynamic.duration` |
| **角色分配类** | 主体身份 / 场景色调 / 镜头参考 | `reference_assignments[*].role`(ref2v 模式) |
| **续写类** | 同风格 / 续写 / 风格化 | `video_metadata.continuation_intent`(v2v 模式) |

冲突优先级:1. 用户显式关键词 > vision 默认建议 2. 用户没提 = vision 自主决定 3. vision 没识别 = 标 unknown,prompt 不写

用户文本(text)处理: keywords 注入 user_overrides;text 注入 user_text(供下游 prompt 引用,不强制覆盖 vision 字段)

## §4 输出 schema(input-report.json v2.0)

完整 schema 见 [references/input-schema.md](references/input-schema.md)。

### §4.1 v2.0 顶层结构

```json
{
  "version": "2.0",
  "input_mode": "i2v | t2v | v2v | ref2v | mm2v",
  "analyzed_at": "<ISO 8601>",
  "input_inventory": { "images": [...], "videos": [...], "audios": [...], "user_text": "..." },
  "subject": { ... }, "scene": { ... }, "cinematography": { ... },
  "aesthetic": { ... }, "dynamic": { ... }, "constraints": { ... },
  "reference_assignments": [...], "video_metadata": { ... },
  "user_overrides": { ... },
  "analyzer_status": "ok | partial: <原因>"
}
```

### §4.2 向后兼容 v1.0 字段

v2.0 MUST 含 v1.0 字段(image_id / subject / scene / cinematography / aesthetic / dynamic / constraints / user_overrides)。i2v 模式时 image_id = input_inventory.images[0].sha1;非 i2v 模式时 image_id 可省,v1.0 下游用 input_mode + input_inventory 判定。

### §4.3 reference_assignments(ref2v 专属)

```json
"reference_assignments": [
  { "media_id": "img-1", "role": "character_identity", "rationale": "主体脸部特写,用于锁定身份一致性" },
  { "media_id": "img-2", "role": "scene_aesthetic", "rationale": "场景色调 / 灯光 / 美学锚" },
  { "media_id": "vid-1", "role": "motion_reference", "rationale": "镜头运动节奏参考" },
  { "media_id": "aud-1", "role": "rhythm_ambient", "rationale": "节奏 / 氛围参考" }
]
```

`role` 候选值:
- `character_identity`(主体身份)/ `scene_aesthetic`(场景色调/美学)/ `motion_reference`(镜头运动参考)/ `rhythm_ambient`(节奏/氛围)/ `first_last_frame`(首尾帧补帧)/ `style_transfer`(风格化参考)/ `extension_prior`(续写前序)

### §4.4 video_metadata(v2v 专属)

```json
"video_metadata": {
  "source_video": "prev.mp4", "duration_s": 5.0, "fps": 24, "resolution": "1920x1080",
  "key_frames": [
    { "time_s": 0.0, "description": "首帧描述" },
    { "time_s": 2.5, "description": "中帧描述" },
    { "time_s": 5.0, "description": "末帧描述" }
  ],
  "last_frame_description": "主角中近景,镜头静止",
  "continuation_intent": "extend | restyle | loop",
  "style_anchor": "Same Art Deco as source"
}
```

### §4.5 input_mode 判定

判定算法 + 边界 case + 优先级 + mm2v 询问协议 → [references/input-mode-detection.md](references/input-mode-detection.md)

## §5 默认路由(按 input_mode)

### §5.1 路由表

```
analyzer 输出 input-report.json  ↓  按 input_mode 字段路由:
  i2v   → i2v-h3-prompt (默认)        → 可切 i2v-seedance-prompt / i2v-kling-prompt
  t2v   → t2v-h3-prompt (待创建)      → 可切 t2v-seedance-prompt
  v2v   → v2v-h3-prompt (待创建)      → 视频续写 / 风格化
  ref2v → ref2v-h3-prompt (待创建)    → 多素材角色分配
  mm2v  → 由主 Agent 询问用户          → 用户确认后转 i2v/t2v/v2v/ref2v
```

### §5.2 跨平台钩子(改造提示块)

```
交付下游 prompt 后,Agent MUST 输出"改造提示":
─────────────────────────────────────────
【已生成】MiniMax H3 / 三段式 prompt
📌 你可以这样改造:
  • "改 Seedance 2.5 版本"  → 路由到 i2v-seedance-prompt(30s 四拍)
  • "改 Kling 3.0 版本"     → 路由到 i2v-kling-prompt
  • "要更短的 5s"           → 调 duration + 压缩 shot
  • "加对白"                → 在 description 段加 S1 says: "..."
  • "改成 Hailuo 02 方括号运镜" → 走 hailuo02-migration.md 反向
  • "加更多参考素材做 R2V"  → 转 ref2v-h3-prompt
  • "加 BGM"               → 在 non_diegetic_music 段补充
─────────────────────────────────────────
```

### §5.3 钩子的 6 类标准改造

| 用户指令 | 路由目标 | 子 skill 内协议段 |
|---------|----------|------------------|
| 改 Seedance 版本 | i2v-seedance-prompt | §1 四拍 + §2 参考预算 |
| 改 Kling 版本 | i2v-kling-prompt | S/M/B 三段式 + element reference |
| 改时长 / 改对白 / 加 BGM | i2v-h3-prompt | §1 三段式内微调 |
| 加更多参考素材做 R2V | ref2v-h3-prompt | §4 参考素材角色分配 |
| 改回 Hailuo 02 方括号 | i2v-h3-prompt | references/hailuo02-migration.md |
| 改成多镜头切镜 | i2v-h3-prompt | §3 时序切镜 |

## §6 失败模式(MUST 避免)

| ❌ 反模式 | ✅ 正确做法 |
|----------|-----------|
| 不调用 vision,直接编主体 | 必须先 vision → 拿到客观信息 |
| 忘记判 input_mode | MUST 输出 input_mode 字段 |
| ref2v 不分配角色 | MUST 输出 reference_assignments(每个素材有 role) |
| v2v 不分析关键帧 | MUST 至少分析首 / 中 / 末 3 帧 |
| vision 输出后硬塞关键词,忽略冲突优先级 | 关键词仅覆盖 vision 字段;未覆盖字段保留 vision 建议 |
| 默认路由忘了给改造钩子 | MUST 输出 §5.2 改造提示块 |
| schema 字段不全 | 必填字段缺失 → 标 `unknown` 而非留空 |
| 跨平台切的时候重跑 vision | vision 报告一次性产出,跨平台只换包装 |
| mm2v 强行路由(不询问用户) | mm2v MUST 询问用户 |

详细反例库 → [references/failure-modes.md](references/failure-modes.md)

## §7 references & 来源

references:
- [input-schema.md](references/input-schema.md) — v2.0 完整 JSON schema(必填 + 选填 + 字段语义 + v1.0→v2.0 迁移矩阵)
- [multi-modal-vocabulary.md](references/multi-modal-vocabulary.md) — 多模态场景 / 风格 / 镜头词表
- [input-mode-detection.md](references/input-mode-detection.md) — input_mode 判定协议 + 优先级 + 边界 case + mm2v 询问
- [failure-modes.md](references/failure-modes.md) — 多模态分析的 7 类坑 + 修复(含 v1.0 复用部分)

关联引用:
- 下游: 各 video prompt 儿子 skill(i2v-h3-prompt / t2v-h3-prompt / v2v-h3-prompt / ref2v-h3-prompt)
- 方法学: ../video-prompt-method/SKILL.md(本 skill extends 它)
- 向后兼容: ../i2v-image-analyzer/SKILL.md(v0.9-deprecated)
- 统一 vision 脚本: ../../scripts/i2v_vision_call.py(已扩展 --input-mode / --video / --reference-images / --audio / --text)
- 共享 HTTP 客户端: ../../../../minimax-multimodal/scripts/_client.py

来源: 蒸馏自 docs/research/2026-08-19-i2v-prompt-skills.md §4-§5;vision 调用协议参考 minimax-multimodal/scripts/image_generate.py 邻接 vision 模式;由 i2v-image-analyzer/v0.9 升级而来(2026-08-20)
