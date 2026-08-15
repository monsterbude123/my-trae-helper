# Stage 3.5 Real Verify — 元信息

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 第一性原则：**启动可见产物是唯一信任基础，不接受自评**。

## 完整骨架（4 步）

```
Step 1: 环境依赖检查
Step 2: 真实验证执行
Step 3: 启动可见产物（5 类项目类型之一）
Step 4: 阻塞处理（5 字段报告）
```

## 5 类项目启动验证

| 项目类型 | 验证产物 |
|---------|---------|
| Web | curl 200 + Playwright 截图 ≥1 |
| Tauri | tauri dev + 主窗口截图 |
| CLI | end-to-end 命令 + 输出 ≥10 行 |
| Library | 集成测试 + 正确返回 |
| 后端 | health 200 + 日志无 ERROR |

## 反例（3 条 + V10 蒸馏）

详见 [anti-patterns/](anti-patterns/)。
