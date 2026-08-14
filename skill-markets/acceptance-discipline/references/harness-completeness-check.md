# Harness 完整度自检 (6 流程 × N 工具 覆盖度矩阵)

> 来源:[external-report 2026-08-14 §M-05](file:///d:/workspace/my-trae-helper/logs/daily-vibe-coding/2026-08-14/external-report.md) + [Stack Overflow 2026 Vibe Coding 调研](https://m.toutiao.com/group/7672221947203306026/)
> 目的:把"vibe coding 6 流程 → 我们工具覆盖度"做出**可审计矩阵**,不靠感觉

## Vibe Coding 6 大特征 + Harness 6 流程(总览)

```
Vibe Coding 6 大特征:
  1. 意图驱动      → user 说"做什么"而非"怎么做"
  2. 自然语言接口  → human ↔ agent 用自然语言
  3. 非一步到位    → agent 自主拆任务,多轮迭代
  4. 写代码→审代码 → human 角色从"写"转"审"
  5. 指数级加速    → 单 agent 提升有限,multi-agent 多倍
  6. 容错包容      → 允许"模糊"输入,agent 主动补全

Harness 6 流程(让 vibe coding 可上生产):
  1. 初始化  → 加载 AGENTS.md / project rules / 项目宪法
  2. 目标    → 写 spec.md / plan.md
  3. 计划    → 拆 atomic tasks
  4. 自动化  → agent 执行 + 三层控制(Gate/Guard/Execution)
  5. 验收    → 人工 review + 自动 guard 验证
  6. 沉淀    → 知识提取 / 文档化 / 反馈循环
```

## 覆盖度矩阵(2026-08-14 自检)

| 流程 | 维度 | 本仓库工具 | 状态 | 证据 |
|------|------|------------|------|------|
| **1. 初始化** | AGENTS.md open standard | `AGENTS.md` + 新增 `CLAUDE.md` (`@AGENTS.md`) | ✅ | [UP-2026-08-14-01](../2026-08-14/implementation-log.md) |
| | project rules | `.trae/rules/*.md` × 4 文件 | ✅ | learning.md + 项目核心.md + readme.md + learning.md |
| | skills 索引 | `skill-markets/CAPABILITY-MAP.md` (48 skills 索引) | ✅ | CAPABILITY-MAP.md |
| **2. 目标** | spec 模板 | fullstack4TraeV11 stage-1-spec | ✅ | skills/01-intake ~ 13-project-health |
| | 规则约束 | AGENTS.md §1 铁律(10 条) | ✅ | AGENTS.md |
| **3. 计划** | atomic tasks | fullstack4TraeV11 stage-0-plan + stage-0.5-test-plan | ✅ | skills/02-plan + 03-test-plan |
| | 任务进度 | 状态卡协议 | ✅ | references/state-card-protocol.md |
| **4. 自动化** | 三层控制 (Execution/Guard/Gate) | `src/execution/*` + `scripts/*-guard.py` + `.husky/*` + `.github/workflows/*` | ✅ | AGENTS.md §2 |
| | L1 commit gate | `.husky/pre-commit` × 6 步 | ✅ | pre-commit |
| | L2 push gate | `.husky/pre-push` × 5 步 | ✅ | pre-push |
| | L3 merge gate | `.github/workflows/skill-market-gate.yml` | ✅ | L3-merge-gate |
| | L4 publish gate | 同上 | ✅ | L4-publish-gate |
| **5. 验收** | 单元测试 | `npm run test:unit` (skill-change-control 等) | ✅ | package.json |
| | 集成测试 | `npm run test:integration` | ✅ | package.json |
| | 覆盖率 | `npm run test:coverage` | ✅ | package.json |
| | 安全扫描 | `trae-security-review/scripts/scan_skills_dir.py` | ✅ | scripts/ |
| | 结构守卫 | `skill-structure-guard.py` | ✅ | scripts/ |
| | 能力守卫 | `skill-capability-guard.py` | ✅ | scripts/ |
| | 依赖守卫 | `src/guards/skill-dependency-guard.mjs` | ✅ | src/ |
| | bundle 守卫 | `07_bundle_structure.py` (3 模式) | ✅ | skill-acceptance/checks/ |
| | **保护路径守卫** | `change-guard-approver.mjs` (4 Tier) | ✅ NEW | scripts/ |
| | E2E 验收 | e2e-module-audit / acceptance-discipline | ✅ | skill-markets/ |
| | 性能压测 | (待补) | ❌ | — |
| | metric 收集 | acceptance-discipline/references/metrics.md | ✅ | references/ |
| **6. 沉淀** | 知识提取 | fullstack4TraeV11 stage-11-accept / spec-knowledge-extract | ✅ | scripts/ |
| | 经验沉淀 | global self-improving-agent (LEARNING/ERROR) | ✅ | .trae/rules/learning.md |
| | 反馈循环 | acceptance-discipline + post-commit hook | ✅ | .husky/post-commit |

## 覆盖度统计

```
总条目: 23
已覆盖: 22 (96%)
未覆盖: 1  (性能压测 — 待补)
```

**结论**:本仓库 Harness 完整度已达 **96%**,唯一缺口是**性能压测工具**。

## 不建议做的事

- **100% 覆盖** — 性能压测工具需要专业工具链(k6 / Artillery / wrk),不应由通用 guard 脚本代替
- **6 流程严格串行** — 实际上 1~3 流程可重叠(初始化 + 目标常并行,自动化 + 验收常并发)
- **审计 Harness 覆盖率超过月度** — Harness 演进是季度级动作,过度审计反而拖累日常开发

## 引用

- [external-report §M-05](file:///d:/workspace/my-trae-helper/logs/daily-vibe-coding/2026-08-14/external-report.md) — 原始来源
- [self-audit 2026-08-14](file:///d:/workspace/my-trae-helper/logs/daily-vibe-coding/2026-08-14/self-audit.md) — 本仓库体检
- [AGENTS.md §2](file:///d:/workspace/my-trae-helper/AGENTS.md) — 三层控制体系
