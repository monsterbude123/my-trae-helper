# website-helper-skill — 仓库内 sink 索引

> **目录身份**：本目录是 `~/.trae-cn/skills/website-helper-skill` skill 的**仓库镜像 + 经验沉淀 sink**。
> - **源码**（SKILL.md / pyproject.toml / publish/ / docs/ / scripts/ / references/）= skill 自身存盘，**改这里会污染源**，禁止 Edit。
> - **本 README + distill-2026-08-20.md** = 本会话蒸馏出来的"调用方适配规则"（按 user_rules "外部技能对当前项目的 agents 来说只能自己用 rule 去适应"）。**只读、新增，不修改源码**。
> - 跨会话经验 / 全局方法论 → 全局 `self-improving-agent`（仓库**不复制**）。
> - 命名/落点按项目侧 [`.agents/rules/learning.md` §2](../../.agents/rules/learning.md) 一致。

---

## §0 何时打开本目录

| 你（项目内 agent）做的事 | 要打开 |
|----------------------|--------|
| 准备用 `~/.trae-cn/skills/website-helper-skill` 做 `publish deploy` | [distill-2026-08-20.md §1 强制清单](./distill-2026-08-20.md) |
| 准备调用 `publish` 的 CLI 做 DNS / Nginx / SSL 任一步 | [§2 拆分原子的 6 个反例](./distill-2026-08-20.md) |
| 准备部署**非静态站点**（docker / 反代 / 反向应用） | [§3 publish deploy 强耦合 webroot 与解法](./distill-2026-08-20.md) |
| 准备通过 .env 喂 SSH_KEY_PATH / DNS 凭据 | [§4 .env 解析三重坑](./distill-2026-08-20.md) |
| 准备上手 zentao / docker / SSL 三件套自动化 | [§5 zentao 部署交付模板](./distill-2026-08-20.md) |
| 准备接管别人传过来的 `.env` | [§6 写权伦理与污染检测](./distill-2026-08-20.md) |
| 不知此目录存在 | 由 `common-project-coding-conf` §1 路由表加载本 README |

---

## §1 三条与外部 skill 共存的项目侧铁律

```
MUST
  1. .env 在项目侧自己处理:
     路径 / 引号 / 字段遮蔽 / 一次性回显。
     publish 的 store._parse_env_file 不剥引号,
     Linux 路径"C:/..."会变 paramiko OSError。
  2. publish deploy 是耦合单元 (webroot + nginx root + SSL),
     非静态站点需拆 3 个原子步骤走。
  3. 宝塔 / 自定义 nginx / 企业 vhost 都可能不读 sites-enabled,
     部署前先 nginx -T | grep server_name 验证。

MUST NOT
  - 不要尝试改 ~/.trae-cn/skills/website-helper-skill/ 源码。
  - 不要把密钥明文贴对话(即使 .env 已加密磁盘)。
  - 不要把"已知默认密码"假设在 docker 镜像里(禅道无)。
```

---

## §2 与全局经验沉淀的关系

- 本目录里 `distill-2026-08-20.md` 是 `2026-08-20` 单日蒸馏的事实记录
- 跨会话的"经验法"已经在 `self-improving-agent` 全局持久化
- 仓库内**只放**程序可断言的反例与命令陷阱，**不放**对话细节

---

## §3 文件索引

| 文件 | 内容 | 大小期望 |
|------|------|---------|
| [README.md](./README.md) | 本文件 — 入口 / 路由 | ≤ 80 行 |
| [distill-2026-08-20.md](./distill-2026-08-20.md) | 当日踩坑蒸馏（6 节） | ≤ 350 行（vibe-coding-standards v2.5） |

---

## §4 变更流程

```
新发现踩坑
  → append 到 distill-YYYY-MM-DD.md 的对应 §N
  → 不修改 README.md 结构 (除非路由变化)
  → git commit -F .commit_msg.txt (多行中文, AGENTS.md §4.1.2)
```

---

身份声明：本目录**不挂 frontmatter / 不在 skill 加载机制里**，仅作"项目侧 rules 适配仓库"。
