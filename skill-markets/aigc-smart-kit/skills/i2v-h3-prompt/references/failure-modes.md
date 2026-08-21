# H3 失败模式 + 修复指令速查

> 实跑 H3 反复踩的 7 类坑。每个坑给根因 + 修复 prompt 增量。

## §1 画面漂移(Camera Drift)

**现象**:静止场景里镜头自己缓缓移动,产品/建筑出现不希望的形变。

**根因**:H3 默认会做相机轨迹推断,没显式锁机位就会漂。

**修复**:
```
增量 prompt:
  "holds a static shot"
  或
  "the camera stays completely locked off"
  或
  "no camera movement throughout the clip"
```

## §2 主体变形 / 面目全非

**现象**:首帧图里的人物生成到一半脸就变了,或四肢 / 服装逐渐失真。

**根因**:动作幅度过大;或 prompt 重新描述了不该改的主体外观。

**修复**:
```
1. 主动作 + 次动作二选一,不要超过 2 个并行动作
2. 用时序词限制: "first... then..." / "slowly... while..."
3. 不要在 prompt 里重新描写身份 / 服装 / 颜色 — 图已锁定
4. 增加参考图(参考素材角色分配中的"锁定身份")
```

## §3 文本渲染糊

**现象**:招牌 / 字幕 / 品牌字生成出来不是预设文字,出现伪字符。

**根因**:没显式 verbatim 标注,H3 自由发挥。

**修复**:
```
rises verbatim: 'OPEN 24H'        ← 海报 / 招牌
subtitle: 'Welcome back'          ← 字幕
```

## §4 对口型错位

**现象**:角色嘴型与对白不一致,音画不同步。

**根因**:对白没标 S1 标签,模型不知道哪句话归谁。

**修复**:
```
S1 says: "First batch of the morning."   ← 显式角色标签
S2 says: "Two croissants, please."
```

## §5 音画错位 / 三层混在一起

**现象**:背景音乐突然盖过对白,或对白出现在 soundscape 字段里。

**根因**:三段顺序错 / 字段用错。

**修复**:必须严格三段顺序
```
1. integrated_multimodal_description   ← 视觉 + 动作触发的具体声音 + 对白
2. overall_soundscape                   ← 环境音 + 持续氛围
3. non_diegetic_music                   ← BGM / 配乐(可留空)
```

## §6 风格漂移

**现象**:同系列 prompt,有的镜头写实,有的镜头变成 3D 渲染。

**根因**:美学词散落 / 一致性不够。

**修复**:
```
在句首 / 景物描写 / 收束各点一次美学词:
  "Live-action, cinematic, color graded teal-and-orange, ..."
  "...color graded teal-and-orange background..."
  "...hold on the final frame, cinematic color graded teal-and-orange."
```

## §7 多镜头切得乱

**现象**:5s 的 clip 切了 3 个镜头,信息密度爆炸;或时间戳错乱。

**根因**:切镜标准没统一 / 时间戳格式错。

**修复**:
```
1. 切镜标准: 仅"有新信息到来"才切 — 距离变化用运镜,场景变化用 cut
2. 时间戳格式: `00:05.000`(5 位小数,非整数)
3. 每个 Shot 必须独立完整(主体/动作/镜头各自成立)
```

## §8 反例叠加:首尾帧模式不补帧

**现象**:给了首帧 + 尾帧两张图,生成出来的中间帧完全偏离尾帧。

**根因**:prompt 没明确说"从首帧过渡到尾帧"。

**修复**:
```
The video begins from the first frame and smoothly transitions to the last
frame. <中间过程的描述>.
```

## §9 速查表

| 现象 | 关键修复词 |
|------|-----------|
| 漂移 | `holds a static shot` / `no camera movement` |
| 变形 | 主动作 + 次动作二选一;不重新描写身份 |
| 文字糊 | `rises verbatim: "..."` |
| 对口型 | `S1 says: "..."` |
| 音画错 | 严格三段顺序 |
| 风格漂 | 美学词在句首 / 景物 / 收束各点一次 |
| 切镜乱 | 仅新信息切;时间戳 `00:NN.NNN` |
| 补帧偏 | "begins from first frame, smoothly transitions to last frame" |

## §10 来源

- [MiniMax H3 官方提示词指南](https://minimaxh3.studio/zh/guide/minimax-h3)
- [promptslove H3 generator tips](https://promptslove.com/free-tools/minimax-video-prompt-generator/)
- 蒸馏自 [docs/research/2026-08-19-i2v-prompt-skills.md](../../../docs/research/2026-08-19-i2v-prompt-skills.md)

---

## §11 中文笔记法专项反例(MUST 避免)

> 蒸馏自 `docs/references/note-video-prompt/` 17 张用户实战截图(2026-08)。
> 完整方法 → [chinese-prompt-method.md](chinese-prompt-method.md)。本节是 9 类反模式速查。

### §11.1 9 类反模式

| ❌ 反模式 | ✅ 正确写法 | 出处图 |
|---------|----------|--------|
| 一段连写 6s 全部内容 | 按 [00:00-00:02] / [00:02-00:05] / [00:05-00:08] 切片 | 时间截法 258 |
| 主角淹没在场景描写(街景/建筑/鹅卵石/咖啡馆大段铺陈) | 主体优先,场景只 1-2 句承载 | 主角锁定 268/275 |
| 镜头语言与主体动作混写("镜头环绕,跟随主角转圈") | 三层独立:景别 + 镜头 + 主体动作 各占一短句 | 三件套 269/270 |
| 抽象词("高级感/震撼/大片感/氛围感拉满") | 具体可见("20 岁少女 + 白色蕾丝裙 + 珍珠耳环 + 蓝眼睛") | 化抽象为具体 259 |
| 6 个主体平均用力 | 主角锁定,配角 ≤2 个 1-2 句话 | 分层 262 |
| 主角设定模糊("年轻貌美女郎") | 精确("20 岁东方少女 + 一字肩蕾丝 + 蝴蝶结 + 珍珠串") | 具体性 260 |
| 6s 里 5 个动作 | 每个时段 1 个主动作 | 时段细分 272 |
| 没有"前因后果"结构 | 登场 → 动作 → 收束 三段弧线 | 时间截法 258 |
| 无声音设计 | BGM 节奏卡动作 + 情绪节拍 + 铃响 cue | 故事板 8 模块 |

### §11.2 修复流程(主 Agent 检测到反例时)

```
1. 定位违反的 §11.1 哪一类(抽象词/淹没/混写/...)
2. 查 [chinese-prompt-method.md](chinese-prompt-method.md) 对应章节找正确写法
   - 抽象词 → §5 化抽象为具体
   - 淹没 → §3 主角锁定 4 步
   - 混写 → §7 三件套分层
   - 6s 连写 → §1 时间截法 + §10 4 时段
   - 模糊 → §4 具体性原则(三层)
3. 重写该段,保持其他段不动
4. 重新跑 §11 检查表 PASS
```

## §12 "主角锁定"约束 — image-report.json 必须含

> 主 Agent 包装 prompt 时 MUST 把以下字段注入 description 的"主体锁定"段,贯穿全文。
> 来源:`chinese-prompt-method.md §3.2`(主角锁定 4 步)+ §3.4(主角锁定示例)。

### §12.1 analyzer §4 schema 调整建议

`constraints.must_not_change` 必须含:

```yaml
must_not_change:
  - subject_face_identity      # 主体脸部(由 image-analyzer subject.name 提供)
  - subject_facial_expression  # 主体表情(如"笑容持续")
```

### §12.2 主 Agent 包装协议

```
Step 1: 读 image-report.json → subject.name + expression
Step 2: 把 subject_face_identity 写入 description 第一句
        "保持 <name> 脸部一致"
Step 3: 把 subject_facial_expression 写入每个时段的主动作前
        "维持 <expression> 不变"
Step 4: §11.1 检查"主角淹没"项 PASS(主体在每段前 1-2 句)
Step 5: 反例检测 → 主角设定模糊 → 用 §4 三层具体改写
```

### §12.3 字段注入示例

```
analyzer 输出:
  subject.name: "20 岁东方少女"
  subject.expression: "嘴角上扬 15°"

注入后 description 句首:
  [Shot 1] [00:00-00:02] Live-action, cinematic,
    保持 20 岁东方少女 脸部一致, 维持 嘴角上扬 15° 不变,
    a medium eye-level shot frames her walking into ...
```

## §13 来源扩展

- 用户实战笔记:`docs/references/note-video-prompt/`(17 张 jpg,2026-08)
- 中文笔记法细则:[chinese-prompt-method.md](chinese-prompt-method.md)
- 主角锁定协议:[chinese-prompt-method.md §3](chinese-prompt-method.md)