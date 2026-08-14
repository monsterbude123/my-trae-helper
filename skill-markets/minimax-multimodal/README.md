# minimax-multimodal

> MiniMax(海螺 AI)开放平台多模态技能包 — 6 大模态可跑通的 Python 客户端。

## 安装

仅依赖 Python 3.8+ 与 `requests`(标准库外唯一依赖)。

```bash
pip install requests
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `MINIMAX_API_KEY` | ✅(国内) | 国内区域 API Key(`api.minimaxi.com`)|
| `MINIMAX_GLOBAL_API_KEY` | ✅(国际) | 国际区域 API Key(`api.minimax.io`)|
| `MINIMAX_BASE_URL` | ⛔ 可选 | 自定义 base URL(默认国内)|
| `MINIMAX_TIMEOUT` | ⛔ 可选 | 请求超时秒数(默认 60)|

## 6 大模态脚本

```bash
# 1. 文本对话(M2.7 / M3)
python scripts/text_chat.py --message "用一句话介绍 MiniMax"
python scripts/text_chat.py --model MiniMax-M3 --message "写首七言绝句" --stream

# 2. 文生图(image-01)
python scripts/image_generate.py --prompt "赛博朋克风格的杭州西湖" --out cyber_westlake.png

# 3. 视频生成(Hailuo-2.3 同步)
python scripts/video_generate.py --prompt "一只猫在草地上追逐蝴蝶" --out cat_chase.mp4

# 4. 视频生成(MiniMax-H3 异步多模态)
python scripts/video_generate.py --model MiniMax-H3 --prompt "保持角色一致性" \
    --reference-image character.png --out h3_video.mp4

# 5. 语音合成(speech-2.8-hd)
python scripts/speech_synthesize.py --text "你好,世界" --voice male-qn-qingse --out hello.mp3

# 6. 音乐生成(music-3.0)
python scripts/music_generate.py --prompt "轻快流行,夏日海边" \
    --lyrics "[verse] 阳光洒在海面上" --out summer_song.mp3

# 7. 图像理解(vision)
python scripts/vision_describe.py --image photo.jpg --prompt "图中是什么?"

# 8. 全量验证(跑通所有模态连通性)
python scripts/verify_all.py
```

## 双区域切换

```bash
# 国内(默认)
export MINIMAX_API_KEY=sk-cn-xxx

# 国际
export MINIMAX_GLOBAL_API_KEY=sk-global-xxx
export MINIMAX_BASE_URL=https://api.minimax.io
```

## 输出位置

| 模态 | 默认输出目录 |
|------|--------------|
| 文本对话 | stdout |
| 文生图 | `./output/image_<timestamp>.png` |
| 视频生成 | `./output/video_<timestamp>.mp4` |
| 语音合成 | `./output/speech_<timestamp>.mp3` |
| 音乐生成 | `./output/music_<timestamp>.mp3` |
| 图像理解 | stdout |

可通过 `--out <file>` 显式指定输出文件。

## 故障排查

| 错误码 | 含义 | 处理 |
|--------|------|------|
| 401 | API Key 无效 | 检查环境变量是否设置正确 |
| 429 | 配额不足 | 检查账户余额或切换区域 |
| 1004 | 余额不足 | 国内常见,需充值 |
| 1002 | 参数错误 | 检查 prompt / model 名是否拼写正确 |
| 1008 | 异步任务失败 | 查看任务返回的 `status_info` 字段 |

详见各模态的 `references/<modality>.md`。

## API 参考

详细 API 文档见 [`references/api-endpoints.md`](references/api-endpoints.md)。

## 安全

- 不在 chat 输出或日志中打印完整 API Key(只显示末 4 位)
- 不向项目路径外写脚本或临时文件
- 所有下载产物默认落 `output/` 或用户显式指定的 `--out`