---
name: i2v-kling-prompt
description: 可灵 Kling 3.0 / Kling V3 Omni / Kling O1 图生视频(I2V)提示词专项。当用户要在可灵 / Kling 平台上为一张参考图或一组参考素材写视频生成 prompt 时加载。覆盖三段式公式(Subject + Movement + Background)、6 段高级公式、element reference 元素锁定、首尾帧补帧、自然语言运镜(推/拉/摇/移/跟)、pro 模式 1080P。Use when the user needs image-to-video prompts for Kling 3.0 / Kling V3 Omni / Kling O1, including subject binding, start/end-frame interpolation, and motion-only prompting.
version: 1.0.0
license: MIT
metadata:
  parent-skill: aigc-smart-kit
  platform:
    - kling-3.0
    - kling-v3-omni
    - kling-video-o1
    - kling-video-v1-6
    - kling-video-v2
  created: 2026-08-20
---

# i2v-kling-prompt — 可灵 Kling 3.0 I2V 提示词专项

> Kling 3.0 是快手 2026-02 推出的视频模型。核心差异 = **运动 prompt 公式(Subject + Movement + Background)** + **element reference 元素锁定** + **首尾帧补帧**。I2V 工作单元不再是"重写场景",而是"只描述运动"。

## §0 何时加载

```
MUST 加载: 用户问以下任一问题
  - "用可灵 / Kling 生成视频,prompt 怎么写"
  - "Kling 3.0 I2V 提示词"
  - "可灵 图生视频"
  - "三段式 Subject Movement Background"
  - "可灵 element reference 怎么锁定主体"
  - "可灵 首尾帧补帧"
  - 平台明确为可灵生态 / Kling V3 Omni / Kling O1

MUST NOT 加载:
  - H3 / Hailuo / 海螺 → 改去 i2v-h3-prompt
  - Seedance / 即梦 / 豆包 / 字节 → 改去 i2v-seedance-prompt
  - Vidu / 万相 → 当前不在本包覆盖范围,告知用户暂未支持
  - 纯文字 T2V(没有图) → 本 skill 仍可加载,公式兼容
  - 图片生成(T2I) → 改去 minimax-multimodal(image)
```

## §1 三段式公式(Kling 3.0 官方)

> ⚠️ **核心铁律**:图是场景,prompt 是运动。**不要重新描写静态要素**。

```
必备三段:
  Subject:    <主体身份 / 特征(简短,假设图已呈现)>
  Movement:   <主体如何运动 + 镜头如何运动(分句写)>
  Background: <环境如何变化 + 音效触发>

控制部件:
  必填: Movement(动作 + 镜头)
  选填: Subject(简短即可)/ Background(环境响应)/ Audio(对白/环境音)

镜头与动作必须分句写(separate sentence):
  ❌ "The camera pushes in while she turns"
  ✅ "She slowly turns her head toward the camera. Camera: slow push-in on her face."
```

### §1.1 完整示例(单图 I2V)

```yaml
Subject: the man in the navy jacket (KEEP IDENTITY LOCKED)
Movement: he turns his head slowly toward the camera and gives a small, confident nod
Background: soft city lights blur behind him; a gentle breeze moves his hair
Camera: slow push-in on his face
Audio: faint street ambience, distant traffic
Duration: 10 seconds
```

### §1.2 反例对照

```
❌ 弱 prompt(重写场景):
  "A woman with coffee, cinematic, 4K, detailed."

✅ 强 prompt(只写运动):
  Subject: the woman in the studio shot
  Movement: she slowly lifts the coffee cup to her lips and smiles; steam rises gently
  Camera: push-in on her face
  Background: soft window light holds
```

## §2 6 段公式(高级版)

> 当主体复杂 / 镜头需精准 / 多元素联动时,扩 3 段为 6 段。

```
必填 6 段:
  Subject:     <身份 + 关键特征 + 是否锁定>
  Movement:    <主动作 + 次动作(1-2 个清晰动词)>
  Camera:      <运镜 + 振幅 + 速度(自然语言)>
  Background:  <环境响应 + 时间氛围>
  Audio:       <对白 / 环境音 / 静音>(可选)
  Duration:    <5 / 10 / 15 秒>(必填)

扩展示例:
  Subject: the barista in the prep kitchen (KEEP IDENTITY LOCKED via element reference)
  Movement: she opens the wooden shutters with both hands; steam rises from the kettle
  Camera: dolly-in from medium shot to close-up of her hands, slow and steady
  Background: dawn light through half-closed blinds; the street is empty
  Audio: wooden shutters scrape open, distant birdsong, soft kettle hiss
  Duration: 10 seconds
```

### §2.1 镜头三件套(自然语言,Kling 不接受方括号)

| 维度 | 取值 | 默认 | 写法示例 |
|------|------|------|----------|
| **类型** | push-in / pull-out / pan left/right / tilt up/down / track / dolly / handheld / static / orbit / crane | - | "Camera: slow push-in" |
| **振幅** | small / large / medium | medium(省略) | "with small amplitude" |
| **速度** | slow / fast / normal | normal(省略) | "at slow speed" |

> ⚠️ 运镜必带 Camera: 标签前缀,避免与 Movement 句混淆。锁定机位:`Camera: static` / `locked off` / `no movement`。

## §3 element reference 元素锁定协议

> **Kling 3.0 关键差异点** — 当主体身份(人脸 / 服装 / 产品 logo)必须从首帧到尾帧保持一致,必须开启 element reference(subject binding)。否则模型在 5 秒后就会让脸漂到另一个陌生人。

```
何时开启(强制):
  - 角色面部需保持 → 必开
  - 品牌 logo / 产品标识需保持 → 必开
  - 服装 / 道具细节需保持 → 必开
  - 抽象风景 / 无主体 → 不必开

prompt 标注写法(锁定意图):
  Subject: the character (KEEP IDENTITY LOCKED)
  Subject: the product logo (LOCKED, no drift)
  Subject: <主体> (bind via element reference)

prompt 不标注(默许漂移):
  ❌ 错误:只描述外观,不写 LOCKED
  ✅ 正确:首句直接 KEEP IDENTITY LOCKED
```

详细策略 → [references/element-reference.md](references/element-reference.md)

## §4 首尾帧补帧

> 当动作轨迹必须精确(门打开 / 产品旋转 / 角色转身)时,提供 **end frame** 让 Kling 自动补中间。

```
模式选择:
  单帧模式(image_mode=reference):
    images: [<首帧图>]
    → 模型根据 prompt 自由发挥

  首尾帧模式(image_mode=first_last_frame):
    images: [<首帧图>, <尾帧图>]
    → 模型插值中间过渡,轨迹受约束

适用场景:
  ✅ 需要精确动作轨迹 → first_last_frame
  ✅ 需要让模型自由发挥 → reference(默认)
  ❌ 同时给 7 张以上参考图 → 选 1-2 张关键的,不要堆

首尾帧 prompt 要点:
  - 描述变化过程,不描述起点和终态(图已给出)
  - "镜头平稳推进,光线由冷转暖"(只描述中间的演化)
```

## §5 运镜 + 时长 + 输出规格

| 项 | Kling 3.0 / V3 Omni | Kling O1 |
|----|---------------------|----------|
| 时长 | 3 / 5 / 8 / 10 / 15 秒 | 5 / 10 秒 |
| 画幅 | 16:9 / 9:16 / 1:1 / 4:3 / 3:4 | 16:9 / 1:1 / 9:16 |
| 分辨率 | std(720P) / pro(1080P) | 720p / 1080p |
| 参考图上限 | ≤ 7(reference) / 2(first_last_frame) | ≤ 2(first_last_frame) |
| 原生音频 | ✅(V3 Omni,kling-v3-omni) | ❌ |
| 水印 | 默认 false(可选 true) | 默认 false |

### §5.1 运镜词表(中文 + 英文)

| 类别 | 英文 | 中文 |
|------|------|------|
| 推 | push-in / dolly in / slow zoom in | 推近 / 缓推 |
| 拉 | pull-out / dolly out / slow zoom out | 拉远 / 后撤 |
| 摇 | pan left / pan right | 左摇 / 右摇 |
| 移 | track left / track right / tracking shot | 横移 / 跟拍 |
| 跟 | follow shot / chase shot | 跟拍 / 追拍 |
| 俯仰 | tilt up / tilt down | 上仰 / 下俯 |
| 升降 | pedestal up / pedestal down / crane up | 升 / 降 |
| 环绕 | orbit / arc shot | 环绕 / 弧线 |
| 静止 | static / locked-off | 锁机位 / 静止 |

详细词表 → [references/camera-vocabulary.md](references/camera-vocabulary.md)

### §5.2 失败模式速查

| 现象 | 根因 | 修复 |
|------|------|------|
| 主体融化 / 形态崩 | 动作幅度过大或描述模糊 | 拆 1 个主动作 + 1 个次动作;幅度调小 |
| 身份漂移(脸变) | 没开 element reference | Subject 句加 `KEEP IDENTITY LOCKED` |
| 主体微抖(micro-wiggle) | prompt 重复静态描述 + 锁定机位缺失 | 删去静态描写 + `Camera: static / locked off` |
| 动作不到位 / 截断 | 时长太短 | 5s 动作给 10s;简单动作给 5s |
| 镜头运动与动作打架 | 动作和运镜写在同一句 | 分句:`Movement: ... \n Camera: ...` |
| 多动作混乱 | 1 段塞 5 个动作 | 1-2 个清晰动词,其他砍掉 |
| 音频没生成 | 用了 O1 写原生音频 | 切 V3 Omni 或明确写 `generate_audio: true` |

详细反例库 → [references/failure-modes.md](references/failure-modes.md)

## §6 输出模板(交付格式)

子 skill 触发后,主代理按此结构产出:

```yaml
【平台】Kling 3.0 / V3 Omni
【模式】I2V(单图首帧 / 首尾帧)
【时长】10s  【分辨率】720P(std) / 1080P(pro)  【画幅】16:9
【element reference】开 / 关

Subject: <主体身份>(KEEP IDENTITY LOCKED,如有需要)
Movement: <主动作>;<次动作>(1-2 个清晰动词)
Camera: <类型> with <振幅> at <速度>
Background: <环境响应 + 时间氛围>
Audio: <对白 / 环境音 / 静音>(可选)
Duration: <5 / 10 / 15> seconds

# API 参数(若调用 LinkAI / 官方):
model: kling-v3-omni
mode: std   # 或 pro
image_mode: reference  # 或 first_last_frame
images: [<首帧图 URL>, <尾帧图 URL>(可选)]
generate_audio: true
```

## §7 子 skill 自检

- 是否只描述运动,没有重写静态要素
- 必填三段齐:Subject + Movement + Background(简版)或 6 段齐(高级版)
- Camera: 标签与 Movement 分句写
- 主体需要身份一致时,Subject 句显式 `KEEP IDENTITY LOCKED`
- 单 prompt 主动作 ≤ 2 个清晰动词
- 时长根据动作幅度选择(简单 5s,复杂 10-15s)
- 不反向引用 H3 / Seedance 公式(本仓内职责分离)

## §8 references

- [references/element-reference.md](references/element-reference.md) — 元素绑定协议 + 三视图策略
- [references/camera-vocabulary.md](references/camera-vocabulary.md) — 推/拉/摇/移/跟 完整词表
- [references/failure-modes.md](references/failure-modes.md) — 6+ 类失败模式 + 修复指令

## §9 来源

- [How to Use Kling 3.0 Image to Video Like a Pro](https://kling3.app/blog/how-to-use-kling-3-0-image-to-video) — 官方实战指南(S/M/B 三段公式)
- [Kling AI Image-to-Video Quickstart](https://kling.ai/quickstart/image-to-video-guide) — 官方工作流
- [Kling Image 3.0 Omni: Native 4K and Series Mode](https://kling.ai/blog/kling-image-3-omni-4k-series-mode-guide) — V3 Omni 规格
- [LinkAI 统一视频接口(Kling 部分)](https://docs.link-ai.tech/platform/api/video-generation) — kling-v3-omni / kling-video-o1 模型参数
- 蒸馏自主入口 [aigc-smart-kit/SKILL.md §3 跨平台共识铁律](../../SKILL.md)