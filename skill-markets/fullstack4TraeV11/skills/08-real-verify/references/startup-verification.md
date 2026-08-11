# 5 类项目启动验证（Startup Verification）

> Stage 3.5 Real Verify Step 3 必走。V10 §0.10 NEW 5 类项目分类。

---

## Web 项目

```bash
# 1. 启动 dev server
pnpm exec vite --port 1420 --host 127.0.0.1 &
sleep 5

# 2. curl 探测
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:1420/
# 必须 200

# 3. Playwright 截图（主上下文亲自执行）
playwright_navigate(url="http://127.0.0.1:1420/")
playwright_resize(width=1440, height=900)
playwright_screenshot(name="evidence-default", fullPage=false)

# 4. 归档到 docs/verifications/{change}/
# 5. LS 验证 size > 5KB
```

## Tauri 项目

```bash
# 1. tauri dev
pnpm exec tauri dev &
sleep 30

# 2. 进程存活检查
ps aux | grep tauri | grep -v grep

# 3. Playwright 连接 Tauri WebView
playwright_navigate(url="tauri://localhost/")

# 4. 主窗口截图 ≥1 张
playwright_screenshot(name="tauri-main-window")

# 5. 归档 + Read
```

## CLI 项目

```bash
# 1. 真实跑一次 end-to-end
./bin/cli --config config.toml --command full-flow

# 2. 输出片段 ≥10 行（保存到 verify-report.md）
# 3. 退出码 = 0
echo $?

# 4. 关键产物存在
ls output/
```

## Library

```python
# 1. 集成测试真实调用
pytest tests/integration/test_real_call.py -v

# 2. 测试中调用真实 API（非 mock）
def test_real_api():
    result = my_lib.call_real_api(endpoint="...")
    assert result.status == 200

# 3. 输出：API 调用证据 + 返回字段
```

## 后端服务

```bash
# 1. 启动服务
python -m my_server &
sleep 5

# 2. 健康检查端点
curl -s http://127.0.0.1:8080/health
# 必须 200 + JSON 含 {"status": "ok"}

# 3. 日志无 ERROR
grep ERROR server.log  # 必须 0 行

# 4. 关键 API 真实调用
curl -s http://127.0.0.1:8080/api/v1/users/1
```

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md)
- [visual-evidence.md](visual-evidence.md)
- [blockage-report.md](blockage-report.md)
