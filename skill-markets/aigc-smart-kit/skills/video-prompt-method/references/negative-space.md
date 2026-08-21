# 留白原则(Video Prompting · Negative Space)

> **定位**:`video-prompt-method/SKILL.md §6` 留白原则的细则。
> **不重复**:SKILL.md §6 的留白分配表;本文给"过度指定反例库" + 负面约束写法 + 留白边界判定。

## §0 何时加载

```
MUST 加载: 主 Agent 处理"用户给了一长串细节" / 修复过度指定 prompt / 优化长 prompt
MUST NOT: 用户只给几个关键词 / 简洁 prompt — 不需要"砍细节"
```

## §1 留白分配表(重申)

| 级别 | 内容 | 必填? |
|------|------|-------|
| **MUST 具体** | 主体身份 / 主动作 / 主光源 / 主要道具 | ✅ |
| **SHOULD 具体** | 主场景(一句话)+ 美学风格(STYLE 锚) | ⚠️ |
| **留白 OK** | 背景杂物 / 路人表情 / 装饰纹理 / 边角物件 | - |
| **留白 MUST** | 倒数第二句之后的内容(给模型发挥空间) | - |

## §2 过度指定反例库

### §2.1 数量 / 程度过度指定

```
❌ "每一颗雪花都不同、夕阳融进霜雪、海面倒映出 12 种渐变色彩"
   → 模型无法理解 + 互相矛盾
✅ "夕阳倒映在冰封的海面,形成一条橙色光带"
```

### §2.2 时间 / 空间过度指定

```
❌ "0.5s 时看向左、1s 时抬头、1.5s 时微笑、2s 时转身、2.5s 时走出画面"
   → 模型不识别毫秒级指令
✅ "[00:00-00:02] 中景, 少女 A 看向左
   [00:02-00:04] 中近景, 少女 A 抬头微笑
   [00:04-00:06] 中景, 少女 A 转身走出画面"
```

### §2.3 装饰过度指定

```
❌ "街道两旁是古老的鹅卵石,维多利亚式建筑,铸铁街灯,
   飘落的梧桐叶,咖啡馆橱窗里陈列着各种糕点,远处传来马车铃声"
   → 8 句话写场景,主体淹没
✅ "街道两旁维多利亚式建筑,远处马车铃声。"
```

### §2.4 不可数 / 不可指定词

```
❌ "极致细节 / 完美光线 / 高级感拉满"
   → 不可数 / 不可指定,模型无法理解
✅ "visible freckles, individual hair strands, fabric texture"
   "golden hour, natural backlight, soft fill from below"
   "1920s Art Deco color palette, cinematic teal-and-orange"
```

## §3 负面约束写法(平台特化指针)

```
通用规则: 负面约束 "no X" 比正面 "完美细节" 更生效

各儿子 skill 字段名:
  H3 / Hailuo:  constraints.must_not_change / .high_risk_motion
  Seedance:    "no camera shake" / "no face distortion"
  可灵:        "consistent identity throughout" / element reference
  Vidu:        negative_prompt 字段
  万相:        negative_prompt 字段
```

### §3.1 负面约束三类

```
1. 身份约束:    "subject face identity remains consistent throughout"
2. 风格约束:    "no camera shake", "no face distortion", "no color shift"
3. 动作约束:    "no rapid rotation", "no zoom past subject", "no excessive motion blur"
```

### §3.2 负面约束的"MUST" vs "SHOULD"

```
MUST 写负面约束(模型已知会漂移):
  - 主体脸部一致性(必写)
  - 主体服饰颜色保持(必写)
  - 主体身份线索(必写)

SHOULD 写负面约束(平台原生问题):
  - H3:        防止画面漂移 → "camera stays locked off"
  - Seedance:  防止过度动效 → "no excessive motion"
  - 可灵:      防止主体变形 → "subject face remains consistent"

OPTIONAL(看场景):
  - 背景元素保持
  - 文字 verbatim 渲染
```

## §4 留白边界判定

### §4.1 何时必须具体

```
判定标准: "去掉这句,模型还能不能稳定产出?"

✅ 必须具体(去掉会漂移):
  - 主体身份 / 外貌 / 服饰
  - 主动作(谁 + 做什么)
  - 主光源(光线方向 + 类型)
  - 主道具(关键物件)
  - 美学风格(STYLE 锚)

❌ 可省略(去掉仍能产出):
  - 背景杂物 / 路人表情
  - 装饰纹理 / 边角物件
  - 倒数第二句之后的内容
```

### §4.2 何时必须留白

```
判定标准: "这句是必备还是装饰?"

必备: 主体 / 主动作 / 主光源 / 主道具 / 美学风格
装饰: 背景杂物 / 路人 / 装饰纹理 / 边角物件 / 远景细节

装饰 = 留白 OK → 让模型自由发挥
```

## §5 实战示例 — 同一概念的不同详细度

### §5.1 过度指定版(❌)

```
一位 20 岁东方少女走入画面中央,身穿白色一字肩蕾丝连衣裙,
头扎白色蝴蝶结发饰与珍珠串,佩戴大珍珠耳环与水晶手镯,
蓝眼睛瓷白肌肤粉润唇。街道两旁是古老的鹅卵石,
维多利亚式建筑,铸铁街灯,飘落的梧桐叶,
咖啡馆橱窗里陈列着各种糕点,远处传来马车铃声,
电影感大片氛围,高级感拉满,极致细节震撼。
```

### §5.2 留白优化版(✅)

```
一位 20 岁东方少女走入画面中央,身穿白色一字肩蕾丝连衣裙,
头扎白色蝴蝶结发饰,佩戴大珍珠耳环。
街道两旁维多利亚式建筑。
1920s Art Deco color palette, cinematic teal-and-orange,
golden hour lighting, soft backlight.
```

### §5.3 差异

```
❌ 过度指定版:
  - 8 句话装饰(鹅卵石 / 铁街灯 / 梧桐叶 / 糕点 / 马车铃声)
  - 抽象词(电影感大片氛围 / 高级感拉满 / 极致细节震撼)
  - 模型可能聚焦装饰,主体淹没

✅ 留白优化版:
  - 主体 4 句话(具体但克制)
  - 场景 1 句话
  - 美学 3 句话(STYLE 锚 + 光线)
  - 模型空间充足,主体优先
```

## §6 反例速查

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| 数量 / 程度过度(12 种渐变 / 每一颗雪花都不同) | 一条橙色光带 |
| 时间过度(0.5s / 1s / 1.5s 毫秒指令) | 切镜时间戳 + 时段分配 |
| 装饰过度(8 句话写场景) | 1-2 句承载,其余留白 |
| 不可数词(极致 / 完美 / 高级感) | 可数物件清单 |
| 不可指定词(完美光线) | 方向 + 类型 + 强度 |
| 没有负面约束 | 加 must_not_change / negative_prompt |
| 倒数第二句之后还写细节 | 留给模型发挥空间 |

## §7 来源

- 蒸馏自 `i2v-h3-prompt/references/chinese-prompt-method.md §6`
- 用户实战笔记:`docs/references/note-video-prompt/` §6.1, §6.2
- 创建日期:2026-08-20
