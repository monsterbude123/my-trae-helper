# Stack — 项目栈细节（V11 不知道的项目独有信息）

> V11 内部有"必跑测试/必含覆盖率/必含 lint"等通用约束。本文件只放**具体命令**。

---

## 项目栈

```yaml
type: web
language: typescript 5.x
framework: react 18 + vite 5
test_framework: vitest 1.x
e2e_framework: playwright 1.4x
package_manager: pnpm 9.x
```

## 命令速查

### 开发服务器
```bash
pnpm dev  # 默认 http://localhost:5173
```

### 测试
```bash
# 单元 + 集成
pnpm test --run

# E2E（需 dev server 先跑）
pnpm exec playwright test

# 覆盖率（≥90% by V11 Article I）
pnpm test --run --coverage
```

### 类型检查
```bash
pnpm tsc --noEmit  # 必须 0 错误
```

### Lint
```bash
pnpm lint  # eslint 0 警告（V11 必 0）
```

### 构建
```bash
pnpm build  # 产出 dist/
```

### V11 验收命令（必跑）
```bash
# 1. 启动验证
pnpm dev > /tmp/dev.log 2>&1 &  # 后台启动
sleep 5
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/  # 必须 200

# 2. Playwright 截图
playwright_screenshot name=default-view fullPage=false

# 3. V11 hooks
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .
```

## 反例（必走 V11）

- ❌ `pnpm test` 不传 `-- --run` → vitest 进入 watch 模式，CI 阻塞
- ❌ `pnpm tsc --noEmit` 失败 → 🛑 REJECT（V11 Article V 验证性主张）
- ❌ 构建后未跑 E2E → 🛑 REJECT（V11 Stage 3.5 必含 5 类项目启动验证）

---

## 关联引用

- [paths.md](paths.md) — 项目级禁读路径
- [git.md](git.md) — Git 工作流
- [V11 SKILL.md §0.5 加载](../../SKILL.md)