# CHANGELOG

本文件记录 Trae 技能包 fullstack4Trae 的版本演进。

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
