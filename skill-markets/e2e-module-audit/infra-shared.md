# 共享基础设施

> 两种 Workflow 共享的 helpers 和推理引擎。Workflow A/B 的区别仅在于输出形式——批量模式输出报告，即时模式输出修复。

---

## 1. 截图 helper

```typescript
// Workflow A 使用（带模块目录）
async function screenshot(label: string, module: string): Promise<string> {
  ensureDir(`screenshots/${module}`)
  const path = `screenshots/${module}/${label}.png`
  await page.screenshot({ path, fullPage: true })
  return path
}

// Workflow B 使用（临时文件）
async function screenshotQuick(label?: string): Promise<string> {
  const ts = label || Date.now()
  const path = `tmp/diag-${ts}.png`
  await page.screenshot({ path, fullPage: false })
  return path
}
```

## 2. 后端日志 helper

```typescript
// === Workflow A 专用：全流程日志捕获 ===

function startLogCapture(module: string): string {
  // 方案 A（推荐）：后端提供端点
  //   GET /api/debug/logs/stream?module=auth → SSE 流式推送
  // 方案 B：tail -f
  //   spawn("tail -f backend/logs/app.log | grep {module} > screenshots/{module}/_logs/backend.log")
  // 方案 C：sidecar IPC
}

function captureLogSnapshot(module: string, label: string): void {
  // 从日志缓冲区取 label 时刻前后 10 秒的日志
  // → screenshots/{module}/_logs/backend-{label}.json
}

function stopLogCapture(module: string): void { }

// === Workflow B 专用：即时日志查询 ===

async function queryRecentLogs(keyword: string, lines = 100): Promise<string> {
  // 优先通过 API 查询（可按关键词过滤）
  const resp = await fetch(`http://localhost:8765/api/debug/logs?tail=${lines}&grep=${keyword}`)
  if (resp.ok) return resp.text()

  // 降级：tail + grep
  const { stdout } = await exec(`tail -n ${lines} backend/logs/app.log | grep "${keyword}"`)
  return stdout
}

function tailLogs(module: string): ChildProcess {
  // 返回一个 tail -f 进程引用，调用方可 .kill()
  return spawn('tail', ['-f', 'backend/logs/app.log'], {
    // 可选 grep 过滤
  })
}
```

## 3. 浏览器上下文捕获 helper

```typescript
// 两种 Workflow 共用

async function captureBrowserContext(page: Page): Promise<BrowserContext> {
  return page.evaluate(() => ({
    console: (window as any).__e2e_console_logs || [],
    network: (window as any).__e2e_network_logs || [],
  }))
}

// 页面加载时注入拦截器（两种 Workflow 共用）
async function injectPageMonitors(page: Page): Promise<void> {
  await page.evaluateOnNewDocument(() => {
    (window as any).__e2e_console_logs = []
    ;(window as any).__e2e_network_logs = []

    // 拦截 console.error/warn
    const origError = console.error
    const origWarn = console.warn
    console.error = (...args: any[]) => {
      ;(window as any).__e2e_console_logs.push({ level: 'error', args: String(args), ts: Date.now() })
      origError.apply(console, args)
    }
    console.warn = (...args: any[]) => {
      ;(window as any).__e2e_console_logs.push({ level: 'warn', args: String(args), ts: Date.now() })
      origWarn.apply(console, args)
    }

    // 拦截 fetch
    const origFetch = window.fetch
    window.fetch = async (...args: any[]) => {
      const start = Date.now()
      try {
        const resp = await origFetch(...args)
        ;(window as any).__e2e_network_logs.push({
          method: args[1]?.method || 'GET',
          url: String(args[0]),
          status: resp.status,
          duration: Date.now() - start,
          ts: Date.now(),
        })
        return resp
      } catch (err: any) {
        ;(window as any).__e2e_network_logs.push({
          method: args[1]?.method || 'GET',
          url: String(args[0]),
          status: 0,
          error: err.message,
          duration: Date.now() - start,
          ts: Date.now(),
        })
        throw err
      }
    }

    // 拦截 XHR（同理）
  })
}
```

## 4. 诊断推理引擎（核心）

> 这是本技能的核心。无论 Workflow A 还是 B，AI 发现异常后都按此引擎推理。
> 区别仅在于输出：A → `_diagnosis.md`，B → 对话 + 修复代码 + 重跑。

### 异常检测触发条件

以下任一触发推理：
- 截图显示非预期状态（空白页、loading 不消失、错误页、UI 错乱）
- 浏览器控制台有 error/warn
- HTTP 响应码 4xx/5xx
- 后端日志出现 ERROR/CRITICAL/WARNING
- 页面加载 / 交互超时

### 推理链路

```
发现异常
  │
  ├─ ① 定位时间窗口
  │   异常时刻 → 取前后 10 秒的后端日志区间
  │
  ├─ ② 后端日志
  │   ├─ ERROR？ → 记录 traceback + 文件 + 行号
  │   ├─ WARNING？ → 记录上下文（往往预示根因）
  │   └─ 无异常？ → 进入 ③
  │
  ├─ ③ 网络请求
  │   ├─ 哪个 API 返回非 2xx？ → 记录 URL + status + payload + response
  │   ├─ 哪个 API 耗时 > 5s？ → 超时嫌疑
  │   └─ 无异常？ → 进入 ④
  │
  ├─ ④ 浏览器控制台
  │   ├─ JS 运行时错误？ → 记录文件 + 行号
  │   ├─ 未捕获 Promise rejection？
  │   └─ 资源加载失败？（CSS/JS 404）
  │
  ├─ ⑤ 形成根因假设
  │   综合 ①-④ 的证据 →
  │   "POST /api/auth/register 返回 500 IntegrityError，因为邮箱重复。
  │    前端 services/auth.ts:32 未处理非 2xx，导致 spinner 不消失。"
  │
  └─ ⑥ 输出
       Workflow A → 写入 _diagnosis.md
       Workflow B → 对话输出 + 直接修复代码 + 重跑验证
```

### 禁止行为（两种 Workflow 通用）

```
❌ "auth 模块好像有问题" — 没有证据和根因
❌ 只看截图不查日志就下结论
❌ 只看后端不看前端（或反过来）
❌ 忽略 WARNING 日志
❌ Workflow A 发现异常后不 recordAnomaly 继续跑
❌ Workflow B 修复后不验证
```

## 5. Workflow A 专用：诊断上下文 + 报告生成

```typescript
interface DiagnosisContext {
  module: string
  anomalies: AnomalyEntry[]
  logSnapshots: LogSnapshot[]
  browserContexts: BrowserContextEntry[]
}

interface AnomalyEntry {
  timestamp: number
  screenshotLabel: string
  type: 'blank_page' | 'loading_stuck' | 'error_page' | 'layout_broken' | 'element_missing' | 'timeout'
  description: string
  screenshotPath: string
}

function recordAnomaly(ctx: DiagnosisContext, entry: AnomalyEntry): void {
  ctx.anomalies.push(entry)
}

function generateDiagnosisReport(ctx: DiagnosisContext): string {
  // 对每个 anomaly，运行推理引擎 ①-⑥
  // 按 Workflow A 诊断报告格式输出 MD
  // → screenshots/{module}/_diagnosis.md
}
```

## 6. 模块清理 helper

```typescript
function clearModuleData(module: string): void {
  rmSync(`screenshots/${module}`, { recursive: true, force: true })
  mkdirSync(`screenshots/${module}/_logs`, { recursive: true })
  // 仅 Workflow A 需要
}
```
