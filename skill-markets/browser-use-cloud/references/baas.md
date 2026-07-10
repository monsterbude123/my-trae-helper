# BaaS — Browser as a Service

Browser Use Cloud 提供裸浏览器即服务（CDP 端点），可用 Playwright/Puppeteer/Selenium 连接。

---

## 创建浏览器

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()
browser = await client.browsers.create()

print(browser.cdp_url)      # CDP WebSocket URL (wss://...)
print(browser.live_url)     # 实时预览 URL（可嵌入 iframe）
```

---

## 连接自动化框架

### Playwright

```python
from playwright.async_api import async_playwright

browser = await client.browsers.create()

async with async_playwright() as p:
    pw_browser = await p.chromium.connect_over_cdp(browser.cdp_url)
    page = pw_browser.contexts[0].pages[0]
    await page.goto("https://example.com")
    # 你的 Playwright 脚本...
    await pw_browser.close()

await client.browsers.stop(browser.id)
```

### Puppeteer

```javascript
const puppeteer = require('puppeteer');

const browser = await client.browsers.create();

const puBrowser = await puppeteer.connect({
    browserWSEndpoint: browser.cdpUrl,
});

const page = await puBrowser.newPage();
await page.goto('https://example.com');
// 你的 Puppeteer 脚本...
await puBrowser.disconnect();

await client.browsers.stop(browser.id);
```

### Selenium

```python
from selenium import webdriver

browser = await client.browsers.create()

options = webdriver.ChromeOptions()
options.debugger_address = browser.cdp_url.replace("wss://", "").replace("ws://", "")

driver = webdriver.Chrome(options=options)
driver.get("https://example.com")
# 你的 Selenium 脚本...
driver.quit()

await client.browsers.stop(browser.id)
```

---

## 实时预览与录制

### 获取 live_url

```python
browser = await client.browsers.create()
print(browser.live_url)  # https://live.browser-use.com/...

# 嵌入前端
# <iframe src="{{ live_url }}" width="1280" height="720"></iframe>
```

### 启用录制

```python
# Agent 模式录制
result = await client.run("...", recording=True)

# Browser 模式录制
browser = await client.browsers.create(recording=True)
```

---

## Agent vs Browser 决策

| | **Agent** | **Browser** |
|---|---|---|
| 方法 | `sessions.create()` / `run()` | `browsers.create()` |
| AI 自动操作 | ✓ | — |
| task（自然语言） | ✓ | — |
| model | ✓ | — |
| proxy / custom_proxy | ✓ | ✓ |
| profile_id | ✓ | ✓ |
| recording | ✓ | ✓ |
| workspace_id | ✓ | — |
| keep_alive | ✓ | — |
| screen size / timeout | — | ✓ |

**用 Agent 当**：需要 AI 理解网页、自然语言任务、结构化输出、文件系统
**用 Browser 当**：需要脚本精确控制、自定义尺寸/超时、已有 Playwright/Puppeteer 代码

---

## 浏览器管理

```python
# 停止浏览器
await client.browsers.stop(browser.id)

# 列出活跃浏览器
browsers = await client.browsers.list()
for b in browsers:
    print(b.id, b.status)
```

## 关键参数

```python
browser = await client.browsers.create(
    proxy_country_code="de",          # 代理国家
    proxy_country_code=None,          # 禁用代理
    custom_proxy={                    # 自定义代理
        "host": "proxy.example.com",
        "port": 8080,
        "username": "user",
        "password": "pass",
    },
    screen_width=1920,                # 屏幕宽度
    screen_height=1080,               # 屏幕高度
    recording=True,                   # 启用录制
    timeout=300,                      # 超时（秒）
)
```
