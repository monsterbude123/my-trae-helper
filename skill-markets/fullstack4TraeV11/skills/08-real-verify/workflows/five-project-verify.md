# Five-Project Verify — Stage 3.5 Real Verify

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

# Step 2: curl 探测
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5173/
# 必须 200

# Step 3: Playwright 截图（主上下文亲自执行）
playwright_navigate url="http://127.0.0.1:5173/"
playwright_screenshot name="verify-default" fullPage=false

# Step 4: 归档截图到 docs/verifications/{change-id}/
mkdir -p docs/verifications/2026-08-11-add-feature
cp /tmp/playwright-screenshot.png docs/verifications/2026-08-11-add-feature/

# Step 5: LS 验证 size
ls -la docs/verifications/2026-08-11-add-feature/
# 必须 ≥ 5KB
```

---

## Tauri 项目工作流

```bash
# Step 1: 启动
cd /path/to/project
pnpm exec tauri dev > /tmp/tauri.log 2>&1 &
sleep 30

# Step 2: 进程存活检查
ps aux | grep tauri | grep -v grep
# 必须有进程

# Step 3: Playwright 连接 WebView
playwright_navigate url="tauri://localhost/"

# Step 4: 主窗口截图
playwright_screenshot name="tauri-main-window"

# Step 5: 归档
```

---

## CLI 项目工作流

```bash
# Step 1: 真实跑一次 end-to-end
./bin/cli --config config.toml --command full-flow

# Step 2: 收集输出
./bin/cli --command full-flow > /tmp/cli-output.txt 2>&1
# 输出片段 ≥ 10 行

# Step 3: 检查退出码
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then echo "✅"; else echo "❌"; fi

# Step 4: 关键产物存在
ls output/
```

---

## Library 项目工作流

```python
# Step 1: 集成测试
pytest tests/integration/test_real_call.py -v

# Step 2: 测试中调用真实 API（非 mock）
def test_real_api():
    result = my_lib.call_real_api(endpoint="...")
    assert result.status == 200

# Step 3: 输出 API 调用证据 + 返回字段
```

---

## Backend 服务工作流

```bash
# Step 1: 启动服务
python -m my_server > /tmp/server.log 2>&1 &
sleep 5

# Step 2: 健康检查
curl -s http://127.0.0.1:8080/health
# 必须返回 {"status": "ok"} + 200

# Step 3: 日志无 ERROR
grep ERROR /tmp/server.log
# 必须 0 行

# Step 4: 关键 API 真实调用
curl -s http://127.0.0.1:8080/api/v1/users/1
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

主上下文执行 5 步时,按下列映射**自动填写** `docs/specs/changes/{id}/.state-card.md`：

| Step | 状态卡字段 | 取值规则 |
|------|-----------|---------|
| Step 1 项目启动验证 | `gate_result.gate` = "real-verify/startup" | step_status: PASS/FAIL |
| | `artifacts[].path` = "screenshots/{name}.png" | exists: true/false(由 visual-content-check.py 实跑决定) |
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