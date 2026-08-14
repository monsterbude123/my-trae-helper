# MiniMax API 端点速查

> 来源:[platform.minimaxi.com/docs/api-reference/api-overview](https://platform.minimaxi.com/docs/api-reference/api-overview)
> 国际镜像:[platform.minimax.io](https://platform.minimax.io/)

## Base URL

| 区域 | Base URL |
|------|----------|
| 国内 | `https://api.minimaxi.com` |
| 国际 | `https://api.minimax.io` |

## 鉴权

```http
Authorization: Bearer <MINIMAX_API_KEY>
api-key: <MINIMAX_API_KEY>          # 部分接口兼容
```

## 端点总表

| 模态 | 端点 | 方法 | 同步/异步 |
|------|------|------|-----------|
| 文本对话 | `/v1/text/chatcompletion_v2` | POST | 同步 |
| 文本对话(Anthropic 兼容) | `/anthropic/v1/messages` | POST | 同步 |
| 文生图 | `/v1/image/generation` | POST | 同步 |
| 视频生成 V1(Hailuo) | `/v1/video_generation` | POST | 异步 |
| 视频生成 V1 查询 | `/v1/query/video_generation?task_id=...` | GET | 轮询 |
| 视频生成 V2(MiniMax-H3) | `/v1/video/generation` | POST | 异步 |
| 视频生成 V2 查询 | `/v1/query/video/generation?task_id=...` | GET | 轮询 |
| 视频文件下载 | `/v1/files/retrieve?file_id=...` | GET | 同步 |
| 语音合成 | `/v1/t2a_v2` | POST | 同步/流式 |
| 异步长文本语音 | `/v1/t2a_async_v2` | POST | 异步 |
| 音色列表 | `/v1/voice/list?language=zh` | GET | 同步 |
| 音色复刻上传 | `/v1/voice/upload_clone_audio` | POST | 同步 |
| 音色快速复刻 | `/v1/voice/clone` | POST | 同步 |
| 音色设计 | `/v1/voice/design` | POST | 同步 |
| 音乐生成 | `/v1/music_generation` | POST | 同步 |
| 文件上传 | `/v1/files/upload` | POST | 同步 |
| 文件列表 | `/v1/files/list` | GET | 同步 |

## 模型清单

### 文本(M 系列)

| 模型 | 上下文 | 输出速度 | 备注 |
|------|--------|---------|------|
| MiniMax-M3 | 1,000,000 | ~60 tps | **最新**,原生多模态,长上下文 |
| MiniMax-M2.7 | 204,800 | ~60 tps | 自我迭代版本 |
| MiniMax-M2.7-highspeed | 204,800 | ~100 tps | M2.7 极速版 |
| MiniMax-M2.5 | 204,800 | ~60 tps | 性价比 |
| MiniMax-M2.5-highspeed | 204,800 | ~100 tps | 极速 |
| MiniMax-M2.1 | 204,800 | ~60 tps | 多语言编程 |
| MiniMax-M2.1-highspeed | 204,800 | ~100 tps | 极速 |
| MiniMax-M2 | 204,800 | ~60 tps | 编码 + Agent |

### 视频

| 模型 | 分辨率 | 时长 | 特点 |
|------|--------|------|------|
| MiniMax-H3 | 768P / 2K | 4-15s | **最新**,多模态输入,首尾帧 |
| MiniMax-Hailuo-2.3 | 768P / 1080P | 6 / 10s | 文生视频 |
| MiniMax-Hailuo-2.3-Fast | 768P / 1080P | 6 / 10s | 图生视频,便宜 |
| MiniMax-Hailuo-02 | 1080P | 6 / 10s | SOTA 指令遵循 |

### 语音(speech 系列)

| 模型 | 特性 |
|------|------|
| speech-2.8-hd | 最新 HD,情绪渲染融合语气词 |
| speech-2.8-turbo | 最新 Turbo,极致速度 |
| speech-2.6-hd | 韵律表现佳 |
| speech-2.6-turbo | 超低时延 |
| speech-02-hd | 复刻相似度高 |
| speech-02-turbo | 小语种增强 |

### 图片

| 模型 | 能力 |
|------|------|
| image-01 | 文生图、图生图(人物主体参考)|
| image-01-live | 文生图 + 多种画风 |

### 音乐

| 模型 | 能力 |
|------|------|
| music-3.0 | 最新,音质全面跃升,人声自然 |
| music-2.6 | 翻唱入心、器乐入魂 |
| music-cover | 一步翻唱 + 风格迁移 |
| music-cover-free | 一步翻唱免费版 |

## 双区域切换

```python
# 国内(默认)
base_url = "https://api.minimaxi.com"
api_key = "<MINIMAX_API_KEY>"

# 国际
base_url = "https://api.minimax.io"
api_key = "<MINIMAX_GLOBAL_API_KEY>"
```

## Token Plan vs 按量付费

- **按量付费**:支持所有模态,API Key 在 [接口密钥](https://platform.minimaxi.com/user-center/basic-information/interface-key) 创建
- **Token Plan**:月度订阅,Key 在 [订阅管理](https://platform.minimaxi.com/user-center/payment/token-plan),独立计费

## 错误码

| 码 | 含义 | 处理 |
|----|------|------|
| 0 | 成功 | — |
| 1002 | 参数错误 | 检查 prompt / model / file_id |
| 1004 | 余额不足 | 充值或切换 Token Plan |
| 1008 | 异步任务失败 | 查看 `base_resp.status_msg` |
| 401 | 鉴权失败 | 检查 API Key |
| 429 | 限流 | 等待后重试 |
| 5xx | 服务端错误 | 重试 |

## 关键约束

- 视频生成 URL 有效期:**9 小时**(32400 秒),下载后立即落盘
- 单次 TTS 同步最大文本:**10,000 字符**
- 异步长文本 TTS 最大文本:**1,000,000 字符**
- H3 输入限制:image ≤ 30MB,video ≤ 50MB,audio ≤ 15MB,总 body ≤ 64MB
- 音色复刻临时保存:**168 小时(7 天)**,过期未使用自动删除

## 官方 SDK / MCP

- **TypeScript SDK**: [mmx-cli/sdk](https://github.com/MiniMax-AI/cli)
- **官方 CLI**: `npm install -g mmx-cli`
- **官方 MCP Python**: [MiniMax-MCP](https://github.com/MiniMax-AI/MiniMax-MCP)
- **官方 MCP JS**: [MiniMax-MCP-JS](https://github.com/MiniMax-AI/MiniMax-MCP-JS)

## CLI 等价命令(参考)

```bash
mmx text chat --message "..."                 # 文本
mmx image "prompt"                            # 文生图
mmx video generate --prompt "..." --download  # 视频
mmx speech synthesize --text "..." --out      # TTS
mmx music generate --prompt "..." --lyrics    # 音乐
mmx vision photo.jpg                          # 图像理解
```