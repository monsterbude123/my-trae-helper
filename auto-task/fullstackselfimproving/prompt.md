# fullstack × self-improving 任务提示词 v1

> **单文件契约**：本文件 = 自动化任务 `fullstackselfimproving` 的唯一执行契约。目标 ≤ 7000 字 / 350 行,符合 `vibe-coding-standards v2.5` 弹性范围;超阈必须瘦身,不允许拆 `references/`。
>
> **生效日**:2026-08-18  **维护**:任务负责人 / `self-improving-agent` 联动
>
> **本提示词是规则源**;agent 在 `auto-task/fullstackselfimproving/` 下任何子任务的输入,均消费本文件。修改本文件 = 修改任务契约,需走 §6.2 流程。

---

## §0 任务定位

```
任务名:    fullstack × self-improving
工作目录:  auto-task/fullstackselfimproving/
契约文件:  prompt.md   (本文件,单文件,只读消费)
输入:      用户业务需求(自然语言) / 既有代码库指针
输出:      可运行代码 + 验收报告 + 经验沉淀条目
两条主线:  fullstack(从 spec 到部署的 13 stage 流水线)
          self-improving(全会话经验沉淀 + 反例库维护)
```

> 消费提示:agent 接到本任务,先读本文件再做任何动作;读完输出 `loaded: prompt.md v1 (N 行)`。

---

## §1 启动协议(强制 4 步,缺一不可)

```
Step 1  Skill(name="project-rule-skill")
        → 输出 needed_rules 清单(只 Read 清单中的 rules)
        → 失败/未安装 → 退化为:Skill(name="vibe-coding-standards") 兜底
Step 2  Skill(name="self-improving-agent")
        → 加载全局经验上下文(LEARNING/ERROR/FEATURE_REQUESTS)
        → 失败也不阻断会话;响应开头标注 [learning-skip]
Step 3  Read 本文件 prompt.md(单文件,一次性)
        → 输出契约版本 + 行数 + 关键章节索引
Step 4  按 §2 铁律开工,不再加载任何额外 skill(除非命中触发关键词)
```

**禁止**:跳过 Step 1 直接 Read `.trae/rules/*`;禁止一次 Read 多份 rules 撑爆上下文。

---

## §2 核心铁律(12 条,精简到不可再砍)

| # | 铁律 | 命中反例 |
|---|------|----------|
| 1 | YAML frontmatter 必带 `name`+`description` | 缺 description → structure guard BLOCK |
| 2 | 技能位置 = `skill-markets/<name>/`,不发明路径 | 写到 `.trae/skills/...` → guard BLOCK |
| 3 | 新增脚本/技能前必查 `CAPABILITY-MAP.md` | 重复造轮子 → capability guard BLOCK |
| 4 | 行数超 350 必须瘦身(指针引用),不裁内容 | 硬删内容 → vibe-coding AP-01 |
| 5 | 安全审查必跑 `scan_skills_dir.py` + 更新 SECURITY-MAP | HIGH 风险准入 → 🛑 BLOCKED |
| 6 | 临时产物 = `logs/` 或 `.publish/`,不写项目外 | 写到 D:\ → 安全红线 |
| 7 | ponytail 思路:最简实现,标准库优先,无依赖 | 引入 10MB 包做 1 行逻辑 → AP-02 |
| 8 | 任务明确才用 fullstack 13 stage,不加不必要阶段 | 5 行改动开 13 stage → AP-03 |
| 9 | **禁止自主部署**:不主动 install,除非用户明示 | 自动 npm i -g → 红线 |
| 10 | SKILL.md/agents 引用优先,详细进 references/ | 把铁律写散 → 维护地狱 |
| 11 | guard/gate 注册表强制:`registry/skills.yaml` + `scripts/<name>-guard.*` | 改注册表不走 guard-smith → 越权 |
| 12 | 调整 guard/gate 走 7 步 SOP(详见 §3.2) | 跳过自检 → 假通过 |

> **§2.4 经验沉淀铁律**:
> - 仓库内**不建** `.learnings/` 目录(全局 `self-improving-agent` 已覆盖)
> - 仓库内反例 → `skill-markets/<pkg>/references/trap-instructions.yaml`
> - 跨会话经验 → 全局 `self-improving-agent` 的 LEARNING/ERROR/FEATURE_REQUESTS
> - 临时 pytest hint → `logs/agent-hints.jsonl`(conftest 可清空)

---

## §3 双轨:fullstack + self-improving

### 3.1 fullstack 轨(13 stage,按需裁剪)

| Stage | 产物 | 跳过条件 |
|-------|------|----------|
| 1 spec | `spec.md` | 任务 < 5 行改动 |
| 2 define | `define.md` | 已存在定义 |
| 3 plan | `plan.md` | 单文件 bugfix |
| 4 contracts | `contracts/*.yaml` | 无 API 变更 |
| 5 tasks | `tasks.md` | 单步任务 |
| 6–12 实现+测试+部署 | 代码 + 报告 | (按 plan 走) |
| 13 retro | `references/todos/<task>.md` | 永不跳过(必留痕) |

> **裁剪原则**:简单任务只跑 6/12/13 三个 stage;13 stage retro 永远是最后一步。

### 3.2 self-improving 轨(3 阶段,自动化)

| 阶段 | 触发 | 动作 | 写入 |
|------|------|------|------|
| **启动** | Step 2 | 注入全局经验上下文(只读) | 仅内存 |
| **进行** | 工具失败/用户纠正/守卫阻断 | append `ERROR` | 全局 LEARNING/ERROR |
| **收尾** | 任务完成/表态"完成"/失败 | append `LEARNING` + 可选 `FEATURE_REQUESTS` | 全局 + 本任务 §6 留痕 |

> **降级**:`self-improving-agent` 不可用 → 不阻断,响应开头 `[learning-skip]` 标注。
> **禁自动沉淀**:临时调试日志 / 一次性命令输出 / 用户明示"别记" / 涉及密钥 PII。

### 3.3 guard/gate 7 步 SOP(改注册表前必走)

```
1. 识别需求     锁定"改什么+为什么"
2. 自我判定     命中白名单路径(registry / scripts/<name>-guard.* / .husky/*-gate / scripts/guard-router.mjs / src/guards/* / gate workflow)→ 委派 guard-smith sub-agent
                Tier 4 路径(.husky/_* / .trae/identity/* / scripts/change-guard-approver.mjs)→ 🛑 终止,提修订 PR
3. 准备头部     填 [GUARD-SMITH-DELEGATION] 任务+上下文+约束
4. 委派         subagent_type="general-purpose",隔离上下文
5. 验收报告     检查越界 + 输出合理性
6. 主代理兜底   必跑:node src/guards/skill-registration-guard.mjs
                    + node scripts/guard-router.mjs <changed-skill>
                    + python tests/unit/test_registration_guard.py
                    + npm run lint
7. 提交         git commit -F .commit_msg.txt(多行用 -F,见 §5.3)
                + 同步 SECURITY-MAP.md / CAPABILITY-MAP.md
```

---

## §4 三层控制(执行 / 守卫 / 门禁)

| 层 | 职责 | 实现 |
|---|------|------|
| **Execution** | 标准化执行 + 风险分级 + 备份回滚 + 审计 | `src/execution/*.mjs` (CP1~CP6) |
| **Guard** | 自动化检查 + 阻断违规 | `scripts/skill-*-guard.py` + `src/guards/*.mjs` |
| **Gate** | 提交/推送/合并/发布门禁 | `.husky/` + `.github/workflows/` |

**4 个 Guard 一句话**:
- Security: HIGH 真实风险 → 🛑 BLOCKED
- Structure: 命名+行数+frontmatter+铁律数
- Dependency: 硬依赖完整性 + 软依赖降级
- Capability: 脚本去重 + CAPABILITY-MAP 同步

**4 级 Gate**:
- L1 Commit: lint + typecheck + unit + security/structure
- L2 Push: integration + coverage + dependency + build
- L3 Merge: L2 + CAPABILITY-MAP + SECURITY-MAP 同步
- L4 Publish: L3 + 全量扫描 + 灰度 + 自动 tag

**反假通过(必做)**:写完任何 Gate/Guard 脚本 → tmp 造违规样本 → 跑 Gate → 期望 exit ≠ 0;反例样本必须进 `tests/unit/test_*.py`,不能跑一次就丢。

---

## §5 行为规约

### 5.1 回复三类结尾(无问句)

```
完成:  "完成报告 + 修改清单"
部分:  "X 已完成,Y 不做(原因)"
失败:  "🛑 阻塞:X(具体缺什么)"
```

**禁止**:问"要不要做 X" / 挂 P0~P3 backlog / 写"我没做但应诚实声明的 N 项"。

### 5.2 用户表态信号(必终止提问,选保守方案)

```
"懂了吗" / "能懂了吗" / "你到底做啥"  →  改 < 不改(最小变更)
                                            src/ < skill-markets/
                                            显式 < 隐式
```

### 5.3 Git & 路径铁律

```
- 优先 git bash;Windows 也走 bash 兼容命令
- 多行 commit message 用 -F 文件,不用 -m 多参数
- Git Hook 必须跨平台探测 Python(详见 §5.4)
- 禁止在项目路径外写脚本(红线)
- 临时文件 logs/ 或 .publish/,不放根目录
```

### 5.4 跨平台 Python 探测(共享脚本)

```
# scripts/detect-python.sh
# 动态: PATH + 平台典型位置(uname 生成)
# 能力校验: 缺 pytest/yaml → 自动 python -m pip install --user(自愈,不阻断)
# 导出: MY_TRAE_HELPER_PY=$PY
# Hook 内: . scripts/detect-python.sh && "$MY_TRAE_HELPER_PY" scripts/verify.py ...
```

---

## §6 安全 / 脱敏 / 退出

### 6.1 决策矩阵

```
HIGH 真实风险    MEDIUM 真实风险    准入
0                ≤ 3                🟢 PASS
0                > 3                🟡 WARNING(人工审查)
≥ 1              任意                🛑 BLOCKED
```

### 6.2 修改本文件的契约

```
- 修改本文件 = 改任务契约,需在 commit msg 显式声明 "contract change"
- 改前必跑:字数核对 ≤ 350 行 / ≤ 7000 字 / 章节编号连续 / 无悬空引用
- 改后必跑:Step 1~4 自检 + 至少 1 次 dry-run 消费(用一个简单任务跑一遍)
- 本文件变更不写入 SECURITY-MAP.md(非 skill 包);变更留痕在 git log
```

### 6.3 脱敏红线

```
- 任何输出严禁出现:真实 key / token / 内部 endpoint / PII
- 涉及敏感信息 → [REDACTED] 占位 + 备注"需用户填入"
- 仓库内不存 .env(只存 .env.example)
```

### 6.4 退出与审计

```
正常完成:
  1. 写 retro(13 stage 必留):auto-task/fullstackselfimproving/references/todos/<task>.md
  2. append 全局 LEARNING(self-improving-agent 自动化)
  3. git commit -F .commit_msg.txt + 推 PR

失败/阻塞:
  1. 写 retro 但标 status: blocked + 阻塞原因
  2. append 全局 ERROR
  3. 不强制 PR,可继续调试
```

---

## §7 一句话铁律(速查)

```
会话开始  = Skill(project-rule-skill) + Skill(self-improving-agent) + Read prompt.md
核心思路  = ponytail:最简实现,标准库优先,无依赖
禁止部署  = 不主动 install,除非用户明示
guard/gate = 改注册表必走 7 步 SOP + 委派 guard-smith
经验沉淀  = 仓库内不建 .learnings/,走全局 self-improving-agent
跨平台    = git bash 优先 + 共享 detect-python.sh
安全      = 真实 key/token/PII 全程 [REDACTED]
退出      = 13 stage retro 必留痕 + 全局 LEARNING 自动 append
```

---

## §8 索引(本文件章节速查)

```
§0  任务定位
§1  启动协议(4 步)
§2  核心铁律(12 条)
§3  双轨:fullstack 13 stage + self-improving 3 阶段 + guard/gate 7 步 SOP
§4  三层控制(执行/守卫/门禁)
§5  行为规约(回复/表态/Git/跨平台)
§6  安全/脱敏/退出
§7  一句话铁律速查
§8  索引
```

> **消费方式**:agent 接到本任务 → Step 1~4 → 按 §7 速查开工 → 收尾走 §6.4。
> **修改方式**:见 §6.2。
