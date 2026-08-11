# Async Health Check — Stage 7 Project Health

> Stage 7 Project Health 必走。异步健康度自检协议。

---

## 流程

```
Step 1: 项目类型判定（web/tauri/cli/library/backend）
Step 2: 4 维度检查（路径一致性 / 目录树 / 版本残留 / 文档同步）
Step 3: 优先级分级（P0/P1/P2/P3）
Step 4: 输出 project-health-{date}.md + .json
```

---

## 4 维度检查

```yaml
dimension_1_path_consistency:
  - check: "docs/INDEX.md 路径 vs 实际文件"
  - check: "docs/api-endpoints/ 路径 vs 代码"
  - check: "docs/modules/ 路径 vs 模块"

dimension_2_directory_tree:
  - check: "与 ARCHITECTURE.md 目录树一致"
  - check: "与 INDEX.md 目录树一致"
  - check: "模块边界无循环依赖"

dimension_3_version_residue:
  - check: ".bak / .old / .tmp / .orig 文件"
  - check: "调试 console.log / debugger"
  - check: "TODO / FIXME / XXX"
  - check: "注释代码（# deleted / // removed）"

dimension_4_doc_sync:
  - check: "INDEX.md ↔ ARCHITECTURE.md ↔ 模块文档"
  - check: "API-REFERENCE ↔ contracts/"
  - check: "CHANGELOG.md 最新条目"
```

---

## 优先级分级

| 优先级 | 含义 | 修复 SLA |
|--------|------|---------|
| **P0** | 阻断（main 不通）| 立即 |
| **P1** | 高优（关键路径腐化）| 当周 |
| **P2** | 中优（次要腐化）| 当月 |
| **P3** | 低优（清理）| backlog |

---

## 输出格式

```yaml
# Project Health Report: {date}

## 总体评分

| 维度 | 评分 | 优先级 |
|------|:---:|:---:|
| 路径一致性 | 95% | P2 |
| 目录树 | 100% | OK |
| 版本残留 | 2 项 | P3 |
| 文档同步 | 88% | P1 |

## 修复项

### P0: 无

### P1 (1 项)
- [ ] docs/modules/ 与 docs/api-endpoints/ 不对齐

### P2 (3 项)
- [ ] ...

### P3 (2 项)
- [ ] 清理 debug.log
```

---

## 异步非阻塞原则

```
Stage 7 Project Health 是异步支线:
  ├─ 可与 Stage 0-6 任一并行
  ├─ 不阻塞主流程
  └─ 输出仅作 backlog 输入
```

---

## 反例

### 反例 A：把 health 当必走流程

```
主流程: Stage 0 → 1 → 2 → ... → 5 → 7  # ❌ 阻塞主流程
正确: Stage 7 异步并行
```

### 反例 B：修复优先级不分明

```
报告: 全平铺，无 P0/P1/P2/P3  # ❌
正确: 必含优先级分级
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [four-dimension-check.md](../references/four-dimension-check.md)
- [anti-distortion.md](../references/anti-distortion.md)