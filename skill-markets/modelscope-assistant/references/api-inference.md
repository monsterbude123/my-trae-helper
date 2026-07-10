# API-Inference 使用指南

魔搭为头部开源模型提供免费 API 调用，每用户每日 2000 次。

## 支持范围

6 万+模型，覆盖：
- 大语言模型（Qwen、DeepSeek、GLM、MiniMax）
- 多模态模型（Qwen-VL 等）
- 文生图（Stable Diffusion 系列）

## 在网页端体验

```
模型页面 → "体验"标签 → 直接输入文本/上传图片 → 查看结果
```

## 通过 SDK 调用

```python
from modelscope.pipelines import pipeline

# 以 Qwen2.5-7B-Instruct 为例
pipe = pipeline(
    'text-generation',
    model='Qwen/Qwen2.5-7B-Instruct',
    api_key='your-api-key'  # 从魔搭个人设置获取
)

result = pipe('你好，请介绍一下你自己')
```

## 获取 API Key

```
魔搭首页 → 个人头像 → API Key 管理 → 创建新 Key
```

## 注意事项

- 每日 2000 次额度按 UTC+8 重置
- HTTP 429 = 当日额度耗尽，次日自动恢复
- API-Inference 使用阿里云算力，响应速度较快
- 支持的模型列表在不断扩充中
