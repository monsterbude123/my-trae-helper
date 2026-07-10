# Workflow B — 即时诊断模式

> 适用：用户反馈某个页面/按钮有问题，需要灵敏定位 + 修复 + 验证的快速闭环。
> 共享基础设施见 [infra-shared.md](infra-shared.md)，通用约定见 [conventions.md](conventions.md)。

---

## B.1 触发条件

以下任一即为 Workflow B 触发：
- 用户说 "XX 页面的 YY 按钮点了没反应"
- 用户说 "帮我看看 ZZ 功能为什么一直 loading"
- 用户贴了一张截图说有问题
- 修复某个 bug 后需要立刻验证视觉 + 行为
- 开发中想快速确认某个交互效果

## B.2 即时诊断协议（AI 必须逐步执行）

```
Step 1: 导航到目标页面
  → Playwright: page.goto(url) 或复用已有 browser context
  → 如果是已打开的页面，直接操作，不重新导航

Step 2: 执行触发操作
  → 点击、输入、切换 tab 等用户反馈的具体操作

Step 3: 并行收集三类证据（不串行）
  ├─ 截图:   page.screenshot({ path: `tmp/diag-{timestamp}.png` })
  ├─ 前端:   page.evaluate(() => ({
  │            console: window.__e2e_console_logs || [],
  │            network: window.__e2e_network_logs || []
  │          }))
  └─ 后端:   tail -n 100 backend/logs/app.log | findstr "{关键词}"
      或     curl -s http://localhost:8765/api/debug/logs?tail=100

Step 4: 即时视觉分析
  → vision-audit --file tmp/diag-{timestamp}.png（单张分析）
  → 或 AI 直接读取截图描述视觉状态

Step 5: 关联诊断
  ├─ 截图异常？
  │   ├─ 空白页 → 检查控制台有无 JS 错误 + 后端有无路由 404/500
  │   ├─ loading 不消失 → 检查网络请求有无 pending/500 + 后端有无异常
  │   └─ UI 错乱 → 检查控制台 CSS 加载失败 + 资源 404
  ├─ 控制台有 error？ → 定位 JS 文件 + 行号
  └─ 后端有 ERROR？ → 定位 API + traceback + 行号

Step 6: 输出结论 → 直接修复 → 立即验证
  格式: "根因: {api/代码位置} → {错误类型}。修复: {文件:行号 具体改动}"
  → 改代码
  → 重新执行 Step 1-4 验证修复
```

## B.3 即时诊断的硬约束

```
✅ 必须同时查前端 + 后端日志，不能只看截图
✅ 根因结论必须引用具体日志行 / 代码行号（禁止猜测）
✅ 修复后必须重新导航 + 操作 + 截图为证
✅ 完成标志 = 操作正常 + 截图正常 + 前后端无 ERROR/WARNING
❌ 禁止只说"页面有问题"而没有日志证据
❌ 禁止跳过日志检查直接猜根因 → 改 → 声称修好了
❌ 禁止修了前端不修后端（或反过来），除非确认只有一端有问题
❌ 修复后禁止不验证就声称完成
```

## B.4 完整示例对话

```
用户: "注册页面的提交按钮点了没反应，帮我看看"

AI:
  Step 1: 导航到 http://localhost:5173/auth/register
  Step 2: 填入测试邮箱 test@test.com，点击"注册"
  Step 3: 并行收集 —
    截图: spinner 一直转，没有跳转也没有错误提示
    前端: console.error → "POST /api/auth/register 500"
           network → { method:"POST", url:"/api/auth/register", status:500, body: null }
    后端: 2026-06-24 14:32:15 ERROR auth.service:register:45
           IntegrityError: UNIQUE constraint failed: users.email
           Traceback: File "backend/app/services/auth_service.py", line 45, in register
  Step 4: 视觉 — spinner 未消失，无错误提示
  Step 5: 关联 —
    前端请求 /api/auth/register → 后端返回 500 IntegrityError
    → 前端 services/auth.ts:32 fetch 未处理 500
    → 后端 auth_service.py:45 重复邮箱抛 IntegrityError 但未转为 409
  Step 6: 根因 + 修复 —
    后端: auth_service.py:45 → 捕获 IntegrityError，raise HTTPException(409, "邮箱已注册")
    前端: AuthView.vue:120 → handleSubmit 中处理 409 → 显示"该邮箱已注册"
    → 修改完成
  Step 1-4 重跑: 用 test@test.com 再次注册 → 页面显示"该邮箱已注册" ✅
  Done.
```

## B.5 Workflow B 不需要的东西

```
❌ 不需要 beforeAll / afterAll 仪式
❌ 不需要 clearScreenshots()
❌ 不需要 _diagnosis.md 报告文件
❌ 不需要 _logs/ 目录归档
❌ 不需要 recordAnomaly()
✅ 只需要: 截图tmp → 读日志 → 读控制台 → 关联 → 修复 → 验证
```

## B.6 AI 行为契约

```
✅ 操作后同时收集截图 + 前端日志 + 后端日志
✅ 推理引擎 ①-⑥ 完整走完再下结论
✅ 根因结论引用具体日志行/代码行号
✅ 修复后重新操作 + 截图 + 验证
❌ 只截图就猜根因
❌ 修完不验证
❌ 只说"可能是什么问题"而不进一步确认
```
