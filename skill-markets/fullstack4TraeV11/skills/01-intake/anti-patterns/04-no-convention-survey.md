# 反例 4：未勘察项目惯例

> Stage -1 Intake Step 2 必走项目惯例勘察（Glob 1 次）。跳过 = 与项目惯例冲突。

---

## 现象

```
主上下文: 加载 Intake skill → 立即初始化状态卡
（未 Glob AGENTS.md / docs/ / .trae/rules/）
```

**识别信号**:
- 状态卡 notes 字段无"项目惯例要点"
- change-id / bug-id 使用 V11 默认而非项目命名
- stage_config 覆盖未识别（项目级覆盖被忽略）
- 自有铁律未加载（与 V11 Articles 冲突未被检测）
- 后续 stage 返工（命名 / 规则冲突）

---

## 根因

| 根因 | 占比 | 说明 |
|------|:---:|------|
| 不知道 V11 §0.5 加载协议要求 | 45% | 未读编排器 SKILL.md |
| 觉得"项目是 V11 默认" | 30% | 默认无项目惯例，跳过勘察 |
| 觉得 Glob 会击穿上下文 | 15% | 错误理解 Glob 机制 |
| 跳过 Step 2 直接进 Step 3 | 10% | 跳步漏检 |

---

## 教训

**项目惯例可能与 V11 默认不同（如命名规则 / 铁律 / stage_config 覆盖）。未勘察 = 与项目惯例冲突。**

真实案例（2026-08-07 蒸馏）:
- 项目 AIGCMediaDesktop 有自有铁律"桩代码必须返回明确错误: 'STUB: 功能未实现'"
- 主上下文未勘察 → 后续 Stage 3 Implement 写出"not supported in phase 2"模糊错误
- 用户质问"为什么没按项目铁律"
- 返工 2 轮改桩代码

---

## 正确替代

```
Step 2: 项目惯例勘察（Glob 1 次）
  ├─ Glob: {project}/AGENTS.md
  ├─ Glob: {project}/docs/constitution.md / docs/INDEX.md
  ├─ Glob: {project}/.trae/rules/*.md
  └─ Glob: {project}/.trae/fullstack4traev11.config.yaml（如有）

Step 3: 解析项目惯例表
  ├─ 命名规则（change-id / bug-id / 文档命名）
  ├─ 自有铁律（.trae/rules/*.md）
  ├─ stage_config_override（项目级覆盖）
  └─ 禁读路径（archive/ / tmp/ 等）

Step 4: 冲突检测
  ├─ 命名规则冲突 → 标注，使用项目命名
  ├─ stage_config 冲突 → 项目优先（V11 dependency-config §3 层优先级）
  ├─ 铁律冲突 → 项目胜出（不与 V11 永不可降级 Articles 冲突）
  └─ 无冲突 → 直接进入 Step 5

Step 5: 输出项目惯例表（写入状态卡 notes）
```

**MUST**: Step 2 必走 Glob 1 次（4 类文件）。

**NEVER**:
- ❌ 不 Glob 直接初始化（即使"项目是 V11 默认"也要明确记录）
- ❌ 递归 Glob `**/*` 击穿上下文
- ❌ Glob 后不 Read（仅靠路径判断）
- ❌ 与项目自有铁律冲突时仍按 V11 默认（如允许 .bak）

---

## 检测方法

主上下文 Step 2 必走自检：

```yaml
checklist:
  - [ ] Glob 4 类项目文件已执行？
  - [ ] AGENTS.md 存在？已 Read？
  - [ ] docs/constitution.md / docs/INDEX.md 存在？已 Read？
  - [ ] .trae/rules/*.md 已 Glob？关键文件已 Read？
  - [ ] .trae/fullstack4traev11.config.yaml 存在？已 Read？
  - [ ] 项目惯例表已写入状态卡 notes？
  - [ ] 冲突检测已执行（无遗漏）？
```

任一未勾选 → 触发本反例 → 回到 Step 2 重新勘察。

---

## 3 层优先级（V11 dependency-config.md §3）

```
优先级（高 → 低）:
1. 项目级 AGENTS.md / .trae/fullstack4traev11.config.yaml（最高）
2. 编排器 SKILL.md stage_config
3. stage skill SKILL.md depends_on（最低）
```

**主上下文决策**:
- 项目覆盖 vs V11 默认 → 项目胜出（写入状态卡 notes）
- 任何依赖冲突 → 警告 + 用户决策

---

## 反例真实场景（再细化）

### 场景 A：未识别命名规则

```
项目惯例: change-id = {YYYY-MM-DD}-{slug}（如 2026-08-11-add-user-auth）
V11 默认: change-id 自由格式
主上下文未勘察 → 用 V11 默认 "add-user-auth"
后续 stage: 与项目编号冲突 → 返工
```

### 场景 B：未识别 stage_config 覆盖

```
项目惯例: stage_config.implement.skills = [ponytail4Trae, react-dev-skill]
V11 默认: stage_config.implement.skills = [ponytail4Trae, gitnexus4Trae]
主上下文未勘察 → 用 V11 默认
Stage 3 Implement: 缺少 react-dev-skill → 实施技术栈不对 → 返工
```

### 场景 C：未识别自有铁律

```
项目惯例: .trae/rules/coding-standards.md → "桩代码必须返回明确错误: 'STUB: 功能未实现'"
V11 默认: 17 Articles 宪法（含 Article XVII Secret Redaction）
主上下文未勘察 → Stage 3 Implement 写模糊错误 "not supported in phase 2"
用户在后续 stage 触发 1 轮纠错 → Stage 1 重做 → 累计 ≥ 2 轮返工
```

---

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — 未勘察不初始化
- [SKILL.md §铁律 7](../SKILL.md) — 编排器依赖空不空路由（指 Intake 自身是入口）
- [project-convention-survey.md](../workflows/project-convention-survey.md) — 项目惯例勘察工作流
- [dependency-config.md](../../../references/dependency-config.md) — 3 层优先级协议
- 编排器 §0.5 Skill 加载协议: [../../../SKILL.md](../../../SKILL.md)
