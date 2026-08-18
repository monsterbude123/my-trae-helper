# fullstack4TraeV11 腐化治理 + 多维度审计调度任务

## 一、任务目的（自上而下）

`skill-markets/fullstack4TraeV11/`（V12.0.0 / V11.8.7.1）近期密集升级：V11.8.6 V12 物理隔离 → V12.0.0 主版本升级 → V11.8.7 audit-fix 5/7 → V11.8.7.1 feedback06 三连修 + V11-AP17 docs/modules/ 死锁修补。CHANGELOG 显式留置 **13 项待 V12 升主版本时跟进**（case 3 followup + audit-cycle-2026-08-17 §3）。

做一次 4 维度腐化扫描 + 多视角质疑性审批，目的是把"反例越具体越有冲突嫌疑"的过时点找出来，**事实唯一、无兼容思想**，落实 V11 "骨感而非堆积 / 干净而非兼容 / 质疑而非自证"。

**硬约束**：
- 不在 skill-markets/fullstack4TraeV11/ 内 Edit / Write / Delete 任何文件（只读扫描 + 输出报告至独立目录）。
- 全程仅输出**汇报文档**，不落任何 patch / migration 脚本（修改权限归主上下文 + 用户授权）。
- 不读全局 self-improving-agent（任务自包含，只用本任务的输出目录 + 项目内 V11 资源）。
- 每次运行先 `git rev-parse HEAD` 记录 SHA，作为本轮报告唯一锚点。
- 如果本轮发现的事实与上一轮相同 → 输出 "本轮无新腐化 + 上轮 SHA=<prev>"，不重复产出。
- 引用问题，修复的过程对于文件之间的引用问题，最期望的方式就是不要出现循环引用的现象，就行代码工程一样，做一个可以解析的良好的引用模式，这样agent 可以高效关联各个文件的引用，可以快速的代码形式的调取出技能里面的文件依赖
---

## 二、强制加载协议（必须先做）

```
Step 1  Skill(name="project-rule-skill")  → 输出 needed_rules
Step 2  Skill(name="self-improving-agent")  → 注入全局经验上下文
Step 3  Read  AGENTS.md §0 / §1 / §1.1 / §1.2 / §1.11 / §1.4 / §4.1
Step 4  Read  skill-markets/fullstack4TraeV11/SKILL.md
Step 5  Read  skill-markets/fullstack4TraeV11/CHANGELOG.md 全部
Step 6  Read  skill-markets/fullstack4TraeV11/references/todos/audit-cycle-2026-08-17.md
Step 7  Read  skill-markets/fullstack4TraeV11/references/trap-instructions.yaml 全部
Step 8  Read  skill-markets/fullstack4TraeV11/references/state-card.schema.json
Step 9  Read  skill-markets/fullstack4TraeV11/registry/{gates,guards,state-machine,repair-flow,roles,stacks}.yaml
Step 10 Read  skill-markets/fullstack4TraeV11/scripts/README.md
Step 11 LS  skill-markets/fullstack4TraeV11/templates/hooks/  +  skill-markets/fullstack4TraeV11/scripts/  +  skill-markets/fullstack4TraeV11/skills/00-boot/agents/
Step 12 Read  skills/00-boot/agents/{jarvis,product-manager,tech-planner,backend-implementer,frontend-implementer,prototype-designer,qa-submitter,test-expert}.md 全部 8 角色
Step 13 Read  references/{role-protocol,sub-agent-rules,gate-configuration-protocol,skeptical-validation-protocol,project-structure,common-iron-rules,common-anti-patterns}.md
```

**禁止 Read**：本任务的 output 目录（避免污染上下文）/ .trae/rules/*.md（按 AGENTS.md §1 强制只走 project-rule-skill 网关）/ my-trae-helper 其他 skill 子目录（本任务只关心 fullstack4TraeV11）。

---

## 三、4 维度子代理并行调研（每个 sub-agent 必须 Read 完必读清单再写报告）

### Agent A — 升级目的 vs 现有反例的冲突审计

**任务**：CHANGELOG 列了 V11.0 → V12.0.0 的所有升级目的，逐条对照 `references/trap-instructions.yaml`（18 条 V11-T1~T6 + V11-JARVIS-* + V11-BH1~7 + V11-AP15~17）+ `references/common-anti-patterns.md`（22 条 P0-P3），找出：

1. **已被新规则覆盖但反例仍细描旧细节**（越具体越冲突嫌疑）→ 标记 `obsolete-detail` + 反例 ID + 文件:行 + 建议处置（删除旧细节 / 引用新规则段落）
2. **新规则存在但反例未补对应条目**（覆盖空白）→ 标记 `coverage-gap` + 新规则锚点（CHANGELOG 版本号 / SKILL.md §）+ 建议反例条目草稿
3. **新规则与反例直接矛盾**（规则说"必做 A"但反例说"禁止做 A"）→ 标记 `direct-conflict` + 双方出处 + 必须裁决方向
4. **反例本身已过时（V12 物理隔离后失去场景）** → 标记 `stale-context` + 失去场景说明

**特别关注（从本会话蒸馏结论）**：
- §15.1 路径配置说"4 类" → 旧反例 V11-AP15 说"5 脚本硬编码 3 路径"，已被 _lib_paths.py 统一；现 §15.2 显式 V11.8.7.1 REMOVED `get_changes_archive_dir`，但 trap-instructions.yaml V11-AP15 仍写 `get_changes_archive_dir`（SUPERSEDED_BY V11-AP16）—— V11-AP16 是新版，但 V11-AP15 文本中"3 个不同路径"细节是否需要删除以免误导？
- state-machine.yaml 第 26 / 32 / 36 / 41 / 46 / 51 / 56 / 61 行引用 gate id：`stage-1-spec` / `stage-2-contract` / `stage-3-implement` / `stage-3.5-real-verify` / `stage-4-review` / `stage-4.5-rot-scan` / `stage-5-accept` —— 但 gates.yaml 用的是 `stage-spec` / `stage-contract` / `stage-implement` / `stage-real-verify` / `stage-review` / `stage-rot-scan` / `stage-accept`。这是 CHANGELOG §"待 V12 升主版本跟进 13 项"中"A fix state-card `health` 字段多 § 定义冲突"未修。**确认是否仍存在 + 给出最小修复路径**。
- V11.8.7.1 SKILL.md frontmatter 写 `version: 12.0.0`，但 5 处"V11.7.0+ 设计入口"仍在多数 sub-skill 顶部出现，措辞未统一成"V12+ 设计入口"。是否系统性过时？

**输出文件**：`logs/v11-corruption-scan/<ISO-timestamp>-A-upgrade-vs-antipattern.md`
**报告结构**：
```
# Agent A 报告 — 升级目的 vs 反例冲突审计

## 元信息
- 运行时间（ISO 8601）
- V11 HEAD SHA:
- 加载 skills: [list]
- 加载 rules: [list]

## §1 已被新规则覆盖但反例仍细描旧细节（obsolete-detail）
[表格：反例 ID | 文件:行 | 旧细节 | 新规则锚点 | 建议处置]

## §2 新规则存在但反例未补对应条目（coverage-gap）
[表格：新规则锚点 | 缺失条目草稿 | 严重度]

## §3 新规则与反例直接矛盾（direct-conflict）
[表格：双方出处 | 矛盾内容 | 必裁决方向]

## §4 反例本身已过时（stale-context）
[表格：反例 ID | 失去场景说明 | 处置]

## §5 关键校验点（state-machine.yaml gate id 漂移）
[表格：state-machine.yaml 行 | 引用 gate id | gates.yaml 实际 id | 一致 / 不一致]

## §6 总结（≥3 条事实唯一结论 + ≥3 条自主决策建议）
[每条结论必须含证据锚点：file:line + git SHA]

## §7 自我质疑（必填 ≥3 项"如果不改会怎样"）
[每项质疑必含"当前腐化度量化"+ "主代理应该决策什么"]
```

---

### Agent B — 8 角色 agents 自检 + 工作流优化

**任务**：读 `skills/00-boot/agents/{jarvis,product-manager,tech-planner,backend-implementer,frontend-implementer,prototype-designer,qa-submitter,test-expert}.md` 全部 8 角色 + `references/role-protocol.md`，从每个角色的视角自检：

1. **该角色的产品文档 / 协议 / 委派头部**是否与 V12.0.0 主版本升级一致（fact/ + stage/ 物理布局？贾维斯时机 ④⑤⑥？qa-loop §3 §4？）
2. **该角色提到的脚本 / 模板 / 路径**是否仍存在于 V11 当前文件树（不存在 = stale reference）
3. **该角色禁止项**是否与 V11 反例库新条目（V11-AP15/16/17 + V11-BH 系列）冲突
4. **该角色履职矩阵**（role-protocol §1）是否每个 cell 都有对应 sub-skill 入口或引用空指针
5. **该角色如果"自检自身过时内容"**会删 / 改什么（自主决策产物：每角色 ≤3 条微调建议，附"不改理由"备选）

**特别注意**：
- `qa-submitter.md` / `test-expert.md` / `prototype-designer.md` 是 V11.9 新增的"核心新增"角色（role-protocol §2.6-2.8），但 `registry/roles.yaml` 是否存在？若不存在 → 落地路线图 §9 批次 2 未做 → 是否记录
- `tech-planner.md` 提到"[JARVIS-DELEGATION] 发起权（type: gate-design）"，jarvis.md §6 反模式 #6 提到"时机④转译 gate 时严禁放宽阈值" —— 两边一致？但 jarvis.md §2 时机④只说"接收 [JARVIS-DELEGATION]"，role-protocol §2.3 才写 tech-planner 有发起权 → 是否补全链路

**输出文件**：`logs/v11-corruption-scan/<ISO-timestamp>-B-roles-self-audit.md`
**报告结构**：
```
# Agent B 报告 — 8 角色自检 + 工作流优化

## 元信息
- 运行时间
- HEAD SHA
- 加载清单

## §1 角色 × V12 主版本一致性矩阵（8 行 × 4 列）
[表格：角色 | 物理布局一致 | 贾维斯时机一致 | qa-loop 一致 | 总分]

## §2 stale reference 清单（角色提到但不存在的资源）
[表格：角色 | 文件:行 | 引用 | 实际不存在 / 已迁 / 名称漂移]

## §3 角色禁止项 vs V11 新反例冲突
[表格：角色 | 禁止项 | 反例冲突条目 | 裁决]

## §4 履职矩阵空指针（cell 无 sub-skill 入口）
[表格：角色 × stage | 是否空指针 | 引用资源]

## §5 各角色 ≤3 条微调建议 + 不改理由备选
[每角色一节，每建议含：变更内容 + 变更文件 + 不改理由 + 风险评估]

## §6 总结 + §7 自我质疑（同 Agent A 结构）
```

---

### Agent C — 13 stage sub-skills 自检（按骨感 v2.5 + 跨 stage 一致性）

**任务**：读 13 个 stage SKILL.md（00-boot + 01-intake + 02-plan + 03-test-plan + 04-spec + 05-prototype + 06-contract + 07-implement + 08-real-verify + 09-review + 10-rot-scan + 11-accept + 12-bug-fix + 13-project-health）+ `references/vibe-coding-standards/SKILL.md` 体积铁律（v2.5 弹性 100~350 行）+ `references/constitution.md` 17 Articles，对每个 stage skill 自检：

1. **体积**：是否在弹性区间；超 350 行是否有 references/ 拆分；< 100 行是否内容空洞
2. **铁律数**：是否 ≤ 10 条；多出是冗余 / 重复 / 应迁 references/
4. **依赖声明**：frontmatter `depends_on.skills / stages / references / scripts` 是否仍在文件树内（stale dep）
5. **跨 stage 一致性**：同名 stage 在不同 SKILL.md 描述是否一致（如 "Stage 3.5 visual-evidence" 4 处是否统一）
6. **V12 物理布局接入度**：每个 stage 是否提及 `fact/` + `stage/{N}/` 物理布局（V12 强制默认）—— 未提及 = 落位规则过时
7. **贾维斯体系接入度**：是否提到 gate-integrity-guard.py hash 锁 + 7 步 gate 改动 SOP + 委派头部（[JARVIS-DELEGATION]）—— 未提 = 与 V11.7.0+ 体系脱节
8. **AC 核销门禁接入度**：Stage 4 review 是否含 `## AC 核销矩阵` 6 列格式（V11.8.7 §10.6 NEW 硬约束）—— 不含 = 与 V11.6.0 门禁制脱节

**特别注意**：
- 13 stage SKILL.md 顶部都写 "V11.7.0+ 设计入口"—— 是否统一升级到 "V12+ 设计入口"？
- Stage 1 spec SKILL.md `references/state-card-stage1-fields.md` 引用路径 ../../references/state-card-stage1-fields.md，文件实际在 skills/04-spec/references/ 下 → 跨目录引用是否合法？
- 09-review SKILL.md 是否含 prototype ↔ implementation 对照表（§3.7.2 #1 硬约束）？
- 11-accept SKILL.md 是否提 spec-knowledge-extract + spec-purge（§0.2.3 必跑）？

**输出文件**：`logs/v11-corruption-scan/<ISO-timestamp>-C-subskills-self-audit.md`
**报告结构**：
```
# Agent C 报告 — 13 stage sub-skills 自检

## 元信息
- 运行时间
- HEAD SHA
- 加载清单

## §1 体积矩阵（13 行 × 体积区间）
[表格：stage | 行数 | 区间（100-350 OK / > 350 需拆 / < 100 空洞）| 处置]

## §2 铁律数矩阵
[表格：stage | 铁律数 | ≤10 OK / >10 冗余 | 处置]

## §3 stale dependency 清单
[表格：stage | depends_on 条目 | 实际不存在 / 已迁 | 处置]

## §4 跨 stage 一致性冲突
[表格：主题 | 描述1 出处 | 描述2 出处 | 冲突点]

## §5 V12 物理布局接入度矩阵
[表格：stage | 是否提及 fact/stage | 是否提 process-layer-guard | 是否提 role-protocol §10 | 缺什么]

## §6 贾维斯体系接入度矩阵
[表格：stage | gate-integrity-guard | 7步 SOP | JARVIS-DELEGATION 头部 | 缺什么]

## §7 AC 核销门禁接入度（重点 Stage 4）
[Stage 4 必含字段 vs 实际含字段]

## §8 ≤3 条微调建议 + 不改理由（同 Agent B）

## §9 总结 + §10 自我质疑
```

---

### Agent D — 跨场景规则冲突深度盘点（按使用场景反推）

**任务**：模拟 4 个真实使用场景，从场景出发倒推 V11 当前规则是否自洽：

**场景 1：项目首次接入 V11**（全新项目）
- 主代理加载 SKILL.md → §0.5 加载协议 → `Skill(name="project-rules")` → 跑 `init-from-zero.py`
- 路径：init-from-zero.py `--rules-layout {files|skill}`（V11.8.7 NEW）二选一
- 跑完创建项目级 `docs/specs/changes/_module.md`（V11.8.7.1 NEW Step 4.6）
- **冲突检查**：state-machine.yaml `current_stage = "1/spec"`（line 26）要求 `gate: stage-1-spec`，但 gates.yaml 无此 gate id → state-card-validator.py 校验会 FAIL → 但用户跑 init-from-zero 永远初始化 OK（因为 _lib_state_card 不用 state-machine.yaml 的 gate id 字段做硬校验？）
- **必查**：state-machine.yaml gate id 漂移是否真在 runtime 触发 BLOCK？

**场景 2：Stage 4 review 提交**
- 主代理产 review-report.md → 跑 `ac-gate.py G1-G5`
- G4 要求 spec 全覆盖 + G1 矩阵存在（V11.8.7 §10.6 NEW 6 列格式：`AC-ID|类型|TC-ID|TC结果|UI证据|状态`）
- **冲突检查**：04-spec/SKILL.md 写 `ac_list.md` 是从 spec.md §Capabilities §Acceptance Criteria 提取 → 但 stage 4 实际需要的是 AC 核销矩阵（review-report.md 内）→ 这两份之间是否有同步约束？

**场景 3：Stage 5 accept 归档**
- 主代理跑 `pre-accept.sh` → 调 `spec-purge.py`（V12 保留物理布局）+ `spec-knowledge-extract.py` + 归档至 `docs/archive/done/{change_id}/`
- V11.8.7.1 后单 archive 真相源 = `docs/archive/done`，原 `docs/specs/changes/archive/` 已废弃
- **冲突检查**：CHANGELOG 提"V11.8.7.1 起 V11 扁平布局已彻底废弃" —— 但 §15.1 仍写 `paths.archive: docs/archive/done`（V11 单路径）→ V12 项目是 fact/ + stage/{N}/，archive 路径是否要改？

**场景 4：贾维斯 gate 设计委派**
- tech-planner 发起 `[JARVIS-DELEGATION] type: gate-design`
- jarvis §1 时机④接收 → 转译为 gates.yaml 条目或 gate-config.json 规则 → 重签 lock → 三态验证
- **冲突检查**：role-protocol.md §2.3 写 tech-planner 有发起权，但 jarvis.md §3 白名单未列 `registry/roles.yaml`（不存在）→ 如果落地路线图 §9 批次 2 未做，整条链路实际无法启动

**输出文件**：`logs/v11-corruption-scan/<ISO-timestamp>-D-cross-scenario-conflicts.md`
**报告结构**：
```
# Agent D 报告 — 4 场景跨规则冲突盘点

## 元信息
- 运行时间
- HEAD SHA
- 加载清单

## §1 场景 1：项目首次接入 V11
### §1.1 期望路径（按当前规则）
### §1.2 实际路径（按运行时脚本）
### §1.3 冲突点（≥3 条，每条含 file:line）
### §1.4 量化影响（受影响用户数 / 受影响项目数 / 触发概率）
### §1.5 主代理决策建议（≤3 条）

## §2 场景 2：Stage 4 review 提交
[同上 5 子节]

## §3 场景 3：Stage 5 accept 归档
[同上 5 子节]

## §4 场景 4：贾维斯 gate 设计委派
[同上 5 子节]

## §5 跨场景共有冲突（≥3 条共性腐化）
## §6 优先级矩阵（冲突 × 严重度 × 修复成本）
## §7 总结 + §8 自我质疑
```

---

## 四、质疑性审批（主代理任务 — 在 Agent A/B/C/D 都产出后由主代理执行，调度任务本身不要求子代理做这步）

每份 Agent 报告提交后，本任务在 output 末尾追加 `## §X 质疑性审批` 段：

```
1. 该 Agent 是否真读了必读清单（检查 Read 调用计数 vs 必读清单项目数）
2. 该 Agent 的"事实唯一结论"是否每条都有 file:line + git SHA 锚点
3. 该 Agent 的"自主决策建议"是否避开兼容思想（"先做 X 后兼容 Y" = 反例）
4. 该 Agent 的"自我质疑"是否 ≥3 项且每项含量化腐化度
5. 该 Agent 是否输出 PASS / FAIL 自评（PASS 必须跑过至少 1 条脚本，否则 N/A）
```

**任一质疑不达标 → 该 Agent 报告追加 [INSUFFICIENT] 标记 + 主代理下一轮调度要求重做。**

---

## 五、输出目录与文件命名（事实唯一锚点）

```
# 1. 创建时间戳目录（必须用 ISO 8601 + 本机时区 Asia/Shanghai）
mkdir -p logs/v11-corruption-scan/
TS=$(date -u +%Y-%m-%dT%H-%M-%SZ)
echo "本轮时间戳: $TS"

# 2. 记录 git SHA（不依赖工作区脏，干净状态才记录）
SHA=$(git -C skill-markets/fullstack4TraeV11 rev-parse HEAD)
echo "HEAD: $SHA"
```

**4 份报告**：`logs/v11-corruption-scan/<TS>-{A-upgrade-vs-antipattern,B-roles-self-audit,C-subskills-self-audit,D-cross-scenario-conflicts}.md`

**本任务 summary**（任务本身的最终输出）：`logs/v11-corruption-scan/<TS>-SUMMARY.md`
```
# 本轮腐化扫描总结

## 元信息
- 时间戳
- HEAD SHA
- 4 份子代理报告路径
- 各 Agent 自评 PASS/FAIL

## 跨报告共有冲突（≥5 条事实唯一）
## 本轮新发现（与上轮 SHA 比对）
## 上轮遗留（仍未解决）
## 主代理下一轮决策建议（≤5 条）
```

**如果本轮 4 份报告都标记 [INSUFFICIENT] / 跨报告无新冲突 → 仅写 SUMMARY 一行："本轮无新腐化，4 Agent 全 INSUFFICIENT 或全 PASS，上轮 SHA=<prev>"**

---

## 六、自主决策边界（不允许 / 允许）

**不允许**：
- ❌ Edit / Write / Delete 任何 skill-markets/fullstack4TraeV11/ 内文件
- ❌ 跑任何脚本（脚本可能写入状态卡 / 锁 / 归档）—— 即使是 dry-run / --validate-only
- ❌ 跑 git commit / git push / git tag
- ❌ 创建 spec/plan/test-plan 文件（属于写产物）
- ❌ 创建 trap-instructions.yaml 新条目（属于改反例库）
- ❌ 输出与 V11 现状不符的"修复 PR patch"（保留主代理决定权）

**允许**：
- ✅ Read 任何 skill-markets/fullstack4TraeV11/ 内文件
- ✅ Glob / Grep / LS 探索
- ✅ 写 logs/v11-corruption-scan/ 内 .md 报告
- ✅ 写 logs/v11-corruption-scan/<TS>-SUMMARY.md
- ✅ 在 .trae/logs/ 追加本轮时间戳 + HEAD SHA 痕迹（append-only）
- ✅ 跑 `git rev-parse HEAD` / `git status` / `git log --oneline -10`（只读）

---

## 七、失败处理（按 V11 §7 Report Growth L1-L4）

```
L1 文件系统：Read 失败 → 记录文件路径 + 跳过该维度（不阻断）
L2 Agent 执行：sub-agent 失败 → 重试 1 次（同 agent_type）→ 仍失败 → 标 [INSUFFICIENT]
L3 状态不一致：本轮 SHA 与上轮不一致但本轮无新发现 → 标 [STALLED]
L4 外部依赖：网络 / MCP 不可用 → 降级 Read 模式 + 报告"工具降级，引用质量降低"
```

**3 次 sub-agent 失败 → 停止当轮，写 SUMMARY 注明阻塞 + 不输出报告，等待下轮重跑。**

---

## 八、本任务与 AGENTS.md / CHANGELOG 的引用

- AGENTS.md §4.2 反例："不给 P0/P1/P2 配硬性条数" — 本任务自主决策建议不强制条数，但要求每条含证据
- AGENTS.md §1.4 经验沉淀路由：本任务不写全局 self-improving-agent（本任务自包含）
- AGENTS.md §1.11 guard/gate 注册表：本任务不动 registry/ / scripts/<name>-guard.* / .husky/<name>-gate（属于 guard-smith 域）
- CHANGELOG.md V12.0.0 段：V12 物理布局事实唯一源（fact/ + stage/{N}/），本任务引用此为基准
- CHANGELOG.md V11.8.7.1 段：5 项硬要求已修，本任务不再质疑这 5 项，专注 13 项待跟进

