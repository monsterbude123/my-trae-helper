# V11 项目级生态管理规范(§14)

> **来源**:V12 SKILL.md §14(项目级生态管理 + V11.8.7 三件套)
> **蒸馏日期**:2026-08-19(从 SKILL.md §14 抽出,合并 §14.1~§14.5)
> **适用对象**:任何 stage skill 涉及项目级配置改动(.trae/rules/ / .trae/skills/project_rules_skills/ / .trae/hooks/ / AGENTS.md 等)

---

## §14.1 5 项铁律

```
1. 单点入口原则      所有项目级规则通过 .trae/skills/project_rules_skills/SKILL.md 路由,
                    按需加载 references/,禁止 agent 直接 Read .trae/rules/{name}.md

2. 物理移走原则      init-from-zero.py --rules-as-skill 必须 move(物理删除源文件)而非 copy,
                    .trae/rules/ 物理状态 = 仅 README.md

3. README 幂等原则  项目拥有 .trae/rules/README.md,init 不强制覆盖,
                    只在缺"project-rules skill 入口"声明时追加入口段

4. 占位模板兜底      项目无 rules 时,从 V11 templates/project-rules-example/ 复制占位,
                    但 README 由项目自己创建,init 不复制

5. 整合协议必走      agent 创建 project-rules skill 后,必走 5 步整合:
                    Read all → 检查 V11 内部重叠 → 完全重叠删除 / 部分重叠保留独有部分 → 纯机械挪移 = 无意义
```

### §14.1.1 V11.8.7 蒸馏补 — 项目级 rules skill 创建 三件套(NEW — 2026-08-18)

**背景**: 任何 agent / sub-agent 在新项目初始阶段被用户/编排器叫去"建立 project rules skills",必须遵循三件套。

```
三件套(强制,缺一即 🛑 REJECT):
1. 强制多选         — 一个项目至少包含 2-3 个 rules(如 stack.md + paths.md + git.md),禁止单 rule
                     (项目级 rules 必须 multi-select — 任何场景都触发 ≥ 2 行 §2 路由表)
2. 强制漏选审查     — 选完后必走 7 维 checklist(paths/code-style/build/git/bug/asset/uncertainty)
                     任一维度 □ 但未加载 → 强制补充,不允许跳过
3. 强制用户通知     — agent 完成配置文件清单后必须主动告知用户
                     格式: 📋 Rules 加载通知(场景 + 命中数 + 漏选数 + checklist 命中)
                     就算一个没选也要说明理由(N/A 描述),禁止静默

铁律覆盖顺序:本 §14.1.1 三件套 > 上述 §14.1 5 项铁律
```

**V11.8.7 必调的两份模板**(已强化,勿私自改写):

| 模板 | 用途 | 必带版本标记 |
|------|------|------------|
| [`templates/project-rules-skill-template/SKILL.md`](../templates/project-rules-skill-template/SKILL.md) | 新建项目时 --rules-as-skill 生成入口 | V11.8.7+ |
| [`templates/project-rules-example/README.md`](../templates/project-rules-example/README.md) | 占位 rule 4 件套 + 7 维 checklist | V11.8.7+ |

**两份模板必含的元素**(agent 自检清单 — 用于检测 init-from-zero.py 输出):

```yaml
- [ ] §0 三件套铁律(强制多选 / 漏选审查 / 用户通知)
- [ ] §2 路由表强制多选(单选 = 反例)
- [ ] §3.5 7 维漏选审查 checklist
- [ ] §4 Completion Report 含 checklist_summary 字段
- [ ] §5 主代理头部 [PROJECT-RULES-GATE] 含 MUST: 多选 / 漏选 / 通知
- [ ] §5 用户通知格式 📋 Rules 加载通知 markdown 块
- [ ] §7 反模式含"单选 1 条 rule" / "选了不 Read" / "不通知用户"
```

---

## §14.2 后续 stage 引用本规范的触发词

| 触发词 | 必引用本规范 |
|--------|------------|
| 改 .trae/rules/ 任何文件 | §14.1 铁律 1-5 + §14.1.1 三件套 |
| 改 init-from-zero.py Step 5 相关逻辑 | §14.1 铁律 2-4 + §14.1.1 |
| 改 .trae/skills/project_rules_skills/ 内容 | §14.1 铁律 1 + 5 + §14.1.1 |
| **新建/初始化 project rules skills(任意 agent)** | **§14.1.1 三件套强制 + 模板必含 7 元素自检** |
| 新建项目级配置文件(如 .trae/hooks/ 新 hook) | §14.1 铁律 1 + README 幂等 |
| sub-agent 提到"项目惯例" | §14.1 铁律 5(先整合再决策) |

---

## §14.3 反例(违反任一即 REJECT)

| 反例 | 后果 |
|------|------|
| 复制 rule 到 references/ 而不删源文件 | 双份真相, agent 读错版本 |
| 强制覆盖 .trae/rules/README.md | 项目自定义内容被破坏 |
| 无 rules 时跳过 --rules-as-skill | SKILL.md §0.5 Step 3 协议等不到触发条件 |
| 纯机械挪移 rule 不做内容整合 | V11 已含内容重复占用 context |
| agent 直接 Read .trae/rules/*.md 而不走 skill 入口 | context 撑爆(违反 §0.5 Step 3) |
| **V11.8.7 NEW** init-from-zero.py 输出 SKILL.md 缺三件套(多选/漏选/通知) | 项目级 rules skill 等于失能 |
| **V11.8.7 NEW** 项目仅含 1 个 rule(如只有 stack.md) | commit 时全乱(违反多选铁律) |
| **V11.8.7 NEW** 创建完未通知用户选了哪些 | 用户无法把关(违反通知铁律) |
| **V11.8.7 NEW** 未走 7 维 checklist 自审 | 必漏掉 1-2 个 rule,产物报错 |

---

## §14.4 关联引用

- §0.5 Step 3 -- 项目级 rules 强制加载入口(Skill(name="project-rules"))
- §0.5.2 加载后验证 -- LS .trae/skills/project_rules_skills/SKILL.md 存在性
- scripts/init-from-zero.py -- Step 5(V11.2 MOVE 模式 + README 幂等 + 占位兜底)
- templates/project-rules-skill-template/ -- project-rules skill 入口模板
- templates/project-rules-example/ -- 占位 rule 模板(4 个文件 + README)

---

## §14.5 项目级 rules > V12 通用层优先级(V12.0.0 已授权)

```
当 V12 通用层(~/.trae-cn/skills/fullstack4TraeV11/)与项目级 rules(.trae/skills/project_rules_skills/)冲突时:

MUST: 项目级 rules 优先于 V12 通用层
MUST: 项目级 .trae/skills/project_rules_skills/references/anti-patterns.md 可补 V12 通用层缺失的反例
MUST: 项目级 .trae/skills/project_rules_skills/rules/governance.md 可强制 V12 通用层未硬化的门槛(如视觉证据)
NEVER: 盲信 V12 通用层, 缺项目级叠加(违反 Article XVI §1.4 重叠校验的反向)
```

**适用场景(V12 通用层缺位时的项目级补全范式)**:

- V12 通用层缺反例 → 项目级 anti-patterns.md 补全
- V12 通用层误判 → 项目级 rules 纠正
- V12 通用层缺硬门槛 → 项目级 governance 强制
- 真实失败案例(V12 实战蒸馏)→ 项目级 references/ 沉淀

**反例来源**:2026-08-12-canvas-asset-folders 会话(V12 §3.5 缺真实浏览器端到端 UI 截图硬门槛,项目级 visual-evidence-gate 补全)。

### §14.5.1 与 §14.1-§14.4 的关系

| 维度 | §14.1-§14.4 项目级生态管理 | §14.5 优先级(V11.2 NEW)|
|------|--------------------------|------------------------|
| 关注点 | init-from-zero + project-rules-skill 创建协议 | V11 通用层 vs 项目级 rules 的冲突优先级 |
| 时机 | init 阶段 + 项目级改动前 | 任意阶段,遇到规则冲突时 |
| 反向约束 | 不创造 rules(物理移走) | 不盲信 V11 通用层(项目级叠加) |

### §14.5.2 引用触发词

| 触发词 | 必引用 §14.5 |
|--------|-------------|
| 跨层规则冲突(V11 通用层 vs 项目级) | §14.5 优先级铁律 |
| 项目级新增反例(V11 通用层未覆盖) | §14.5 "适用场景" 第 1 项 |
| 项目级 governance 强制门槛 | §14.5 "适用场景" 第 3 项 |
| AI 自述 "V11 没规定" | §14.5 NEVER 反向铁律 |