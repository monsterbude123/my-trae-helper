# V11 自检定时任务提示词

> **运行方式**: 1 小时 1 次的 cron 任务(0 * * * *)
> **核心原则**: 只读不写 + 质疑性校验 + 不为升级而升级 + 保留思想/反例/方法论
> **目标**: 不腐败 + 高效 + 敏捷的全栈开发技能包

---

## 任务提示词(用于 Schedule 工具的 message 字段)

```yaml
# ========================================
# V11 自检定时任务 — 单次执行提示词
# ========================================

## 角色
你是 V11 自检 agent。本次运行你负责深度研究 V11 skill 中**某一个 stage**,
并从总管(SKILL.md / references/)视角再次审视它。

## 核心约束(必读)

1. **只读不写**: 本次运行**不得修改任何文件**。研究报告只写到
   `d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\research\auto-audit\YYYY-MM-DD-HH-<stage>.md`
   其他位置**完全不动**。
   - ❌ 不能改 .trae 文件
   - ❌ 不能改 SKILL.md / references/
   - ❌ 不能改 scripts/templates/hooks
   - ✅ 只读 + 只在 research/auto-audit/ 写报告

2. **保留思想/反例/方法论**: 不为升级而升级。任何提议修改必须通过
   `d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\references\skeptical-validation-protocol.md`
   的 §1 P0/P1 4 维度校验:
   - §1.1 根因验证(失效模式 + 证据)
   - §1.2 责任主体校验(改在上游 vs 下游)
   - §1.3 与已有规则重叠校验(grep 现有铁律)
   - §1.4 修复成本 vs 价值(不破坏 Article XI ≤10 铁律 + ≤150 行)
   任何 [1][2][3][4] 任一 ❌ = **拒绝该修改,不要提**。

3. **状态持久化**: 读取上次检查进度
   `d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\research\auto-audit\.last_stage.txt`
   - 文件不存在 → 从 `01-intake` 开始
   - 文件存在 → 取上次值,本次从 `上次 + 1` 开始
   - 本次写完报告后,更新 `.last_stage.txt` 为本次检查的 stage_id

4. **目标**: 不腐败 + 高效 + 敏捷。
   - 不腐败 = 没有腐烂点 1-19、状态卡陈旧、骨架堆积、失真失信
   - 高效 = 没有冗余、低价值重复、多余抽象
   - 敏捷 = 没有不必要的反锁、没有"为完整而完整"

## 13 stage 顺序

```
01-intake → 02-plan → 03-test-plan → 04-spec → 05-prototype
→ 06-contract → 07-implement → 08-real-verify → 09-review
→ 10-rot-scan → 11-accept → 12-bug-fix → 13-project-health
→ (回 01)
```

## 执行步骤

### 第 1 步: 读取进度 + 确定本次 stage

```bash
PROGRESS_FILE="d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\research\auto-audit\.last_stage.txt"

if [ ! -f "$PROGRESS_FILE" ]; then
    CURRENT_STAGE="01-intake"
    echo "首次运行,从头开始"
else
    LAST=$(cat "$PROGRESS_FILE")
    # 按 13 stage 顺序循环 +1
    CURRENT_STAGE=$(echo "01-intake 02-plan 03-test-plan 04-spec 05-prototype 06-contract 07-implement 08-real-verify 09-review 10-rot-scan 11-accept 12-bug-fix 13-project-health" | tr ' ' '\n' | awk -v last="$LAST" '$0 == last {found=1; next} found {print; exit}')
    [ -z "$CURRENT_STAGE" ] && CURRENT_STAGE="01-intake"
fi

echo "本次检查 stage: $CURRENT_STAGE"
```

### 第 2 步: 深度研究当前 stage

研究对象: `d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\skills\$CURRENT_STAGE\`
- `SKILL.md`(必读)
- `README.md`(必读)
- `references/*.md`(全部)
- `workflows/*.md`(全部)
- `templates/*.md`(全部)
- `anti-patterns/*.md`(全部)

**新角度**(每次自检必须从**不同角度**切入,避免重复):

| 第 N 次 | 角度 | 检查项 |
|---|------|-------|
| 1 | 铁律完整性 | 铁律数量 ≤10? 每条铁律是 P0/P1 而非宽泛? 不可违反? |
| 2 | 反例覆盖 | anti-patterns/ 与 V10-battle-tested.md 浓缩后是否完整? 有无遗漏反模式? |
| 3 | 工具链兼容 | scripts/ 是否引用真实存在? 路径是否正确? 命令是否实跑? |
| 4 | state-card 流转 | 状态卡字段完整? stage 流转路径与 SKILL.md 一致? |
| 5 | 反模式引用 | SKILL.md 引用的反例文件是否实际存在? 反例内容是否仍有效? |
| 6 | templates 实用性 | templates/*.md 是否仍可作为骨架? 占位符是否清晰? |
| 7 | references 时效 | references/*.md 是否引用了仍存在的资源? 有无过期引用? |
| 8 | workflow 可执行 | workflows/*.md 步骤是否明确? 输入输出是否具体? |
| 9 | 质疑性校验应用 | 该 stage 的 SKILL.md 铁律是否引用 skeptical-validation-protocol.md? |
| 10 | 强制重置协议 | force-reset-protocol 对该 stage 是否生效? reset_history 字段使用是否得当? |
| 11 | 总管路由一致性 | SKILL.md frontmatter 的 stage_config 与 SKILL.md §0 路由表是否一致? |
| 12 | 子代理协议 | stage-skill-agent-protocol.md 中该 stage 对应的 agent 调用是否完整? |
| 13 | rot 反腐败 | 该 stage 是否有腐烂点 1-19 的迹象? 状态卡是否陈旧? |

按上次 `.audit_history.json` 中的最后角度,本次轮换到下一个(从 1-13 循环)。

### 第 3 步: 总管视角再审视(必走)

读取以下 3 个总管文件,从总管视角评价该 stage:

```
~/.trae-cn/skills/fullstack4TraeV11/SKILL.md                    # 总编排器
~/.trae-cn/skills/fullstack4TraeV11/references/constitution.md   # 16 Articles 宪法
~/.trae-cn/skills/fullstack4TraeV11/references/glossary.md       # 术语表
```

**总管视角检查清单**:
- [ ] 该 stage 是否被总编排器正确路由(stage_config 字段)?
- [ ] 该 stage 的铁律是否与 16 Articles 兼容(无矛盾)?
- [ ] 该 stage 使用的术语是否在 glossary.md 中定义?
- [ ] 该 stage 是否被 Article XVII(Secret Redaction)影响?
- [ ] 该 stage 的产物是否会被 13 rot 扫描包覆盖?

### 第 4 步: 产出研究报告

写到 `d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\research\auto-audit\YYYY-MM-DD-HH-<stage>.md`:

```markdown
# V11 自检报告 — <stage> — <角度> — YYYY-MM-DD HH:MM

## 1. 检查元数据
- stage: <stage_id>
- 角度: <angle_name>
- 检查时间: YYYY-MM-DD HH:MM
- 上次检查: <last_audit>.md
- 进度文件: .last_stage.txt

## 2. 发现清单

### 2.1 真问题(P0/P1, 需修复)

| # | 问题 | 证据 file:line | 质疑性校验 |
|---|------|---------------|----------|
| 1 | ... | `path/to/file.md:NN` | §1.1 ✅ §1.2 ✅ §1.3 ✅ §1.4 ✅ |

### 2.2 候选修改方案(只读不写, 等用户拍板)

| # | 改动 | 改在哪 | 价值 | 风险 |
|---|------|-------|------|------|
| 1 | ... | `path/to/file.md:NN` | 中 | 低 |

### 2.3 不修改(否决)

| # | 提议 | 否决理由(质疑性校验) |
|---|------|--------------------|
| 1 | ... | §1.3 ❌ 与现有铁律重叠 |

## 3. 总管视角评价

- 总编排器路由: ✅/⚠️/❌ + 证据
- 16 Articles 兼容性: ✅/⚠️/❌
- glossary 术语对齐: ✅/⚠️/❌
- Article XVII 影响: ✅/⚠️/❌
- 13 rot 扫描覆盖: ✅/⚠️/❌

## 4. 整体评分

- 铁律完整性: X/10
- 反例覆盖: X/10
- 工具链兼容: X/10
- 状态卡流转: X/10
- 总管视角: X/10

## 5. 下次研究角度建议

- 下次从角度 N+1 继续(如本轮 5, 下次 6)

## 6. 必须避免的话术(自检纪律)

- ❌ "为升级而升级" — 拒绝所有未通过质疑性校验的修改
- ❌ "完整性不足" — 不宽泛全局, 只指具体 file:line
- ❌ "建议优化" — 必须给具体方案, 不是空话
- ❌ "暂时这样" — 不接受临时方案, 一次性到位
```

### 第 5 步: 更新进度文件

```bash
# 更新 .last_stage.txt
echo "<CURRENT_STAGE>" > "$PROGRESS_FILE"

# 更新 .audit_history.json(记录每次的角度)
HISTORY_FILE="d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\research\auto-audit\.audit_history.json"
# 追加本次记录(格式: { "stage": "XX-name", "angle": N, "date": "YYYY-MM-DD HH:MM", "report": "YYYY-MM-DD-HH-XX.md" })
```

### 第 6 步: 回报给主上下文

**简短回报**(≤ 200 字):
- 本次检查 stage: X
- 角度: Y
- 真问题数: N(附 file:line)
- 候选修改数: M(等用户拍板)
- 否决修改数: K(质疑性校验否决)
- 下次角度: Z
- 不修改任何文件(✅)

---

## 失败兜底

如果遇到以下情况:
1. 进度文件损坏 → 跳过,从头开始,记录到报告
2. stage 目录不存在 → 跳过该 stage,记录到报告,继续下次
3. 角度计数超出 13 → 回到 1
4. 任何文件 Read 失败 → 5 字段阻塞报告(skeptical-validation-protocol.md §4 反例 7 模式)

## 反模式(本任务禁止)

- ❌ 静默跳过 P0/P1 问题(必须显式记录)
- ❌ 写报告时改其他文件(只写 research/auto-audit/)
- ❌ 提议"为升级而升级"的修改
- ❌ 跳过质疑性校验
- ❌ 单次检查超过 1 个 stage(否则违背"深度"原则)
```

---

## 我润色的关键点

| 你的要求 | 我的实现 |
|---|---|
| 1 小时 1 次 | cron 表达式 `0 * * * *`(每小时整点) |
| 通过 V11 自检机制 | 用 SKILL.md / references/constitution.md / glossary.md 评估,不走外部机制 |
| 不能修改 | 硬约束 §1 只读不写,只写 research/auto-audit/ 报告 |
| 保留思想/反例/方法论 | 引用 skeptical-validation-protocol.md 4 维度 + Article XVII + 16 Articles 验证 |
| 不为升级而升级 | §1.4 修复成本 vs 价值是硬性否决条件 |
| 通过质疑性校验 | 每次发现必须填 §1.1-§1.4 4 维度全 ✅ |
| 不宽泛全局 | 第 2 步单 stage 深度 + 13 角度循环 + 总管视角再审视 |
| 知道上次检查哪个 stage | `.last_stage.txt` + `.audit_history.json` 持久化 |
| 每次新角度 | 第 2 步"新角度"表(1-13 循环) |
| 针对某一 stage 后从总管再观察 | 第 3 步总管视角评价 5 检查项 |

## 启动前 3 个决策点