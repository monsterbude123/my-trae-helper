# 第一性原则 — README.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 7-35 行（保留信息密度）

---

## 第一性原则（3 条）

### 原则 1：意图是路由的唯一输入

```
用户输入 → 意图识别 → 路由决策 → 状态卡初始化 → 下一 stage
```

意图不明 = 路由失败 = Intake 阻塞。必须 AskUserQuestion 澄清，不可臆断。

### 原则 2：状态卡是 Intake 的唯一产出

Intake 不写 spec / 不写 plan / 不改代码。Intake 只产生 3 类状态卡之一：
- project（项目级）
- change（单个功能 / 重构）
- bug（用户反馈问题）

状态卡初始化 = Intake 完成。

### 原则 3：项目惯例勘察不可跳过

未 Glob 1 次项目自身的 AGENTS.md / docs/ / .trae/rules/ → 不可初始化状态卡。理由：
- 项目可能有自命名规则（编号 / 日期格式）
- 项目可能有自规则（铁律 / 反例 / 安全审查）
- 项目可能有自脚本（lighthouse / e2e）

未勘察 = 与项目惯例冲突 = 后续 stage 返工。

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
