# 技能生长：report-{0X}.md — V7 异常处理与生长机制（V7 NEW）

> report 是 V7 的 **Try-Catch 机制**。Agent 执行中的一切意外——打断、报错、阻塞、磕绊、决策错误——都通过 report 结构化记录，反馈给用户和技能设计者。report 既是异常处理通道，也是技能自我进化的数据源。

---

## 为什么是 Try-Catch

传统程序的异常处理：

```
try {
  doSomething()
} catch (e) {
  log.error(e)
  notify(human)
}
```

Agent 流水线没有 try-catch。Agent 遇到意外时：
- 可能编造结果（最危险）
- 可能卡住不动（用户不知道）
- 可能跳过步骤（产出残缺）

report 机制就是 Agent 流水线的 catch 块：**捕捉异常 → 结构化记录 → 通知人类 → 可追溯**。

---

## 异常分层（L1-L4）

### L1: 文件系统异常

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| 读文件不存在 | 不编造，标记缺失 | `[L1] 文件缺失: {path}, 期望存在但不存在` |
| 写文件失败 | retry 1次 → 仍失败则阻塞 | `[L1] 写入失败: {path}, 原因: {error}` |
| 路径错误 | 搜索正确路径 → 找不到 AskUser | `[L1] 路径错误: 尝试了 {path1} 和 {path2}` |

### L2: Agent 执行异常

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| 子代理返回空 | retry 1次不同 prompt → 仍空则阻塞 | `[L2] 子代理 {name} 返回空, prompt: {...}` |
| 子代理超时 | 简化输入重试 → 仍超时跳过+标记 | `[L2] 子代理 {name} 超时, 已跳过` |
| 输出格式不对 | 解析 + 修复 → 修不了则 report | `[L2] 输出格式不符预期: 期望 {format}, 实际 {...}` |

### L3: 状态不一致

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| state-card 与文件系统矛盾 | 不信任 state-card，以文件系统为准 | `[L3] 状态失真: state-card 说 {claim}, 实际 {reality}` |
| tasks.md 未全部 [x] 但称完成 | 回退，逐个检查 | `[L3] 任务提前标记完成: {N} 项未实际完成` |
| spec 与 contracts 矛盾 | 标记漂移，不静默 | `[L3] 漂移: {spec-says} vs {contract-says}` |

### L4: 外部依赖异常

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| GitNexus 索引过期 | 先更新索引再继续 | `[L4] GitNexus 索引过期, 已自动更新` |
| npm/pip 安装失败 | report + 阻塞 | `[L4] 依赖安装失败: {package}, 错误: {error}` |
| Git 操作失败 | report + 不强制 | `[L4] Git 操作失败: {command}, 错误: {error}` |

---

## 异常处理原则

```
1. NEVER SILENT FAIL     异常必须有可见输出（report 或 Cockpit 标记）
2. RETRY ONCE, THEN STOP 可恢复的异常最多重试 1 次，不无限循环
3. FAIL FAST, REPORT NOW 不可恢复的异常立即 report + 标记阻塞
4. NEVER GUESS           不确定的东西用 AskUserQuestion，不编造
5. STATE CARD IS TRUTH   状态卡同步记录异常，下次会话 Agent 看到后处理
6. AOP FIRST, REPORT SECOND   AOP 自检能拦截的先拦截，拦截不了再 report
```

---

## report 的读者

| 读者 | 读什么 | 用在哪 |
|------|--------|--------|
| **用户（你）** | 问题 + 建议行动 → 确认是否已处理 | 交付时检查 |
| **技能设计者（我）** | L2/L3 模式 → 决定是否升级技能/AOP/流程 | 技能迭代时 |
| **未来 Agent** | L3 状态失真 → 避免重复踩坑 | 重入时参考 |

---

## 触发时机

### 随时触发（catch 任何异常）

| 场景 | 动作 | 谁写 |
|------|------|------|
| 用户打断反馈 | 开子代理写 report（用户原文 + 反思） | 被中断的 Agent |
| Agent 执行报错 | 就地写 report（错误 + 根因 + 建议） | 报错的 Agent |
| 发现流程优化点 | 写 report（发现 + 建议方案） | 发现的 Agent |
| 自动驾驶磕绊 | 写 report（场景 + 感受 + 建议） | 主动反思的 Agent |
| 执行不顺畅 | 写 report（阻塞点 + 期望） | 受阻的 Agent |
| AOP 自检 FAIL 但无法修正 | 写 report（哪个 Q 失败 + 为什么） | 当前 Agent |

### 交付时强制整理

change 进入 accept 阶段时：
1. 主 Agent 遍历 change 下所有 `report-{0X}.md`
2. 汇总为交付报告
3. 检查每个 report 的用户处理状态
4. 未处理的 → 提醒用户
5. 按异常等级分组统计（L1/L2/L3/L4）

---

## report 格式

```markdown
# report-{0X}.md

**时间**: YYYY-MM-DD HH:MM
**变更**: {change-name}
**作者**: {triggering Agent}
**异常等级**: {L1/L2/L3/L4}

---

## 触发场景
{用户打断 / Agent报错 / 优化发现 / 磕绊 / 不顺畅 / AOP自检失败}

## 用户反馈原文（如有）
> ...

## 问题描述
{发生了什么}

## 根因分析
{为什么会发生}

## Agent 尝试的修正（如有）
{AOP 自检 + 修正尝试 + 为什么失败了}

## 建议完善
{怎么做可以避免}

## 影响范围
- 当前 change: 是/否
- 可能影响其他 change: 是/否

## 用户处理状态
- [ ] 待处理 / [x] 已处理 / [-] 不适用
```

---

## 编号规则

`report-{0X}.md` 中 X 为两位数字，按创建顺序递增：
- report-01.md
- report-02.md
- ...

交付后归档时保留原编号。

---

## 交付汇总模板（按异常等级分组）

```markdown
# Report 交付汇总

## 统计
- **总 report 数**: {N}
  - L1 文件系统: {N}
  - L2 Agent 执行: {N}
  - L3 状态不一致: {N}
  - L4 外部依赖: {N}
- **已处理**: {N}
- **待处理**: {N}

## 需立即处理（L1 + L3）
| # | 等级 | 问题 | 建议行动 |
|---|------|------|---------|
| 01 | L1 | docs/modules/user.md 缺失 | 反推生成模块文档 |
| 03 | L3 | state-card 与文件系统矛盾 | 回溯到真实状态 |

## 可延后处理（L2 + L4）
| # | 等级 | 问题 | 处理状态 |
|---|------|------|---------|
| 02 | L2 | 子代理超时 | [ ] 待评估 |
| 04 | L4 | npm install 失败 | [x] 已手动安装 |
```

---

## 从 report 到技能升级

技能设计者在阅读 report 后，决定是否升级技能：

1. 累积 report → 发现模式（如"5 个 report 都是 L2 子代理超时问题"）
2. 判断是否需要改进 AOP / Schema QA / 门禁 / 流程
3. 提出修改方案 → 修改 agent 指令 / 流程 / 模板
4. 跑 evals 验证 → 确认修改不破坏已有正确行为
5. 发布新版技能

---

## report 与 AOP 的关系

```
正常路径:
  Agent 产出 → AOP 后置自检 → 通过 → 移交

异常路径 A:
  Agent 产出 → AOP 后置自检 → FAIL → 能修正 → 修正 → 重新自检 → 通过 → 移交

异常路径 B:
  Agent 产出 → AOP 后置自检 → FAIL → 无法修正 → 写 report → 移交用户决策

异常路径 C:
  Agent 执行中报错 → catch → 写 report → 标记阻塞 → 等待用户
```

AOP 是第一道防线（自动拦截可修正的问题），report 是第二道防线（记录不可自动修正的问题）。

---

## 与 SKILL.md 的集成

SKILL.md 中的铁律 12：

```
12. REPORT FOR GROWTH  技能通过 report 自我进化，实战反馈必须可追溯
```

执行原则 10：

```
10. 报告随时写：磕绊就写 report，交付必整理
```

参考路由：`[references/report-growth.md](references/report-growth.md)` + `[templates/report.md](templates/report.md)`
