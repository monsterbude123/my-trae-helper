# V12.0.0 角色注册表（Role × Stage 正交 — V12 已授权）

> **定位**: 本目录是 role-protocol.md §2 的 8 角色定义落盘处。角色回答"谁、职责边界、权限";stage skill 回答"何时、流程、产物"。一个角色跨多 stage 履职，一个 stage 由多角色协作——**不是每个 stage 配一个角色**。
> **权威源**: 角色规格全文见 [role-protocol.md](../../references/role-protocol.md) §2（本目录 8 个 .md 与权威源双向漂移后失效，冲突时以 V12.0.0 强制布局为准）。

## 8 角色文件路径

| 角色 | 文件 | 依据 | 备注 |
|------|------|------|------|
| 贾维斯 | `jarvis.md` | §2.1 | 现有，V12.0.0 已扩展时机④⑤⑥ + `registry/roles.yaml` 白名单(V12 §1.11 增补条款) |
| 产品策划经理 | `product-manager.md` | §2.2 | V12 fact/ 白名单 + 落地追踪表 |
| 技术策划 | `tech-planner.md` | §2.3 | V12 fact/tech-plan.md + 验收规则 |
| 后端实施者 | `backend-implementer.md` | §2.4 | V12 stage/3/implement/backend-impl-notes.md |
| 前端实施者 | `frontend-implementer.md` | §2.5 | V12 stage/3/implement/frontend-impl-notes.md |
| 原型设计师 | `prototype-designer.md` | §2.6 | **核心新增**,V12 stage/1.5/prototype/ 物理隔离 |
| 代码提测 | `qa-submitter.md` | §2.7 | **核心新增**,V12 stage/3/implement/qa-submit-notes.md |
| 测试专家 | `test-expert.md` | §2.8 | **核心新增**,V12 stage/3.5/real-verify/verify-notes.md |

## Role × Stage 履职矩阵（对照 role-protocol.md §1,V12.0.0 已扩 7/health 列）

| 角色 \ Stage | -1 | 0/0.5 | 1 | 1.5 | 2 | 3 | 3.5 | 4 | 4.5/5 | 6 | 7/health |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 贾维斯 | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate | ✅全域 gate |
| 产品策划经理 | ✅需求 | | ✅spec 产品侧 | | | | | ⚙验收对照 | ✅归档 | | ⚙项目健康 |
| 技术策划 | | ✅方案拆分 | ⚙ | | ✅契约输入 | | | | | | ⚙项目健康 |
| 后端实施者 | | | | | ✅契约输入 | **主** | | | | | |
| 前端实施者 | | | | ⚙原型对照 | ✅契约输入 | **主** | | | | | |
| 原型设计师 | | | | **主** | | ⚙交接/演进 | | | | | |
| 代码提测 | | | | | | | **主代理** | | ✅提测报告 | **主代理** | |
| 测试专家 | | ✅测试计划 | ⚙AC 可测性 | | | | **子代理** | **子代理** | ⚙bug 单验收 | **子代理** | ⚙项目健康 |

**协作注释**:
- **主/子**: 同一 stage 的"主"与"子"/"⚙"协作关系由该 stage 的 SKILL.md 声明，不由角色自定（矩阵铁律 2）。
- 主上下文仍是驾驶舱（`registry/state-machine.yaml` pilot 不变）——角色都是被委派的执行者，角色体系不改变状态机所有权。
- 角色只在矩阵标注的 stage 内履职，越界 = Article IX 违规（矩阵铁律 1）。

## 与 sub-agent-rules.md 的边界声明

- **角色文件是 sub-agent-rules.md 的特化**：公共底座（通用证据规则 §2 / 汇报纪律 §4 / 上下文经济 §3 / 破坏性操作流程 §12 / 委派模板 §7 / 失败处理 §5 等）由 [sub-agent-rules.md](../../references/sub-agent-rules.md) 统一承载，**8 个角色 .md 均不重复这些内容**。
- 角色文件只写该角色特化内容：身份定位、目标、职责边界、权限/禁止、产物。
- 加载顺序：委派 sub-agent 时先注入 sub-agent-rules.md（底座），再注入对应当前 stage 的角色文件（特化）。
- 通用铁律（Article V 可验证声明 / IX 质疑式验收 / XI 骨感等）见 [common-iron-rules.md](../../references/common-iron-rules.md)，角色文件仅在需要强调的禁止项内引用编号，不内联全文。