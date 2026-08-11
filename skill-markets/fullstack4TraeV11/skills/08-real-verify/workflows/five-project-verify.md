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

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [startup-verification.md](../references/startup-verification.md)
- [visual-evidence.md](../references/visual-evidence.md)
- [blockage-report.md](../references/blockage-report.md)