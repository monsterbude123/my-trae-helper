---
name: browser-use-cloud
version: 1.0.0
version: 1.0.0
description: Browser Use 浏览器自动化技能——开源版（browser-use[core]）优先，Cloud API（browser-use-sdk）辅助。覆盖本地 Agent 运行、LLM 配置（ChatBrowserUse/local llm/OpenAI/Anthropic）、Chrome Profile 认证、CLI 交互、结构化提取、多步工作流、MCP 集成、Webhook 异步。当用户提到 browser-use、浏览器自动化、网页抓取、网页数据提取、网站自动操作、网页表单填写、browser agent 时主动加载。配置从项目根目录 .env.browseruse 读取。
status: observing
intent: Browser Use 浏览器自动化技能——开源版（browser-use[core]）优先，Cloud API（...
category: other
audience: [agent]
---
# Browser Use — 浏览器自动化技能

> **状态：⏳ 等待观察（Observing）** — 本地模型（local llm）表现很差，暂不推荐生产使用。优先使用 Cloud API 或 ChatBrowserUse 云端模型。

你是 Browser Use 平台的专家。覆盖**开源版**（`browser-use`，本地运行）和 **Cloud API**（`browser-use-sdk`，云端托管）。

---

## 技能加载策略

本技能采用渐进式三级加载：

1. **本文档** — 模块导航 + 核心速查（决策树/安装/常用模式/参数速查）
2. **references/ 目录** — 各专题深度文档，按需读取
3. **scripts/ 目录** — 可执行脚本，直接运行或作为模板

### 模块导航

| 模块 | 读取文件 | 一句话说明 |
|------|---------|-----------|
| **本地使用（默认）** | `references/local-usage.md` | `browser-use[core]` 安装、Agent API、LLM 配置、CLI、Chrome Profile 认证 |
| Agent 会话（Cloud） | `references/agent-tasks.md` | run()、Follow-up、Live Streaming、手动轮询 |
| 结构化提取 | `references/agent-tasks.md` | Pydantic/Zod schema、类型安全输出 |
| 文件与工作区 | `references/workspaces.md` | 上传文件给 agent、下载 agent 生成的文件 |
| BaaS 接入 | `references/baas.md` | 裸浏览器 CDP、Playwright/Puppeteer/Selenium、实时预览 |
| Profile 与代理 | `references/profiles-proxies.md` | 持久浏览器状态、住宅代理 195+ 国家、自定义代理 |
| MCP 集成 | `references/mcp-integration.md` | Claude Code/Cursor/Windsurf MCP Server 配置与 Tools |
| Webhook 与异步 | `references/webhook-async.md` | 任务状态通知、HMAC 签名验证、防重放攻击 |
| 认证集成 | `references/authentication.md` | 1Password、Secrets、Agent 自主注册 |
| 确定性重执行 | `references/deterministic-rerun.md` | @{{}} 参数缓存、$0 LLM 成本重跑、Auto-healing |
| 错误与成本 | `references/error-cost.md` | 常见错误、成本优化策略、状态监控 |
| API 速查 | `references/api-reference.md` | 完整 REST API 端点速查 |
| 快速开始（Cloud） | `references/quickstart.md` | 云端安装、API Key、第一个 Cloud 任务、Agent 自主注册 |

### 可执行脚本

| 脚本 | 用途 |
|------|------|
| `scripts/api_check.py` | API Key 有效性检查、账户余额查询、最近 session 列表 |
| `scripts/structured_extract.py` | 结构化数据提取模板（Pydantic 模型 + run 调用） |
| `scripts/batch_sessions.py` | 批量并发 session 管理（asyncio.gather 模式） |
| `scripts/webhook_server.py` | Webhook 接收服务器（FastAPI + 签名验证 + 事件处理） |

---

## 决策树

```
第一步：选运行方式
│
├─ 🏠 本地开发/调试/学习？
│   → 开源版（默认推荐）
│   pip install "browser-use[core]"
│   from browser_use.beta import Agent
│   详见 → references/local-usage.md
│
└─ ☁️ 生产/大规模/需要 stealth+代理？
    → Cloud API
    pip install browser-use-sdk
    from browser_use_sdk.v3 import AsyncBrowserUse
    详见 → references/quickstart.md

第二步（Cloud API）：选 Agent 还是 Browser
├─ 需要 AI 自主操作？ → Agent (sessions.create / client.run)
│   ├─ 需要结构化数据？ → output_schema (Pydantic/Zod)
│   ├─ 需要多步操作？ → Follow-up tasks (同 session_id)
│   ├─ 需要文件？ → Workspace
│   ├─ 需要登录？ → Secrets 或 1Password
│   ├─ 需要重复跑？ → Deterministic Rerun (@{{}})
│   └─ 需要异步通知？ → Webhooks
└─ 已有 Playwright/Puppeteer 脚本？ → Browser (browsers.create)
    ├─ 需要自定义代理？ → custom_proxy
    └─ 需要特定分辨率？ → screen_width/height

公共能力（本地和云端均可用）：
├─ 需要持久登录态？ → Profiles / Chrome user_data_dir
├─ 需要嵌入 AI 助手？ → MCP Server
├─ 需要成本控制？ → Deterministic Rerun + 模型选择
└─ 需要实时观看？ → live_url (iframe 嵌入)
```

---

## 快速上手（本地版 · 推荐）

### 1. 安装

```bash
pip install "browser-use[core]"
```

### 2. 配置

在项目根目录创建 `.env.browseruse`：

```bash
# .env.browseruse
BROWSER_USE_API_KEY=bu_your_key_here

# 如果用本地 local llm：
# BROWSER_USE_BASE_URL=http://localhost:11434/v1
# BROWSER_USE_MODEL=qwen2.5
```

加载环境变量：

```python
# 在脚本开头
from dotenv import load_dotenv
load_dotenv(".env.browseruse")
```

### 3. 第一个任务

```python
from browser_use.beta import Agent, BrowserProfile, ChatBrowserUse
from dotenv import load_dotenv
import asyncio

load_dotenv(".env.browseruse")

async def main():
    agent = Agent(
        task="Find the number of stars of the browser-use repo on GitHub",
        llm=ChatBrowserUse(),
        browser_profile=BrowserProfile(
            headless=False,              # 能看到浏览器操作
            allowed_domains=["*.github.com"],
        ),
    )
    history = await agent.run()
    print(history.final_result())

asyncio.run(main())
```

---

## 快速上手（Cloud API · 生产场景）

```bash
pip install browser-use-sdk
export BROWSER_USE_API_KEY=bu_your_key_here
```

```python
from browser_use_sdk.v3 import AsyncBrowserUse
import asyncio

async def main():
    client = AsyncBrowserUse()
    result = await client.run("List the top 20 posts on Hacker News")
    print(result.output)

asyncio.run(main())
```

---

## 五大核心模式

以下为本地版 API。Cloud API 对应模式见 `references/agent-tasks.md`。

### ① 基础 Agent 任务

```python
from browser_use.beta import Agent, BrowserProfile, ChatBrowserUse

agent = Agent(
    task="Go to wikipedia.org and tell me today's featured article",
    llm=ChatBrowserUse(),
    browser_profile=BrowserProfile(headless=False),
)
history = await agent.run()
print(history.final_result())
```

### ② LLM 灵活切换

```python
# 默认（Browser Use 优化模型，最快最准）
llm = ChatBrowserUse()

# 通过 Browser Use 中转调用其他模型（一个 Key 全通）
llm = ChatBrowserUse(model='anthropic/claude-sonnet-4-6')
llm = ChatBrowserUse(model='openai/gpt-5.5')

# ⚠️ 本地模型（local llm）表现很差，不推荐
# 本地小模型在浏览器自动化场景下会频繁卡住、误判元素、上下文溢出
# 如需本地跑，建议至少用 32B+ 模型，且任务简单明确
from browser_use.beta import ChatOpenAI
llm = ChatOpenAI(model='qwen2.5', base_url='http://localhost:11434/v1', api_key='local llm')
```

### ③ Chrome Profile 认证（一次登录永久复用）

```python
profile = BrowserProfile(
    user_data_dir="~/.chrome-for-agent",  # 指定 profile 目录
    headless=False,
)

# 首次运行 → agent 打开浏览器 → 你手动登录各网站
# 关闭后 cookies 自动保存
# 后续运行 → 自动使用已保存的登录态，无需再登
agent = Agent(task="Check my GitHub notifications", llm=llm, browser_profile=profile)
```

### ④ CLI 快速交互

```bash
browser-use open https://example.com
browser-use state                 # 列出可点击元素
browser-use click 5               # 点击元素
browser-use type "Hello World"    # 输入文字
browser-use screenshot page.png   # 截图
browser-use close
```

### ⑤ 自定义工具

```python
from browser_use.beta import Tools

tools = Tools()

@tools.action(description='Search internal database for user info.')
def search_user(email: str) -> str:
    return f"Found: {email}"

agent = Agent(task="Look up orders for john@example.com", llm=llm, tools=tools)
```

---

## 关键参数速查

### 本地版（Agent）

| 参数 | 类型 | 说明 |
|------|------|------|
| `task` | `str` | 自然语言任务描述 |
| `llm` | `ChatBrowserUse` / `ChatOpenAI` / `ChatAnthropic` | LLM 实例 |
| `browser_profile` | `BrowserProfile` | headless、域名限制、代理、user_data_dir |
| `tools` | `Tools` | 自定义工具集合 |

### BrowserProfile

| 参数 | 说明 |
|------|------|
| `headless` | `False` = 显示浏览器窗口（调试）/ `True` = 无头 |
| `allowed_domains` | 限制访问域名，如 `["*.github.com"]` |
| `user_data_dir` | Chrome profile 目录，复用登录态 |
| `start_url` | 初始页面 |
| `keep_alive` | 任务间保持浏览器存活 |
| `record_video` | 录制操作视频 |
| `proxy` | 自定义代理 `{"server": "...", "username": "...", "password": "..."}` |

### Cloud API（client.run）

| 参数 | 类型 | 说明 |
|------|------|------|
| `task` | `str` | 任务描述，1-50000 字符 |
| `model` | `str` | `claude-sonnet-4.6` / `claude-opus-4.6` / `gpt-5.4-mini` |
| `output_schema` | Pydantic/Zod | 结构化输出 schema |
| `session_id` / `workspace_id` / `profile_id` | `str` | 复用已有资源 |
| `proxy_country_code` / `custom_proxy` | — | 代理配置 |
| `recording` / `flash_mode` / `thinking` | `bool` | 行为开关 |

---

## 本地 vs Cloud 对比

| | **开源版**（本地 · 默认推荐） | **Cloud API**（生产场景） |
|---|---|---|
| 安装 | `pip install "browser-use[core]"` | `pip install browser-use-sdk` |
| 导入 | `from browser_use.beta import Agent` | `from browser_use_sdk.v3 import AsyncBrowserUse` |
| 浏览器位置 | 你的机器 | Browser Use 云端 |
| LLM | 你自己配 Key | 云端自动选 |
| Stealth / 代理 / CAPTCHA | 需 Cloud Browser 辅助 | 内置 |
| 成本 | 免费（只付 LLM API） | 按 token 计费 |
| 配置 | `.env.browseruse` | `BROWSER_USE_API_KEY` 环境变量 |
| 适用 | 开发 / 调试 / 学习 / 简单脚本 | 生产 / 大规模 / 复杂任务 |

---

## 重要提示

- **技能状态：⏳ 等待观察** — 本地模型表现很差，整体技能在观察期，暂不建议大规模采用
- **本地模型不推荐**：local llm 等本地小模型（< 32B）在浏览器自动化场景下表现极差——频繁卡住、误判元素、上下文溢出。如需本地跑，至少 32B+ 模型且任务简单明确。**强烈建议用 `ChatBrowserUse()` 云端模型**
- **本地版默认推荐**：开发调试用开源版（`headless=False` 可观察浏览器操作），生产上量用 Cloud API
- **认证**：本地版用 `BrowserProfile(user_data_dir=...)` 复用 Chrome 登录态；Cloud API 用 Profiles 或 1Password
- **混用**：可以开源版 Agent + Cloud Browser（通过 CDP 连接云端 stealth 浏览器）
- **配置**：所有 key 从 `.env.browseruse` 加载，不硬编码在代码中
- **消息格式陷阱**（直接调用 `llm.ainvoke()` 时）：0.13+ 使用强类型消息，传字符串会报 `TypeError: Unknown message type: <class 'str'>`，必须用 `UserMessage/SystemMessage/AssistantMessage`。详见 `references/local-usage.md` 的"直接调用 LLM 与消息格式"
- **local llm token**：新版不再接受占位符 `lm-studio`，必须从 UI 复制真实 token（形如 `sk-lm-xxx:xxx`）。详见 `references/local-usage.md` 的"本地模型（local llm）"

---

> **深入某个专题？** 读取 `references/` 下对应文件。
> **需要即用脚本？** 查看 `scripts/` 目录。
