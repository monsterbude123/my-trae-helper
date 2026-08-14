# 术语表 — V11

> 完整继承 V10 `references/glossary.md` 64 行 + V11 新增 5 大类术语。
> 来源:V10 references/glossary.md(基础+V10.4/10.5/10.6/10.8 蒸馏)+ V11 子代理扫描报告。

---

## 一、通用术语(V10 基础 — 完整继承)

| 术语 | 定义 |
|------|------|
| Spec | 规格说明,OpenSpec 格式的可执行蓝图 |
| Define | 定义阶段,合并 Proposal + Plan + Closure 的紧凑文档 |
| OpenSpec | 开放式规格格式,WHEN-THEN-AND + SHALL 语义 |
| Contract | 接口契约,API/模型/事件的不可变定义 |
| TDD | Test-Driven Development,测试驱动开发 |
| RED | TDD 第一步,编写失败的测试 |
| GREEN | TDD 第二步,编写实现让测试通过 |
| REFACTOR | TDD 第三步,优化代码质量 |
| DOC SYNC | 文档同步,确保文档与代码一致 |
| Drift | 漂移,规格/契约/代码之间的不一致 |
| Cockpit | 驾驶舱,项目状态总览 |
| Visual Gate | 视觉验收,涉及 UI 时截图比对原型 |
| Closure | 业务闭环,P0 步骤确保功能完整可用 |
| Acceptance | 验收,E2E/性能/安全门禁 |
| ADDITIVE | 兼容性契约变更(新增可选字段/接口) |
| BREAKING | 破坏性契约变更(删字段/改类型),需用户确认 |

---

## 二、V10.4-10.8 新增术语(完整继承)

### V10.4

| 术语 | 定义 |
|------|------|
| Article IX | TDD 即时 — 改实现/删组件必须立即同步改测试/删测试,同 PR atomic |
| Article XI | 视觉真实验证 — PIL 完整解码 + 颜色直方图多样性 + 4 象限亮度极差,杜绝视觉假阳性 |
| Article XIV | rot-detector 必跑 — Phase 4.5 Proactive Rot Scan 不可跳过,任一 FAIL = 🛑 REJECT |
| rot-detector | 主动诊断腐化的 Agent,不被动等用户问,调 proactive-scan.py 扫描目标项目 |
| Phase 4.5 | Proactive Rot Scan 双层:4.5.1 self-diagnose(检测器自检)/ 4.5.2 proactive-scan(项目扫描) |
| self-diagnose.py | Meta 自我诊断脚本,验证 V10 检测器自身无腐烂(regex/阈值/锚定) |
| visual-content-check.py | 视觉内容深度校验,PIL 解码 + 直方图 + 象限亮度,3 层硬门禁 |
| orphan-detector.py | 孤儿测试/组件检测,写新合约前必跑,防测试与组件失配 |
| dist-hash-check.py | Bundle 一致性检查,改 TS 后必跑,防 dist 与源码漂移(Tauri 项目) |
| 腐烂点 9-14 | 视觉假阳性 / 自验自签 / 孤儿测试 / 隐式 build / Agent 不主动诊断 / 检测器自身腐烂 |

### V10.5

| 术语 | 定义 |
|------|------|
| Article XII | 文档诚实 — state-card/INDEX 声称的 INV 必在 spec.md 落地,不可自评"完成"无证据 |
| Article XIII | 骨架是债 — 骨架(只 define.md)= 隐性技术债,2 周未推进必冻结或归档 |
| 腐烂点 15-17 | 自我吹嘘 / 状态卡陈旧 / 骨架堆积,由 rot-reinforcer 实战暴露 |

### V10.6

| 术语 | 定义 |
|------|------|
| Evidence 独立抽检 | 主上下文对 agent 返回的 evidence 亲自验证(Read file:line ≤50 行),不匹配 = 🛑 REJECT(虚假汇报) |

### V10.8

| 术语 | 定义 |
|------|------|
| 反踩坑 6 条铁律 | 临时指令不作交付 / 陌生域先 probe / 半截文件不暴露 / URL query 必 dry-run / API metadata 报三层 / 用户连续 2 轮表达 ≥ 3 次否定判断立即停止自动推理并升级人工决策 |
| 破坏性操作红线 | 4 步协议:列清单 → 用户确认 → trash 兜底 → 跨盘额外校验;rmtree/不可逆变换结构性失败 |
| 严重度分层 P0/P1/P2/P4 | P0 生产阻断 / P1 架构规范 / P2 代码风格 / P4 资产卫生,与阶段门禁链叠加 |
| 小任务流线化 | 门禁链例外条款:≤6 Task + LOW + 无新 API + 无 UI 变更(或仅微调)→ Intake→Define→Implement→Review |
| 通过依据 3 类分层 | [1] 后端/编译类(不证用户视角)/ [2] UI 渲染类(机器可验证)/ [3] 用户视角类(不可代签) |
| 质疑式验收官 | reviewer role_stance:ZERO TRUST / EVIDENCE MANDATORY / ACTIVE FALSIFICATION / REQUIREMENT TRACING |
| DOC_WHITELIST | 子代理文档读取白名单,task-execution-mode 隐含禁读 docs/archive/、docs/bugs/、docs/reports/、docs/history/ 等 |
| bug-workflow | Bug 快速链:B.1 Plan 轻量(根因+影响面)/ B.2 Implement(RED 重现→GREEN 修复→回归)/ B.3 Review 轻量(回归通过即可) |

---

## 三、V11 新增 13 Stage 架构术语

### Stage 命名规范(13 个)

| Stage ID | 名称 | 职责 |
|---------|------|------|
| `-1/intake` | Stage -1 Intake | 意图受理 + 路由起点(所有请求必先经意图识别 + 状态卡初始化 + 项目惯例勘察) |
| `0/plan` | Stage 0 Plan | 探索 + 规划(3 路并行探索 + GitNexus impact + plan.md 产出) |
| `0.5/test-plan` | Stage 0.5 Test Plan | 测试覆盖映射(验收维度 → 测试用例映射,spec.md 测试覆盖映射) |
| `1/spec` | Stage 1 Spec | 规格增强 + 验收维度(Enhanced Acceptance + INV ≥1 + E2E ≥2 + clarify ≥2 轮) |
| `1.5/prototype` | Stage 1.5 Prototype | 双源兼容原型(设计稿 + 代码原型必须一致) |
| `2/contract` | Stage 2 Contract | 契约四件套(DOMAIN FIRST + ADDITIVE/BREAKING 变更流程 + 孤儿契约测试清理) |
| `3/implement` | Stage 3 Implement | TDD RED→GREEN 实施(契约驱动 + 深度业务理解 + 漂移检测) |
| `3.5/real-verify` | Stage 3.5 Real Verify | 启动可见产物(**唯一信任基础,不接受自评**) |
| `4/review` | Stage 4 Review | 质疑式验收(FAIL IS FAIL + 4 维评分 + 主动证伪 + DOC SYNC) |
| `4.5/rot-scan` | Stage 4.5 Rot Scan | 腐化扫描(proactive-scan.py 8 项必跑 + 元检测 + 修复,NO ROT NO ACCEPT) |
| `5/accept` | Stage 5 Accept | 归档门禁(归档不可变 + 知识沉淀 + INDEX 更新) |
| `6/bug-fix` | Stage 6 Bug Fix | 独立专精流程(根因不明不修复 + e2e 先行 + 6 层排查 + TDD 修复) |
| `7/project-health` | Stage 7 Project Health | 项目健康度自检(**异步非阻塞** + 4 维度检查 + 防失真) |

### 架构核心概念

| 术语 | 定义 |
|------|------|
| 高内聚专家架构 | V11 架构升级核心。从 V10 `agents/ + references/` 分散架构升级为"高内聚专家 skill"架构 — 每个 stage 自包含骨架/铁律/反例/模板/脚本/依赖声明,像插拔组件一样可独立管理 |
| stage_config | SKILL.md frontmatter 字段。V11 NEW。13 stage 路由 + depends_on 声明,由编排器解析 |
| stage skill agent | 用 Task 启动子代理 + 注入 stage skill 调用约定 = 完成的代理(V11 不新增 stage agent skill,而是给现有 agent 一个调用 stage skill 的标准协议) |
| stage-gate.py | V11 阶段门禁(13 stage 统一)。stage 切换前必跑 |

---

## 四、V11 新增协议

| 协议 | 定义 |
|------|------|
| state-card-protocol | 状态卡协议。3 类卡(project / change / bug)+ 字段定义 + 更新时机 + 交叉验证 + 模板 |
| stage-card-protocol | 状态卡流转协议。3 类状态卡必填字段 + 推进/回退/阻塞/归档规则 + 陈旧检测(30 分钟阈值)+ stage-gate.py 集成 |
| stage-interaction-protocol | stage 间交互协议。13 stage 间必走 4 步交互协议(Completion Report 4 字段 → AOP 移交自检清单 → 状态卡更新 → 启动 Stage B) |
| skeptical-validation-protocol | 质疑性校验协议(V10 蒸馏 + V11 增强版)。§1 P0/P1 4 维度质疑 + §2 通用质疑三层 + §3 强制声明格式 + §4 7 反例库 + §7 永久激活 stage 清单(Plan / Spec / Contract / Implement / Review / Bug Fix / Project Health) |
| force-reset-protocol | 状态卡强制重置协议(V11 NEW)。§7.1 重置前必走 3 步 + §7.2 重置操作 5 步 + §7.3 不允许操作红线 + §7.4 reset_history 字段 |
| dependency-config | 3 层优先级依赖配置。Layer 1 全局(user-level)+ Layer 2 V11(编排器)+ Layer 3 项目级(`.trae/fullstack4traev11.config.yaml`),优先级 3 > 2 > 1 |
| document-layer | 4 层文档架构。SPEC(What/Why)/ PLAN(How)/ CONTRACT(接口真相)/ IMPLEMENT(已写代码) |
| stage-skill-agent-protocol | stage skill agent 协议。4 步协议:委派头部 → agent 加载 stage skill → agent 必读文档 → agent 完成 4 字段 Completion Report |

### 协议相关子概念

| 术语 | 定义 |
|------|------|
| AOP 移交自检清单 | 每 stage 通用自检清单(必填产物 / 每个产物附 evidence / 状态卡字段完整 / 状态卡 next_stage 指向下一 stage / 任一项 ❌ → 修正后重新移交) |
| Completion Report 4 字段 | 子代理返回必填:`artifacts` / `status`(PASS \| FAIL \| PARTIAL)/ `evidence`(command+output+file_line)/ `next_hook`(pre-stage.sh \| post-stage.sh \| pre-accept.sh) |
| §0.5 Skill 加载协议 | 主上下文收到 "Use Skill: fullstack4traev11" 后必走 7 步:加载 SKILL.md → 必读 7 个公共 references → Glob 1 次项目自身约定 → 3 层优先级合并 → 列"我能踩的雷"清单 → Bug 录入触发词识别 → 进入 Stage -1 Intake |
| §0.5.1 同类约定强制清单 | 第 3 步"Glob 1 次"具体 Glob 哪些目录。按任务类型激活强制清单(截屏 / 视觉验证 / 浏览器自动化 / UI 测试 / E2E 框架 / 录屏 / a11y / 性能 / 契约对齐 / 时间时区 10 项) |
| 强制声明格式(§3) | 升级方案汇报前必按格式声明:根因验证 / 责任主体校验 / 重叠校验 / 修复成本 vs 价值 4 维度 |
| §7 永久激活 stage 清单 | skeptical-validation-protocol 必走的 7 个 stage(Plan / Spec / Contract / Implement / Review / Bug Fix / Project Health) |

---

## 五、V11 新增状态卡概念

| 术语 | 定义 |
|------|------|
| 三类状态卡(card_type) | `project` 级(项目整体健康度 + 当前活跃 change 指针)/ `change` 级(单个 change 的 stage 进度)/ `bug` 级(OPEN → CLOSED 状态机) |
| 项目级 vs change 级(路径区分) | 路径区分:`docs/specs/.state-card.md`(项目级)vs `docs/specs/changes/{id}/.state-card.md`(change 级),两类状态卡在不同目录,文件系统无冲突。类比:项目级 = 公司仪表盘 / change 级 = 单个项目任务卡 |
| reset_history 字段(V11 NEW) | 状态卡新增可选字段,记录重置历史(date / from_stage / to_stage / reason / preserved_artifacts / removed_artifacts / archive_note / git_decision / reset_by) |
| stage_status 5 态 | `pending` / `working` / `completed` / `blocked` / `skipped`(V11 新增 `skipped`) |
| health 3 态 | 🟢 on-track / 🟡 degraded / 🔴 blocked |
| gate_result 4 态 | `PASS` / `FAIL` / `N/A` / `PENDING` |
| stage_started_at / stage_ended_at | ISO 8601 必填字段(stage_status=completed 时 stage_ended_at 必有值) |
| 状态 emoji(V11.2 NEW — 蒸馏自 01-intake 自检报告) | 🛑 = P0 安全事件 / REJECT / 必须停止 / 阻塞;⚙ = 需用户决策(常配合 AskUserQuestion);❌ = 否决 / 不通过(轻量级);⚠️ = 警告 / 需关注(可继续) |

---

## 六、V11 新增 Article + 反例

### Article 宪法

| Article | 定义 |
|---------|------|
| Article XVII — Secret Redaction(V11 NEW) | **唯一新增铁律**。P0 安全条款,6 条硬约束:17.1 用户提供的 secret → 必通过环境变量 / .env 注入,**绝不**写到工具调用参数里;17.2 工具调用参数中出现 secret → 🛑 REJECT + 立即通知用户改密码;17.3 `.env` / `secrets/` / `credentials/` → forbidden_paths 强制禁读;17.4 即使"测试用"的 secret 也不写到 commit / tool log / 截图;17.5 secret 误写 → 立即回滚 + 用户重置 + 写入 audit log;17.6 shell / script 中出现的 `$PASSWORD` / `$TOKEN` → 必用 `${VAR:-}` 形式 + 在 audit log 中 redacted |
| Article V — GitNexus First(V11 强化) | V10 Article V 蒸馏,V11 不可降级。5.5-5.8:GitNexus 不可用 → L4 异常 → 标注风险 + 汇报用户(**不静默降级**) |
| 5 模式诊断(V11 NEW) | agent 失败 5 模式根因 → 现有铁律映射表。模式 1 盲信子代理 / 模式 2 应付性 PASS / 模式 3 rule 太长不读 / 模式 4 甩锅用户 / 模式 5 secret 泄露。5 个模式中**只有 1 个真正需新增**(模式 5 → Article XVII),其余 4 个是已含铁律的遵守问题 |
| 不冗余原则(Article XVI §1.4) | 新增铁律必走 4 检查:现有铁律 / 反例库 / 引用代替 / 修复成本 vs 价值 |

### 反例

| 反例 | 定义 |
|------|------|
| 反例 §19 — 循环 PASS 模式(Loop PASS Pattern) | V11 NEW。连续 ≥ 3 轮"我搞错了"+重新委派,无具体改进。6 轮循环 + 每次"具体改进"=重新委派 = 0 价值进步 |
| 反例 §20 — 甩锅用户模式(User Orchestration Pattern) | V11 NEW。Agent 用"请你去做 X"代替自己能做的部分。反模式短语库必禁:"你要不要..." / "你能不能..." / "请你去做..." / "你累不累..." / "明天再继续吧..." / "你想怎么处理？" / "你来定吧" |
| 反例 §21 — 未读 rule 就自评 PASS(Unread Rule PASS Pattern) | V11 NEW。rule 太长没读完 + 反复踩同一雷 + 自评 PASS。V11 §0.5 加载协议强化 6 步 |
| 反例 §22 — Secret 写入工具调用参数(Secret in Tool Argument) | V11 NEW + V11 Article XVII 触发。Agent 把密码/token 写到工具调用参数 → 工具调用日志 = 明文泄露 |
| "我能踩的雷"清单(V11.1 NEW) | 主上下文加载任意 skill 后必列的清单:反例 §19-22 + 现有 Article V/IX/XI 必逐项 |
| 同类约定强制清单(V11.1 NEW) | 10 项必 Glob 目录清单:截屏 / 视觉验证 / 浏览器自动化 / UI 测试 / E2E 框架 / 录屏 / a11y / 性能 / 契约对齐 / 时间时区 |

---

## 七、V11 新增工具/脚本

| 脚本 | 定义 |
|------|------|
| init-from-zero.py | 全新项目完整初始化(4 步全流程):Step 1 config.yaml + hooks / Step 2 `.trae/rules/` / Step 3 AGENTS.md / Step 4 文档系统骨架 |
| sync-after-upgrade.py | 技能升级后覆盖性更新项目文件。检查 + 更新范围:hooks(覆盖式更新)+ config.yaml(覆盖式)+ rules(提示差异)+ AGENTS.md(提示差异)+ scripts(提示新增) |
| _lib_state_card.py | 状态卡 frontmatter 解析共用库。3 个脚本(state-card-validator / stage-gate / change-status)共用。优先 PyYAML(精确解析嵌套),未安装时回退手写解析 |
| upgrade-from-v10.py | V10 → V11 升级兼容性检查 |
| install-hooks.py | Hook 安装到项目 `.trae/` |
| hooks-fidelity.py | Hook 完整性验证 |
| scan-templates.py | 模板扫描 |
| reason-classifier.py | 抽象理由分类器(6 类) |
| change-status.py | 读取 change 真实状态 |
| GitNexus 双端 Hook | 读端:`gitnexus-session-check.py`(SessionStart,staleness 检测 + 后台刷新)+写端:`gitnexus-session-finalize.py`(Stop,写新 HEAD → 后台刷新) |
| GitNexus 3 次重试协议 | 第 1 次修参数 → 第 2 次换工具(impact ↔ context ↔ query)→ 第 3 次 list_repos(看索引状态)→ 仍失败 → 5 字段阻塞报告。NEVER: 直接降级为 grep/glob(违反 Article V.5 不可降级) |
| V11 Hook 清单(13 个) | 覆盖 5 种 TRAE IDE event + 3 个 V11 shell hook。V11 独有:pre-stage.sh / post-stage.sh / pre-accept.sh(shell)+ gitnexus 双端(SessionStart + Stop) |

---

## 八、V11 新增子代理 agent 类型(12 个)

| Agent | 委派 stage |
|-------|-----------|
| task-notification-agent | Stage -1 Intake |
| explore-agent | Stage 0 Plan / 0.5 Test Plan(3 路径并行探索) |
| spec-writer-agent | Stage 1 Spec |
| prototype-builder-agent | Stage 1.5 Prototype |
| contract-writer-agent | Stage 2 Contract |
| code-implementer-agent(TDD 必跑 GitNexus) | Stage 3 Implement |
| e2e-verifier-agent | Stage 3.5 Real Verify |
| review-agent(不修代码) | Stage 4 Review |
| rot-detector-agent | Stage 4.5 Rot Scan |
| archive-agent | Stage 5 Accept |
| debugger-agent(e2e 先行 FAIL 必跑 GitNexus) | Stage 6 Bug Fix |
| health-auditor-agent | Stage 7 Project Health |

---

## 九、V11 强化的概念

| 概念 | 定义 |
|------|------|
| task-execution-mode vs proactive-scan-mode | `task-execution-mode`(读取作为依据)→ 必须严格遵守 layer 白名单(fact 层);`proactive-scan-mode`(检测腐化)→ 允许扫描 process/log 层,但发现的问题**不得作为"验收依据"**,仅作为"待治理清单" |
| fact / process / log 三层文档 | fact 层(真相源,子代理必读)/ process 层(过程产物,子代理禁读)/ log 层(历史快照,可读但不验收) |
| DOC_WHITELIST 委派注入模板 | 6 字段委派头部:`[MUST-READ]` + `[PIPELINE]` + `[DOC_WHITELIST]` + `[FORBIDDEN]` + `[GITNEXUS]` + `[TASK]` + `[OUTPUT]` |
| 子代理产物三层独立验证(V11 NEW) | evidence 存在性 + pass_count 准确性 + 产物存在性。任一层不匹配 = 🛑 REJECT + 计入失败 1 次 |
| 批量并行推进三步流水线(V11 NEW) | Step 1 Exhaustive Gap Sweep → Step 2 Priority Batching(每批 ≤3 agent,上限 5)→ Step 3 Batch-Roll-Verify(全部返回 → 逐文件 git diff --stat → 死 agent 重委派) |
| 死 agent 检测(V11 NEW) | 收集预期产物文件列表 → 每个文件 git diff --stat → diff 为空 → 标记"死 agent"→ 立即重委派 |
| 视觉验证增强(V11 NEW) | Step 1 视觉任务委派前:主上下文 Read 目标截图 + 提取 hex 码值 inline 进 prompt → Step 2 子代理返回后:主上下文亲自 Read 截图 → 验证 AI 描述 vs 实际像素 → Step 3 不符立即停止。铁律:**AI 描述 ≠ 真实像素** |
| 类型系统陷阱(V11 NEW) | hash/ID/token 字符串比较必须大小写不敏感;数据库 BLOB 写入用 hex 字面量(SQLite `X'hex'`)不用字符串 |
| 破坏性操作 4 步强制流程(V11 NEW) | Step 1 列清单(find/ls/Get-ChildItem | measure)→ Step 2 用户确认 → Step 3 Trash 兜底(mv 到同盘 `_trash_<timestamp>/`)→ Step 4 跨盘/外接盘额外校验 |
| 安全自主判断三硬条件(V11 NEW) | A 范围明确 + B 可完全回滚 + C 风险可见 |
| 试水纪律 3 步(V11 NEW) | Step 1 detect(只读)→ Step 2 pilot(试水 1 个文件 + verify 验证)→ Step 3 batch(批量 + 抽检验证) |
| Process Supervisor 进程管理(V11 NEW — 项目化) | Worker Agent 禁止直接 `kill`/`taskkill`/`restart`,所有进程操作通过 Supervisor 代理。重启请求走 append-only 消息文件(禁止覆盖) |

---

## 十、Report Growth L1-L4(V11 强化)

| 等级 | 定义 | 输出 stage |
|------|------|-----------|
| L1 — 简短结论(< 1 屏) | Capability 列表 + Non-Goals + 3 路径评估 | Stage 0 Plan |
| L2 — 详细计划(1-3 屏) | AC + INV + Edge Cases + 验收标准 | Stage 1 Spec |
| L3 — 完整文档(3-10 屏) | 详细设计 + 实现细节 | Stage 2 Contract / Stage 4 Review |
| L4 — 归档完整包(10+ 屏) | 完整归档 + 知识沉淀 | Stage 5 Accept |

升 L 时机:新增独立 Capability → L1→L2;新增 ≥3 个新 API → L2→L3;新增 ≥3 stage 流转 → L3→L4

---

## 关联引用

- V10 glossary.md — V10 原始术语表（已蒸馏；V11 仓库根目录无对应文件，此处仅作历史记录）
- [V11 state-card-protocol.md](state-card-protocol.md) — 状态卡协议(含路径定义)
- [V11 skeptical-validation-protocol.md](skeptical-validation-protocol.md) — 质疑性校验协议
- [V11 common-iron-rules.md](common-iron-rules.md) — 公共铁律(含 Article XVII)
- [V11 common-anti-patterns.md](common-anti-patterns.md) — 公共反例
- [V11 SKILL.md](../SKILL.md) — 总编排器
