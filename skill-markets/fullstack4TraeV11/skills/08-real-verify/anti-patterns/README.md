# Anti-patterns — Stage 3.5 Real Verify 反例库

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | "启动 = 完成"软指标 | [01-startup-equals-done.md](01-startup-equals-done.md) |
| 2 | 容器未启声称迁移成功 | [02-container-not-started.md](02-container-not-started.md) |
| 3 | 跳过 Playwright 截图 | [03-skip-screenshot.md](03-skip-screenshot.md) |
| 4 | V10 实战蒸馏 | [V10-battle-tested.md](V10-battle-tested.md) |

## 自检清单

```yaml
real_verify_checklist:
  - [ ] 环境依赖（DB / 缓存 / .env / 端口）全 PASS？
  - [ ] 迁移 / 测试 / 类型检查 / dev 启动 全 PASS？
  - [ ] 启动可见产物存在（按项目类型）？
  - [ ] 主上下文亲自 Read 截图 / curl 输出？
  - [ ] 任一 FAIL → 5 字段阻塞报告？
```