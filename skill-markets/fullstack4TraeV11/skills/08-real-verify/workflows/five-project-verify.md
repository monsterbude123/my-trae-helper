# Five-Project Verify — Stage 3.5 Real Verify

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 3.5 Real Verify 必走。5 类项目启动验证协议。

---

## 5 类项目验证矩阵

| 类型 | 启动命令 | 验证命令 | 可见产物 |
|------|---------|---------|---------|
| **Web** | `npm run dev` / `pnpm dev` | `curl 200 + Playwright 截图` | PNG ≥5KB |
| **Tauri** | `cargo tauri dev` | `ps + 主窗口截图` | PNG ≥5KB |
| **CLI** | `bin/cli --command` | `exit 0 + 输出 ≥10 行` | log file |
| **Library** | 集成测试 | `pytest integration -v` | PASS 输出 |
| **Backend** | `python -m server` | `curl /health + 日志无 ERROR` | log file |

---

## Web 项目工作流

```bash
# Step 1: 启动 dev server
cd /path/to/project
npm run dev > /tmp/dev.log 2>&1 &
sleep 10

# Step 2: curl 探测（端口与 references/startup-verification.md L17 一致 = 5173）
<!-- scan-whitelist -->STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5173/) || { echo "❌ Web Step 2 FAIL: curl 命令失败"; exit 1; }<!-- /scan-whitelist -->
[ "$STATUS" = "200" ] || { echo "❌ Web Step 2 FAIL: curl 返回 $STATUS（非 200）"; exit 1; }
echo "✅ Web Step 2 PASS: curl 200"

# Step 3: Playwright 截图（主上下文亲自执行，V10-battle-tested.md 蒸馏 2 改进路径：直接指定归档路径）
<!-- scan-whitelist -->playwright_navigate url="http://127.0.0.1:5173/" || { echo "❌ Web Step 3 FAIL: playwright_navigate 失败"; exit 1; }<!-- /scan-whitelist -->
playwright_screenshot name="verify-default" fullPage=false path="docs/verifications/2026-08-11-add-feature/verify-default.png" || { echo "❌ Web Step 3 FAIL: playwright_screenshot 失败"; exit 1; }
echo "✅ Web Step 3 PASS: screenshot 已归档"

# Step 4: 归档截图（跨平台兼容：MCP 直接写入归档目录，避 Downloads/ 陷阱）
mkdir -p docs/verifications/2026-08-11-add-feature || { echo "❌ Web Step 4 FAIL: mkdir 失败"; exit 1; }
# MCP 截图已存到指定路径；若 MCP 不支持 path 参数，回退用跨平台 SCREENSHOT_PATH：
# Windows: %USERPROFILE%\Downloads\  |  macOS/Linux: $HOME/Downloads/
if [ -n "$SCREENSHOT_PATH" ]; then
  cp "$SCREENSHOT_PATH/verify-default.png" docs/verifications/2026-08-11-add-feature/ || { echo "❌ Web Step 4 FAIL: cp 失败"; exit 1; }
fi
echo "✅ Web Step 4 PASS: 归档完成"

# Step 5: LS 验证 size（必须 ≥ 5KB）
SCREENSHOT_SIZE=$(stat -c%s "docs/verifications/2026-08-11-add-feature/verify-default.png" 2>/dev/null || stat -f%z "docs/verifications/2026-08-11-add-feature/verify-default.png" 2>/dev/null || echo 0)
[ "$SCREENSHOT_SIZE" -ge 5000 ] || { echo "❌ Web Step 5 FAIL: 截图 ${SCREENSHOT_SIZE}B < 5KB"; exit 1; }
echo "✅ Web Step 5 PASS: 截图 ${SCREENSHOT_SIZE}B ≥ 5KB"

# 反例: anti-patterns/01-startup-equals-done.md（看到进程即通过）+ 03-skip-screenshot.md（跳过截图）
```

---

## Tauri 项目工作流

```bash
# Step 1: 启动
cd /path/to/project
pnpm exec tauri dev > /tmp/tauri.log 2>&1 &
sleep 30

# Step 2: 进程存活检查（必须有进程）
ps aux | grep tauri | grep -v grep > /tmp/tauri-procs.txt
[ -s /tmp/tauri-procs.txt ] || { echo "❌ Tauri Step 2 FAIL: tauri 进程未存活"; exit 1; }
echo "✅ Tauri Step 2 PASS: tauri 进程存活"

# Step 3: Playwright 连接 WebView
playwright_navigate url="tauri://localhost/" || { echo "❌ Tauri Step 3 FAIL: playwright_navigate 失败"; exit 1; }
echo "✅ Tauri Step 3 PASS: WebView 连接"

# Step 4: 主窗口截图（V10-battle-tested.md 蒸馏 2 改进路径：直接归档）
mkdir -p docs/verifications/2026-08-11-add-feature || { echo "❌ Tauri Step 4 FAIL: mkdir 失败"; exit 1; }
playwright_screenshot name="tauri-main-window" fullPage=false path="docs/verifications/2026-08-11-add-feature/tauri-main-window.png" || { echo "❌ Tauri Step 4 FAIL: playwright_screenshot 失败"; exit 1; }
echo "✅ Tauri Step 4 PASS: 主窗口截图已归档"

# Step 5: 归档验证 size ≥ 5KB
SCREENSHOT_SIZE=$(stat -c%s "docs/verifications/2026-08-11-add-feature/tauri-main-window.png" 2>/dev/null || stat -f%z "docs/verifications/2026-08-11-add-feature/tauri-main-window.png" 2>/dev/null || echo 0)
[ "$SCREENSHOT_SIZE" -ge 5000 ] || { echo "❌ Tauri Step 5 FAIL: 截图 ${SCREENSHOT_SIZE}B < 5KB"; exit 1; }
echo "✅ Tauri Step 5 PASS: 截图 ${SCREENSHOT_SIZE}B ≥ 5KB"

# 反例: anti-patterns/01-startup-equals-done.md（看到进程即通过）
```

---

## CLI 项目工作流

```bash
# Step 1: 真实跑一次 end-to-end
./bin/cli --config config.toml --command full-flow > /tmp/cli-output.txt 2>&1
EXIT_CODE=$?
[ $EXIT_CODE -eq 0 ] || { echo "❌ CLI Step 1 FAIL: 退出码 $EXIT_CODE（非 0）"; exit 1; }
echo "✅ CLI Step 1 PASS: 退出码 0"

# Step 2: 收集输出 + 校验 ≥ 10 行
./bin/cli --command full-flow > /tmp/cli-output.txt 2>&1 || { echo "❌ CLI Step 2 FAIL: 命令执行失败"; exit 1; }
OUTPUT_LINES=$(wc -l < /tmp/cli-output.txt)
[ "$OUTPUT_LINES" -ge 10 ] || { echo "❌ CLI Step 2 FAIL: 输出 $OUTPUT_LINES 行（< 10）"; exit 1; }
echo "✅ CLI Step 2 PASS: 输出 $OUTPUT_LINES 行 ≥ 10"

# Step 3: 检查退出码（冗余防御，双重确认）
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then echo "✅ 退出码 0"; else echo "❌ 退出码 $EXIT_CODE"; fi

# Step 4: 关键产物存在（必须非空）
ls output/ > /dev/null 2>&1 || { echo "❌ CLI Step 4 FAIL: output/ 不存在"; exit 1; }
OUTPUT_COUNT=$(ls output/ | wc -l)
[ "$OUTPUT_COUNT" -gt 0 ] || { echo "❌ CLI Step 4 FAIL: output/ 为空"; exit 1; }
echo "✅ CLI Step 4 PASS: output/ 含 $OUTPUT_COUNT 个产物"

# 反例: anti-patterns/02-container-not-started.md（容器未启声称迁移成功）
```

---

## Library 项目工作流

```python
# Step 1: 集成测试（必须真调用 + ≥90% 覆盖率）
pytest tests/integration/test_real_call.py -v > /tmp/lib-test.log 2>&1 || { echo "❌ Library Step 1 FAIL: pytest 失败"; exit 1; }
TEST_EXIT=$?
[ $TEST_EXIT -eq 0 ] || { echo "❌ Library Step 1 FAIL: 退出码 $TEST_EXIT"; exit 1; }
echo "✅ Library Step 1 PASS: pytest 全 PASS"

# Step 2: 测试中调用真实 API（非 mock，状态断言）
def test_real_api():
    result = my_lib.call_real_api(endpoint="...")
    assert result.status == 200, f"API 返回 {result.status}（非 200）"

# Step 3: 收集 API 调用证据（test_real_api 必含 file:line 调用点 + 返回字段）
grep -A2 "call_real_api" /tmp/lib-test.log > /tmp/lib-evidence.txt || { echo "❌ Library Step 3 FAIL: 找不到 API 调用证据"; exit 1; }
[ -s /tmp/lib-evidence.txt ] || { echo "❌ Library Step 3 FAIL: API 调用证据为空"; exit 1; }
echo "✅ Library Step 3 PASS: API 调用证据已归档 /tmp/lib-evidence.txt"

# 反例: anti-patterns/01-startup-equals-done.md（PASS 自评无证据）
```

---

## Backend 服务工作流

```bash
# Step 1: 启动服务
python -m my_server > /tmp/server.log 2>&1 &
sleep 5

# Step 2: 健康检查（必须返回 {"status": "ok"} + 200）
<!-- scan-whitelist -->HEALTH=$(curl -s -w "\n%{http_code}" http://127.0.0.1:8080/health) || { echo "❌ Backend Step 2 FAIL: curl 失败"; exit 1; }<!-- /scan-whitelist -->
HEALTH_STATUS=$(echo "$HEALTH" | tail -1)
HEALTH_BODY=$(echo "$HEALTH" | head -n -1)
[ "$HEALTH_STATUS" = "200" ] || { echo "❌ Backend Step 2 FAIL: /health 返回 $HEALTH_STATUS（非 200）"; exit 1; }
echo "$HEALTH_BODY" | grep -q '"status": "ok"' || { echo "❌ Backend Step 2 FAIL: /health body 不含 status:ok"; exit 1; }
echo "✅ Backend Step 2 PASS: /health 200 + status:ok"

# Step 3: 日志无 ERROR（必须 0 行）
ERROR_COUNT=$(grep -c "ERROR" /tmp/server.log 2>/dev/null || echo 0)
[ "$ERROR_COUNT" -eq 0 ] || { echo "❌ Backend Step 3 FAIL: 日志含 $ERROR_COUNT 行 ERROR"; exit 1; }
echo "✅ Backend Step 3 PASS: 日志 0 行 ERROR"

# Step 4: 关键 API 真实调用（必须 200）
<!-- scan-whitelist -->API_STATUS=$(curl -s -o /tmp/api-response.txt -w "%{http_code}" http://127.0.0.1:8080/api/v1/users/1) || { echo "❌ Backend Step 4 FAIL: curl 失败"; exit 1; }<!-- /scan-whitelist -->
[ "$API_STATUS" = "200" ] || { echo "❌ Backend Step 4 FAIL: API 返回 $API_STATUS（非 200）"; exit 1; }
echo "✅ Backend Step 4 PASS: API 200 + 响应归档 /tmp/api-response.txt"

# 反例: anti-patterns/02-container-not-started.md（容器未启声称迁移成功）
```

---

## 阻塞处理（Article XV）

任一 FAIL → 5 字段阻塞报告 + 状态卡 health = 🔴 blocked。

```yaml
blocker:
  type: "env_dependency" | "test_fail" | "type_error" | "startup_fail" | "other"
  description: "{具体错误信息}"
  attempted_solution: "{已尝试方案}"
  time_consumed_minutes: N
  attempt_count: N
```

### 阻塞升级路径（V11.2 NEW — 蒸馏自 08-real-verify 自检报告）

`attempt_count ≥ 3` 仍未解决 → 必走升级路径,禁止主上下文硬扛：

| 升级层级 | 触发条件 | 动作 |
|---------|---------|------|
| L1 自助修复 | attempt_count 1-2 | 主上下文 + sub-agent 继续修 |
| L2 主上下文决策 | attempt_count = 3 | **必 AskUserQuestion** 三选项：① 接受风险(降级/PASS 豁免) ② 等待修复(暂停 stage) ③ 显式豁免(标 acceptable_risk,记录决策理由) |
| L3 用户审批 | attempt_count ≥ 5 或用户主动升级 | 主上下文汇报 + 用户确认是否继续 / 回滚 / 改方向 |

**禁止**:attempt_count ≥ 3 后不升级、继续硬扛 → 必触发 Article XV Obstacle Honesty 反例。

详见 [references/blockage-report.md §升级路径](../references/blockage-report.md)。

## Step → 状态卡字段映射表（V11.2 NEW — 蒸馏自 08-real-verify 自检报告）

> **§5.8 主上下文唯一改声明（V11.2.1 NEW — state-card-protocol.md §5.8 同步升级）**：
> 状态卡 5 字段（`stage_status` / `current_stage` / `gate_result.status` / `health` / `next_stage.id`）**只能由主上下文亲自 Edit**，子代理禁止直接写入。
> 子代理只能在 Completion Report 中"建议"状态变更，主上下文亲自 Edit。
> 本表是主上下文 Edit 的参考模板，**不是子代理直接写的清单**。
> 详见 [references/state-card-protocol.md §5.8](../../references/state-card-protocol.md)。

主上下文执行 5 步时,按下列映射**亲自 Edit** `docs/specs/changes/{id}/.state-card.md`：

| Step | 状态卡字段 | 取值规则 |
|------|-----------|---------|
| Step 1 项目启动验证 | `gate_result.gate` = "real-verify/startup" | status: PASS/FAIL（state-card-protocol §2.1 用 `status`，非 `step_status`） |
| | `artifacts[].path` = "docs/verifications/{change-id}/{name}.png"（与归档路径对齐） | exists: true/false(由 visual-content-check.py 实跑决定) |
| Step 2 类型/Lint/测试 | `gate_result.gate` = "real-verify/quality" | PASS 需 ≥90% 覆盖率 + 0 lint + 0 type error |
| Step 3 视觉证据(PIL 3 层校验) | `artifacts[].evidence` = "visual-content-check.py PASS" | 见 [references/visual-evidence.md](../references/visual-evidence.md) |
| Step 4 契约/产物对照 | `gate_result.gate` = "real-verify/contract-drift" | FAIL 时 `health = 🔴 blocked` + `next_stage = blocked` |
| Step 5 全 PASS | `stage_status` = "completed", `stage_ended_at` = ISO 8601 | `next_stage = "4/review"` |
| 任何 FAIL | `health = 🔴 blocked` | 立即按阻塞升级路径走 |

完整字段定义见 [references/state-card-protocol.md §二](../../references/state-card-protocol.md)。

## 5 工作流 × 4 维度总览表（V11.2 NEW — 蒸馏自 08-real-verify 自检报告）

| 项目类型 | 输入物 | 输出物 | 失败兜底 | 验证手段 |
|---------|--------|--------|---------|---------|
| **Web** | `package.json` 启动脚本 | dev server 200 + 首页截图 ≥5KB | 进程未启动 → 检查端口占用 + 重启 3 次 | `curl %{http_code}` + playwright_screenshot + PIL 3 层 |
| **Tauri** | `src-tauri` + `package.json` | cargo build OK + tauri dev 截图 | cargo 编译错误 → `cargo clean` 重试 | `ps aux \| grep tauri` + playwright_screenshot |
| **CLI** | `bin/` 或 `dist/` 可执行文件 | end-to-end run 输出非空 + 退出码 0 | 二进制缺失 → `cargo build --release` 或 `pnpm build` | 直接执行 + 退出码断言 |
| **Library** | `lib/` 或 `dist/lib` + 测试 | 单元测试全 PASS + 覆盖率 ≥90% | 测试失败 → 看失败用例输出 | `pnpm test --run --coverage` 或 `cargo test --coverage` |
| **Backend** | `src/server.*` + 启动脚本 | 端口 200 + 关键 endpoint 健康检查 | 端口未就绪 → 看日志 + 重启 | `curl %{http_code}` + 日志 tail |

> 注: 5 项目类型命令在 [§1-§5 各小节](../workflows/five-project-verify.md)详写;本表只标"4 维度",主上下文按表判读。

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [startup-verification.md](../references/startup-verification.md)
- [visual-evidence.md](../references/visual-evidence.md)
- [blockage-report.md](../references/blockage-report.md)