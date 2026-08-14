# 文本对话(text_chat)

## 端点

`POST /v1/text/chatcompletion_v2`

## 最小请求

```bash
python scripts/text_chat.py --message "1+1=?"
```

## 完整参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--message` | str | 必填 | 用户消息 |
| `--model` | str | `MiniMax-M2.7` | 见 SKILL.md 路由表 |
| `--system` | str | None | 系统提示词 |
| `--max-tokens` | int | 512 | 最大输出 token |
| `--temperature` | float | 0.7 | 采样温度(0~2)|
| `--stream` | flag | False | 流式输出 |
| `--api-key` | str | env | 覆盖环境变量 |

## 模型选择建议

- **长上下文(> 200K tokens)**:只能用 `MiniMax-M3`(1M context)
- **Agent + 工具调用**:`MiniMax-M3` 或 `MiniMax-M2.7`
- **速度快 + 价格低**:`MiniMax-M2.7-highspeed`(100 tps)
- **极致编码**:`MiniMax-M2.5-highspeed` 性价比最高
- **中文场景**:全系列均可,M3 在中文表现最优

## Chain-of-Thought 注意事项

MiniMax M 系列**默认带 CoT 推理**(`reasoning_content` 字段)。因此:

- `max_tokens` 建议 **≥ 512**,否则推理过程可能吃掉所有 token,最终 `content` 为空(`finish_reason="length"`)
- 响应中三段:
  - `choices[0].message.content`:最终答案(主用)
  - `choices[0].message.reasoning_content`:推理文本(非答案,只是思考)
  - `choices[0].message.reasoning_details[]`:结构化推理段
- `text_chat._extract_content()` 只取 `content`(避免误把推理当答案)

## Anthropic SDK 兼容

如果想用 Anthropic SDK 调用,设置:

```python
from anthropic import Anthropic

client = Anthropic(
    api_key="<MINIMAX_API_KEY>",
    base_url="https://api.minimaxi.com/anthropic",
)
resp = client.messages.create(
    model="MiniMax-M3",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}],
)
```

## OpenAI SDK 兼容

```python
from openai import OpenAI

client = OpenAI(
    api_key="<MINIMAX_API_KEY>",
    base_url="https://api.minimaxi.com/v1",
)
resp = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[{"role": "user", "content": "你好"}],
)
```

## 流式响应处理

流式走 SSE(`event: data: {...}`),每个 chunk 含 `choices[0].delta.content`。

`_client.py` 的 `chat()` 已实现 stream 模式处理,直接打印 + 收集。

## 错误重试

`_client.py` 内置 3 次指数退避(1.5s / 2.25s / 3.375s),仅对网络异常和 5xx 生效。
401/403/429 立即抛错。

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| `invalid api key` | Key 错/过期 | 在 [接口密钥](https://platform.minimaxi.com/user-center/basic-information/interface-key) 重置 |
| `quota exceeded` | 余额不足 | 充值或换 Token Plan |
| `model not found` | model 名拼错 | 查 SKILL.md 路由表的精确名 |
| `context too long` | 输入超 200K(M3 除外) | 换 M3 或截断 |