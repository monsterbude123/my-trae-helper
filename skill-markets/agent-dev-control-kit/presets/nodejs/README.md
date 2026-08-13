# Node.js Preset

> Node.js + JavaScript/TypeScript 项目脚手架。

## 适用场景

- Node.js 后端服务（Express / Fastify / Koa / Hapi）
- CLI 工具
- 通用 npm 包
- TypeScript 项目（通过 `tsconfig.json` 启用）

## 工具链

| 组件 | 默认 | 备选 |
|------|------|------|
| 包管理 | npm | yarn / pnpm / bun |
| 运行时 | Node.js ≥18 | — |
| 测试 | node:test (内置) | vitest / jest |
| Lint | eslint | biome |
| 格式化 | prettier | biome |
| 类型检查 | tsc --noEmit（可选） | — |

## 目录约定

```
.
├── src/              # 源码
├── tests/            # 测试（unit / integration / e2e）
├── config/           # 配置（可选）
├── docs/             # 文档
├── gates/            # 门禁脚本
├── guards/           # 守卫脚本
└── scripts/          # 初始化/工具脚本
```

## 使用

```bash
python scripts/init-from-preset.py --preset nodejs --target ./my-app
```

## 关键脚本

- `template/scripts/init.sh` — 初始化（`npm install` + 创建 `.env`）
- `template/gates/pre-commit.sh` — L1 门禁（lint + typecheck + unit test）
- `template/guards/api-contract-guard.mjs` — API 契约守卫
- `template/guards/test-coverage-guard.mjs` — 测试覆盖率守卫（≥80%）