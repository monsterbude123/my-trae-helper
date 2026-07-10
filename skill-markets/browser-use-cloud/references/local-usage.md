# 本地使用 — 开源版 browser-use

Browser Use 开源版 (`browser-use`) 在你的本地机器上运行 AI 浏览器 agent。免费开源，只需自备 LLM API Key。

所有配置从项目根目录的 `.env.browseruse` 加载。

---

## 环境配置

在项目根目录创建 `.env.browseruse`：

```bash
# .env.browseruse — Browser Use 配置
BROWSER_USE_API_KEY=bu_your_key_here

# 如果使用本地 local llm 或其他 OpenAI 兼容服务：
# BROWSER_USE_BASE_URL=http://localhost:11434/v1
# BROWSER_USE_MODEL=qwen2.5

# 如果直接使用 OpenAI / Anthropic Key（不用 ChatBrowserUse 中转）：
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

加载方式（在脚本开头）：

```python
from dotenv import load_dotenv
load_dotenv(".env.browseruse")  # 自动读取项目根目录的 .env.browseruse
```

## 安装

```bash
# Python >= 3.11
pip install "browser-use[core]"

# 或用 uv
uv add "browser-use[core]"
```

`[core]` 安装 Rust 编写的原生浏览器运行时。

---

## 快速开始

### 方式一：CLI 交互

```bash
browser    # 进入交互终端
```

### 方式二：模板生成

```bash
uvx browser-use init --template default    # 生成脚手架
uvx browser-use init --template advanced   # 全配置模板
uvx browser-use init --template tools      # 自定义工具模板
python browser_use_default.py
```

### 方式三：Python 脚本

```python
from browser_use.beta import Agent, BrowserProfile, ChatBrowserUse
import asyncio

async def main():
    agent = Agent(
        task="Find the number of stars of the browser-use repo",
        llm=ChatBrowserUse(),   # 默认模型
        browser_profile=BrowserProfile(
            headless=False,     # False = 能看到浏览器窗口
            allowed_domains=["*.github.com"],
        ),
    )
    history = await agent.run()
    print(history.final_result())

asyncio.run(main())
```

---

## LLM 配置

### ChatBrowserUse（推荐，一键连所有模型）

一个 `BROWSER_USE_API_KEY` 同时访问 OpenAI、Anthropic、Google 等：

```python
from browser_use.beta import ChatBrowserUse

# Browser Use 优化模型（速度最快，准确率最高）
llm = ChatBrowserUse()                              # 默认 bu-2-0

# 通过 Browser Use 中转调用其他模型
llm = ChatBrowserUse(model='openai/gpt-5.5')
llm = ChatBrowserUse(model='anthropic/claude-sonnet-4-6')
llm = ChatBrowserUse(model='google/gemini-3-pro')
```

### ChatOpenAI

```python
from browser_use.beta import ChatOpenAI

llm = ChatOpenAI(model='gpt-5.5')
# export OPENAI_API_KEY=sk-...
```

### ChatAnthropic

```python
from browser_use.beta import ChatAnthropic

llm = ChatAnthropic(model='claude-opus-4-8')
# export ANTHROPIC_API_KEY=sk-ant-...
```

### 本地模型（local llm）

> ⚠️ **本地模型在浏览器自动化场景下表现很差**，不推荐用于生产任务。小模型（< 32B）频繁卡住、误判元素、上下文溢出。仅建议用于极简任务测试。

```python
from browser_use.beta import ChatOpenAI

llm = ChatOpenAI(
    model='qwen2.5',
    base_url='http://localhost:11434/v1',
    api_key='local llm',  # local llm 不验证 key
)
```

### 本地模型（local llm）

> ⚠️ 同上，本地模型表现很差。如需使用，至少 32B+ 模型且任务简单明确。

local llm 提供 OpenAI 兼容接口，但**新版要求实际 API token**，`api_key='lm-studio'` 已失效——会收到 `invalid_api_key` 错误。Token 需从 local llm UI 获取，形如 `sk-lm-xxx:xxx`。

```python
from browser_use.beta import ChatOpenAI

llm = ChatOpenAI(
    model='qwen3-vl-8b-instruct',
    base_url='http://localhost:1234/v1',
    api_key='sk-lm-xxx:xxx',  # 必须是 local llm UI 生成的真实 token
    max_completion_tokens=128,  # 本地模型建议显式限制，避免内存吃满
)
```

连接验证（带 Authorization Header，不带会被拒）：

```bash
curl -s -H "Authorization: Bearer sk-lm-xxx:xxx" http://localhost:1234/v1/models
```

---

## 直接调用 LLM 与消息格式

Agent 场景下 `task` 是字符串没问题，但**直接调用 `llm.ainvoke()` 时不能传字符串**——browser-use 0.13+ 使用强类型消息格式，传字符串会报 `TypeError: Unknown message type: <class 'str'>`。

```python
from browser_use.llm.messages import UserMessage, SystemMessage, AssistantMessage

# ❌ 错误：直接传字符串
# response = await llm.ainvoke("回复 OK")
# TypeError: Unknown message type: <class 'str'>

# ❌ 错误：误用 BaseMessage（它是 typing.Union 别名，无法实例化）
# from browser_use.llm.base import BaseMessage
# BaseMessage(content="OK", type="human")
# TypeError: Cannot instantiate typing.Union

# ✅ 正确：用具体消息类型
response = await llm.ainvoke([UserMessage(content="回复 OK")])
```

响应结构（用于 token 监控、调试、提取思考过程）：

```python
response.content              # 文本内容
response.thinking             # 思考过程（仅 thinking 模型）
response.usage.prompt_tokens  # 输入 token
response.usage.completion_tokens  # 输出 token
```

---

## BrowserProfile 配置

```python
from browser_use.beta import BrowserProfile

profile = BrowserProfile(
    headless=False,                    # True = 无头模式
    allowed_domains=["*.github.com"],  # 限制访问域名
    start_url="https://github.com",    # 初始页面
    user_data_dir="~/.chrome-profile", # 复用本地 Chrome profile（含登录态）
    keep_alive=True,                   # 任务间保持浏览器存活
    record_video=True,                 # 录制操作视频
    proxy={
        "server": "http://proxy:8080",
        "username": "user",
        "password": "pass",
    },
)
```

---

## 认证：复用本地 Chrome Profile

最方便的登录方式——直接用你日常使用的 Chrome profile：

```python
import os

profile = BrowserProfile(
    user_data_dir=os.path.expanduser("~/.chrome-for-agent"),
    # 首次运行 → 手动登录各网站 → 关闭 agent → 登录态自动保存
    # 后续运行 → 自动使用已保存的 cookies/session
)
```

**流程**：
1. 指定 `user_data_dir`（新建目录）
2. `headless=False` 跑一次任务
3. agent 打开浏览器后手动登录目标网站
4. 关闭浏览器，cookies 已保存
5. 后续任务直接用同一个 `user_data_dir`，无需再登录

---

## CLI 命令

```bash
browser-use open https://example.com     # 打开网页
browser-use state                        # 查看可点击元素
browser-use click 5                      # 点击第 5 个元素
browser-use type "Hello"                 # 输入文本
browser-use screenshot page.png          # 截图
browser-use close                        # 关闭浏览器
```

浏览器在命令之间保持运行，便于快速迭代调试。

---

## 自定义工具

```python
from browser_use.beta import Agent, Tools

tools = Tools()

@tools.action(description='Search internal database for user info.')
def search_user(email: str) -> str:
    """根据邮箱查找用户信息"""
    # 你的数据库查询逻辑
    return f"User found: {email}"

agent = Agent(
    task="Look up the recent orders for john@example.com",
    llm=llm,
    tools=tools,
)
```

---

## Cloud vs 开源 对比

| | **开源版** (`browser-use`) | **Cloud API** (`browser-use-sdk`) |
|---|---|---|
| 浏览器位置 | 本地机器 | Browser Use 云端 |
| 安装 | `pip install "browser-use[core]"` | `pip install browser-use-sdk` |
| LLM | 自己配 Key | 云端自动选 |
| Stealth 指纹 | 需 Cloud Browser 辅助 | 内置 |
| 住宅代理 | 需 Cloud Browser | 内置 195+ 国家 |
| CAPTCHA | 需 Cloud Browser | 内置 |
| 成本 | 免费（只付 LLM） | 按 token 计费 |
| 并发管理 | 自己管 Chrome 内存 | 云端自动扩缩 |
| 适用 | 开发/调试/学习/简单脚本 | 生产/大规模/复杂任务 |

---

## 最佳实践

### 开发阶段 → 开源版

```python
# 本地调试：headless=False，能看浏览器操作
agent = Agent(
    task="...",
    llm=ChatBrowserUse(),
    browser_profile=BrowserProfile(headless=False),
)
```

### 生产阶段 → Cloud API

```python
# 生产环境：云端 stealth 浏览器 + 代理 + CAPTCHA
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()
result = await client.run("...")
```

### 混合：开源 Agent + Cloud Browser

```python
# 用开源版 Agent 逻辑，但浏览器跑在云端（更好的 stealth）
from browser_use.beta import Agent
from browser_use.browser.remote import RemoteBrowser

browser = RemoteBrowser(
    cdp_url="wss://...",  # 从 Cloud API browsers.create() 获取
)
agent = Agent(task="...", llm=llm, browser=browser)
```

更多见 [开源版文档](https://docs.browser-use.com/open-source/introduction)。

---

## 故障排查

实际使用中常见的报错与根因，按发生频率排列：

| 症状 | 根因 | 解决 |
|------|------|------|
| `TypeError: Unknown message type: <class 'str'>` | 直接给 `llm.ainvoke()` 传字符串 | 用 `UserMessage`/`SystemMessage`/`AssistantMessage` 包装成列表 |
| `TypeError: Cannot instantiate typing.Union` | 误用 `from browser_use.llm.base import BaseMessage` 实例化 | 改用 `from browser_use.llm.messages import UserMessage` 等具体类型 |
| `ImportError: cannot import name 'X'` | browser-use 版本与示例不匹配 | `pip show browser-use` 确认版本，对照官方文档调整导入路径 |
| local llm 返回 `invalid_api_key` | 用了旧占位符 `'lm-studio'` 或没带 Authorization | 从 local llm UI 复制真实 token，curl 也必须带 `Authorization: Bearer` |
| Agent 卡住不动 / OOM | 本地模型上下文吃满或 `max_completion_tokens` 未设 | 显式设 `max_completion_tokens`，限制 `allowed_domains` 避免漂移 |
| Agent 访问无关网站 | 未限制域名 | `BrowserProfile(allowed_domains=["*.github.com"])` |

**导入速查**（0.13+ 验证通过）：

```python
# Agent 与浏览器配置
from browser_use.beta import Agent, BrowserProfile, ChatBrowserUse, ChatOpenAI

# 强类型消息（直接调用 llm 时必须用）
from browser_use.llm.messages import UserMessage, SystemMessage, AssistantMessage
```
