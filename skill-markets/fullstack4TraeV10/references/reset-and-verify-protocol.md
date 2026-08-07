# 主上下文重置与真实验证协议

> 版本: V10.8 (2026-08-05)
> 来源: 实战暴露的腐烂点 + 视觉证据假阳性蒸馏
> V10.3.9: 视觉证据硬门禁三层校验 (PNG magic + bytes + PIL 亮度) + 文件活跃性 7 天
> V10.8: 视觉证据 3 校验 G1/G2/G3 (截图新鲜度 + 渲染 smoke ≠ 设计合规 + 升档证据映射)

## 教训

```
旧模式（错）: 子代理说完成 → 主上下文相信 → 跑 audit 看脚本 → "完成"（未 fresh-run、未真实验证）
新模式（对）: Stage 0 重置 + Stage 1 fresh-run + Stage 2 独立验证 + Stage 1.5 视觉证据 G1/G2/G3
```

## Stage 0 — 重置（任何"完成"判断前必做）

```powershell
# 1. 停掉所有遗留进程（按 PID 精确杀，禁止模糊匹配 Get-Process "chrome"）
Get-NetTCPConnection -LocalPort {app_port} -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Test-NetConnection 127.0.0.1 -Port {app_port} -InformationLevel Quiet → 必须 False
# 2. 清理缓存产物（review-latest.md / state-card / 临时 audit 输出）
# 3. 检查 binary 时间戳（防 release 二进制过期）→ 若 < 今天 → 必须 cargo build --release 重建
Get-Item target/release/{app}.exe | Select-Object LastWriteTime
```

## Stage 1 — Fresh-run 真实验证

```powershell
# 1. 启动应用 + 端口探测
Start-Process -FilePath ".\target\release\{app}.exe" -WorkingDirectory src-tauri
Start-Sleep 5..10
Test-NetConnection 127.0.0.1 -Port {app_port} -InformationLevel Quiet → 必须 True

# 2. 真实 curl 所有声明的端点
$base = "http://127.0.0.1:{app_port}"
foreach ($ep in $contracts_endpoints) {
  $code = (curl -s -o /dev/null -w "%{http_code}" -X $method "$base$path" --max-time 3)
  # 期望 2xx 或业务 4xx；5xx 或 connect failure = 真错
}
```

## Stage 1.5 — 应用启动与视觉验证（V10.3.8 + V10.8）

> 适用于 Tauri / Electron / 任何有桌面 UI 的应用。仅端口 LISTEN + 端点 200 还不够，必须**亲眼看到 UI 渲染**。

```powershell
# 1. 启动 release exe + 验证窗口
Start-Process -FilePath ".\target\release\{app}.exe" -WorkingDirectory src-tauri
Start-Sleep 8
Get-Process -Name "{app}" | Select Id, MainWindowTitle, MainWindowHandle, WorkingSet64
# MainWindowTitle 非空 + MainWindowHandle 非 0 + WorkingSet64 > 0 = 窗口已开

# 2. Chrome headless 截图（关键 3 张：主界面 + 关键 Tab + 异常态）
# 必须带 --user-data-dir=<tmpdir> 隔离启动，结束按 PID 精确杀
```

**判定**：
- ✅ 窗口已开 + 截图能渲染 UI + 关键 Tab 内容可见 → 真实验证通过
- 🛑 MainWindowTitle 为空 / 截图白屏 → "应用在跑"≠"应用可见"，立即报告

## Stage 2 — Audit 校验

```powershell
python "scripts/acceptance-audit.py" --project-root "{project}" --feature {change_id} --strict-artifacts
# 强制: code PASS (cargo test 真实 0 failed) / api PASS 或 N/A / uiux PASS / boundary PASS / drift_detect PASS / artifact_schema PASS
```

## Stage 3 — 独立交叉验证

```
audit 输出 vs 真实 curl 必须一致:
  - audit 5/5 命中 → curl 必须 5/5 200
  - 不一致 = 立即报告（常见原因：binary 过期、测试桩 mock、drift）

仅当以下都成立才能声称"完成":
  ✓ Stage 0 清理完成
  ✓ Stage 1 fresh-run 端点真实 200
  ✓ Stage 1.5 视觉证据 G1/G2/G3 通过（V10.8）
  ✓ Stage 2 audit fresh-run 6 维度 PASS
  ✓ Stage 3 audit 与 curl 一致
```

## V10.3.9 视觉证据门禁（三层校验 + 活跃性）

> 适用范围: 项目含 `src-tauri/tauri.conf.json`（Tauri 桌面应用）。uiux 维度必须含 `docs/verifications/tauri/*.png` 视觉证据。

| 层 | 校验 | 阈值 | 失败动作 |
|---|------|------|---------|
| 1 | PNG magic number | 前 8 字节 == `b'\x89PNG\r\n\x1a\n'` | 🛑 REJECT |
| 2 | 文件大小 | ≥ 5000 bytes | 🛑 REJECT |
| 3 | PIL 平均亮度 | [30, 240]（深色主题合法，软警告） | ⚠️ 仅警告 |
| 4 | 文件活跃性 | 最近 7 天内（168h） | 🛑 REJECT |
| 5 | 视觉证据目录 | `docs/verifications/tauri/*.png` | 🛑 REJECT |

**视觉证据目录约定**:
```
<project-root>/docs/verifications/tauri/
├── YYYY-MM-DD-main.png        # 主界面
├── YYYY-MM-DD-tab-X.png        # 关键 Tab
└── YYYY-MM-DD-error-state.png  # 异常态（如有）
```
文件名必须含**日期 + 意图**，方便追踪证据版本。

**降级路径**: 仅 Plan 阶段显式锁定 uiux N/A → 才允许 `--no-visual` 跳过。降级条件必须写入 plan.md "不适用维度锁定" 段，无锁定记录 → review 阶段拒绝接收降级。

## V10.8 视觉证据 3 校验 G1/G2/G3（NEW）

> 来源: 视觉证据假阳性蒸馏。截图"存在"≠"已比对"；能渲染 ≠ 符合设计；升分必须伴随证据新增。
> 触发: Reviewer 声称 uiux PASS / Completion Report 出现"截图 N 张已生成" / 评分上升但无新增证据 / 任何"SKIPPED"绕过表述。

### G1 — 截图新鲜度

> 旧截图/他人截图/占位图都能让证据链看起来完整。截图"存在"不能证明是本次 Review 期间生成的。

```
Step 1.5a — 时间戳校验
  Get-Item docs/verifications/tauri/*.png | Select Name, LastWriteTime
  → 全部截图 LastWriteTime ≥ Reviewer 启动时间
  → 任一截图早于 Reviewer 启动 → 🛑 证据过期，REJECT

Step 1.5b — 目录新鲜度
  → 目录时间必须晚于 implementer 上一次交付时间
  → 目录不存在 → 🛑 无证据，REJECT

Step 1.5c — 非占位校验
  → 截图文件大小 ≥ 5KB（占位 PNG 通常 < 2KB）
  → 文件数 ≥ 声明的状态数（5 状态 × 3 闭环 = ≥ 8 张）
```

### G2 — 渲染 smoke ≠ 设计合规

> Playwright 截图成功只能证明"页面渲染不报错"，不能证明"页面符合 prototype 设计"。两类证据必须独立存在。

| 证据类型 | 命令 | 证明什么 | 不能证明什么 |
|---------|------|---------|------------|
| 渲染 smoke | `npx playwright test capture-*` | 组件挂载 + 不崩溃 | 布局/颜色/字段符合 prototype |
| 设计合规 | `vision-audit` / 逐元素比对报告 | 元素存在 + 颜色匹配 + 布局对齐 | — |

```
Step 2.5a — 两类证据必须同时存在
  [ ] 渲染 smoke: verifications/tauri/*.png 文件
  [ ] 设计合规: 比对报告（每张截图 vs 对应 prototype 清单）
  → 缺任一 → 🛑 uiux_dimension FAIL

Step 2.5b — 比对报告必须逐元素含量化指标
  - 元素存在率（如 14/15 = 93%）
  - 颜色偏差（hex 对比，如 bg 期望 #0F172A 实际 #4C1D95 → FAIL）
  - 布局坐标（如网格 4 列 vs 实际 2 列 → FAIL）
  → 报告无量化指标 → 🛑 视为未比对，REJECT

Step 2.5c — 禁止等价表述
  "截图已生成" ≠ "已比对"
  "vision-audit 可用" ≠ "vision-audit 已跑"
  "dev server 未启动所以跳过" = 未执行 Visual Gate = FAIL（不是 CONDITIONAL）
```

**反例（V10.8）**:
- 当时做了: V3 reviewer 以"10 PNG 已生成"为 uiux 证据，评分 4.71
- 导致后果: PNG 只是渲染 smoke 产物，从未与 8 份 prototype 比对；Archive 后用户发现 UI 全不符合
- 根因: 只校验了"文件存在"，未校验"文件何时生成 + 是否用于比对"
- 教训: 时间戳 + 目录新鲜度 + 非占位 = 截图的"出生证明"

### G3 — 升档证据映射

> V1→V2→V3 连续升分但 UI 维度证据始终为 0，说明评分机制被"会写报告"的 agent 欺骗。

```
Step 3.5a — 升档证据映射
  V{N} 评分 vs V{N-1} 评分:
    → 每上升 0.5 分，必须对应至少 1 类新增证据:
      代码证据 / API 证据 / 视觉证据 / 文档证据
    → 升分但无新增证据 → 🛑 机械拦截: "升分无证据支撑"

Step 3.5b — 维度证据连续性
  单维度得分跨轮次变化时，该维度的 checklist 判定必须同步变化:
    uiux 3.0 → 4.71 但 checklist 从未从 FAIL 翻转为 PASS
    → 🛑 判定矛盾，REJECT

Step 3.5c — 证据链日志
  每次 Review 完成，scorecard 必须附证据链段:
    V1: uiux FAIL (Visual Gate 未跑)
    V2: uiux FAIL (SKIPPED 不被接受)
    V3: uiux PASS (14/15 元素比对通过 + vision-audit 0 差异)
  → 无轮次证据链 → 🛑 评分不可追溯
```

**反例（V10.8）**:
- 当时做了: V3 总分 4.71 PASS，但 V1 至 V3 的 uiux 维度从未有真实比对证据
- 导致后果: 分数上升只是代码层修修补补积累，UI 从未被验证
- 根因: 评分是 checklist 刚性推导，但 checklist 空转时分数仍虚高；缺"升分↔证据"绑定
- 教训: 分数上升必须能指向"这次多了什么证据"，否则就是流程表演

### 主上下文强制动作 + G1/G2/G3 检查清单

```
Reviewer 返回 uiux 证据后，主上下文:
  1. 抽 1 张截图亲自 Read（不靠 agent 描述，AI 描述 ≠ 真实像素）
  2. 抽 1 项比对报告量化指标，与实际截图核对
  3. 与上一轮 scorecard 对比，确认升分有新增证据
  任一不通过 → 🛑 退回 reviewer，不计入完成

G1/G2/G3 检查清单:
[ ] 截图时间戳 ≥ Reviewer 启动时间 + 目录新鲜 + 非占位（≥5KB + ≥8 张）
[ ] 渲染 smoke 与设计合规两类证据独立存在
[ ] 比对报告含量化指标（元素存在率/颜色/布局）
[ ] 升分对应新增证据（升档映射成立）
[ ] 主上下文已亲自 Read 抽检 ≥ 1 张截图
```

## 腐烂点案例（实战记录，精简）

| # | 现象 | 根因 | 修复 |
|---|------|------|------|
| 1 | audit 6/6 PASS 但应用未启动 | audit 依赖历史 binary 残留 / 子代理自报 | Stage 0-3 强制 fresh-run |
| 2 | 5 端点 404 | release 二进制过期，不含新路由 | Stage 0 检查 binary 时间戳 |
| 3 | cargo build --release 失败 | 源码 mod.rs 缺失 | implementer 修复源码 |
| 4 | 后端跑着、端口 LISTEN、audit PASS，但用户说"看不见应用" | 验收只看命令行证据，没启动桌面应用 + 视觉截图 | Stage 1.5 必须真实启动 + Chrome headless 截图 3 张 |
| 5 | 每做完一步停下来等用户确认，4 轮才闭环 | 偷懒把责任推回用户 | 委派时一次性给全任务清单 |
| 6 | Chrome 进程 0 个时尝试查/启进程 | 看到异常就动手，没判断是否"真的异常" | Chrome 0 个 = 用户可能已重启，不查不操作 |
| 7 | headless chrome `Get-Process "chrome" | Stop-Process` 误杀其他 chrome | 模糊匹配 | 必须带 `--user-data-dir=<tmpdir>` 隔离，按 PID 精确杀 |
| 8 | PowerShell 中文正则字面量乱码，audit 计数全为 0 | PowerShell 5.x 默认 ANSI，UTF-8 中文字面量被破坏 | 用 unicode code point 拼接，或优先用 Python 写 audit |

## 反虚假完成清单

```
❌ 禁止的"完成"理由:
  - acceptance-audit 脚本输出 PASS
  - 子代理 Completion Report 说 PASS
  - 代码文件存在 / cargo test 通过 / 之前一轮跑通过

✅ 必须的真实证据:
  - Test-NetConnection 端口 True（fresh-run）
  - curl 真实 HTTP 状态码（fresh-run）
  - 进程 PID LISTEN（fresh-run）
  - acceptance-audit fresh-run 6 维度 PASS
  - audit 输出 vs 真实响应交叉验算一致
  - 视觉证据 G1/G2/G3 通过（V10.8）
```

## 适用场景

任何验收前必走 Stage 0-3 + Stage 1.5：归档 / Accept / 提交前 / 用户质疑"是否真的做完"。

## 与 agent-机械验证.md 的关系

| 维度 | agent-机械验证.md | 本协议 |
|------|------------------|--------|
| 范围 | 委派 agent 返回结果（artifacts 字段值校验） | 主上下文自主验证（应用真实可用） |
| 启动器 | agent 返回后立即 | 任何"完成"判断前 |

## §Stage 1.5 Runtime Gate（V10.8 NEW — 回流自 acceptance-runtime-gate）

> 命题：静态门禁全绿 ≠ 功能可用。G1/G2/G3 是视觉层；本段补**执行层**（启动+点击+计分卡对比）。
> 触发：Agent 声称"功能完成" / 计分卡残留"补审"字样 / workbench 黑屏 / 按钮报错。

### 三铁律

```
铁律 1: 静态门禁全绿 ≠ 功能可用。必须启动应用 + 点击关键按钮。
铁律 2: 计分卡是历史快照。Review 阶段必须重新运行门禁，对比实际值。
铁律 3: 补审完成 = 必须清理历史快照噪声（"补审" → "Review"，删除 commit 引用）。
```

### 启动应用端到端验证（5 步）

```
Step 1 — 启动应用（dev 或 release 模式，按项目）
Step 2 — 等待就绪（端口 LISTEN + 首屏 HTML 返回）
Step 3 — 浏览器访问 + curl 端点（≥1 个核心端点真实 2xx）
Step 4 — 点击关键路径（≥3 个核心功能按钮，无 uncaught error）
Step 5 — 检查控制台（无 404/500/红色错误）+ 截图留证
```

### 计分卡 vs 实际对比

```
Review 阶段声称 G1/G3/G4 通过 → 必须重新执行并对比:
  npx tsc --noEmit → 实际错误数 vs 计分卡
  cargo test → 实际通过率 vs 计分卡
  npx vitest run → 实际 pass 数 vs 计分卡
  → 计分卡记录 ≠ 实际值 → 更新计分卡 + 标注"历史快照已同步"
```

### 历史快照噪声清理

| 噪声类型 | 示例 | 处理 |
|---------|------|------|
| 补审字样 | "补审通过" / "补审产出" | → "Review 通过" / "Review 产出" |
| commit 引用 | "（代码已存在，commit xxx）" | 删除整个括号内容 |
| 合并历史表 | "## 合并历史" 章节 | 删除整个章节 |

清理后验证：`grep -r "补审" docs/specs/` 必须返回 0 行。

### 反例

```
反例（静态门禁假阳性）:
  - 当时做了: tsc/cargo test/vitest 全绿 → 自评 100 分 → 声称 PASS
  - 导致后果: 用户启动发现 workbench 黑屏 + 点击按钮报错
  - 根因: 验收流程缺实际运行验证
  - 教训: 编译通过 ≠ 功能可用，必须真机点击 ≥3 个核心按钮

反例（历史快照噪声残留）:
  - 计分卡残留"补审（代码已存在，commit xxx）"
  - 违反"禁止引用历史验收状态"，下次验收误判
  - 教训: 补审完成 = 必须清理为"Review 通过"
```

> 来源: example/test-fullstack-init 会话蒸馏，V10.8 通用化回流（去项目特定端口/命令，保留通用执行层验证协议）
