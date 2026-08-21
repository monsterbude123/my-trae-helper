---
name: website-helper-skill
description: "Use when the user wants to publish a local web project to a sub-domain via the publish CLI. Triggers on: 'publish a site', 'deploy a sub-domain', 'add sub-domain', 'update website', '发布', '部署子域名', '更新网站', '上线路由', 'create cert for sub-domain', 'rollback previous version', 'design and deploy a page'. This skill is self-contained — the publish tool ships inside the skill. Credentials come from a .env file in the current working directory (never from chat). The skill never prints, echoes, or summarizes real secret contents."
---

# website-helper-skill — 自动子域名发布

> 一键把本地网页发布到子域名（HTTPS 自动证书）。**自闭环**：publish 工具、配置模板、安装脚本全部内置，不做外部路径假设。

---

## 0. 守则（必须遵守）

1. **绝不**在回复/日志/截图里复述 `.env` 中的任何 `*_KEY`、`*_SECRET`、`*_PASSWORD`、`*_TOKEN` 字段值。
2. 读 `.env` 时只读**字段名**和**是否存在**，不读具体值；如果用户粘贴了真实 secret，**立即提醒轮换**。
3. 引导用户自己编辑 `.env`；不在对话里直接写或改凭据值。
4. `publish config show` 输出时，密码字段必须掩码。
5. 本 skill 的所有文件都在 `$SKILL_DIR` 下自发现，不依赖特定项目路径。

---

## 1. 自闭环结构

```
$SKILL_DIR/                          # 即本 skill 的根目录
├── SKILL.md                         # 本文件 — 入口 + 路由
├── pyproject.toml                   # 可 pip install -e . 安装
├── publish/                         # 自带的 publish CLI 工具
│   ├── cli.py                       # 入口
│   ├── dns/base.py                  # DNS 提供商（Aliyun / Cloudflare / DNSPod）
│   ├── ssh/client.py                # SSH 客户端
│   ├── nginx/deploy.py              # Nginx 部署 + certbot
│   ├── certs/cert_manager.py        # SSL 证书管理
│   ├── cockpit/logger.py            # 驾驶舱日志
│   └── config/store.py              # 配置存储（从 cwd/.env 加载）
├── references/
│   └── .env.example                 # 配置模板
├── scripts/
│   ├── install-server.sh            # 云机器初始化
│   └── init-publish.sh              # 环境检查 + config init
└── docs/
    ├── usage.md                     # 使用指南
    ├── troubleshooting.md           # 故障排查
    ├── credential-management.md     # 凭据管理
    ├── design-deploy-workflow.md    # 设计 → 开发 → 部署
    └── limitations.md               # 限制 / 已知短板
```

---

## 2. 路由（按意图跳转）

| 用户说 | 跳到 |
|--------|------|
| "帮我发布 / 上线 / 部署到 xxx.<domain>" | [docs/usage.md → 2. 部署](docs/usage.md) |
| "帮我做个页面 / 图站 / UI / 设计并部署" | [docs/design-deploy-workflow.md](docs/design-deploy-workflow.md) |
| "更新一下 / 重新发一下" | [docs/usage.md → 2.3 幂等更新](docs/usage.md) |
| "回滚 / 退回上一版" | [docs/usage.md → 2.4 回滚](docs/usage.md) |
| "证书 / SSL / 续签" | [docs/usage.md → 2.5 证书](docs/usage.md) |
| "publish 命令不工作 / 报错" | [docs/troubleshooting.md](docs/troubleshooting.md) |
| "我要修改密钥 / 改密码" | [docs/credential-management.md](docs/credential-management.md) |
| "能做什么 / 不支持什么" | [docs/limitations.md](docs/limitations.md) |
| "装 nginx / 装 certbot" | [scripts/install-server.sh](scripts/install-server.sh) |

---

## 3. 开机三步

### 3.1 安装 publish 工具

```powershell
cd $SKILL_DIR
pip install -e .    # 安装 publish 命令到 PATH
```

> 本 skill 自带 `pyproject.toml`，`pip install -e .` 后 `publish` 全局可用。

### 3.2 创建并填写配置

```powershell
# 从模板复制（模板在 references/.env.example）
cp $SKILL_DIR/references/.env.example .env
# 编辑 .env 填入你的真实值
```

### 3.3 加载配置

```powershell
publish config init    # 从当前目录的 .env 加载
```

---

## 4. 速查命令

```powershell
publish config init                                # 从 cwd/.env 加载
# 静态模式
publish deploy NAME -d DOMAIN -w DIR [--ip]        # 部署 / 更新
# 反代模式 (VR-009, 2026-08-20)
publish deploy NAME -d DOMAIN --proxy --upstream URL [--ip]
publish rollback DOMAIN                            # 回滚
publish list                                       # 列出已发布
publish cert status                                # 证书状态
publish cert renew [DOMAIN]                        # 续签
```

### 4.5 反代模式（VR-009 / VR-010 / VR-011）

Docker 容器 / 反向代理场景下，**不能用** `--webroot`（静态模式把文件上传到 `/var/www/...`），
请用：

```bash
publish deploy zentao \
  -d zentaopms.example.com \
  --proxy \
  --upstream http://127.0.0.1:8088 \
  --ip 1.2.3.4
```

行为：
- **自动探测 vhost 路径**（宝塔 → `/www/server/panel/vhost/nginx/`，cPanel → `/etc/nginx/conf.d/`，原生 Debian → `sites-enabled`）。**写到错目录是 2026-08-20 唯一翻车点**。
- **certbot nginx 插件缺失时自动降级**到 `--standalone`（临时停 nginx + iptables 锁 80，完成 HTTP-01 challenge 后恢复）。

---

## 5. 检查清单

```
[ ] pip install -e $SKILL_DIR（首次）
[ ] cwd/.env 存在且填写了真实值
[ ] .env 在 .gitignore 中
[ ] references/.env.example 是模板（无真实值）
[ ] publish config init 成功
[ ] 用户提供了：子域名 + 本地目录
[ ] 首次 deploy 给了 --ip
```
