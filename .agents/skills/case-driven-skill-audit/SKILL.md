---
name: case-driven-skill-audit
description: Use when auditing or upgrading any skill by exercising it on a real end-to-end case study rather than spot-checking documentation. Triggers on "case study", "实跑 case", "走完整流水线", "skill 升级调研", "skill 真假", "演练收集经验", "case-driven audit". Generates structured evidence (file:line, git log, screenshot) and surfaces spec gaps that doc-only reviews miss. Escalates findings to the target skill's `references/todos/` for later patching.
version: 1.0.0
created: 2026-08-17
origin: case 2 desktop-pet-v11 audit (feedback04)
---

# case-driven-skill-audit — 演练驱动 skill 审计

> **核心哲学**:不读文档判断 skill 行不行,**实跑一遍完整 case** 让规范漏洞自己暴露出来。
>
> **来源**:case 2 (desktop-pet-v11) 桌面宠物 V11 规范审计。子代理跑完整 13 stage 后,自报 7 个 V11 文档/脚本不一致问题 — 这是读文档 100 小时都不会发现的。

---

## §0 触发条件

**必须** 在以下场景调用:

- 任何 skill 升级 / V 主版本变更前(预防回归)
- 任何新 skill 引入 / 合并后(验证真能用)
- 跨 stage 门禁 / 钩子 / 配置文件变更(逻辑耦合)
- 用户口头质疑"这个 skill 行不行"

**禁止** 场景:

- 只读文档答"看起来 OK"(违反 case-driven 原则)
- 不让子代理亲自跑案例(主代理手写 = 选词填空)

---

## §1 工作流 7 步

### Step 1: 选定 case 题目

| 维度 | 选择标准 |
|------|---------|
| **复杂度** | 中等(不能太简单暴露不了问题,不能太难跑不完) |
| **覆盖度** | 必须覆盖目标 skill 声明的所有 stage / 钩子 / 配置 |
| **可验证** | 产出有视觉/功能可验证的"完成"标志 |
| **时间预算** | 30-60 min 完成 |

**选题决策表**:
- 第一次跑 → 选同源行业(参考前一个 case)
- 用户指定 → 直接用
- 用户没指定 → 选能最大化暴露目标 skill"已知坑"的方向

### Step 2: 准备子代理委派上下文

**必含 6 块**:

```
[PROJECT-RULE-GATE]
- 子代理先调 Skill(name="project-rule-skill") 拿规则清单
- 只 Read 清单中的文件

[DECISION-CONTEXT]
- 任务 + 技术栈 + 项目位置
- 主代理不会替你写代码

[FULLSTACK || TARGET-SKILL 强制要求]
- 列出不允许省略的初始化项(物理布局 / 配置文件 / 钩子 / git)
- 每个必跑命令

[AC - 验收标准]
- 5-9 条 AC,带可验证方式(curl / 截图 / 单元测试)

[严格自我约束]
- 不允许"宽松"
- 不允许"选词填空"
- 报告必须带 self-attest 证据
- 报错必须报告,不绕过

[OUTPUT 报告必须含]
- 项目树 + 流水线产物清单 + git log + 索引(类 GitNexus)
- 启动截图 / 验证截图
- 你在跑的过程中发现的规范问题(1-N 条)
```

### Step 3: 委派子代理(强制)

**必须** 用 `Task` 工具 + `subagent_type="general_purpose_task"`。

**禁止** 主代理自己动手写代码 — 你一旦动手,就只看到"我做了 X",看不到"哪些 X 故意没做"。

### Step 4: 监控 + 等回报

- 子代理跑完会返回 self-attest 报告
- 主代理**不立刻接受** — 走 §5 硬验收

### Step 5: 硬验收(主代理亲自 file:line 抽检)

**5 类必查**:

| 检查项 | 验证方式 |
|--------|---------|
| 1. 物理布局 | `ls / Glob` 验证必含目录 |
| 2. 配置文件 | `Read` 验证路径字段、敏感字段填值 |
| 3. git 工作流 | `git log --oneline` + `git status` |
| 4. 索引 | 选 `GitNexus` / `doc-map-manager` 跑一次 |
| 5. 截图 / 实测 | `Read` 截图(若是 image) / 实跑启动命令 |

**FAIL 判定**:
- 任何子代理 self-attest "完成"但 file:line 抽检不到的 = 假 PASS
- 任何子代理说"我做了 X"但 `git log` / `ls` 找不到 = 选词填空

### Step 6: 暴露问题清单(子代理自报 + 主代理总结)

**两类问题**:

| 类型 | 来源 | 处理 |
|------|------|------|
| **A. 目标 skill 规范问题** | 子代理在跑过程中遇到错 | 写 `references/todos/<case-id>-audit.md` |
| **B. 流程方法论问题** | 我们委派/审计方法漏洞 | 写 `.trae/reports/feedback<N>.md` |

### Step 7: 决策下一步

| 决策 | 触发条件 |
|------|---------|
| 立即修目标 skill | A 类 P0/P1 问题 ≥ 3 条 |
| 仅记录,等下次 case | A 类 P0/P1 < 3 且用户没要求 |
| 升级此工作流 | B 类方法论问题 ≥ 1 条 |

---

## §2 报告模板 — `references/todos/<case-id>-audit.md`

```markdown
# <case-id>-audit — 目标 skill 规范审计待修清单

> **来源**:case <N> (<name>) 子代理 self-attest + 主代理硬验收
> **日期**:YYYY-MM-DD
> **状态**:�� 审计完成,修补待决定
> **关联**:[feedback<N>.md](../../../.trae/reports/feedback<N>.md) 完整记录

## A. 待修目标 skill 脚本问题(HIGH)

### A-1: <一句话>
- 位置:scripts/<file>.py:<line>
- 现象:<具体错误输出或行为>
- 修复:<具体改动方案>
- 预估:1 文件 + 1 commit

## B. 待修目标 skill 文档问题(MEDIUM)
...

## C. 待入 trap-instructions.yaml(LOW)
...

## D. 已完成(验收通过)
...

## E. 优先级
| P | 项 | 原因 |
|---|---|---|
| P0 | A-1 | ... |
| P1 | ... | ... |

## F. 等下次修补决定
...
```

---

## §3 验收报告模板 — `.trae/reports/feedback<N>.md`

```markdown
# Feedback #<N> — case <N> <topic> 主体 skill 暴露问题清单

> 来源:case <N> 子代理 self-attest + 主代理硬验收
> 日期:YYYY-MM-DD
> 状态:✅ 记录完成,等下一轮 case + 修补

## 主代理反思(诚实)
- 上一轮我哪里"选词填空"
- 这个 case 改正了什么

## case <N> 验收通过证据(file:line)
| 规范项 | 位置 | 状态 |
|--------|------|------|
| ... | ... | ✅/❌ |

## 暴露的 N 个规范问题(子代理自报 + 主代理验证)
|<编号> | 现象 | 根因 | 修复建议 |
|---|---|---|---|
| ... | ... | ... | ... |

## 主代理决策
- ...

## 下一步
- 等 case N+1 指令
- 修补项 + 优先级
```

---

## §4 反例(不许这么干)

| ❌ 反例 | 后果 |
|--------|------|
| 主代理亲自写代码 | 变选词填空,看不到漏洞 |
| 信任子代理 self-attest "完成" | 假 PASS,案例 1 todoapp-v11 就是这么翻车的 |
| 跳过 git init / 钩子 / 配置 | V11 范错位,案例 1 todoapp-v11 漏的就是这些 |
| 不跑 GitNexus | 违反 V11 §0.5 "默认开启 GitNexus" |
| 案例太简单 | 暴露不出复杂 stage 链路问题 |
| 案例太复杂 | 跑不完,留半成品 |
| 报告只讲故事 | self-attest 必带 file:line + 命令输出 |

---

## §5 适用范围

任何 skill 升级 / 引入场景,优先用本工作流而不是"读文档+ 拍脑袋"。经验证:

- case 1 (todoapp-v11) — **我不规范**,漏 7 项初始化
- case 2 (desktop-pet-v11) — **子代理规范**,暴露 7 个 V11 漏洞

差异在**是否走完整流程**。本文工作流就是**强制不让"我"走"宽松"**。

---

## §6 关联引用

- [AGENTS.md §1.3 会话启动加载协议](../../../AGENTS.md)
- [fullstack4TraeV11/references/todos/case-2-desktop-pet-v11-audit.md](../../../skill-markets/fullstack4TraeV11/references/todos/case-2-desktop-pet-v11-audit.md)(本工作流首次实战)
- [.trae/reports/feedback04.md](../../../.trae/reports/feedback04.md)(案例 2 完整报告)
- [project-rule-skill SKILL.md](file:///D:/workspace/my-trae-helper/.agents/sk