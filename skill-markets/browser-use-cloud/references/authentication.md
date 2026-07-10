# Authentication — 认证集成

## 方式选择

| 方式 | 安全性 | 适用场景 |
|------|--------|---------|
| **1Password** | ⭐⭐⭐ 最高 | 正式项目，有多个网站需登录 |
| **Secrets** | ⭐⭐ 中等 | 快速原型，简单场景 |
| **Agent 注册** | — | Agent 自己没有 Browser Use 账号时 |

---

## 1Password 集成（推荐）

Agent 看不到真实密码，凭据被程序化填充。

### 设置步骤

**1. 创建专用 Vault**

在 1Password 中创建专用 Vault，添加 agent 需要的凭据（用户名、密码、TOTP/2FA）。

**2. 创建 Service Account Token**

1. 打开 [1Password Developer Tools](https://my.1password.eu/developer-tools/active/service-accounts)
2. 点击 **New Service Account**，命名为 "Browser Use Cloud"
3. 授予对专用 Vault 的 **read 权限**
4. 复制生成的 token

**3. 连接到 Browser Use Cloud**

1. 打开 [Browser Use Cloud Settings → Secrets](https://cloud.browser-use.com/settings?tab=secrets)
2. 点击 **Create Integration**
3. 粘贴 service account token

### 使用

```python
from browser_use_sdk import AsyncBrowserUse

client = AsyncBrowserUse()
result = await client.run(
    "Log into my Jira account and create a new ticket for Q4 release",
    op_vault_id="your-vault-id",
    allowed_domains=["*.atlassian.net"],
)
```

### SSO/OAuth 重定向

包含所有认证流程中的域名：

```python
result = await client.run(
    "Log into Jira and create a ticket",
    op_vault_id="your-vault-id",
    allowed_domains=["*.atlassian.net", "*.okta.com", "*.google.com"],
)
```

### 工作原理

Agent 遇到登录表单时：
1. 识别服务（如 Twitter、GitHub、LinkedIn）
2. 从 1Password Vault 获取匹配凭据
3. 自动填充用户名和密码
4. 如需要 2FA 且存有 TOTP，自动生成并输入验证码

**Agent 看不到真实凭据**——用户名、密码和 2FA 代码被程序化填充。

---

## Secrets（域名凭证）

直接传凭证，按域名作用域限制。

### 基本使用

```python
from browser_use_sdk import AsyncBrowserUse

client = AsyncBrowserUse()
result = await client.run(
    "Log into GitHub and star the browser-use/browser-use repo",
    secrets={"github.com": "username:password123"},
    allowed_domains=["github.com"],
)
```

### 多域名 SSO

```python
result = await client.run(
    "Log into the company portal and download the Q4 report",
    secrets={
        "portal.example.com": "user@company.com:password123",
        "okta.com": "user@company.com:password123",
    },
    allowed_domains=["portal.example.com", "*.okta.com"],
)
```

### 域名通配符

```python
allowed_domains=["*.example.com"]  # 匹配 sub.example.com, app.example.com
allowed_domains=["example.com"]     # 只匹配 example.com
```

> **安全提示**：Secrets 明文传给 agent，可能被 AI 模型看到。敏感场景优先使用 1Password。

---

## Agent 自主注册

Agent 没有 Browser Use 账号时可以自主创建：

```bash
# 1. 请求挑战
curl -X POST https://api.browser-use.com/cloud/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "User Name"}'

# Response: {"challenge_id": "uuid", "challenge_text": "What is 12 * 12?"}

# 2. 求解数学题，答案保留两位小数
answer = "144.00"

# 3. 验证
curl -X POST https://api.browser-use.com/cloud/signup/verify \
  -H "Content-Type: application/json" \
  -d '{"challenge_id":"uuid","answer":"144.00"}'

# Response: {"api_key": "bu_..."}

# 4. 创建 claim link（供人类认领，有效期 1 小时）
curl -X POST https://api.browser-use.com/cloud/signup/claim \
  -H "X-Browser-Use-API-Key: bu_..."
# Response: {"claim_url": "https://..."}
```

也可以用 CLI：
```bash
browser-use cloud signup
browser-use cloud signup --verify <challenge-id> <answer>
browser-use cloud signup --claim
```
CLI 将 key 保存到 `~/.browser-use/config.json`。
