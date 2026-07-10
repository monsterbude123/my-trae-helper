# voice-acting-skill · 多音字词典

> 配置文件路径：`scripts/vaslib/config/voices.py::POLYPHONE_DICT`
>
> 此文件为人类可读导出版本，便于人工审查和扩充。运行时仍以 `voices.py` 为准。

## 数据格式

```python
POLYPHONE_DICT: dict[str, dict[str, str]] = {
    "词": {"default": "拼音"},
    ...
}
```

- **键**：剧本中出现的具体词（不是单字）
- **值**：`{ "default": "拼音声调" }`
- **解析顺序**：长词优先（`行长` 在 `银行` 之前匹配）

## 词典列表（81 词）

### 通用多音字

| 词 | 拼音 |
|---|---|
| 银行 | yín háng |
| 行长 | háng zhǎng |
| 处理 | chǔ lǐ |
| 重庆 | chóng qìng |
| 重要 | zhòng yào |
| 重新 | chóng xīn |
| 长度 | cháng dù |
| 长大 | zhǎng dà |
| 地方 | dì fang |
| 地道 | dì dào |
| 明白 | míng bai |
| 分开 | fēn kāi |
| 过分 | guò fèn |
| 分析 | fēn xī |
| 行走 | xíng zǒu |
| 行李 | xíng li |
| 便宜 | pián yi |
| 方便 | fāng biàn |
| 大便 | dà biàn |
| 差不多 | chà bu duō |
| 差别 | chā bié |
| 出差 | chū chāi |
| 差劲 | chà jìn |
| 参差 | cēn cī |
| 觉得 | jué de |
| 睡觉 | shuì jiào |
| 角落 | jiǎo luò |
| 角色 | jué sè |
| 主角 | zhǔ jué |
| 胶水 | jiāo shuǐ |

### 医疗 / 肛肠科

| 词 | 拼音 |
|---|---|
| 开塞露 | kāi sāi lù |
| 肛门 | gāng mén |
| 便秘 | biàn mì |
| 肠镜 | cháng jìng |
| 异物钳 | yì wù qián |
| 探头 | tàn tóu |
| 固化 | gù huà |
| 查封 | chá fēng |
| 肛肠科 | gāng cháng kē |
| 导诊 | dǎo zhěn |

### 神话 / 古典

| 词 | 拼音 |
|---|---|
| 永久 | yǒng jiǔ |
| 封印 | fēng yìn |
| 恩怨 | ēn yuàn |
| 仇恨 | chóu hèn |
| 连坐 | lián zuò |
| 蟠桃 | pán táo |
| 夜明珠 | yè míng zhū |
| 炼丹炉 | liàn dān lú |
| 炉灰 | lú huī |
| 玉帝 | yù dì |
| 瑞兽 | ruì shòu |
| 招财进宝 | zhāo cái jìn bǎo |
| 只进不出 | zhǐ jìn bù chū |
| 守财 | shǒu cái |

### 口语 / 方言

| 词 | 拼音 |
|---|---|
| 拉屎 | lā shǐ |
| 坠胀 | zhuì zhàng |
| 丹田 | dān tián |
| 干哈 | gàn há |
| 私密 | sī mì |
| 玩意儿 | wán yì er |
| 完犊子 | wán dú zi |
| 虎了吧唧 | hǔ le bā jī |
| 粘住 | zhān zhù |
| 指甲油 | zhǐ jia yóu |
| 傲娇 | ào jiāo |
| 痞气 | pǐ qì |
| 中二 | zhōng èr |
| 捧哏 | pěng gén |
| 耙耳朵 | pá ěr duo |
| 凡尔赛 | fán ěr sài |
| 老炮儿 | lǎo pào er |
| 气氛组 | qì fēn zǔ |
| 搞军事演习 | gǎo jūn shì yǎn xí |
| 补铁 | bǔ tiě |
| 嘿嘿 | hēi hēi |

### 俚语

| 词 | 拼音 |
|---|---|
| 我牙刷 | wǒ yá shuā |
| 你妈卖 | nǐ mā mài |

## 扩充指南

编辑 `scripts/vaslib/config/voices.py`，在 `POLYPHONE_DICT` 中追加：

```python
POLYPHONE_DICT = {
    "新词": {"default": "xīn cí"},
    ...
}
```

测试：`python -m pytest scripts/tests/test_core.py::TestResolvePolyphones`

## 拼音格式转换

`convert_to_tone_pinyin("yín háng")` → `"yin2hang2"`
- 去声调符号
- 数字 1-4 表示四声，5 表示轻声
- `ü` → `v`
