# fullstack-skill-architect 调用模板

> 主上下文调用本 skill 时,产出物标准格式。

---

## §1 触发协议

```yaml
触发词:
  - "技能设计" / "技能升级" / "技能瘦身"
  - "V11→V12" / "V11.3" / "V12"
  - "物理隔离" / "门禁硬化" / "子代理越界"
  - "验收精简" / "革命性清理" / "陈旧移除"
  - "全栈技能设计"

主上下文动作:
  1. Skill(name="fullstack-skill-architect")
  2. 必读 references/methodology.md + traps.md
  3. 走 §2 5 步骨架流程
  4. 出 §3 Completion Report
```

---

## §2 5 步骨架流程产出模板

### Step 1:诊断期 — 精华/糟粕二元判定表

```yaml
## 精华清单(必保留)
✅ {精华 1}: {一句话理由}
✅ {精华 2}: {一句话理由}
...

## 糟粕清单(必剔除)
❌ {糟粕 1}: {现象 + 根因 + 剔除方案}
❌ {糟粕 2}: {同上}
...

## 质疑性校验 4 维度
[1] 根因验证: ✅/❌ {file:line}
[2] 责任主体校验: ✅/❌ {论证}
[3] 重叠校验: ✅/❌ {grep 结果}
[4] 修复成本 vs 价值: ✅/❌ {行数 + 替代方案}
```

### Step 2:设计期 — 5 把刀启用矩阵

```yaml
## 5 把刀启用决策
  物理隔离: [启用 / 跳过 / 不适用]
    WHY: {理由}
    实现: {fact/ + stage/ 双目录布局 / 借鉴 Docker}
  门禁硬化: [启用 / 跳过 / 不适用]
    WHY: {理由}
    实现: {stage-gate-pre-stage.sh / 借鉴 husky}
  子代理边界: [启用 / 跳过 / 不适用]
    WHY: {理由}
    实现: {doc_whitelist / 借鉴 K8s RBAC}
  验收瘦身: [启用 / 跳过 / 不适用]
    WHY: {理由}
    实现: {拆分页面 vs 代码 / 一封信}
  革命性瘦身: [启用 / 跳过 / 不适用]
    WHY: {理由}
    实现: {V 过渡产物 + research/ 删除}
```

### Step 3:验尸期 — 质疑性校验通过依据

```markdown
## 质疑性校验通过依据(每改必走)

### [1] 根因验证
- ✅/⚠️/❌ 引用的章节/SKILL.md 条款真实存在 — 证据: {file:line}
- ✅/⚠️/❌ 失效模式有真实证据 — 证据: {用户反馈/日志/测试报告}

### [2] 责任主体校验
- ✅/⚠️/❌ 修复位置 vs 上游层效果一致 — {论证}
- ✅/⚠️/❌ 已有 skill/rule 不覆盖 — {grep 结果}

### [3] 与已有规则重叠校验
- ✅/⚠️/❌ 现有规则 grep 不重叠 — {grep 关键词}
- ✅/⚠️/❌ 新规则差异化 — {一句话说明}

### [4] 修复成本 vs 价值
- ✅/⚠️/❌ 修复行数 / 影响范围 — {数字}
- ✅/⚠️/❌ 不破坏 §11 铁律 — {论证}
- ✅/⚠️/❌ 替代方案已评估 — {列 1-2 个}

结论: [1][2][3][4] 全 ✅ → 可执行 / 任一 ❌ → 修正方案
```

### Step 4:落地期 — 最小改动方案

```yaml
## 改动清单(零迁移优先)
| # | 类型 | 文件 | 改动行数 | 内容 |
|---|------|------|---------|------|
| 1 | 新建 | {path} | {N} | {一句话说明} |
| 2 | 新建 | {path} | {N} | {一句话} |
| 3 | 修改 | {path} | {N} | {必走质疑性校验} |
| 4 | 删除 | {path} | -{N} | {0 引用证据} |

总计: 新建 X 行 + 修改 Y 行 + 删除 Z 行 = 净 {+/- 行数}

## 升级路径
  V{N}.x → V{N}.x+1: 零迁移(只新增,不改老路径)
  V{N}.x → V{N+1}.0: 破坏性(用户决策)
```

### Step 5:验证期 — 验证 + 瘦身报告

```bash
# 1. 验证无引用断裂
grep -r "{deleted-file}" references/ skills/ scripts/ SKILL.md
  → 必须 0 命中

# 2. 跑全套校验脚本
python scripts/state-card-validator.py docs/specs/.state-card.md  # X/X PASS
python scripts/proactive-scan.py  # X/X PASS
python scripts/self-diagnose.py  # X/X PASS
python scripts/hooks-fidelity.py --project-root .  # PASS
```

```yaml
## 瘦身报告(docs/reports/v{N}.x-slim-{date}.md, ≤ 60 行)
  ## 体积瘦身统计
  - 删除文件: X
  - 删除行数: Y
  - 体积变化: -Z%
  - 验证: state-card-validator X/X + proactive-scan X/X + self-diagnose X/X
  - 引用断裂: 0(grep 验证)
```

---

## §3 Completion Report 协议

```yaml
## Completion Report — fullstack-skill-architect
- target_skill: {被改造的 skill, e.g. fullstack4TraeV11}
- 5 把刀启用情况:
  - 物理隔离: [启用 / 跳过 / 不适用]
  - 门禁硬化: [启用 / 跳过 / 不适用]
  - 子代理边界: [启用 / 跳过 / 不适用]
  - 验收瘦身: [启用 / 跳过 / 不适用]
  - 革命性瘦身: [启用 / 跳过 / 不适用]
- artifacts:
  - {path-1}
  - {path-2}
- 体积影响: {+/- 行数, +/-%}
- 质疑性校验: 4/4 通过 / N 项未过
- evidence:
  - file: {file}:line
  - command: {cmd} + output: {output}
- next_step: [用户确认 / 继续优化 / 阻塞]
```

---

## §4 实施序列(3 阶段 × N commit)

```
阶段 1: V{N}.x 收口(必做,2 文件)
  commit 1: feat(v{N}.x): 补齐 stage-gate-pre-stage.sh + CHANGELOG 条目

阶段 2: 革命性瘦身(选做,N 文件)
  commit 2: refactor(v{N}.x): 删除 V{N-1} 过渡产物 X 文件(-Y 行)

阶段 3: 验证(必做,1 报告)
  commit 3: verify(v{N}.x): 瘦身 X 文件验证通过,体积 -Z%
```

---

## §5 反向提示词(必走)

```markdown
NEVER: 加 README 治文档债务(陷阱 1)
NEVER: 阶段门禁放水(陷阱 2)
NEVER: 验收 stage 读 src/*.ts 代码细节(陷阱 3)
NEVER: 子代理读白名单外文件(陷阱 4)
NEVER: 物理重置时删 fact 层(陷阱 5)
NEVER: 加法式升级膨胀技能包(陷阱 6)
NEVER: 重复蒸馏新建技能(陷阱 7)
```

---

*配套: fullstack-skill-architect/SKILL.md + references/{methodology,patterns,traps}.md*