# Kling 3.0 — 失败模式 + 修复指令速查

> 实跑 Kling 3.0 反复踩的 8 类坑。每个坑给根因 + 修复 prompt 增量。

## §1 主体融化 / 形态崩(melting)

**现象**:杯子融进手、衣服化进皮肤、头发糊成一团。

**根因**:
- 动作幅度过大(主体跨越多个空间)
- 描述模糊(没说清主体边界)
- 主体与背景颜色相近(模型分不清)

**修复**:
```
1. 拆 1 个主动作 + 1 个次动作
   ❌ "she reaches, grabs, pours, slides" (4 个动作)
   ✅ "she reaches for the cup and pours slowly" (2 个动作)

2. 描述主体与背景的对比
   ✅ "she wears a white apron against the dark kitchen"

3. 时长给 10s+ — 短时长下模型被迫加速动作
```

## §2 身份漂移(face drift)

**现象**:5 秒后主角的脸 / 服装变成另一个人。

**根因**:没开 element reference,Subject 句没标 LOCKED。

**修复**:
```
1. Subject 句加 L3 强标注
   ✅ Subject: the man in the navy jacket (KEEP IDENTITY LOCKED)

2. 在 Kling 创作平台打开 subject binding 开关

3. 15s 长镜头 → 拆 2 段 × 8s

4. 360° 旋转 → 加 3 张三视图参考图
```

详见 [references/element-reference.md](references/element-reference.md)

## §3 微抖(micro-wiggle)

**现象**:主体在静帧里小幅抖动,像呼吸 / 风吹,但用户没要求。

**根因**:
- prompt 重复静态描述(模型无法确认"是否要动")
- 没说"锁定机位"
- 默认 Kling 会给画面加微动

**修复**:
```
1. 删除静态描写(图已给出,prompt 不必说)
   ❌ "the woman stands in the kitchen" (图已展示站立)
   ✅ 只写运动: "she turns her head slowly"

2. Camera 句显式锁定
   ✅ Camera: static / locked off / no movement

3. 加 "holds a static shot"
```

## §4 动作不到位 / 截断

**现象**:动作刚开始 / 中途就被切掉,主体没完成动作。

**根因**:时长太短,动作跨度大。

**修复**:
```
1. 简单动作(点头 / 微笑 / 转身)— 5s
2. 中等动作(走两步 / 拿起物品)— 8-10s
3. 复杂动作(完整流程 / 多步骤)— 15s

示例对照:
  ❌ "she walks across the room and sits down" 给 5s → 截断
  ✅ "she walks across the room and sits down" 给 10s → 完成
```

## §5 镜头与动作打架

**现象**:镜头运动和主体动作同时发生,看起来混乱。

**根因**:Movement 和 Camera 写在同一句,模型难以分配注意力。

**修复**:
```
❌ "Camera pushes in while she turns"
✅ Movement: she turns her head slowly
✅ Camera: slow push-in

原则:
  - Camera 句只写运镜 + 振幅 + 速度
  - Movement 句只写动作
  - 短镜头(5s):只选一个(Camera 或 Movement 重)
  - 长镜头(10s+):Camera 慢 + Movement 主动作
```

## §6 多动作混乱(action overflow)

**现象**:1 段 5s 里塞了 5 个动作,模型随机选 1-2 个,其他忽略。

**根因**:prompt 超载,主动作过多。

**修复**:
```
铁律: 5 秒内 ≤ 2 个清晰动词

❌ "she enters, looks around, sits, picks up the cup, drinks, smiles"
✅ "she enters and sits down" (5s)
✅ "she picks up the cup and takes a sip" (5s)

长内容 → 拆分多段 + 拼接
```

## §7 音频没生成

**现象**:期望原生音频但输出静默;或用了 O1 模型写 audio 字段被忽略。

**根因**:
- 模型不支持原生音频(O1)
- generate_audio 字段未传或为 false

**修复**:
```
1. 切到 kling-v3-omni(V3 Omni 支持原生音频)
2. LinkAI 接口示例:
   {
     "model": "kling-v3-omni",
     "prompt": "...",
     "generate_audio": true
   }
3. O1 模型必须外加音轨(后期合成)
```

## §8 静音场景被强制加音

**现象**:用户要纯静帧 / 默片,但模型自动加了脚步 / 环境音。

**根因**:Audio 段为空时,Kling 会自行生成环境音。

**修复**:
```
1. Audio 段显式写 "silence" / "no audio" / "mute"
   ✅ Audio: silence throughout the entire clip

2. V3 Omni 中 generate_audio: false
   {
     "model": "kling-v3-omni",
     "generate_audio": false
   }

3. 后期静音处理(兜底方案)
```

## §9 一键速查表

| 现象 | 关键词定位 | 修复标签 |
|------|-----------|----------|
| 融化 | 主动作 >2 / 描述模糊 | 拆动作 + 主体对比 |
| 身份漂 | 没 LOCKED | KEEP IDENTITY LOCKED |
| 微抖 | 静态描写 / 没锁机 | 删静态 + Camera: static |
| 截断 | 时长短 | 5s/10s/15s 时长分级 |
| 镜头打架 | Movement + Camera 同句 | 分句 |
| 动作多 | >2 个动词 | 砍到 ≤2 |
| 没音 | 用了 O1 | 切 V3 Omni |
| 强制加音 | Audio 段空 | 写 "silence" |

## §10 来源

- [Kling 3.0 I2V — Avoid these mistakes](https://kling3.app/blog/how-to-use-kling-3-0-image-to-video)
- [Kling 3.0 I2V — 第 7 节单变量迭代](https://kling3.app/blog/how-to-use-kling-3-0-image-to-video)
- [LinkAI 视频接口 — kling 系列参数](https://docs.link-ai.tech/platform/api/video-generation)
- 蒸馏自主 SKILL.md §5.2 失败模式速查