# CHANGELOG

本文件记录 Trae 技能包 fullstack4Trae 的版本演进。

---

## [v8.0] - 2026-07-12

### 治理动机

V7 在实战中暴露了三个结构性臃肿问题：

1. **Agent 文件臃肿**：10 个 Agent 文件平均 400+ 行，内联模板、场景代码、详细步骤塞入主文件 → 上下文击穿
2. **References 重叠**：43 个 reference 文件存在 5 组 2-4 个文件的内容重复（prototype/spec/contract/doc-sync/review）
3. **DOC SYNC 双写**：#1（写内容）和 #2（验证+改标记）两次写 modules/ → 内容漂移 + 审计困难

V8 围绕**去重、瘦身、脚本化**三大原则进行治理，不改变核心意图。

### 核心变更

#### 1. DOC SYNC 合并协议（BREAKING）
- V7: DOC SYNC #1（plan confirmed 后写） + #2（review 后验证）
- V8: 单写 + 标记流转（🟡 provisional → 🟢 confirmed）
- 写次数从 2 次降为 1 次，消除双写漂移
- 标记可审计（🟢=已确认，🟡=待验证）
- 新增 [doc-sync-protocol.md §七](doc-sync-protocol.md) 描述合并协议

#### 2. Agent 瘦身（10 个全部）
- 全部 Agent 从 300-680 行瘦身至 104-151 行
- 内联模板/场景/代码块移出到 references/
- 新增 reference 文件：contract-format.md、spec-format.md、doc-sync-scenarios.md（均已合并入对应主文件）

#### 3. References 合并（43→36）
- prototype 3→1：prototype-rules.md + prototype-ascii-template.md → prototype.md
- spec 4→2：spec-templates.md + spec-format.md → spec-driven-development.md（spec-overlap-merge.md 保留独立）
- contract 2→1：contract-format.md → contract-first.md
- doc-sync 2→1：doc-sync-scenarios.md → doc-sync-protocol.md
- review 2→1：code-review.md → quantitative-acceptance.md（重命名：量化验收与代码审查 V7.0）

#### 4. Buglist-Cockpit 联动
- cockpit-state-card.md 新增 🐛 活跃缺陷段（含用户反馈列）
- buglist.md 新增 Agent 上下文恢复协议（重入必读）
- intake 步骤 0.05：Bug 信号优先检查

#### 5. Closure 审 维度
- reviewer.md §5：P0 闭环覆盖率验证（< 100% → FAIL，总分封顶 3.0）
- 维度 3 "测试质量" 增加闭环覆盖率子项

#### 6. 🔷 基石模块接入手册
- doc-updater 场景 8：自动生成 integration.md
- spec-format.md：Published Interfaces 模板（已并入 spec-driven-development.md §十三）
- contract-format.md：@published 注释块规则（已并入 contract-first.md §十一-H）
- 模板：templates/integration-manual.md

#### 7. 其他修复
- SKILL.md §6：prototype-rules.md → prototype.md（引用修复）
- verification-loop.md：spec-templates.md → spec-driven-development.md（引用修复）
- Cockpit 模板精简（29 行）
- 移除嵌套的 fullstack4TraeV7/ 子目录残留

#### 8. 文档治理五补丁（基于 AIGCMediaDesktop 实战审计）

> 来源：[docs/references/(1) 优化Agent文档检索.md](../../../docs/references/(1) 优化Agent文档检索.md)

V8 上线后在 AIGCMediaDesktop 项目实战中发现文档臃肿（状态卡 446 行、ARCHITECTURE 85% 噪音、无 INDEX），暴露了 DOC SYNC 协议的 5 个系统性缺口。全部补入 [doc-sync-protocol.md](doc-sync-protocol.md)：

| # | 补丁 | 落点 | 内容 |
|---|------|------|------|
| 1 | **禁止写入清单** | §九 | 7 项禁止（Review 评分/时间戳/Bug 过程/实现细节...）+ 7 项允许 + 自检清单 |
| 2 | **文档体积硬上限** | §十 | 6 类文档硬上限表 + prune 优先级 + intake 健康快检 |
| 3 | **.history.md Append-Only 协议** | §十二 | 6 节完整协议（职责/时机/方式/模板/索引/使用协议）— 一次 change 一生写一条 + 禁止全文读 |
| 4 | **文档治理决策树** | §十一 | 3 步自主决策（严重度→范围+根因→用户确认阈值）+ 治理 change 简化链 |
| 5 | **Cockpit 编辑安全协议** | cockpit-state-card.md | Section delimiter 标记 + 并发编辑禁止 + 文档健康字段 |

**其他伴随变更**：
- doc-updater Agent：步骤 0 前置体积检查 + 写前禁止清单自检
- cockpit 模板：新增 `文档健康` 字段（🟡 N 个文件接近上限 / 🔴 状态卡 > 100 行）

#### 9. 全链路排查补丁（保真 + 察觉 + 路径闭环）

深入审计 SKILL.md 骨架流程，发现 13 个缺口（察觉机制缺失/保真机制缺失/协议覆盖缝隙/引用断裂），逐项补入：

| # | 缺口 | 修复 |
|---|------|------|
| G1 | Phase 0 无文档健康快检 | Phase 0 +`文档健康快检（Cockpit + §十）` |
| G2 | Intake 不识别"文档治理"任务 | 关键词映射 +`文档治理/膨胀/瘦身 → 治理链` |
| G4+G13 | DOC SYNC 无事实保真校验 | 新增 [§十三 保真迁移协议](doc-sync-protocol.md#十三保真迁移协议) — Phase A 事实编目 → B 执行迁移 → C 验证（4 项硬性检查全 PASS） |
| G6 | Implementer 无文档修改保真 | 新增铁律 14: `NO DOC MODIFICATION WITHOUT FIDELITY CHECK` |
| G7+G8 | 异常路径缺文档膨胀类型 | 异常路径 +`文档膨胀→治理决策树` + 新增 `治理链` 定义 |
| G9 | 铁律缺文档治理不失真 | 新增铁律 8: `文档治理不失真` |
| G10 | §6 参考索引缺治理章 | +`文档治理（禁止写入+体积上限+决策树+保真协议）` |
| G11 | Spec 缺治理专用不变量 | 跳过（spec-format 通用 Invariant 框架可覆盖） |

**连锁更新**: Intake 步骤 0.05 合并 Bug+文档健康检查 / doc-updater 步骤 0 前置保真协议 / implementer 15→15 铁律重新编号

### 删除的文件
- `references/prototype-rules.md`（并入 prototype.md）
- `references/prototype-ascii-template.md`（并入 prototype.md）
- `references/spec-templates.md`（并入 spec-driven-development.md）
- `references/spec-format.md`（并入 spec-driven-development.md）
- `references/contract-format.md`（并入 contract-first.md）
- `references/doc-sync-scenarios.md`（并入 doc-sync-protocol.md）
- `references/code-review.md`（并入 quantitative-acceptance.md）
- `fullstack4TraeV7/`（嵌套残留目录）

---

## [v7.0] - 2026-06-29

### 重构动机

V5 在实战中暴露了三个结构性缺陷：

1. **假性完成**：Agent 中途停止，state-card 显示 ✅ 但实际无产出。用户看不出进度，spec 爆炸到 50+ 个。
2. **单角色盲区**：AI 写 spec 时缺乏多视角交叉验证，遗漏边界情况、可测试性问题、用户体验盲区。
3. **技能僵化**：技能写好就"冻结"，实战中的磕绊、打断、报错无结构化记录，无法从经验中进化。

V7 围绕 Cockpit 驾驶舱 + 圆桌会议 + Report 生长三个核心机制进行升级。

### 主要变更

#### 1. Cockpit 驾驶舱 — 双层状态卡（NEW）
- 新增项目级 `docs/specs/.state-card.md`（全局仪表盘）
- per-change 状态卡新增 `最后产出时间` 字段
- 新会话自检：Agent 激活时验证文件系统 vs 状态卡，检测假性完成
- Spec 堆积风险自动预警（🟢<3 / 🟡3-5 / 🔴>5）

#### 2. 30% 原子化需求去重（NEW）
- intake 新增步骤 1.5：拆用户需求为原子功能点 → 搜索已有 change → 计算重叠度
- 重叠 ≥ 70%：完全覆盖，不创建新 change
- 重叠 30-70%：合并候选，根据已有 change 阶段决定
- 重叠 < 30%：创建新 change

#### 3. 圆桌会议 — 多角色交叉评审（NEW）
- 6 角色子代理（前端经理/后端经理/产品经理/测试经理/用户经理/业界经验）
- 干净上下文并行评审
- meeting-notes 落盘（`meeting-notes/round-{N}.md`）
- config.yaml `roundtable.enabled` 控制开关

#### 4. Report 生长机制（NEW）
- `report-{0X}.md`：Agent → 人 + Agent → 技能通信通道
- 随时触发（打断/报错/磕绊/优化发现）
- 交付时强制汇总
- 技能设计者据此决定是否升级技能

#### 5. Doc-Updater V7 升级（MODIFIED）
- 同步范围：CODEMAP → CODEMAP + prototypes/ 回流 + archive/ 维护 + test-plan/ 同步 + modules/ 同步
- 归档拆分：单层 `archive/` → `archive/out/`（淘汰）+ `archive/done/`（完成）

#### 6. 原型双层体系（MODIFIED）
- 项目级 `docs/prototypes/`（Cockpit 组件速查）
- per-change `prototypes/`（施工图纸）
- 完成回流由 doc-updater 处理

#### 7. 铁律扩展（9 → 14 条）
- +STATE CARD ALWAYS HONEST（状态卡必须真实，新会话自检）
- +SPEC OVERLAP MUST MERGE（需求重叠 > 30% 必须合并）
- +REPORT FOR GROWTH（磕绊必写报告）
- +GITNEXUS FIRST（分析前必须更新索引）
- +NO DEGRADING FALLBACK（禁止 `||`/`??` 降级兼容）

#### 8. 目录结构升级
- 新增：`docs/test-plan/`（项目级测试方案）、`docs/prototypes/`（项目级原型）
- 新增：`docs/archive/out/`、`docs/archive/done/`
- 新增：`meeting-notes/`、`report-{0X}.md`
- 状态卡双层化：`docs/specs/.state-card.md` + per-change `.state-card.md`

#### 9. Agent 变更
- intake：新增步骤 0（Cockpit 读取）+ 步骤 1.5（30% 去重）
- doc-updater：职责从"代码地图生成器"升级为"全栈文档管家"（6 类同步）
- 其他 7 个 Agent 不变

#### 10. 新增文档
- `GUIDE.md`：用户/Agent 快速操作指南
- `references/cockpit.md`：驾驶舱方法论
- `references/roundtable.md`：圆桌会议方法论
- `references/report-growth.md`：技能生长方法论
- `references/spec-overlap-merge.md`：30% 去重规则
- `templates/roundtable-agent-prompt.md`：圆桌子代理指令模板
- `templates/cockpit-state-card.md`：项目级驾驶舱模板
- `templates/meeting-notes.md`：圆桌会议纪要模板
- `templates/report.md`：技能生长报告模板

---

## [v5.2] - 2026-06-28

Agent 名称统一加 `fullstack-` 前缀，V5.1 增量修复。

---

## [v5.1] - 2026-06-27

原型设计环节补充。fullstack-spec-writer 扩展原型产出（ASCII 线框图 + 交互说明）。

---

## [v5.0] - 2026-06-25

全栈文档驱动开发技能包正式发布。9 Agent 流水线 + DOC FIRST + Contract-First + Spec-Driven + TDD。
