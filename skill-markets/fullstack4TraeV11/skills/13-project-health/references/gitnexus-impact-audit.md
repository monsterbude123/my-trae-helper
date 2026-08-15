# GitNexus 项目健康度审计 — Stage 7 Project Health

> Stage 7 Project Health 输出前必走 (V10 project-health-auditor.md Step 4 蒸馏)。
> 注: V11 Stage 13 SKILL.md 4 步骨架中 Step 4 = "输出 report",本文档的 GitNexus 5 调用作为 Step 4 的子步 (Step 4.1 启动前影响面评估) 嵌入输出流程。
> 用 GitNexus MCP 工具评估项目健康度的影响面。

---

## Step 4.1: GitNexus 影响面评估 (输出前)

```
对不符合项运行 gitnexus impact() 评估影响面
```

---

## 4 类健康度评估 + GitNexus 工具

| 评估项 | GitNexus 工具 | 输出 |
|--------|-------------|------|
| 路径一致性 | `query(query="{module}")` | 路径 vs 代码 实际位置 |
| 目录树 | `query(query="module {name}")` | 模块边界 + 循环依赖风险 |
| 版本残留 | `detect_changes(scope=branch)` | 已删除但仍引用的代码 |
| 文档同步 | `query(query="{api-name}")` | API 引用 vs 实际实现 |

---

## Stage 7 必走的 5 个 GitNexus 调用

```
Step 1: 项目健康检查启动 → impact(target="{project_root}") 总览影响面
Step 2: 不符合项定位 → impact(target="{violation}") 单项影响
Step 3: 路径核对 → query(query="path {path}") 找实际位置
Step 4: 版本残留 → detect_changes(scope=compare, base_ref="main") 找 stale 代码
Step 5: 文档同步 → query(query="{api}") 对比 API 引用
```

---

## 真实案例（V10 蒸馏）

### 案例：项目重构后 health 报告

```yaml
# Stage 7 输出
project_health:
  path_consistency: 95%
  directory_tree: 100%
  version_residue: 2 项
  doc_sync: 88%

# GitNexus 辅助定位
fix_list:
  - id: 1
    name: "version_residue"
    finding: "UserService 旧方法 deprecated 但 3 处仍引用"
    gitnexus_call: "mcp__gitnexus__impact(target='UserService.deprecated_method')"
    callers: 3 处
    fix_action: "替换为新方法 + 删除旧方法"
```

---

## 反例（必走 V11）

- ❌ 用 grep 找版本残留 → 🛑 REJECT（Article V）
- ❌ 不跑 GitNexus 直接 health 报告 → 🛑（4 维度不完整）

---

## 检测（project-health-{date}.md 必含）

```yaml
project_health_report:
  gitnexus_calls:
    - impact(target=project_root)
    - impact(target=violation)
    - query(query=path)
    - detect_changes(scope=branch)
    - query(query=api)
  4_dim_check: path / dir / version / doc
  P0_count: N
  P1_count: N
  P2_count: N
  P3_count: N
```

任一维度缺失 GitNexus 调用 → 🛑 REJECT

---

## 关联引用

- [four-dimension-check.md](four-dimension-check.md) — 4 维度检查协议
- [Stage 2 impact-assessment.md](../../02-plan/references/impact-assessment.md) — 工具基础
- [公共铁律 Article V](../../../references/common-iron-rules.md)
- V10 来源（开发期，已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）agents/project-health-auditor.md` Step 4