# Paths — 项目级禁读路径（项目独有）

> V11 默认禁读 `docs/archive/**` + `.trae/tmp/**`（V11 Article VIII 归档不可变）。
> 本文件只放**项目独有**的禁读路径（如生产配置、部署密钥）。

---

## 项目级禁读路径

```yaml
project_forbidden_paths:
  # 生产配置（必读须 PR review）
  - deploy/prod.yaml
  - deploy/k8s/production/**  
  - config/production.json

  # 密钥与凭证
  - secrets/**
  - .env.production
  - .env.local

  # 客户数据（如适用）
  - data/customers/**
  - data/backups/**

  # 第三方 SDK 锁定文件（不可读）
  - node_modules/
  - pnpm-lock.yaml

  # 构建产物（重建后必读但禁写）
  - dist/**
  - build/**
  - coverage/**
```

## 启动主上下文必读检查（Glob）

```bash
# 1. 扫描禁读路径（无残留引用的 hardcode）
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/code-hygiene.py \
    --project-root . --src src

# 2. 路径一致性
git diff --stat deploy/ config/ secrets/  # 必为空（无改动）
```

## 反例（必走 V11）

- ❌ 读 `secrets/api-key.json` 并硬编码 → 🛑 REJECT（V11 Article VII 无固定产物 + L4 硬编码）
- ❌ 把生产数据库连接串写到 `.env.example` → 🛑 REJECT
- ❌ 修改 `pn-lock.yaml` 但未提交 `package依赖.json` → 🛑 REJECT（依赖漂移）

---

## 关联引用

- [stack.md](stack.md) — 项目栈命令
- [git.md](git.md) — Git 工作流
- [V11 §3 层依赖配置](../../references/dependency-config.md) — 项目级覆盖规则