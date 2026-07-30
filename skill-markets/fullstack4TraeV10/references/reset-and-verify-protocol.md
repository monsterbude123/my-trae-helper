# 主上下文重置与真实验收协议

> 版本: V10.3.9 (2026-07-29)
> 来源: AIGCMediaDesktop 实战暴露的腐烂点
> V10.3.9 升级: 视觉证据硬门禁三层校验 (PNG magic + bytes + PIL 亮度) + 文件活跃性 7 天

## 教训

```
旧模式（错）:
  子代理说完成 → 主上下文相信 → 跑 audit 看脚本 → "完成"
  ❌ 跨轮次复用记忆、未 fresh-run、未真实验证应用
  
新模式（对）:
  Stage 0 重置 + Stage 1 fresh-run + Stage 2 独立验证
```

## Stage 0 — 重置（任何"完成"判断前必做）

```powershell
# 1. 停掉所有遗留进程
Get-NetTCPConnection -LocalPort {app_port} -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Test-NetConnection 127.0.0.1 -Port {app_port} -InformationLevel Quiet → 必须 False

# 2. 清理缓存产物
# - review-latest.md / state-card / 临时 audit 输出
# - 这些产物可能基于虚假 audit 通过，不能复用

# 3. 检查 binary 时间戳（防 release 二进制过期）
Get-Item target/release/{app}.exe | Select-Object LastWriteTime
# → 若 < 今天 → 必须 cargo build --release 重建
```

## Stage 1 — Fresh-run 真实验证

```powershell
# 1. 启动应用（release binary 或 cargo run）
Start-Process -FilePath ".\target\release\{app}.exe" -WorkingDirectory src-tauri
Start-Sleep 5..10

# 2. 端口探测
Test-NetConnection 127.0.0.1 -Port {app_port} -InformationLevel Quiet → 必须 True

# 3. 真实 curl 所有声明的端点
$base = "http://127.0.0.1:{app_port}"
foreach ($ep in $contracts_endpoints) {
  $code = (curl -s -o /dev/null -w "%{http_code}" -X $method "$base$path" --max-time 3)
  # 期望 2xx (200/201) 或业务 4xx (400/404 for not-found 资源)
  # 期望不出现 5xx (500+ 表示真错) 或 connect failure
}
```

## Stage 1.5 — 应用启动与视觉验证（V10.3.8 新增）

> 适用于 Tauri / Electron / 任何有桌面 UI 的应用。仅端口 LISTEN + 端点 200 还不够，必须**亲眼看到 UI 渲染**。

```powershell
# 1. 启动 Tauri release exe（不是 vite 后端）
Start-Process -FilePath ".\target\release\{app}.exe" -WorkingDirectory src-tauri
Start-Sleep 8

# 2. 验证窗口（多路）
Get-Process -Name "{app}" | Select Id, MainWindowTitle, MainWindowHandle, WorkingSet64
# MainWindowTitle 非空 = 窗口已开
# MainWindowHandle 非 0 = 窗口句柄存在
# WorkingSet64 > 0 = 进程占用内存

# 3. Chrome headless 截图（关键 3 张）
# 因 RDP / headless 限制无法直接截桌面，用 Chrome headless 渲染 SPA
# 截图: 主界面 + 关键 Tab + 异常态
```

**判定**：
- ✅ 窗口已开 + 截图能渲染 UI + 关键 Tab 内容可见 → 真实验证通过
- 🛑 MainWindowTitle 为空 / 截图白屏 → "应用在跑"≠"应用可见"，立即报告

## Stage 2 — Audit 校验

```powershell
# 跑 acceptance-audit fresh-run（不是看历史输出）
python "D:\workspace\my-trae-helper\skill-markets\fullstack4TraeV10\scripts\acceptance-audit.py" `
  --project-root "D:\workspace\ai-dev\{project}" `
  --feature {change_id} `
  --strict-artifacts

# 强制要求:
# - code PASS (cargo test 真实 0 failed)
# - api PASS (5/5 端点命中) 或 N/A (纯前端)
# - uiux PASS (190 测试文件)
# - boundary PASS (E2E ≥ 88%)
# - drift_detect PASS (contracts vs 实际 import)
# - artifact_schema PASS (6 件标准件)
```

## Stage 3 — 独立交叉验证

```
audit 输出 vs 真实 curl 必须一致:
  - audit 5/5 命中 → curl 必须 5/5 200
  - audit 5/5 N/A → 无需 curl
  - 不一致 = 立即报告（常见原因：binary 过期、测试桩 mock、drift）

仅当以下都成立才能声称"完成":
  ✓ Stage 0 清理完成
  ✓ Stage 1 fresh-run 端点真实 200
  ✓ Stage 2 audit fresh-run 6 维度 PASS
  ✓ Stage 3 audit 与 curl 一致
```

## 腐烂点案例（实战记录）

### 案例 1: 虚假 audit（2026-07-28）
- 现象: acceptance-audit 6/6 PASS，但应用未启动
- 根因: audit 依赖历史 binary 残留 / 子代理自报
- 修复: Stage 0-3 强制 fresh-run

### 案例 2: release binary 过期（2026-07-28）
- 现象: `/api/v1/diagnostics/*` 5 端点 404
- 根因: release 二进制 2026-07-15 编译，不含 2026-07-26 后路由
- 修复: Stage 0 必须检查 binary 时间戳

### 案例 3: 源码 mod.rs 缺失（2026-07-28 重编译尝试）
- 现象: `cargo build --release` 失败
- 根因: `src/contracts/module.rs` 存在但 `src/contracts/mod.rs` 缺失（09-models 推进时引入）
- 修复: implementer agent 修复源码（verifier 不可独立解决，必须升级 implementer）

### 案例 4: 命令行证据 ≠ 应用可见（2026-07-29）
- 现象: 后端进程跑着、端口 LISTEN、audit PASS、commit 落地 — 但用户说"看不见应用"
- 根因: 验收只看命令行证据，没启动 Tauri 桌面应用 + 视觉截图
- 修复: Stage 1.5 必须真实启动 Tauri release exe + Chrome headless 截图 3 张（主界面 + 关键 Tab + 异常态）
- 教训: "进程在跑 ≠ 应用在跑 ≠ 用户能看到应用"

### 案例 5: 碎片化反馈循环（2026-07-29）
- 现象: 每做完一步停下来等用户确认，再做下一步 — 4 轮才闭环
- 根因: 偷懒把责任推回用户
- 修复: 委派时一次性给全任务清单，不要等"是否继续"

### 案例 6: Chrome 进程 0 个时勿操作（2026-07-29）
- 现象: 探测到 Chrome 进程 0 个，尝试查/启进程
- 根因: 看到异常就动手，没判断是不是"真的异常"
- 修复: Chrome 进程 0 个 = 用户可能已重启/未开，不查不操作，避免触发更多进程副作用

### 案例 7: headless chrome 未隔离（2026-07-29）
- 现象: verifier 启动的 headless chrome 用完后用 `Get-Process "chrome" | Stop-Process` 模糊匹配 → 误杀其他 chrome 进程
- 修复: 启动临时 headless chrome **必须**带 `--user-data-dir=<tmpdir>` 隔离，结束按 PID 精确杀

### 案例 8: V10 验收脚本 uiux 维度升级前后对比（2026-07-29）

**升级前（V10.3.8）**: 仅校验 `bytes ≥ 5000`
```python
if size < 5000:
    return ("FAIL", "疑似空白页，必须重截")
```
- ❌ 0 byte 伪 PNG 通过 magic 检查但不通过字节检查
- ❌ 全黑截图（avg_lum < 30）通过字节检查但视觉无效
- ❌ 7 天前的过期截图通过字节检查但无活跃性

**升级后（V10.3.9）**: 三层校验 + 活跃性
```python
# 1. PNG magic number (前 8 字节)
if header != b'\x89PNG\r\n\x1a\n':
    return ("FAIL", "不是真实 PNG")

# 2. 文件大小
if size < 5000:
    return ("FAIL", "疑似空白页")

# 3. 活跃性（最近 7 天）
if age_hours > 168:
    return ("FAIL", "视觉证据过期，必须重截")

# 4. PIL 像素亮度 (软警告, 深色主题合法)
if avg_lum < 30:
    lum_warn = "⚠️ 深色主题 (合法)"
elif avg_lum > 240:
    lum_warn = "⚠️ 过亮 (可能白屏)"
```

**对比示例**（AIGCMediaDesktop `2026-07-29-fix-attempt.png`）:
- 16089 bytes → V10.3.8 PASS（仅看字节）
- PNG magic ✅ + 16089 bytes + 亮度 16.2 (深色主题警告) + 唯一色 38 → **V10.3.9 PASS**（软警告但通过）

**视觉证据目录约定** (V10.3.9 新增):
```
<project-root>/docs/verifications/tauri/
├── YYYY-MM-DD-main.png        # 主界面
├── YYYY-MM-DD-tab-X.png        # 关键 Tab
└── YYYY-MM-DD-error-state.png  # 异常态（如有）
```
文件名必须含**日期 + 意图**，方便追踪证据版本。

**降级路径** (V10.3.9 强化):
- 仅 Plan 阶段显式锁定 uiux N/A → 才允许 `--no-visual` 跳过
- 降级条件必须写入 plan.md "不适用维度锁定" 段
- 无锁定记录 → review 阶段拒绝接收降级

### 案例 9: 中文正则字面量在 PowerShell 脚本中乱码（2026-07-29）

**现象**：编写 audit 脚本扫描 spec.md 中的中文模糊词（可能/大概/似乎/适当/等等），用字面量写正则：

```powershell
$content = Get-Content $spec -Raw
$vagueCount = ([regex]::Matches($content, "可能|大概|似乎|适当|等等")).Count
```

→ 运行后计数全为 0（误判通过），或控制台输出乱码。

**根因**：
1. PowerShell 5.x 默认 ANSI 编码，UTF-8 中文字面量被破坏为 mojibake
2. 脚本文件即使以 UTF-8 保存，运行时也按 ANSI 解析（除非带 BOM）
3. `[regex]::Matches` 对损坏的字节序列返回 0 匹配

**正确做法**：用 unicode code point 拼接，绕开编码问题：

```powershell
$vaguePatterns = @(
    ([char]0x53EF + [char]0x80FD),    # 可能
    ([char]0x5927 + [char]0x6982),    # 大概
    ([char]0x4F3C + [char]0x4E4E),    # 似乎
    ([char]0x9002 + [char]0x5F53),    # 适当
    ([char]0x7B49 + [char]0x7B49)     # 等等
)
$vagueCount = 0
foreach ($p in $vaguePatterns) {
    $c = ([regex]::Matches($content, [regex]::Escape($p))).Count
    if ($c -gt 0) { $vagueCount += $c }
}
```

**替代方案**：脚本顶部强制 UTF-8：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```
但这个只能保证控制台输出正确，**字面量正则解析仍会失败**。

**教训**：
- PowerShell 审计脚本中**禁止**使用中文正则字面量
- 优先用 code point 拼接（最稳）
- 或在 audit 脚本顶部加 `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`（部分有效）
- Python 脚本无此问题（默认 UTF-8），如可能优先用 Python 写 audit

## 反虚假完成清单

```
❌ 禁止的"完成"理由:
  - acceptance-audit 脚本输出 PASS
  - 子代理 Completion Report 说 PASS
  - 代码文件存在
  - cargo test 通过
  - 之前一轮跑通过

✅ 必须的真实证据:
  - Test-NetConnection 端口 True（fresh-run）
  - curl 真实 HTTP 状态码（fresh-run）
  - 进程 PID LISTEN（fresh-run）
  - acceptance-audit fresh-run 6 维度 PASS
  - audit 输出 vs 真实响应交叉验算一致
```

## 适用场景

任何验收前必走 Stage 0-3：
- 归档（archived phase gate）
- Accept 阶段
- 提交前（pre-commit gate）
- 用户质疑"是否真的做完"

## 与 agent-机械验证.md 的关系

| 维度 | agent-机械验证.md | 本协议 |
|------|------------------|--------|
| 范围 | 委派 agent 返回结果 | 主上下文自主验证 |
| 焦点 | artifacts 字段值校验 | 应用真实可用 |
| 启动器 | agent 返回后立即 | 任何"完成"判断前 |
| 必做性 | V10 硬门禁 | 用户要求的主上下文保护 |