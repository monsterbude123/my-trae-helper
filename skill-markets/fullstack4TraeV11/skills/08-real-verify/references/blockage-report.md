# 5 字段阻塞报告（Blockage Report）

> Stage 3.5 Real Verify Step 4 必走。V10 Article XV 障碍诚实。

---

## 5 字段必含

```yaml
blocker:
  type: "环境依赖" | "测试失败" | "类型错误" | "启动失败" | "其他"
  description: "具体阻塞描述（含错误信息）"
  attempted_solution: "已尝试的方案"
  time_consumed_minutes: N
  attempt_count: N
```

---

## 处置流程

```
Real Verify 任一 FAIL
  ↓
5 字段阻塞报告（必含 5 项）
  ↓
状态卡 health = 🔴 blocked + blocked_by = 报告内容
  ↓
禁止:
  - ❌ 跳过（"先继续，回头再看"）
  - ❌ 隐藏（"等下修，先标完成"）
  - ❌ 声称"完成"
  ↓
主上下文必亲自 Read 阻塞报告
  ↓
可选:
  ├─ 用户决策（接受风险 / 等待修复 / 显式豁免）
  └─ Stage 3 回退（修复后重试）
```

---

## 反例

### 反例 A：隐瞒容器未启

```
Real Verify: 迁移脚本报告 success
实际: docker compose ps postgres → Exit 1
主上下文: 隐瞒 → 声称 Real Verify PASS  # ❌ V10.10 反虚假交付
正确: 5 字段报告 + health = 🔴
```

### 反例 B：抽象理由

```
主上下文: "理解偏差" / "流程裁剪" / "心理障碍"  # ❌ V10.10 抽象理由
正确: 5 字段具体描述 + 尝试次数
```

---

## 关联引用

- [SKILL.md §铁律 5](../SKILL.md) — 阻塞诚实
- 公共铁律 Article XV: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
