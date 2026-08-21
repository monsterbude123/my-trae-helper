# Seedance 2.5 — 失败模式 + 修复指令速查

> 实跑 Seedance 反复踩的 7 类坑。每个坑给根因 + 修复 prompt 增量。

## §1 30 秒像 30 个随机镜头

**现象**:画面快速切换,主体在不同场景间穿梭,没有连续感。

**根因**:写成了分镜头列表(Shot 1 / Shot 2 / ... / Shot 30),而非 1 个连续 30 秒。

**修复**:
```
重写为四拍弧线:
  opening (0s to 6s): 1 个连续 take
  progression (6s to 16s): 同一空间持续
  turn (16s to 24s): 同空间内的转向
  resolution (24s to 30s): 同一镜头收束
加 "one continuous take" 强制单段连续
```

## §2 Turn 不明显 / 缺失

**现象**:30 秒里 Opening → Progression → Resolution 直接跳过 Turn,情绪平淡无转折。

**根因**:大多数 brief 隐含 Turn 但 prompt 没显式写。

**修复**:
```
Turn beat 显式写 3 选 1:
  - 情绪转向:tension → calm / cold → warm
  - 场景转向:indoor → outdoor / wide → close
  - 角色转向:observer → protagonist / protagonist → antagonist
```

## §3 角色身份漂移

**现象**:30 秒里角色 A 在 Progression 时变成另一个人,或服装变了。

**根因**:参考图角色没绑定 + 30s 单段太长,模型在中段丢失约束。

**修复**:
```
1. 主体 ≤ 4 个,每个 3-5 张参考图
   @Image1 @Image2 @Image3  → A 身份锁定
   @Image4 @Image5 @Image6  → B 身份锁定
2. prompt 显式:"identity locked by @Image1"
3. 关键节点反复提身份:turn 时 "A still wears the @Image2 jacket"
```

## §4 对白长段独白糊

**现象**:长段对白生成出来音画不同步,口型对不上。

**根因**:单段太长 + 没情绪标注 + 没用双引号。

**修复**:
```
1. 双引号包裹: A barista says, "Your oat latte is ready."
2. 每条 1-2 句,长独白拆多个 beat
3. 情绪标注:whispered / urgent / warm / dry
4. 语言标注(in English / in Mandarin)
```

## §5 镜头一直抖 / 没节奏

**现象**:30 秒里镜头行为一直在动(handheld + shake + dolly 混用),看着累。

**根因**:每个 beat 都用动态运镜,累加效应 = 全程不稳。

**修复**:
```
四拍镜头节奏:
  Opening: locked-off(稳)
  Progression: slow dolly in(缓推)
  Turn: 微抖或转场(动)
  Resolution: pull back 拉远定格(落)

加 "no shake, no handheld" 锁住全局稳定
```

## §6 超出参考预算被截断

**现象**:上传 35 张图 + 12 段视频 + 8 段音频,模型只用前 30 张图 + 截断视频音频。

**根因**:50 槽是 3 个独立预算(30/10/10),不是 1 个 50 池子。

**修复**:
```
图片 ≤ 30,视频 ≤ 10,音频 ≤ 10,各自不超
```

## §7 音乐卡点错

**现象**:@Audio1 音乐播放,但画面动作没在音乐节拍上。

**根因**:没说时间点。

**修复**:
```
1. 时间锚定:
   "Cut the edit to the rhythm of @Audio1 with beats landing on the
    flashes at 6s, 14s, 22s."
2. 关键节点显式标记:
   "At 6s, drop in @Audio1 with a kick drum hit."
```

## §8 长视频接不上(多段续写)

**现象**:第 1 段 30s 末帧和第 2 段开头画面风格 / 主体动作差异大。

**根因**:第 1 段没留"尾帧衔接"位,第 2 段没引用第 1 段末态。

**修复**:
```
1. 第 1 段 Resolution 留 hold 帧:
   "hold on the last two seconds" — 给模型空间

2. 第 2 段 Opening 接住:
   "Opening (30s to 36s): the same wide shot from the previous clip's
    final frame, ..."

3. 共享参考图锁定视觉一致性:
   @Image1 @Image2 同时被两段引用
```

## §9 反 prompt 与负面约束

> Seedance 没有显式 negative_prompt 字段,但 prose 否定有效。

```
负面写法:
  "no camera shake"
  "no identity drift"
  "no on-screen text"
  "no jump cut between shots"
```

## §10 速查表

| 现象 | 关键修复词 |
|------|-----------|
| 像分镜头列表 | "one continuous take" + 四拍弧线 |
| Turn 缺失 | Turn beat 显式写情绪 / 调色 / 场景转向 |
| 身份漂移 | 主体 ≤4 + 参考图绑定 + 关键节点反复提身份 |
| 对白糊 | 双引号 + 1-2 句 + 情绪 + 语言标注 |
| 镜头抖累 | Opening 锁定 / Resolution 拉远定格 |
| 预算超 | 30/10/10 独立预算 |
| 音乐卡点错 | "beats land on X" 时间锚定 |
| 多段续写 | 共享 @Image 引用 + Resolution hold 帧 |

## §11 来源

- [Seedance 2.5 官方页面](https://www.seeddance.io/zh/seedance-2-5)
- [CometAPI Seedance 2.5 prompting](https://www.cometapi.com/how-to-prompt-seedance-2-5/)
- [Venice.ai Seedance 2.5 tips](https://venice.ai/blog/seedance-2-5-prompt-tips)
- [Segmind Seedance 2.5 prep](https://blog.segmind.com/seedance-2-5-prompts-how-to-prep-your-workflow-now/)
- 蒸馏自 [docs/research/2026-08-19-i2v-prompt-skills.md](../../../docs/research/2026-08-19-i2v-prompt-skills.md)