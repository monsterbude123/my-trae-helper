# Profiles & Proxies — 持久状态与代理

## Profiles（持久浏览器状态）

Profile 保存 cookies、localStorage、保存的密码。登录一次，跨 session 复用。

### 创建和使用

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()

# 创建 profile
profile = await client.profiles.create(name="user-id-1")

# 或搜索已有 profile
# profile = (await client.profiles.list(query="user-id-1")).items[0]

# 创建使用此 profile 的 session
session = await client.sessions.create(profile_id=profile.id)
result = await client.run("Check browser-use github stars", session_id=session.id)

# ⚠️ 必须 stop session 才会持久化 profile 状态！
await client.sessions.stop(session.id)
```

### Profile 管理 API

```python
# 创建
profile = await client.profiles.create(name="work-account")

# 列出所有
response = await client.profiles.list()
for p in response.items:
    print(p.id, p.name)

# 按名称搜索
response = await client.profiles.list(query="user-id-1")
profile = response.items[0]

# 获取单个
profile = await client.profiles.get(profile_id)

# 更新
await client.profiles.update(profile_id, name="renamed")

# 删除
await client.profiles.delete(profile_id)
```

### 使用模式

- **Per-user profiles**：为每个终端用户创建独立 profile。按名称查询获取 profile ID，或在数据库中存储映射关系
- **状态持久化**：profile 状态仅在 session `stop()` 时保存。如果 session 被遗弃或超时，修改可能丢失
- **错误处理**：使用 profile 的每个代码路径都要确保 stop session，包括异常处理分支

---

## Proxies（代理）

默认启用美国住宅代理，覆盖 195+ 国家。

### 按国家选择代理

```python
client = AsyncBrowserUse()

# Agent 使用德国代理
result = await client.run(
    "Get the price of iPhone 16 on amazon.de",
    proxy_country_code="de",
)

# Browser 使用德国代理
browser = await client.browsers.create(proxy_country_code="de")
print(browser.cdp_url)
print(browser.live_url)
```

### 禁用代理

不需要代理时（如 QA 测试内网环境）：

```python
browser = await client.browsers.create(proxy_country_code=None)
result = await client.run("Go to http://localhost:3000", proxy_country_code=None)
```

### 自定义代理

自带 HTTP 或 SOCKS5 代理：

```python
client = AsyncBrowserUse()
browser = await client.browsers.create(
    custom_proxy={
        "host": "proxy.example.com",
        "port": 8080,
        "username": "user",
        "password": "pass",
    },
)
```

---

## 反封锁策略

Stealth 和代理默认开启。如果仍然被封锁：

1. **使用带登录态 profile** — 绕过登录墙
2. **尝试不同代理国家** — 匹配目标地区
3. **联系支持** — 在 Cloud Dashboard 内发送目标页面链接

---

## Stealth（反检测）

每个 cloud browser session 在加固版 Chromium fork 中运行，默认启用 stealth：

- **反指纹浏览**：Canvas、WebGL、字体、navigator 等浏览器指纹每 session 随机化，通过 CreepJS、BrowserLeaks 等检测
- **广告/Cookie 横幅屏蔽**：自动关闭横幅，agent 看到干净页面
- **Cloudflare/反爬绕过**：支持 Cloudflare、PerimeterX 等反爬服务
