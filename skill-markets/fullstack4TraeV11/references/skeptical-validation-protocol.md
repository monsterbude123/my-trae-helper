# 质疑性校验协议 — Skeptical Validation Protocol

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> **触发**: 任何 P0/P1 决策、升级方案、子代理"完成"声明、方向二选一、文档漂移疑似。
> **核心立场**: 接受输入前必须独立校验,不盲信。
> **本质**: 防止"看似合理的修复"实际是"矫枉过正"或"重复造轮子"。
> **永久激活 stage**: Plan / Spec / Contract / Implement / Review / Bug Fix / Project Health。

---

## §0 触发场景

```
MUST 激活质疑性校验:
  - 用户提出 P0/P1 缺陷清单（任何"必须修"列表）
  - 用户提出升级方案（含具体修改点）
  - 子代理返回"完成"/"通过"声明
  - Agent 在两个方向间二选一时
  - 文档与现实疑似漂移（路径不存在 / 描述不符）

不适用:
  - 用户明确"按 X 执行"且 X 已通过质疑性校验
  - 纯文本查询（Read/Glob 不触发）
  - 子代理返回的 evidence 已附 file:line 且通过 Read 抽检
```

---

## §1 P0/P1 必要性质疑（4 维度）

针对每个 P0/P1 主张,独立校验:

### §1.1 根因验证

```
质疑: 这是真问题吗？还是衍生品？
检查:
  [ ] 引用的章节/SKILL.md 条款真实存在？（不基于"应该存在"决策）
  [ ] 失效模式有真实证据？（用户反馈 / 日志 / 测试报告，不是"理论推断"）
  [ ] 根因不在更上游？（如果根因在 A，P0/P1 只修了 B，则修复是衍生品）

输出: 根因定位 file:line + 失效证据 + 影响面估算
```

### §1.2 责任主体校验

```
质疑: 这个修复应该改在哪个文件/哪一层？
检查:
  [ ] 改在当前层 vs 改在上游层，效果是否一致？
  [ ] 已有别的 skill/rule 是否已覆盖？（避免重复）
  [ ] 改在错误位置会导致什么？

输出: 修复位置论证 + 拒绝方案 + 候选位置列表

反例: "反向提示词挂 implementer/reviewer 铁律"
  → 质疑发现 reviewer.md 已有 ZERO TRUST + EVIDENCE MANDATORY 等价铁律
  → 改 reviewer.md = 冗余（矫枉过正）
```

### §1.3 与已有规则重叠校验

```
质疑: 新加的规则和已有的规则是补强还是重复？
检查:
  [ ] 现有规则 grep 关键词，命中几处？
  [ ] 已覆盖章节的"反向提示词" / "NEVER" 是否已包含新主张？
  [ ] 新规则的"差异化"在哪里？必须说清楚"已有的没说 X，新加是为了 X"

输出: 重叠检查表 + 差异化论证

反例: §0.10 启动验证加"Playwright 截图 ≥1 张"
  → 质疑发现 acceptance-gates §通过依据 [2] 已有同等约束
  → 但 §0.10 是 Phase 3.5 实施者层，[2] 是 Phase 4 Review 层 — 不重叠
  → 处理: §0.10 缩窄为"可见产物定义"，明示边界区分
```

### §1.4 修复成本 vs 价值校验

```
质疑: 这个修复值得做吗？
检查:
  [ ] 修复行数 / 影响范围（10 行 vs 100 行）
  [ ] 是否破坏 Article XI（skill 文件遵循 vibe-coding-standards v2.5 弹性 100~350 行）
  [ ] 是否有更低成本的等价方案？（如文档引用优于内联）
  [ ] 修复能否被"挂载时机"取代？

输出: 成本估算 + 替代方案 + 推荐处理（采纳 / 缩窄 / 取消）

反例: 反向提示词挂 reviewer.md 铁律
  → 成本: 改 reviewer.md 1 行
  → 价值: 0（已覆盖）
  → 推荐: 取消
```

---

## §2 通用质疑三层（防盲信）

### §2.1 问题质疑层

```
检查问题的"前提合法性":
  [ ] 错误前提: 描述基于不存在的路径 / 不存在的章节 / 不存在的规则
      → 不基于错误前提决策，直接指出
  [ ] 逻辑跳跃: "A 出错 → 必须修 B" 但 A 与 B 的因果没证明
      → 列出 A→B 的因果链，要求证据
  [ ] 信息缺失: 缺少必要的上下文（哪个项目 / 哪个版本 / 哪个文件）
      → 补全信息后再决策
```

### §2.2 方案质疑层

```
检查方案的"必要性 + 副作用":
  [ ] 必要性: 这个修复真的解决问题，还是治标不治本？
  [ ] 副作用: 改了这里，会不会破坏那里的约束？
  [ ] 替代方案: 有没有更简单的做法？
  [ ] 优先级: 是 P0 还是 P1？敢不敢延后？
```

### §2.3 实施质疑层

```
检查实施的"可执行性 + 验证手段":
  [ ] 路径是否真实存在？（不是基于"应该存在"）
  [ ] 委派协议是否触发？（仅在 SKILL.md 写不算，挂到铁律才算）
  [ ] 验证手段是什么？（evidence 抽检 / phase-gate / 单元测试）
  [ ] 失败兜底: 改了之后回归测试怎么办？
```

---

## §3 强制声明格式（升级方案回报必走）

每次汇报升级方案前必须按此格式声明:

```markdown
## 质疑性校验通过依据

### [1] 根因验证
- ✅/⚠️/❌ 引用的章节/SKILL.md 条款真实存在 — 证据: file:line
- ✅/⚠️/❌ 失效模式有真实证据 — 证据: 用户反馈/日志/测试报告

### [2] 责任主体校验
- ✅/⚠️/❌ 修复位置 vs 上游层效果一致 — 论证
- ✅/⚠️/❌ 已有 skill/rule 不覆盖 — grep 结果

### [3] 与已有规则重叠校验
- ✅/⚠️/❌ 现有规则 grep 不重叠 — grep 关键词
- ✅/⚠️/❌ 新规则差异化 — 一句话说明

### [4] 修复成本 vs 价值
- ✅/⚠️/❌ 修复行数 / 影响范围 — 数字
- ✅/⚠️/❌ 不破坏 Article XI 铁律 — 论证
- ✅/⚠️/❌ 替代方案已评估 — 列 1-2 个

结论: [1][2][3][4] 全 ✅ → 可执行 / 任一 ❌ → 修正方案
```

---

## §4 反例库（8 条 — V10 蒸馏 5 + V11 新增 2 + V11.2 新增 1）

### 反例 1: 盲信 P0 必要性（V10 蒸馏）

```
现象: 反馈会话列出 5 条 P0，主上下文未质疑直接采纳
后果: P0-2"反向提示词挂铁律"实际是冗余（已有等价铁律），属于矫枉过正
教训: P0/P1 必须按 §1.1-§1.4 四维度独立校验，不基于"用户列了就是 P0"
```

### 反例 2: 责任主体误判（V10 蒸馏）

```
现象: "Playwright MCP :filename Downloads 陷阱"反馈归属到 fullstack4TraeV10
实际: 陷阱是 MCP 工具行为，应归 screenshot skill 或 视觉证据铁律
教训: 修复前必须 §1.2 责任主体校验，不基于"反馈语境就改当前包"
```

### 反例 3: 与已有规则重叠未检出（V10 蒸馏）

```
现象: §0.10 启动验证加 "Playwright 截图 ≥1 张"
实际: acceptance-gates §通过依据 [2] 已有同等约束
处理: 缩窄为"可见产物定义"，明示两层边界
教训: §1.3 grep 现有规则关键词是必做，不是可选
```

### 反例 4: AGENTS.md 路径漂移盲信（V10 蒸馏）

```
现象: AGENTS.md 写"`.trae/skills/skill-optimization-method/SKILL.md`"
实际: 路径不存在，真实文件在 `skill-markets/fullstack4TraeV10/references/`
教训: 引用任何路径前必须 Glob 验证，不基于"AGENTS.md 写的就存在"
```

### 反例 5: 验收"货不对版"盲信（V10 蒸馏）

```
现象: implementer 提交"模型管理"任务，evidence 是欢迎页截图
      reviewer 看到"有截图" → 放行
实际: evidence 与当前 feature 完全无关（货不对版）
根因: reviewer 跳过产品侧验收，只看 evidence 路径不看内容
教训: 验收必须按三件必读（用户原文 + spec.md + evidence 实际内容）
      强制 3 问判定（需求归属 / 行为匹配 / 用户会认可吗）
      任一 ❌ → 失败分类标签 + 自动循环机制
```

### 反例 6: 子代理"循环 PASS"盲信（V11 新增 — 来被子代理反思)

```
现象: 子代理报告"主上下文 Read 通过"，主上下文未实际 Read 就采纳
      Round 2 自评 PASS 4.75/5，Round 3 才发现证据是空白页面
根因: 未执行 Article IX.1"主上下文亲自跑测、亲自抽检"
教训: 子代理报告"主上下文 X 通过" → 主上下文必须实际执行 X
关联: [agent-error-diagnosis.md §1](agent-error-diagnosis.md) + [loop-pass-pattern.md](loop-pass-pattern.md)
```

### 反例 7: Secret 进工具参数（V11 新增 — 来自子代理反思)

```
现象: 用户提供的密码写到工具调用参数里，进入工具日志 = 明文泄露
根因: 没有"用户 secret 必须 redacted"硬约束
教训: 用户提供的密码/token/API key → 用环境变量或 .env 注入，绝不写到工具调用参数
关联: [common-iron-rules.md Article XVII](common-iron-rules.md) + [secret-in-tool-arg.md](secret-in-tool-arg.md)
```

### 反例 8: 跳过 §0.5 加载协议（V11.2 新增 — 蒸馏自 canvas-asset-folders 实战)

```
现象: agent 收到 "Use Skill: fullstack4traev11" 后，跳过 §0.5 加载协议 9 步，
      直接用 grep/Glob 搜项目 rules 或套用 V10 残留路径（如 .trae/state-card.md）
根因:
  - 不知道 §0.5 Step 3 必须强制调 Skill(name="project-rules")
  - 不知道 §0.5 Step 5 必须核对 V11 标准路径（docs/specs/.state-card.md）
  - 套用项目 config.yaml 里的 V10 旧字段，未核对 V11 §1.1 协议
教训:
  - 收到任何 V11 触发后必走 §0.5 9 步加载协议
  - Step 3 强制调 Skill(name="project-rules")（如项目已有 .trae/skills/project_rules_skills/）
  - Step 5 核对状态卡路径 docs/specs/.state-card.md（项目级）/ docs/specs/changes/{id}/.state-card.md（change 级）
  - 禁止用 .trae/state-card.md（V10 残留）
关联: [SKILL.md §0.5](../SKILL.md) + [state-card-protocol.md §1.1](state-card-protocol.md)
```

---

## §5 与现有规则的关系

| 现有规则 | 关系 | 协作 |
|---------|------|------|
| [constitution.md Article XVI](constitution.md) | 宪法层 | 本协议是 Article XVI 的可执行展开 |
| [common-iron-rules.md Article XVII](common-iron-rules.md) | 互补 | §1.1 根因"必须证据" + Article XVII secret redaction |
| [agent-error-diagnosis.md](agent-error-diagnosis.md) | 诊断手册 | §4 反例 6/7 来自 agent 5 模式 |
| [common-anti-patterns.md §19-22](common-anti-patterns.md) | 反例库 | §4 反例 6/7 的索引 |
| skill-optimization-method.md | 父级方法论（已蒸馏到 V11 common-iron-rules.md） | 触发词"升级前" + §1 Step 0 引用本协议 |

---

## §6 验收门禁

```
升级方案汇报前自检:
  [ ] 已按 §3 强制声明格式回复
  [ ] 4 维度质疑校验全 ✅ 或显式标 ⚠️
  [ ] 任一 ❌ → 修正方案，不接受"P0 用户说了就必须做"借口

reviewer 验收升级:
  [ ] 主代理回复含 §3 格式声明
  [ ] 4 维度独立验证（不基于主代理自述）
  [ ] 反例 §4 的 7 种盲信模式已检查
```

---

## §7 永久激活 stage 清单

以下 stage 的 SKILL.md 铁律必须引用本协议(不是只引用 Article XVI):

| Stage | 铁律编号 | 引用方式 |
|-------|---------|---------|
| 0 Plan | 铁律 7 | "P0/P1 规划按 [skeptical-validation-protocol.md] 走质疑性校验" |
| 1 Spec | 铁律 10 | "P0/P1 spec 按 [skeptical-validation-protocol.md] 质疑性校验" |
| 1.5 Prototype | 铁律 3 | "designer-handoff P0/P1 边缘状态(hover/loading/error/empty)按 [skeptical-validation-protocol.md] 质疑性校验 — V11.2 NEW(蒸馏自 05-prototype 自检报告 §问题 1)" |
| 2 Contract | 铁律 10 | "P0/P1 修复按 [skeptical-validation-protocol.md] 质疑性校验" |
| 3 Implement | 铁律 9 | "实现方案/升级改动走 [skeptical-validation-protocol.md]" |
| 4 Review | 铁律 9-10 | "质疑式验收 SUITE + SKEPTICAL VALIDATION 必走" |
| 6 Bug Fix | 铁律 8 | "P0/P1 bug 修复按 [skeptical-validation-protocol.md] 质疑性校验" |
| 7 Project Health | 铁律 4 | "防失真机制按 [skeptical-validation-protocol.md]" |

---

*来源: V10 `references/skeptical-validation-protocol.md`(240 行)+ V11 子代理反思新增反例 6/7。*
*版本: 2.0.0 — V11 完整继承 + 新增 2 反例 + §7 永久激活清单。*
