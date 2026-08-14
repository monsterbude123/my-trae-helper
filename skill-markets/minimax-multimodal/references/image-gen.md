# 文生图 / 图生图(image_generate)

## 端点

`POST /v1/image/generation`

## 最小请求

```bash
python scripts/image_generate.py --prompt "红色圆点" --out dot.png
```

## 完整参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--prompt` | str | 必填 | 图像描述 |
| `--model` | str | `image-01` | 或 `image-01-live` |
| `--aspect-ratio` | str | `1:1` | 1:1/16:9/9:16/4:3/3:4 |
| `--n` | int | 1 | 生成张数(1~4)|
| `--reference-image` | path | None | 图生图参考图 |
| `--style` | str | None | 画风(仅 `image-01-live`)|
| `--out` | path | auto | 输出文件 |

## 模型对比

| 模型 | 能力 | 典型用途 |
|------|------|----------|
| image-01 | 文生图 + 人物主体参考 | 商品图、人物写真 |
| image-01-live | + 画风(动漫/水墨/写实) | 创意插画 |

## 画风选项(`image-01-live`)

常用:`日式动漫`、`水墨画`、`油画`、`赛博朋克`、`中国风水墨`、`3D 卡通`

完整列表调用 `mmx speech voices` 不适用;直接传 prompt 中的风格描述即可。

## 图生图(主体参考)

```bash
python scripts/image_generate.py \
    --prompt "同一个人穿西装" \
    --reference-image portrait.jpg \
    --out suit.png
```

实现:`subject_reference: [{type: image, image_file: <base64>}]`

## 响应格式

```json
{
  "image_urls": ["https://.../abc.png"],
  "metadata": {"width": 1024, "height": 1024}
}
```

或 `base64` 模式:`{"data": ["base64..."]}`。本脚本默认 `url` 模式(下载更稳)。

## URL 有效期

9 小时。脚本立即下载到 `output/`,不依赖 URL 缓存。

## 失败模式

| 错误 | 原因 |
|------|------|
| `prompt too long` | 描述 > 1500 字符 |
| `nsfw detected` | 内容审核拦截,改写 prompt |
| `quota exceeded` | 余额不足 |
| `aspect_ratio invalid` | 不支持的宽高比 |