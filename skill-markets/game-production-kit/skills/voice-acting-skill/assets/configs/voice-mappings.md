# voice-acting-skill · 配置文件

> 配置文件 `assets/configs/` 目录存放人类可读的参考配置。
> 运行时配置集中在 `scripts/vaslib/config/voices.py` 中。

## 方言→音色映射表

> 详见 `scripts/vaslib/config/voices.py::DIALECT_MAPPINGS`

| 剧本方言提示 | QwenTTS 音色 | CosyVoice instruct | OmniVoice design |
|---|---|---|---|
| 渝普 / 川渝 | Sunny | 用川渝口音说话 | 男/女/中年/四川话 |
| 东北口音 | Ethan | 用东北口音说话 | 男/女/中年/东北话 |
| 沪普 | Jada | 用上海口音说话 | 男/女/中年/上海话 |
| 北京口音 | Dylan | 用北京口音说话 | 男/女/中年/北京话 |
| 天津口音 | Dylan | 用天津口音说话 | 男/女/中年/天津话 |
| (默认) | Cherry | (无方言模板) | 男/女/中年 |

## 性别 / 年龄映射

### OmniVoice 性别 (vaslib/config/voices.py::OMNIVOICE_GENDER_MAP)

| 角色属性 | 文本 |
|---|---|
| male | 男 |
| female | 女 |
| other | 男 |

### OmniVoice 年龄 (OMNIVOICE_AGE_MAP)

| 角色属性 | 文本 |
|---|---|
| child | 儿童 |
| young | 青年 |
| middle | 中年 |
| elderly | 老年 |

## 角色 ID 映射 (vaslib/parser/script_parser.py::CHARACTER_ID_MAP)

| 中文名 | id | 性别 |
|---|---|---|
| 貔貅 | pixiu | male |
| 老龟 | laogui | male |
| 凤 | feng | female |
| 龙 | long | male |
| 麒麟 | qilin | male |

未列出的中文名会被 `extract_characters` 跳过。如需添加新角色：

```python
# scripts/vaslib/parser/script_parser.py
CHARACTER_ID_MAP = {
    "新角色": "new_id",
    ...
}
GENDER_MAP = {
    "新角色": "male",  # 或 female/other
    ...
}
```

## 引擎参数

| 引擎 | 模型 | 服务默认地址 | 协议 |
|---|---|---|---|
| QwenTTS | qwen3-tts-flash-2025-11-27 | (HTTP API) | Aliyun DashScope |
| CosyVoice | cosyvoice-v2 | http://127.0.0.1:50000 | Gradio HTTP + SSE |
| OmniVoice | k2-fsa/OmniVoice | http://localhost:7860 | Gradio HTTP |
