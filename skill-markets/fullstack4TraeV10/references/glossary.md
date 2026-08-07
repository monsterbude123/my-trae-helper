# 术语表

## 通用术语

| 术语 | 定义 |
|------|------|
| Spec | 规格说明，OpenSpec 格式的可执行蓝图 |
| Define | 定义阶段，合并 Proposal + Plan + Closure 的紧凑文档 |
| OpenSpec | 开放式规格格式，WHEN-THEN-AND + SHALL 语义 |
| Contract | 接口契约，API/模型/事件的不可变定义 |
| TDD | Test-Driven Development，测试驱动开发 |
| RED | TDD 第一步，编写失败的测试 |
| GREEN | TDD 第二步，编写实现让测试通过 |
| REFACTOR | TDD 第三步，优化代码质量 |
| DOC SYNC | 文档同步，确保文档与代码一致 |
| Drift | 漂移，规格/契约/代码之间的不一致 |
| Cockpit | 驾驶舱，项目状态总览 |
| Visual Gate | 视觉验收，涉及 UI 时截图比对原型 |
| Closure | 业务闭环，P0 步骤确保功能完整可用 |
| Acceptance | 验收，E2E/性能/安全门禁 |
| ADDITIVE | 兼容性契约变更（新增可选字段/接口） |
| BREAKING | 破坏性契约变更（删字段/改类型），需用户确认 |

## V10.4 新增术语

| 术语 | 定义 |
|------|------|
| Article IX | TDD 即时 — 改实现/删组件必须立即同步改测试/删测试，同 PR atomic |
| Article XI | 视觉真实验证 — PIL 完整解码 + 颜色直方图多样性 + 4 象限亮度极差，杜绝视觉假阳性 |
| Article XIV | rot-detector 必跑 — Phase 4.5 Proactive Rot Scan 不可跳过，任一 FAIL = 🛑 REJECT |
| rot-detector | 主动诊断腐化的 Agent，不被动等用户问，调 proactive-scan.py 扫描目标项目 |
| Phase 4.5 | Proactive Rot Scan 双层：4.5.1 self-diagnose（检测器自检）/ 4.5.2 proactive-scan（项目扫描） |
| self-diagnose.py | Meta 自我诊断脚本，验证 V10 检测器自身无腐烂（regex/阈值/锚定） |
| visual-content-check.py | 视觉内容深度校验，PIL 解码 + 直方图 + 象限亮度，3 层硬门禁 |
| orphan-detector.py | 孤儿测试/组件检测，写新合约前必跑，防测试与组件失配 |
| dist-hash-check.py | Bundle 一致性检查，改 TS 后必跑，防 dist 与源码漂移（Tauri 项目） |
| 腐烂点 9-14 | 视觉假阳性 / 自验自签 / 孤儿测试 / 隐式 build / Agent 不主动诊断 / 检测器自身腐烂 |

## V10.5 新增术语

| 术语 | 定义 |
|------|------|
| Article XII | 文档诚实 — state-card/INDEX 声称的 INV 必在 spec.md 落地，不可自评"完成"无证据 |
| Article XIII | 骨架是债 — 骨架（只 define.md）= 隐性技术债，2 周未推进必冻结或归档 |
| 腐烂点 15-17 | 自我吹嘘 / 状态卡陈旧 / 骨架堆积，由 rot-reinforcer 实战暴露 |

## V10.6 新增术语

| 术语 | 定义 |
|------|------|
| Evidence 独立抽检 | 主上下文对 agent 返回的 evidence 亲自验证（Read file:line ≤50 行），不匹配 = 🛑 REJECT（虚假汇报） |

## V10.8 新增术语

| 术语 | 定义 |
|------|------|
| 反踩坑 6 条铁律 | 临时指令不作交付 / 陌生域先 probe / 半截文件不暴露 / URL query 必 dry-run / API metadata 报三层 / 用户语气转硬立即停 |
| 破坏性操作红线 | 4 步协议：列清单 → 用户确认 → trash 兜底 → 跨盘额外校验；rmtree/不可逆变换结构性失败 |
| 严重度分层 P0/P1/P2/P4 | P0 生产阻断 / P1 架构规范 / P2 代码风格 / P4 资产卫生，与阶段门禁链叠加 |
| 小任务流线化 | 门禁链例外条款：≤6 Task + LOW + 无新 API + 无 UI 变更（或仅微调）→ Intake→Define→Implement→Review |
| 通过依据 3 类分层 | [1] 后端/编译类（不证用户视角）/ [2] UI 渲染类（机器可验证）/ [3] 用户视角类（不可代签） |
| 质疑式验收官 | reviewer role_stance：ZERO TRUST / EVIDENCE MANDATORY / ACTIVE FALSIFICATION / REQUIREMENT TRACING |
| DOC_WHITELIST | 子代理文档读取白名单，task-execution-mode 隐含禁读 docs/archive/、docs/bugs/、docs/reports/、docs/history/ 等 |
| bug-workflow | Bug 快速链：B.1 Plan 轻量（根因+影响面）/ B.2 Implement（RED 重现→GREEN 修复→回归）/ B.3 Review 轻量（回归通过即可） |
