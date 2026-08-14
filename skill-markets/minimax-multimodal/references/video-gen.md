# 视频生成(video_generate)

## 双接口

### V1:Hailuo 系列(同步轮询)

`POST /v1/video_generation` → `GET /v1/query/video_generation?task_id=...`

模型:`MiniMax-Hailuo-2.3` / `MiniMax-Hailuo-2.3-Fast` / `MiniMax-Hailuo-02`

### V2:MiniMax-H3(异步多模态)

`POST /v1/video/generation` → `GET /v1/query/video/generation?task_id=...`

模型:`MiniMax-H3`(唯一)

## V1 用法

```bash
python scripts/video_generate.py \
    --prompt "一只猫在草地上追逐蝴蝶" \
    --model MiniMax-Hailuo-2.3 \
    --duration 6 \
    --resolution 768P \
    --out cat.mp4
```

| 参数 | 选项 | 说明 |
|------|------|------|
| `--duration` | 6 / 10 | 秒数 |
| `--resolution` | 768P / 1080P | 分辨率 |

## V2 用法(MiniMax-H3)

### 纯文本

```bash
python scripts/video_generate.py \
    --model MiniMax-H3 \
    --prompt "日落时分的海滩" \
    --duration 6 \
    --resolution 2K \
    --out beach.mp4
```

### 文 + 参考图

```bash
python scripts/video_generate.py \
    --model MiniMax-H3 \
    --prompt "保持同一角色,开始走路" \
    --reference-image character.png \
    --out walk.mp4
```

### 首尾帧

```bash
python scripts/video_generate.py \
    --model MiniMax-H3 \
    --prompt "镜头从远处缓慢推近" \
    --first-frame start.png \
    --last-frame end.png \
    --out fl.mp4
```

### 多模态参考(图像 + 视频 + 音频)

```bash
python scripts/video_generate.py \
    --model MiniMax-H3 \
    --prompt "参考视频1的希区柯克镜头,让图中角色唱歌,音色匹配音频3" \
    --reference-video motion.mp4 \
    --reference-image singer.png \
    --reference-audio vocal.mp3 \
    --out multi.mp4
```

## H3 参数

| 参数 | 范围 | 说明 |
|------|------|------|
| `--duration` | 4 ~ 15 秒 | |
| `--resolution` | 768P / 2K | 2K 是 H3 默认 |
| `--aspect-ratio` | 16:9 / 9:16 / 1:1 | |

## 输入限制

| 资产 | 最大 |
|------|------|
| image | 30 MB |
| reference video | 50 MB |
| reference audio | 15 MB |
| 请求 body 总大小 | 64 MB |

## 轮询参数

- V1 间隔:5s,超时 600s
- H3(V2)间隔:8s,超时 900s(H3 视频生成时间长)

## 任务状态字段

| V1 | V2 |
|----|----|
| `task_id` | `task_id` |
| `status`: `Queueing` / `Processing` / `Success` / `Fail` | `status`: 同上 |
| `file_id`(成功后) | `content[].url`(成功后) |

## 失败处理

```bash
# 查看任务详情(失败原因在 status_info)
GET /v1/query/video_generation?task_id=12345
```

`base_resp.status_msg` 含可读错误描述。

## 成本提示

- Hailuo-2.3 768P 6s ≈ ¥2
- Hailuo-2.3 Fast 768P 6s ≈ ¥1.35(最低)
- H3 2K 5s 价格 < 同类模型 1/3
- 跑通验证默认 skip 视频,需 `--include-video` 才付费