# 语音合成(speech_synthesize)

## 端点

`POST /v1/t2a_v2`(HTTP 同步 + 可选流式)

异步长文本:`POST /v1/t2a_async_v2` + `GET /v1/query/t2a_async_v2`(本脚本未集成,留给后续)

## 最小请求

```bash
python scripts/speech_synthesize.py --text "你好世界" --out hello.mp3
```

## 完整参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--text` | str | - | 文本(与 `--text-file` 二选一)|
| `--text-file` | path | - | 长文本走文件 |
| `--model` | str | `speech-2.8-hd` | 见下表 |
| `--voice` | str | `male-qn-qingse` | 音色 ID |
| `--speed` | float | 1.0 | 语速(0.5~2.0)|
| `--vol` | float | 1.0 | 音量(0~10)|
| `--pitch` | int | 0 | 语调(-12~12)|
| `--format` | str | `mp3` | mp3 / pcm / flac / wav |
| `--sample-rate` | int | 32000 | 8000 / 16000 / 22050 / 24000 / 32000 / 44100 |
| `--bitrate` | int | 128000 | 32000~320000 |
| `--channels` | int | 1 | 1 单声道 / 2 立体声 |
| `--stream` | flag | False | 流式输出 |

## 模型选择

| 模型 | 延迟 | 音质 | 价格 |
|------|------|------|------|
| speech-2.8-hd | 中 | **最佳** | ¥3.5/万字符 |
| speech-2.8-turbo | **低** | 优 | ¥2/万字符 |
| speech-2.6-hd | 中 | 优 | 历史 |
| speech-2.6-turbo | 低 | 良 | 历史 |

**建议**:演示用 turbo(快+便宜),正式产品用 hd。

## 常用音色

完整列表:`python scripts/speech_synthesize.py --list-voices --language zh`

### 中文

| voice_id | 描述 |
|----------|------|
| `male-qn-qingse` | 青年男声,清亮 |
| `female-shaonv` | 少女声 |
| `male-qn-jingying` | 精英男声 |
| `female-yujie` | 御姐声 |
| `presenter_male` | 男主播 |
| `presenter_female` | 女主播 |

### 英文

| voice_id | 描述 |
|----------|------|
| `English_magnetic_voiced_man` | 磁性男声 |
| `English_expressive_narrator` | 表现力叙述 |
| `English_Graceful_Lady` | 优雅女声 |

### 日文

| voice_id | 描述 |
|----------|------|
| `Japanese_Graceful_Lady` | 优雅女声 |

## 流式输出

```bash
python scripts/speech_synthesize.py --text "实时播报" --stream | mpv -
```

流式响应:`data: {"data": {"audio": "<hex>", "status": 1}}`,逐 chunk 拼接。

## 长文本(> 10000 字符)

同步接口单次上限 **10,000 字符**。超过用:

```bash
python scripts/speech_synthesize.py --text-file book.txt --out audiobook.mp3
```

脚本自动从文件读取;若仍超限,走异步长文本接口(`t2a_async_v2`,本脚本未实现)。

## 支持 40 种语言

中文、粤语、英语、西班牙、法、俄、德、葡、阿、意、日、韩、印尼、越南、土、荷、乌克兰、泰、波、捷、罗、希、芬、印地、保、丹、希伯来、马来、波斯、斯洛伐克、瑞典、克罗地亚、菲律宾、匈牙利、挪威、斯洛文尼亚、加泰罗尼亚、尼诺斯克、泰米尔、阿非利卡。

## 错误码

| 错误 | 原因 |
|------|------|
| `invalid voice_id` | 音色不存在,用 `--list-voices` 查 |
| `text too long` | 超过 10000 字符,走异步 |
| `quota exceeded` | 余额不足 |