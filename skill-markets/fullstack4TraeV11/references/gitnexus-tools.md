# GitNexus MCP 工具集（V11 核心）

> V11 **核心技能**（Article V GitNexus First — 不可降级）。
> 4 个 MCP 工具 + 双端 hook（SessionStart + Stop）+ Stage 2/3/6/7 必走。

---

## 为什么 GitNexus 是 V11 核心

V11 比 V10 增加了 **Stage 2 Plan 影响面评估**、**Stage 3 实施前追踪**、**Stage 6 Bug 6 层排查**、**Stage 7 健康度审计** 4 个必走场景。每个场景都依赖 GitNexus 的代码图谱能力（不是 grep 替代）。

**违反 = 🛑 REJECT（Article V 不可降级）**。

---

## 4 个 MCP 工具

### impact({target, direction})

```python
mcp__gitnexus__impact(target="UserService.authenticate", direction="upstream")
```

| 字段 | 含义 | 处置 |
|------|------|------|
| `direct_callers` | 直接调用此 symbol 的代码 | 必读 + 改 caller 测试 |
| `indirect_callers` | 间接调用 | 抽样 + 关注高风险路径 |
| `affected_processes` | 受影响的执行流 | 走完整 e2e 测试 |
| `risk_level` | LOW/MEDIUM/HIGH/CRITICAL | 影响 plan.md Impact 段 |

### context({name})

```python
mcp__gitnexus__context(name="authenticate")
# 返回: 完整调用图 + 文件位置 + 代码片段
```

### query({query})

```python
mcp__gitnexus__query(query="user authentication flow")
# 返回: 相关代码片段 + 文件路径
```

### detect_changes({scope, base_ref})

```python
mcp__gitnexus__detect_changes(scope="compare", base_ref="main")
# 返回: 与 main 的 diff + 冲突风险
```

---

## 4 个 stage 必走 gitnexus

| Stage | 必走场景 | 工具组合 |
|-------|---------|---------|
| **0 Plan** | 影响面评估（3 路径评估 B 路径）| impact + context |
| **3 Implement** | 实施前影响追踪 + RED 阶段用例参考 + 实施后冲突检测 | impact + context + query + detect_changes |
| **6 Bug Fix** | 6 层排查（每层用对应工具）| impact + context + query |
| **7 Project Health** | 4 维度检查（路径 / 目录 / 版本 / 文档）| impact + query + detect_changes |

---

## V11 GitNexus 双端 Hook（V10.10 NEW）

### 读端：SessionStart（gitnexus-session-check.py）

```
会话启动时:
  ├─ meta.json 缺失 → 后台触发 analyze
  ├─ meta.lastCommit != HEAD → 后台触发 analyze（staleness）
  ├─ meta 解析失败 → 后台触发 analyze
  └─ 索引同步 → 跳过

后台执行：subprocess.Popen + DETACHED_PROCESS
退出码：始终 0（失败只打警告）
可关闭：GITNEXUS_AUTO_ANALYZE=0
日志：.gitnexus/analyze.log
```

### 写端：Stop（gitnexus-session-finalize.py）

```
会话结束时:
  ├─ HEAD == meta.lastCommit → 跳过（已同步）
  └─ 否则 → 后台触发 analyze（写端）

设计与 SessionStart 配对: 读端 staleness + 写端 refresh
```

### 安装

```bash
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/install-hooks.py --project-root .
```

---

## 反例（V11 Article V 必走）

```python
# ❌ 反例 1: 跳过 gitnexus 用 grep
subagent: grep -r "authenticate" src/  # 找到 12 处
# 实际影响 28 处 → 实施时漏改 16 处

# ❌ 反例 2: 不跑 impact() 直接实施
implementer: 看一眼代码 → 改 → 提交  # 违反 Article V

# ❌ 反例 3: 不跑双端 hook
project: 无 .gitnexus/ 目录 → 索引永远过期 → 后续会话用错图谱

# ❌ 反例 4: GitNexus 失败不重试直接降级
debugger: impact() 失败 → 直接 grep  # 违反 3 次重试协议
正确: 必走 3 次重试协议（修参数 → 换工具 → list_repos）→ 仍失败 → 5 字段阻塞报告
```

## 失败处理（3 次重试协议 — V10.8 蒸馏）

详见 [gitnexus-retry-protocol.md](gitnexus-retry-protocol.md)。

```
MUST: GitNexus 调用失败时必走 3 次重试协议
NEVER: 直接降级为 grep/glob（违反 Article V.5 不可降级）
NEVER: 跳过重试直接静默继续
```

**3 次重试**:
1. 修参数（target / name / scope / base_ref）
2. 换工具（impact ↔ context ↔ query）
3. list_repos（看索引状态）
4. 仍失败 → 5 字段阻塞报告

---

## 检测（PR/CI 必走）

```yaml
gitnexus_compliance:
  stage_2_plan:
    impact_called: true
    no_grep_in_subagent_prompt: true
  stage_3_implement:
    gitnexus_calls >= 4: true
    no_grep_in_commit_diff: true
  stage_6_bug:
    impact_called: true
    context_called: true
  stage_7_health:
    impact_called: true
    detect_changes_called: true

hooks:
  session_start_present: true
  stop_present: true
```

任一缺失 → 🛑 REJECT

---

## 关联引用

- [Stage 0 Plan impact-assessment.md](../skills/02-plan/references/impact-assessment.md)
- [Stage 3 Implement gitnexus-impact.md](../skills/07-implement/references/gitnexus-impact.md)
- [Stage 6 Bug Fix gitnexus-6-layer.md](../skills/12-bug-fix/references/gitnexus-6-layer.md)
- [Stage 7 Health gitnexus-impact-audit.md](../skills/13-project-health/references/gitnexus-impact-audit.md)
- [公共铁律 Article V](common-iron-rules.md)
- V10 来源（开发期）: `../../fullstack4TraeV10/templates/hooks/gitnexus-session-{check,finalize}.py`