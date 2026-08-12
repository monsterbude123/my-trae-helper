# 子代理通用铁律（V11 — 蒸馏自 V10.8 实操）

> V11 全 agent 通用，主上下文委派时引用本文件路径（不内联全文）。
> 关联: [stage-skill-agent-protocol.md](stage-skill-agent-protocol.md) 委派速查 + [bug-workflow](../../skills/12-bug-fix/references/bug-state-machine.md) 任务路由 + [document-layer.md](document-layer.md) 索引器范围 + [acceptance-gates-v10.md](stage-interaction-protocol.md) 通过依据 + [agent-error-diagnosis.md](agent-error-diagnosis.md) 错误诊断。

---

## §0. 主上下文 Skill 加载必读清单（V11 NEW — 防再放）

> 来源：V10.9 用户反馈（4 轮返工蒸馏）+ V11 §0.5 加载协议。

主上下文加载任意 skill 后，**必读**以下 references（如该 skill 有）：

| 类别 | 必读文件 | 用途 |
|------|----------|------|
| 铁律 | `references/common-iron-rules.md` | 17 Articles 必走 |
| 反例 | `references/common-anti-patterns.md` | 22 反例避坑 |
| 委派 | `references/sub-agent-rules.md` | 委派注入模板（本文件即此） |
| 入门 | `references/stage-skill-agent-protocol.md` | agent 使用 stage skill 4 步协议 |
| 诊断 | `references/agent-error-diagnosis.md` | agent 失败 5 模式根因 |
| Constitution | `references/constitution.md` | 17 Articles 全文 |

### 主上下文启动检查清单

```
□ Skill SKILL.md 已加载
□ references/ 目录已 LS
□ 必读 6 个 references（按上表）
□ Glob 项目同类约定目录（每次必做）
□ 列"我能踩的雷"清单（反例 §19-22 + 现有 Article V/IX/XI 必逐项）
□ 询问用户"项目惯例 vs skill 默认"差异（如有冲突）
□ 才进入工作模式（详见 SKILL.md §0.5）
```

### 用户提到"代号式 / 段号 / 编号"等命名偏好时

- ❌ 错误：直接动手建目录
- ✅ 正确：先搜项目内 Glob `**/NN-NN-*/`、`**/{L0,L1}-*/`，看现有命名 → 不存在 → 询问用户"是要新建项目级约定，还是续编现有"

---

## §1. 文档分层（3 条 — V10.8 蒸馏）

- **只读 fact 层**：contracts/、spec.md、ARCHITECTURE.md、模块文档 — `task-execution-mode` 必读
- **禁读 process 层**：diagnose.md、fix_result.md、分析手记、v1v2v3 — 主上下文提取事实摘要注入，子代理不主动读
- **log 层不作依据**：changelog、commit log、review 报告 — 可看但不作验收依据

### 1.1 主动扫描 vs 任务执行读取区分（V11 — 修正冲突）

```
`task-execution-mode` (读取作为依据) → 必须严格遵守 layer 白名单（fact 层）
`proactive-scan-mode` (检测腐化)    → 允许扫描 process/log 层
                                        但发现的问题不得作为"验收依据"，仅作为"待治理清单"
```

- Reviewer `task-execution-mode` 禁读 `docs/reports/`(log 层)，但可在 Review 阶段 `proactive-scan-mode` 主动扫描历史报告作为对照（不作验收依据）
- Rot Detector `proactive-scan-mode` 允许读 `docs/`，但 `task-execution-mode` 禁止读 process/log 层
- 索引器扫描范围详见 [document-layer.md](document-layer.md) §索引器范围白/黑名单

---

## §2. 证据规则（3 条）

- **raw_payload 优先**：字段语义以当前原始数据为准，不以历史诊断结论为准
- **历史结论不复用**：上一会话的判定 = 线索，不是事实；需重新取证验证
- **完成 = 多维可观测**：status=SUCCESS 必须含 ≥3 维证据（文件+测试+hash/DB/CSV）

---

## §3. 上下文经济（4 条）

- **只读白名单**：主上下文注入 [DOC_WHITELIST]，白名单外不读
- **不遍历目录**：禁止 `ls docs/bugs/` 或 `glob docs/reports/*` 考古
- **不复制全文**：引用路径，不把文档内容搬进 prompt 或产物
- **大索引文件禁读**：`DOCSMAP.md` / `.docmap.json` / `.docindex.json` 等机器索引文件动辄数万行，直接 Read 会瞬间击穿上下文。查询文档始终用 `query-index.py --grab/--lookup/--file` 等工具，禁止直接 Read 这些文件

---

## §4. 汇报纪律（2 条）

- **≤300 字符**：Completion Report 只含 status / evidence(file:line) / pass_count / next_hook
- **详情走 json**：详细产物放 `.trae/logs/agent-detail/`，不进 markdown 报告

---

## §5. 失败处理（4 条）

- **连续 2 次失败 → 切 agent 类型**：不继续派同一 agent
- **5 次失败 → rescue hatch**：回退 Stage 0 重做需求分析
- **禁止应付性汇报**：不说"我搞错了""子代理给了虚假内容""应该 xxxx"——发现问题直接报告现状 + 阻塞点，不道歉不甩锅
- **禁止编造 evidence**：evidence 必须指向真实 file:line，pass_count 必须与实际测试结果一致；主上下文会独立抽检，造假 = 🛑 REJECT + 计入失败计数

---

## §6. 视觉任务铁律

- **视觉任务委派前必须 Read 至少 1 张目标截图** inline 进 prompt
- **视觉 token 不能写形容词**（"墨绿"），必须写 hex/rgb（#1a3a2a）
- **委派 prompt 必须含"相差超过 50% 停下报告"**：如果实现与截图相差超过 50%，立即停下报告，不要交付骨架
- **主上下文不许凭印象猜视觉**——必须现场 Read 截图/录屏帧再下结论

---

## §7. 委派注入模板（V11 升级）

> 完整 6 字段委派头部详见 [stage-skill-agent-protocol.md §1](stage-skill-agent-protocol.md)。

```
[MUST-READ] AGENTS.md + .trae/rules/
[PIPELINE] stage: {N}
[DOC_WHITELIST] {whitelist}
[FORBIDDEN] docs/archive/**, .trae/tmp/**, diagnostic/bugs/**
[GITNEXUS] impact()
[TASK] {≤200 chars}
[OUTPUT] 4 字段: status / evidence / pass_count / next_hook
```

---

## §8. 子代理产物三层独立验证（V11 NEW）

```
MUST: 子代理返回 Completion Report 后，主上下文必须独立验证三层
  ├─ evidence 存在性: 随机抽 1 个 → 主上下文亲自 Read 验证内容匹配
  ├─ pass_count 准确性: 主上下文亲自运行测试命令 → 对比实际输出
  └─ 产物存在性: 主上下文亲自 Glob/LS 验证文件存在

NEVER: 子代理返回 "PASS" 就直接接受
```

任一层不匹配 = 🛑 REJECT + 计入失败 1 次。

### 反例 8.1 — evidence 造假主上下文盲信

```
现象: implementer 自评 32/32 PASS，evidence 指向 file:line 但该行内容不匹配
根因: 主上下文未独立抽检 evidence，盲信 Completion Report
教训: 每次必须随机抽 1 个 evidence → 主上下文亲自 Read 验证
```

---

## §9. 批量并行推进三步流水线（V11 NEW）

适用: 单次 change 需实施 20+ 个独立子任务，任务间无强依赖。

```
Step 1 Exhaustive Gap Sweep: 左端读目标参照物 + 右端盘点当前实现 → P0/P1/P2 分级 gap 清单
Step 2 Priority Batching: P0→批次1，P1→批次2+，P2→末批；每批 ≤3 agent（上限 5）
Step 3 Batch-Roll-Verify: 全部返回 → 逐文件 git diff --stat → 死 agent 重委派 → 通过后下一批
```

MUST: 每批 agent 返回后必须 `git diff --stat` 逐文件确认（agent 可能返回无关内容但无报错）。
NEVER: 单批次并行 >5 个 agent；强依赖任务放入同一批次。

### 9.1 死 agent 检测

```
Step 1 收集该批次预期产物文件列表
Step 2 对每个文件 git diff --stat
Step 3 diff 为空 → 标记 "死 agent"
Step 4 立即重委派（不等下一批）
Step 5 重委派后再次验证
```

### 反例 9.1 — agent 返回无关内容但无报错

```
现象: implementer-J 任务为实现某组件，返回一段"Skill 工具"介绍文字（无报错 Completion Report 正常）
根因: agent 误进入无关分支，主上下文未 git diff 验证 → 任务实际未执行
教训: git diff --stat 是唯一权威证据；agent "看起来返回了" 不等于任务做了
```

---

## §10. 视觉验证增强（V11 NEW）

```
Step 1 视觉任务委派前: 主上下文 Read 目标截图 + 提取 hex 码值 inline 进 prompt
Step 2 子代理返回视觉产物后: 主上下文亲自 Read 截图 → 验证 AI 描述 vs 实际像素
Step 3 发现 AI 描述与实际不符 → 立即停止，不编造事实
```

铁律: **AI 描述 ≠ 真实像素**。

### 反例 10.1 — 把 AI 描述当成真实像素

```
现象: 主上下文 Read PNG 工具返回 AI 描述，编造"日志显示 XXX 路径"
根因: 把 AI 描述当成真实截图内容，未亲自对比像素
教训: 主上下文必须亲自 Read 截图 + 对比 AI 描述 vs 实际像素；不符立即停止
```

---

## §11. 类型系统陷阱（V11 NEW）

数据"看起来对"但验证失败时，检查实际存储格式 vs 预期格式。铁律: 任何 hash/ID/token 字符串比较必须用大小写不敏感比较（外部 API 大写 vs hasher 输出小写）；数据库 BLOB 写入用 hex 字面量（SQLite `X'hex'`）不用字符串。

---

## §12. 破坏性操作 4 步强制流程（V11 NEW）

适用: `rmtree` / `rm -rf` / `Remove-Item -Recurse -Force` / 跨盘整目录 mv / 不在 git 跟踪的大文件 Delete / 任何外接盘整目录操作。

```
Step 1 列清单（强制）: 输出"将影响路径列表 + 估算字节数"（find/ls/Get-ChildItem | measure）
Step 2 用户确认（强制）: 清单+字节数+风险（不可逆 vs 可恢复）发给用户，回复"确认"前禁止执行
Step 3 Trash 兜底（强制）: 删除前先 mv 到同盘 _trash_<timestamp>/，保留 7 天可恢复
Step 4 跨盘/外接盘额外校验: 即使 implementer 报告"目录为空"，主上下文也要自己 ls 一次
```

主上下文责任（升级到 P0）:
- 委派含"删除/移动/restore"任务前 → 注入"破坏性操作清单模板"
- implementer 返回后 → 主上下文自己 ls 确认（不信描述）
- 任何"测试后 rmtree/cleanup" → 默认禁止，只能 mv 到 _trash

### 反例 12.1 — 测试后无确认直接 rmtree

```
现象: implementer 在 E2E 测试后无确认直接 rmtree 整个目录，永久删除用户累计数据
根因: 规则未写明"破坏性操作必须先列清单 + 用户确认 + trash 兜底"
教训: 任何"测试后 cleanup"默认禁止，只能 mv 到 _trash_<ts>/；主上下文不信 implementer 描述
```

---

## §13. 安全自主判断三硬条件（V11 NEW）

用户授权"安全的就自己决策"，但"安全"必须同时满足三硬条件。

```
A. 范围明确: 用户指定具体路径/文件/数量（非"帮我清一下"模糊指令）
B. 可完全回滚: trash/反向 mv/字节级可还原（不可恢复 = 不允许自主）
C. 风险可见: 字节数/路径/影响范围能执行前列出
```

红线清单（即使事后追认也视为结构性失败）:
- 任何 `rmtree` / `rm -rf` / `Remove-Item -Recurse -Force`
- 不在 git 跟踪的大文件 Delete（阈值项目化）+ mv 后不保留 trash
- 外接盘整目录 mv 或 Delete（即使"目录看起来是空的"）
- 不可逆数据变换（覆写原文件 / sha256 改变原文件）

收到用户"别用力过猛/三思而行" → 立即降级为最小动作 + 后续每步先汇报意图等确认。"安全所以自主" ≠ "任务扩展所以自主"。

---

## §14. 试水纪律 3 步（V11 NEW）

```
Step 1 detect: 检测候选（只读，不动文件）
Step 2 pilot: 试水 1 个文件 + verify 验证（通过才进 batch）
Step 3 batch: 批量 + 抽检验证
FAIL 立刻停 → 走紧急恢复（trash 还原 / 反向 mv）
```

---

## §15. 进程管理 Process Supervisor（V11 NEW — 项目化，按需启用）

> 触发: 多 Agent 并发协作需要重启应用服务时。本节为项目化方案，非通用铁律；
> 项目可按需实现自己的 Supervisor，核心原则通用：Worker Agent 禁止直接 kill，统一代理。

通用原则（项目实现自己的 Supervisor 时遵循）:
- Worker Agent 禁止直接 `kill`/`taskkill`/`restart`，所有进程操作通过 Supervisor 代理
- 重启请求走 append-only 消息文件（禁止覆盖），Supervisor 负责去重 + 冷却 + 熔断
- 热更新判定: `--reload`/HMR 模式自动生效，否则需重启

项目化部分（.agent.msg 格式、LRU 容量、冷却阈值等）由项目自行定义，不在此强制。

---

## 自检清单（子代理返回后必走）

```
子代理返回后:
  [ ] §8 三层验证: evidence Read + pass_count 跑测试 + 产物 Glob
  [ ] §9 批量场景: git diff --stat 检测死 agent
  [ ] §10 视觉任务: 主上下文亲自 Read 截图 + 对比 AI 描述
  [ ] §12 破坏性操作: 主上下文自己 ls 确认（不信 implementer 描述）

任一答 N → 🛑 不放行
```

---

## 关联引用

- [stage-skill-agent-protocol.md](stage-skill-agent-protocol.md) — agent 调用 stage skill 标准协议
- [agent-error-diagnosis.md](agent-error-diagnosis.md) — 5 模式失败根因
- [common-iron-rules.md](common-iron-rules.md) — 17 Articles
- [common-anti-patterns.md](common-anti-patterns.md) — 22 反例
- [document-layer.md](document-layer.md) — 索引器范围白/黑名单
- [stage-interaction-protocol.md](stage-interaction-protocol.md) — 通过依据 3 类分层
- V10 来源（开发期）: `../../fullstack4TraeV10/references/sub-agent-rules.md`