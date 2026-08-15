# 5 类项目启动验证（Startup Verification）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 3.5 Real Verify Step 3 必走。V10 §0.10 NEW 5 类项目分类。

---

## Web 项目

```bash
# 1. 启动 dev server
pnpm exec vite --port 5173 --host 127.0.0.1 &
sleep 5

# 2. curl 探测（端口与 workflows/five-project-verify.md L29 一致 = 5173）
<!-- scan-whitelist -->curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5173/<!-- /scan-whitelist -->
# 必须 200（端口以本项目 package.json 实际 dev server 端口为准，演示用 Vite 默认 5173）

# 3. Playwright 截图（主上下文亲自执行）
<!-- scan-whitelist -->playwright_navigate(url="http://127.0.0.1:5173/")<!-- /scan-whitelist -->
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
<!-- scan-whitelist -->curl -s http://127.0.0.1:8080/health<!-- /scan-whitelist -->
# 必须 200 + JSON 含 {"status": "ok"}

# 3. 日志无 ERROR
grep ERROR server.log  # 必须 0 行

# 4. 关键 API 真实调用
<!-- scan-whitelist -->curl -s http://127.0.0.1:8080/api/v1/users/1<!-- /scan-whitelist -->
```

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md)
- [visual-evidence.md](visual-evidence.md)
- [blockage-report.md](blockage-report.md)