# Workflow A — 批量验收模式

> 适用：模块级 E2E 回归、CI/CD 门禁、发版前全量检查。
> 共享基础设施见 [infra-shared.md](infra-shared.md)，通用约定见 [conventions.md](conventions.md)。

---

## A.1 工作流总览

```
Phase 0: 诊断准备
  ├── clearScreenshots(module)
  ├── startLogCapture(module)     ← 启动后端日志流
  ├── setupTestData()
  └── 注入浏览器 console/network 拦截器

Phase 1: 路由导航截图
  for each route in module:
    ├── navigate(route)
    ├── screenshot(label, module)
    ├── captureLogSnapshot(module, label)
    └── captureBrowserContext(page, module, label)
        └── 异常检测 → recordAnomaly() 如有

Phase 2: 页面内交互截图
  for each interaction in module:
    ├── screenshot("interact-{n}-start")
    ├── captureLogSnapshot + captureBrowserContext
    ├── click / type / select
    ├── screenshot("interact-{n}-after")
    └── captureLogSnapshot + captureBrowserContext
        └── 异常检测 → recordAnomaly() 如有

Phase 3: 深入交互截图
  ── 子页面导航 + 返回 + 状态变更
  ── 同 Phase 2 的截图 + 日志模式

Phase 4: 诊断报告生成
  ├── stopLogCapture(module)
  └── generateDiagnosisReport(ctx)
      → screenshots/{module}/_diagnosis.md
```

## A.2 目录结构

```
screenshots/
├── auth/
│   ├── route-01-Login.png
│   ├── route-02-Register.png
│   ├── interact-01-login-flow-start.png
│   ├── interact-01-login-flow-after.png
│   ├── _logs/
│   │   ├── backend-route-01.json
│   │   ├── backend-route-02.json
│   │   ├── console-route-01.json
│   │   └── network-route-01.json
│   └── _diagnosis.md              ← 结构化诊断报告
├── dashboard/
│   └── ...
└── settings/
    └── ...
```

## A.3 核心约定

**约定 A1**：一个模块 = 一个测试文件 + 一个截图子目录 + 一个诊断报告
```
{test_dir}/modules/auth.spec.ts  →  screenshots/auth/ + screenshots/auth/_diagnosis.md
```

**约定 A2**：截图文件名包含视图名称
```
✅ route-01-LoginView.png    ❌ route-01.png
命名: {phase}-{序号}-{描述}.png
```

**约定 A3**：beforeAll 清旧图 + 清旧日志，保证每次都是最新状态

**约定 A4**：vision-audit 递归扫描
```bash
vision-audit --dir screenshots/          # 全量
vision-audit --dir screenshots/auth/     # 单模块
```

## A.4 spec 模板

```typescript
// {module}.spec.ts — 批量验收模板
//
// 使用：替换 {MODULE} → 填路由列表 → 实现交互 → 诊断报告自动生成

const MODULE = '{MODULE}'
const ctx = createDiagnosisContext(MODULE)

// === Phase 0: 诊断准备 ===
beforeAll(async () => {
  clearScreenshots(MODULE)
  startLogCapture(MODULE)
  setupTestData()
  await page.evaluateOnNewDocument(/* console + network 拦截 */)
})

afterAll(async () => {
  stopLogCapture(MODULE)
  const report = generateDiagnosisReport(ctx)
  console.log(`Diagnosis report: ${report}`)
})

// === Phase 1: 路由导航 ===
describe('页面初始态', () => {
  const routes = [{ name: 'ViewName', path: '/route' }]
  for (const [i, r] of routes.entries()) {
    it(`${r.name}`, async () => {
      await navigate(r.path)
      const label = `route-${pad(i+1)}-${r.name}`

      await screenshot(label, MODULE)
      captureLogSnapshot(MODULE, label)
      await captureBrowserContext(page, MODULE, label)

      // 异常检测
      if (await isPageBlank(page)) {
        recordAnomaly(ctx, { timestamp: Date.now(), screenshotLabel: label,
          type: 'blank_page', description: `${r.name} 页面空白`,
          screenshotPath: `screenshots/${MODULE}/${label}.png` })
      }
      if (await hasConsoleErrors(page)) {
        recordAnomaly(ctx, { timestamp: Date.now(), screenshotLabel: label,
          type: 'error_page', description: `${r.name} 有控制台错误`,
          screenshotPath: `screenshots/${MODULE}/${label}.png` })
      }
    })
  }
})

// === Phase 2: 页面交互 ===
describe('页面交互', () => {
  for (const [i, { path, action }] of interactions.entries()) {
    it(`${action}`, async () => {
      await navigate(path)
      const labelPre = `interact-${pad(i+1)}-start`
      await screenshot(labelPre, MODULE)
      captureLogSnapshot(MODULE, labelPre)
      await captureBrowserContext(page, MODULE, labelPre)

      await click(action.target)

      const labelPost = `interact-${pad(i+1)}-after`
      await screenshot(labelPost, MODULE)
      captureLogSnapshot(MODULE, labelPost)
      await captureBrowserContext(page, MODULE, labelPost)

      if (await isLoadingStuck(page)) {
        recordAnomaly(ctx, { timestamp: Date.now(), screenshotLabel: labelPost,
          type: 'loading_stuck', description: `${action} 交互后 loading 不消失`,
          screenshotPath: `screenshots/${MODULE}/${labelPost}.png` })
      }
    })
  }
})

// === Phase 3: 深入交互 ===
describe('深入交互', () => {
  // 子页面 + 返回 + 状态变更，同 Phase 2 模式
})

// === Phase 4: 诊断报告在 afterAll 自动生成 ===
```

## A.5 诊断报告格式

```markdown
# [E2E 诊断报告] {模块名}

**生成时间**: {ISO}
**总截图数**: {N}  **异常数**: {M}

---

## 异常 1: {一句话描述}

### 视觉证据
- 截图: `screenshots/{module}/{label}.png`
- 现象: {描述}

### 后端日志（时间窗口: {ts} ± 10s）
```
{相关日志行，带时间戳}
```

### 网络请求
| 方法 | URL | 状态码 | 耗时 | 响应体摘要 |
|------|-----|--------|------|-----------|
| POST | /api/xxx | 500 | 234ms | {"detail":"..."} |

### 浏览器控制台
```
[error] Uncaught (in promise) TypeError: ...
```

### 根因分析
{综合证据链的推理，必须引用具体日志行}

### 建议修复
1. **后端**: {文件}:{行号} — {修改}
2. **前端**: {文件}:{行号} — {修改}

---

## 诊断总结
| # | 类型 | 严重度 | 根因明确 | 建议修复 |
|---|------|--------|---------|---------|
| 1 | loading_stuck | HIGH | ✅ 是 | 见上方 |
```

## A.6 AI 行为契约

```
✅ 每个用例截图后立即 captureLogSnapshot + captureBrowserContext
✅ 每次检测到异常立即 recordAnomaly
✅ afterAll 必须 generateDiagnosisReport
✅ 诊断报告含：证据链 → 根因 → 修复建议 → 关联代码
❌ 只跑截图不拉日志
❌ 发现异常跳过诊断继续跑
❌ 结论是"模块有问题"而没有根因
```
