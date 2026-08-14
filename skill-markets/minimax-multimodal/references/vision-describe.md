# 图像理解(vision_describe)

## 实现

复用文本对话端点 `/v1/text/chatcompletion_v2`,`messages[].content` 传多模态数组。

`MiniMax-M3` 原生支持图片输入(多模态架构)。

## 端点

`POST /v1/text/chatcompletion_v2`

## 用法

### 本地图片

```bash
python scripts/vision_describe.py \
    --image photo.jpg \
    --prompt "图中是什么品种的狗?" \
    --out report.txt
```

### 网络图片

```bash
python scripts/vision_describe.py \
    --image https://example.com/photo.jpg \
    --prompt "用中文描述这张图"
```

## 参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--image` | path/url | 必填 | 本地路径或 HTTP(S) URL |
| `--prompt` | str | "请详细描述" | 提问 |
| `--model` | str | `MiniMax-M3` | M3 / M2.7 / M2.5 |
| `--system` | str | None | 系统提示词 |
| `--max-tokens` | int | 1024 | 最大输出 |

## content 数组结构

```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "请描述这张图"},
    {
      "type": "image_url",
      "image_url": {
        "url": "data:image/jpeg;base64,..."   // 或 "https://..."
      }
    }
  ]
}
```

`url` 字段支持:
- `data:image/<fmt>;base64,<base64>`(本地文件,脚本自动转换)
- `http://...` / `https://...`(远程 URL)

## 文件大小

base64 编码后约 33% 膨胀,本地 5MB 图片 ≈ 6.7MB base64,适合 M3 的 1M context。

## 输出格式

纯文本回复(不像 OpenAI vision 支持 JSON 结构化输出)。如需结构化,在 prompt 里要求:

```bash
python scripts/vision_describe.py \
    --image photo.jpg \
    --prompt "输出 JSON 格式:{objects: [], scene: '', mood: ''}"
```

## 限制

- 单次最多 8 张图片(`content` 数组长度)
- 单图最大 ~20MB(实际受 context 限制)
- 支持格式:JPG / PNG / WebP / GIF(取首帧)
- 不支持 PDF

## 多图对比

```bash
# 需手写 Python 调用,本 CLI 仅支持单图
python -c "
import requests, base64, json
img = base64.b64encode(open('a.jpg', 'rb').read()).decode()
resp = requests.post(
    'https://api.minimaxi.com/v1/text/chatcompletion_v2',
    headers={'Authorization': 'Bearer YOUR_KEY'},
    json={
        'model': 'MiniMax-M3',
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': '比较这两张图'},
                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{img}'}},
                {'type': 'image_url', 'image_url': {'url': 'https://example.com/b.jpg'}},
            ],
        }],
    },
)
print(resp.json())
"
```