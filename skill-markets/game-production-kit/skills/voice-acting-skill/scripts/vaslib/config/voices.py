"""
方言→音色映射、多音字词典、引擎参数映射配置模块。

完全独立，不依赖任何其他模块。
"""

DIALECT_MAPPINGS: dict[str, dict] = {
    "渝普": {
        "qwen_tts_voice_id": "Sunny",
        "cosyvoice_instruct": "用川渝口音说话，{personality}，{emotion}",
        "omnivoice_design": "{gender}, {age}, Sichuan dialect",
    },
    "川渝": {
        "qwen_tts_voice_id": "Sunny",
        "cosyvoice_instruct": "用川渝口音说话，{personality}，{emotion}",
        "omnivoice_design": "{gender}, {age}, Sichuan dialect",
    },
    "东北口音": {
        "qwen_tts_voice_id": "Ethan",
        "cosyvoice_instruct": "用东北口音说话，{personality}，{emotion}",
        "omnivoice_design": "{gender}, {age}, Dongbei accent",
    },
    "沪普": {
        "qwen_tts_voice_id": "Jada",
        "cosyvoice_instruct": "用上海口音说话，{personality}，{emotion}",
        "omnivoice_design": "{gender}, {age}, Shanghai dialect",
    },
    "北京口音": {
        "qwen_tts_voice_id": "Dylan",
        "cosyvoice_instruct": "用北京口音说话，{personality}，{emotion}",
        "omnivoice_design": "{gender}, {age}, Beijing accent",
    },
    "天津口音": {
        "qwen_tts_voice_id": "Dylan",
        "cosyvoice_instruct": "用天津口音说话，{personality}，{emotion}",
        "omnivoice_design": "{gender}, {age}, Tianjin accent",
    },
}

DEFAULT_DIALECT_MAPPING: dict = {
    "qwen_tts_voice_id": "Cherry",
    "cosyvoice_instruct": "{personality}，{emotion}",
    "omnivoice_design": "{gender}, {age}",
}

QWEN_TTS_LANGUAGE_MAP: dict[str, str] = {
    "渝普": "Chinese",
    "川渝": "Chinese",
    "东北口音": "Chinese",
    "沪普": "Chinese",
    "北京口音": "Chinese",
    "天津口音": "Chinese",
}

COSYVOICE_DEFAULT_VOICE_ID: str = "longxiaochun"

OMNIVOICE_GENDER_MAP: dict[str, str] = {
    "male": "男",
    "female": "女",
    "other": "男",
}

OMNIVOICE_AGE_MAP: dict[str, str] = {
    "child": "儿童",
    "young": "青年",
    "middle": "中年",
    "elderly": "老年",
}

OMNIVOICE_DIALECT_MAP: dict[str, str] = {
    "渝普": "四川话",
    "川渝": "四川话",
    "东北口音": "东北话",
    "沪普": "上海话",
    "北京口音": "北京话",
    "天津口音": "天津话",
}

OMNIVOICE_INSTRUCT_GENDER: dict[str, str] = {
    "male": "Male / 男",
    "female": "Female / 女",
    "other": "Male / 男",
}

OMNIVOICE_INSTRUCT_AGE: dict[str, str] = {
    "child": "Child / 儿童",
    "young": "Young Adult / 青年",
    "middle": "Middle-aged / 中年",
    "elderly": "Elderly / 老年",
}

POLYPHONE_DICT: dict[str, dict[str, str]] = {
    "银行": {"default": "yín háng"},
    "行长": {"default": "háng zhǎng"},
    "处理": {"default": "chǔ lǐ"},
    "重庆": {"default": "chóng qìng"},
    "重要": {"default": "zhòng yào"},
    "重新": {"default": "chóng xīn"},
    "长度": {"default": "cháng dù"},
    "长大": {"default": "zhǎng dà"},
    "地方": {"default": "dì fang"},
    "地道": {"default": "dì dào"},
    "明白": {"default": "míng bai"},
    "分开": {"default": "fēn kāi"},
    "过分": {"default": "guò fèn"},
    "分析": {"default": "fēn xī"},
    "行走": {"default": "xíng zǒu"},
    "行李": {"default": "xíng li"},
    "便宜": {"default": "pián yi"},
    "方便": {"default": "fāng biàn"},
    "大便": {"default": "dà biàn"},
    "差不多": {"default": "chà bu duō"},
    "差别": {"default": "chā bié"},
    "出差": {"default": "chū chāi"},
    "差劲": {"default": "chà jìn"},
    "参差": {"default": "cēn cī"},
    "觉得": {"default": "jué de"},
    "睡觉": {"default": "shuì jiào"},
    "角落": {"default": "jiǎo luò"},
    "角色": {"default": "jué sè"},
    "主角": {"default": "zhǔ jué"},
    "胶水": {"default": "jiāo shuǐ"},
    "开塞露": {"default": "kāi sāi lù"},
    "肛门": {"default": "gāng mén"},
    "便秘": {"default": "biàn mì"},
    "肠镜": {"default": "cháng jìng"},
    "异物钳": {"default": "yì wù qián"},
    "探头": {"default": "tàn tóu"},
    "固化": {"default": "gù huà"},
    "查封": {"default": "chá fēng"},
    "永久": {"default": "yǒng jiǔ"},
    "封印": {"default": "fēng yìn"},
    "恩怨": {"default": "ēn yuàn"},
    "仇恨": {"default": "chóu hèn"},
    "连坐": {"default": "lián zuò"},
    "蟠桃": {"default": "pán táo"},
    "夜明珠": {"default": "yè míng zhū"},
    "炼丹炉": {"default": "liàn dān lú"},
    "炉灰": {"default": "lú huī"},
    "玉帝": {"default": "yù dì"},
    "瑞兽": {"default": "ruì shòu"},
    "招财进宝": {"default": "zhāo cái jìn bǎo"},
    "只进不出": {"default": "zhǐ jìn bù chū"},
    "守财": {"default": "shǒu cái"},
    "拉屎": {"default": "lā shǐ"},
    "坠胀": {"default": "zhuì zhàng"},
    "丹田": {"default": "dān tián"},
    "干哈": {"default": "gàn há"},
    "私密": {"default": "sī mì"},
    "玩意儿": {"default": "wán yì er"},
    "完犊子": {"default": "wán dú zi"},
    "虎了吧唧": {"default": "hǔ le bā jī"},
    "粘住": {"default": "zhān zhù"},
    "肛肠科": {"default": "gāng cháng kē"},
    "导诊": {"default": "dǎo zhěn"},
    "指甲油": {"default": "zhǐ jia yóu"},
    "傲娇": {"default": "ào jiāo"},
    "痞气": {"default": "pǐ qì"},
    "中二": {"default": "zhōng èr"},
    "捧哏": {"default": "pěng gén"},
    "耙耳朵": {"default": "pá ěr duo"},
    "凡尔赛": {"default": "fán ěr sài"},
    "老炮儿": {"default": "lǎo pào er"},
    "气氛组": {"default": "qì fēn zǔ"},
    "搞军事演习": {"default": "gǎo jūn shì yǎn xí"},
    "补铁": {"default": "bǔ tiě"},
    "嘿嘿": {"default": "hēi hēi"},
    "我牙刷": {"default": "wǒ yá shuā"},
    "你妈卖": {"default": "nǐ mā mài"},
}


_TONE_MAP: dict[str, str] = {
    "ā": "a1",
    "á": "a2",
    "ǎ": "a3",
    "à": "a4",
    "ē": "e1",
    "é": "e2",
    "ě": "e3",
    "è": "e4",
    "ī": "i1",
    "í": "i2",
    "ǐ": "i3",
    "ì": "i4",
    "ō": "o1",
    "ó": "o2",
    "ǒ": "o3",
    "ò": "o4",
    "ū": "u1",
    "ú": "u2",
    "ǔ": "u3",
    "ù": "u4",
    "ǖ": "v1",
    "ǘ": "v2",
    "ǚ": "v3",
    "ǜ": "v4",
    "ń": "n2",
    "ň": "n3",
    "ǹ": "n4",
    "ü": "v",
}

_TONE_CHAR_TO_NUM: dict[str, int] = {
    "ā": 1,
    "á": 2,
    "ǎ": 3,
    "à": 4,
    "ē": 1,
    "é": 2,
    "ě": 3,
    "è": 4,
    "ī": 1,
    "í": 2,
    "ǐ": 3,
    "ì": 4,
    "ō": 1,
    "ó": 2,
    "ǒ": 3,
    "ò": 4,
    "ū": 1,
    "ú": 2,
    "ǔ": 3,
    "ù": 4,
    "ń": 2,
    "ň": 3,
    "ǹ": 4,
}


def _find_tone(syllable: str) -> int:
    """查找音节中声调数字, 无声调返回5."""
    for ch in syllable:
        if ch in _TONE_CHAR_TO_NUM:
            return _TONE_CHAR_TO_NUM[ch]
    return 5


def _strip_tone(syllable: str) -> str:
    """去掉声调符号, 同时处理ü→v."""
    result = []
    for ch in syllable:
        if ch in _TONE_MAP:
            mapped = _TONE_MAP[ch]
            result.append(mapped.rstrip("12345"))
        else:
            result.append(ch)
    return "".join(result)


def convert_to_tone_pinyin(pinyin: str) -> str:
    """
    将带声调的拼音转换为去声调+数字格式。

    例: "yín háng" -> "yin2hang2"
         "chǔ lǐ" -> "chu3li3"
    """
    syllables = pinyin.strip().split()
    result_parts = []
    for syl in syllables:
        tone = _find_tone(syl)
        stripped = _strip_tone(syl)
        result_parts.append(f"{stripped}{tone}")
    return "".join(result_parts)


def resolve_polyphones(text: str) -> str:
    """
    按 POLYPHONE_DICT 替换文本中的多音字为 `词[拼音]` 格式。

    按词长度排序(长词优先匹配)，用 str.replace 替换。
    """
    sorted_words = sorted(POLYPHONE_DICT.keys(), key=len, reverse=True)

    result = text
    for word in sorted_words:
        pinyin = POLYPHONE_DICT[word]["default"]
        result = result.replace(word, f"{word}[{pinyin}]")
    return result


def get_pinyin_overrides(text: str) -> dict[str, str]:
    """
    返回文本中出现的多音字的拼音覆盖。

    拼音转换为去声调+数字格式 (如 yín háng -> yin2hang2)。
    """
    overrides: dict[str, str] = {}
    for word, entry in POLYPHONE_DICT.items():
        if word in text:
            pinyin = entry["default"]
            overrides[word] = convert_to_tone_pinyin(pinyin)
    return overrides
