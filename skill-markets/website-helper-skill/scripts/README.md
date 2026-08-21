# scripts/

所有脚本通过 `$SKILL_DIR`（脚本自身目录的父目录）自发现 skill 资源。

---

## install-server.sh

一次性在**云机器**上安装 nginx + certbot + python3-certbot-nginx。

```bash
cd <你的项目目录>    # .env 所在目录
bash $SKILL_DIR/scripts/install-server.sh
```

- 从 **cwd/.env** 读取 SSH_HOST / SSH_USER / SSH_PORT / SSH_PASSWORD / SSH_KEY_PATH
- 支持 Ubuntu / Debian / CentOS / RHEL / Rocky / AlmaLinux / Alinux
- 不打印凭据

---

## init-publish.sh

环境检查 + `publish config init` 包装。

```bash
bash $SKILL_DIR/scripts/init-publish.sh [.env所在目录，默认cwd]
```

检查项：
- cwd/.env 存在
- .gitignore 含 .env
- references/.env.example 无真实 secret 模式
- publish 已安装（否则自动 pip install -e $SKILL_DIR）

---

## 不暴露的秘密

所有脚本**不打印** `*_PASSWORD`、`*_SECRET`、`*_KEY` 字段值，只显示字段名和是否存在。
