# 音乐生成(music_generate)

## 端点

`POST /v1/music_generation`

## 最小请求

```bash
python scripts/music_generate.py \
    --prompt "轻快流行,夏日海边" \
    --lyrics "[verse] 阳光洒海面" \
    --out song.mp3
```

## 完整参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--prompt` | str | 必填 | 风格/灵感描述 |
| `--lyrics` | str | None | 歌词(带 `[verse]/[chorus]` 标签)|
| `--lyrics-optimizer` | flag | False | 让模型根据 prompt 自动写词 |
| `--instrumental` | flag | False | 纯器乐 |
| `--vocals` | str | None | 结构化:人声描述 |
| `--genre` | str | None | 结构化:流派 |
| `--mood` | str | None | 结构化:情绪 |
| `--instruments` | str | None | 结构化:乐器 |
| `--bpm` | int | None | 结构化:速度 |
| `--key` | str | None | 结构化:调性 |
| `--audio-file` | path | None | 翻唱参考音频 |
| `--cover-feature-id` | str | None | 翻唱预处理 ID |
| `--model` | str | `music-3.0` | 见下表 |
| `--output-format` | str | `url` | url / hex |

## 模型对比

| 模型 | 能力 | 价格 |
|------|------|------|
| music-3.0 | **最新**,音质跃升,人声更自然 | ¥1/首 |
| music-2.6 | 翻唱入心、器乐入魂 | 历史 |
| music-cover | 两步翻唱(可改歌词)| ¥1/首 |
| music-cover-free | 一步翻唱(自动提词)| 免费 |

## 歌词格式

```
[verse]
第一段主歌的歌词
[chorus]
副歌的歌词
[bridge]
桥段的歌词
```

## 模式一:普通生成(lyrics + prompt)

```bash
python scripts/music_generate.py \
    --prompt "Indie folk, melancholic, rainy night" \
    --lyrics-optimizer \
    --out song.mp3
```

## 模式二:纯器乐

```bash
python scripts/music_generate.py \
    --prompt "Cinematic orchestral, no vocals" \
    --instrumental \
    --out bgm.mp3
```

## 模式三:结构化 prompt(music-3.0 推荐)

```bash
python scripts/music_generate.py \
    --prompt "A beautiful song" \
    --vocals "warm male baritone" \
    --genre "jazz" \
    --mood "relaxing" \
    --instruments "piano, saxophone" \
    --bpm 120 \
    --key "C major" \
    --out jazz_song.mp3
```

## 模式四:翻唱(一步免费)

```bash
python scripts/music_generate.py \
    --prompt "Jazz piano trio with warm intimate vocal" \
    --audio-file original.mp3 \
    --model music-cover-free \
    --out cover.mp3
```

## 模式五:翻唱(两步可改歌词)

第一步:预处理获取 feature_id(本脚本未集成,需手动调 `/v1/music_cover_preprocess`)

第二步:

```bash
python scripts/music_generate.py \
    --model music-cover \
    --prompt "Acoustic folk with gentle strings" \
    --cover-feature-id "feature-id-here" \
    --lyrics "[Verse]\nNew rewritten lyrics" \
    --out cover2.mp3
```

## 异步说明

音乐生成是同步接口(响应即结果),但生成本身需要 30s~2min。脚本默认超时 300s,慢的话提到 600s。

## 错误

| 错误 | 原因 |
|------|------|
| `quota exceeded` | 余额不足 |
| `lyrics too long` | 歌词 > 3000 字符 |
| `model not found` | model 名拼错 |