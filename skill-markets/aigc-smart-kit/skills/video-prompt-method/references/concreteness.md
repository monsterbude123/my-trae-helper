# 具体性原则(Video Prompting · Concreteness)

> **定位**:`video-prompt-method/SKILL.md §4` 具体性原则的细则。
> **不重复**:SKILL.md §4 的三层具体;本文给"化抽象为具体"流程 + 抽象词弃用清单 + 跨平台改写示例。

## §0 何时加载

```
MUST 加载: 用户用中文模糊词("高级感 / 氛围感 / 震撼") / 主 Agent 改写抽象 prompt
MUST NOT: 用户已给具体描述 — 跳过具体性,直接进入时间切片
```

## §1 三层具体(重申)

```
1. 年龄 / 身份       (20 岁东方少女)
2. 外貌可数特征       (一字肩蕾丝 / 蝴蝶结 / 珍珠串)
3. 装饰 / 细节        (大珍珠耳环 / 水晶手镯 / 蓝眼睛 / 瓷白肌肤)
```

## §2 抽象词 9 类必弃

```
MUST NOT:
  - 高级感 / 高级感拉满
  - 大片感 / 大片感拉满
  - 氛围感 / 氛围感拉满
  - 震撼 / 震撼感
  - 唯美 / 浪漫(无具体对象时)
  - 史诗(无具体对象时)
  - 极致细节(不可数)
  - 完美光线(不可指定)
  - 高级灰色调(换具体颜色)
```

### §2.1 抽象词 → 具体词替换表

| 抽象词 | 具体替代 |
|--------|----------|
| 高级感 | `1920s Art Deco color palette, cinematic teal-and-orange` |
| 氛围感 | `warm golden hour lighting, soft volumetric fog` |
| 大片感 | `anamorphic lens, shallow depth of field, 35mm film grain` |
| 震撼 | `low-angle uphold shot, slow push in, deep bass rumble` |
| 唯美 | `soft pink palette, lens flare, bokeh` |
| 史诗 | `wide aerial shot, dramatic orchestral swell, golden hour` |
| 完美光线 | `golden hour, natural backlight, soft fill from below` |
| 极致细节 | `visible freckles, individual hair strands, fabric texture` |
| 高级灰 | `cool grey #4A4A4A with subtle blue undertone` |

## §3 抽象 → 具体改写流程

```
Step 1 找抽象词所在句
Step 2 问"眼睛能看见的具体物件是什么?"
Step 3 列 3-5 个具体物件 / 动作 / 颜色 / 材质
Step 4 替换抽象词为具体清单
Step 5 重新朗读,确保"闭上眼能想象出画面"
```

### §3.1 改写示例 1(主体抽象 → 具体)

```
❌ 抽象: "年轻貌美的女郎穿过走廊"
   抽象词: 年轻貌美(空泛)、女郎(性别 + 年龄但无具体物件)

Step 2 问: 眼睛能看见的具体物件是什么?
Step 3 列: 20 岁 + 东方 + 一字肩蕾丝连衣裙 + 白色蝴蝶结 + 珍珠串 +
          大珍珠耳环 + 水晶手镯 + 蓝眼睛 + 瓷白肌肤 + 粉润唇
Step 4 替换:
✅ "20 岁东方少女走入画面中央,
    身穿白色一字肩蕾丝连衣裙,
    头扎白色蝴蝶结发饰与珍珠串,
    佩戴大珍珠耳环与水晶手镯,
    蓝眼睛瓷白肌肤粉润唇"
```

### §3.2 改写示例 2(场景抽象 → 具体)

```
❌ 抽象: "一片美丽的森林"
Step 3 列: 古老红杉林 + 阳光透过树冠 + 光柱 + 苔藓覆盖地面 +
          直径 2 米圆形巨石 + 远处小溪流水声
✅ "古老红杉林,阳光透过树冠形成光柱,
    苔藓覆盖地面直径 2 米的圆形巨石,远处小溪流水声"
```

### §3.3 改写示例 3(情绪抽象 → 具体)

```
❌ 抽象: "她闻到很多很多的过往"
   "闻到"是感官动词,但"过往"不可见

✅ 具体: "出现破碎的记忆闪回——模糊的哭泣、破碎的家庭、
              逝去的亲人身影,如同雾般散出熄灭消散"
   可视元素清单:
     - 哭泣(表情)
     - 破碎(裂痕)
     - 家庭(合影)
     - 亲人(剪影)
     - 雾散(粒子)
```

## §4 反例速查

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| 年龄模糊("年轻 / 中年 / 老年") | 具体数字("20 岁 / 35 岁 / 60 岁") |
| 外貌泛指("漂亮 / 帅 / 好看") | 可数特征("一字肩 + 蕾丝 + 蝴蝶结 + 珍珠") |
| 服饰泛指("衣服 / 裙子") | 材质 + 款式 + 颜色("白色 + 一字肩 + 蕾丝连衣裙") |
| 场景抽象("美丽的 / 安静的 / 神秘的") | 物体清单("红杉林 + 光柱 + 苔藓 + 巨石") |
| 情绪抽象("唯美 / 浪漫 / 史诗") | 配色 + 光线 + 镜头("Art Deco + golden hour + low-angle") |
| 不可数词("极致细节 / 完美") | 可数物件("visible freckles, individual hair strands") |
| 不可指定词("完美光线") | 方向 + 类型 + 强度("golden hour backlight, soft fill") |

## §5 与留白(§6 negative-space)的边界

```
具体性原则 vs 留白原则 — 互补关系:

具体性: 必填要素写具体(主体 / 动作 / 主光源 / 主道具)
留白:   装饰 / 背景 / 边角 留空

不是"越具体越好",而是"关键三处具体,其他留白":

✅ 关键三处具体:  主体(20 岁东方少女) + 主动作(spin clockwise) + 主光源(golden hour backlight)
✅ 装饰留白:      背景建筑物 / 路人 / 装饰纹理 不写
```

## §6 来源

- 蒸馏自 `i2v-h3-prompt/references/chinese-prompt-method.md §4, §5`
- 用户实战笔记:`docs/references/note-video-prompt/` §4, §5
- 创建日期:2026-08-20
