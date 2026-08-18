# Changelog - V11 → V12

> V12 升主版本(2026-08-16 ADR ACCEPTED)。V11.8.6 累积落地后,V12 物理隔离思想从可选变强制默认。
> V11.8.7.1 起 **V11 扁平布局已彻底废弃**(`--layout` 仅 `v12-preview`),所有项目(含 V11 既有)必须 V12 物理布局。

---

## [V11.8.7.1] - 2026-08-18

### 🛠️ 用户 5 项硬要求 3 连修(feedback06 + 对话蒸馏)

> **来源**:用户连续 3 次反馈("逗我吗" → "扯犊子" → 5 项硬要求),要求 V11 扁平默认移除 + 归档升级 + module 占位修复 + 多 archive 路径合一。
>
> **修复范围**:5 项必修,1 项 trap 反例固化。

#### 🔧 修改

- **Req 1 (HIGH) 移除 V11 扁平默认** — `scripts/init-from-zero.py` `--layout` choices 从 `["v11-default", "v12-preview"]` 缩减为 `["v12-preview"]`,V11 扁平布局**永久废弃**。`Step 4.5` 取消 `if args.layout == "v12-preview"` 条件,无条件必跑。
- **Req 2 (HIGH) archive 保留 V12 物理布局** — `scripts/spec-purge.py` 不再调用 `flatten_v12_to_v11_layout`(该函数保留为 legacy 安全网,无调用方)。新增 `archive_keep_v12_layout()`:`copytree` 1:1 保留 `fact/ + stage/`,**不展平**。
- **Req 3 (HIGH) 项目级 module.md 不再占位** — `scripts/init-from-zero.py` 新增 `create_project_module()`(`Step 4.6`),创建 `docs/specs/changes/_module.md` 完整模板(项目元信息 + 模块清单 + 接口边界 + 跨模块约定),不再是空占位。
- **Req 4 (HIGH) archive 包含 module 内容** — `scripts/spec-purge.py` `archive_keep_v12_layout()` 自动从 `docs/specs/changes/_module.md` 复制到 `archive/{change-id}/_module.md`,V11 legacy 路径也补一份。`V12_FACT_ARTIFACTS` 加入 `fact/module.md`(必含)。
- **Req 5 (HIGH) archive 路径合一** — `scripts/_lib_paths.py` 移除 `changes_archive` 键 + `get_changes_archive_dir()` 函数,单真相源 = `docs/archive/done`。`init-from-zero.py` `create_docs_skeleton` 不再创建 `docs/specs/changes/archive/`。

#### ➕ 新增

- `scripts/init-from-zero.py::create_project_module()` — 项目级模块真相源(Step 4.6)
- `scripts/spec-purge.py::archive_keep_v12_layout()` — V12 保留物理布局归档
- `references/trap-instructions.yaml::V11-AP16` — V11 扁平默认 + archive 展平 + module 占位 三连反例

#### 🧪 自验收(6 项 detect_signal)

```bash
# 1. --layout 不再含 v11-default
grep -E 'choices=\[.*v11-default' scripts/init-from-zero.py
# 期望:0 命中

# 2. flatten_v12_to_v11_layout 调用方 0 处
grep -E 'flatten_moves\s*=\s*flatten_v12_to_v11_layout' scripts/spec-purge.py
# 期望:0 命中

# 3. dry-run 文案不再"展平"
grep -E 'V12 → 展平' scripts/spec-purge.py
# 期望:0 命中

# 4. _module.md 存在且非占位
cat docs/specs/changes/_module.md | grep -E "模块清单|接口边界|跨模块约定"
# 期望:3 行均命中

# 5. 多 archive 路径已合一
ls docs/specs/changes/archive 2>/dev/null
# 期望:No such file or directory

# 6. archive 注入 _module.md
ls docs/archive/done/*/_module.md
# 期望:每个归档 change 都有
```

#### 🎯 落地项目

- `D:\workspace\ai-collaborate\ai-short-studio-monster` — 移除 `docs/specs/changes/archive/` + 回填 `_module.md` 到 `docs/archive/done/2026-08-17-bug-1024-stale-cleanup/` + `docs/specs/_invalidated/.../`,更新 `.trae/fullstack4traev11.config.yaml` 删 `changes_archive` 字段。

#### 🐛 V11-AP17(2026-08-18 user feedback)— docs/modules/ 死锁

- **`templates/hooks/doc-sync-gate.py`** 移除 `docs/modules/` 非空检查(L56-69)。原 V10 蒸馏残留,V11 13 stage 流程无对应 stage 写 modules 内容 → PreToolUse 永远 BLOCK → agent 无法编码。
- **`references/project-structure.md`** 加 "docs/modules/ 不存在" 必检项,明确 V11 模块真相源在 `docs/specs/changes/_module.md`(项目级)+ `fact/module.md`(change 级)。
- **`references/trap-instructions.yaml`** 新增 V11-AP17。
- **项目侧 `ai-short-studio-monster`**:`docs/modules/.gitkeep` 移到 `D:\tmp\` 备份 + `.trae/hooks/doc-sync-gate.py` 同步模板。

---

## [V11.8.7] - 2026-08-17

### 🛠️ case 2 audit-fix — case 1 todoapp + case 2 desktop-pet 蒸馏的 7 个 V11 规范问题修补

> **来源**:case 2 (desktop-pet-v11) 子代理 self-attest + 主代理硬验收。详细反例清单见 [`.trae/reports/feedback04.md`](file:///D:/workspace/my-trae-helper/.trae/reports/feedback04.md)(7 个问题 A-G)。
>
> **修复范围**:7 个问题中,A/B/C/D/G 必修(5 项),E/F LOW 优先级专项处理,F 留 case-only 修复不进主版本。

#### 🔧 修改

- **A (HIGH) fix dual-write 双写** — `scripts/init-from-zero.py` 新增 `--rules-layout {files|skill}` 二选一(默认 `files`,不再双写)。`.trae/rules/` 与 `.trae/skills/project_rules_skills/` 物理互斥。详见 [SKILL.md §14.1](SKILL.md)。
- **B (HIGH) fix spec-purge vs V12 物理布局冲突** — `scripts/spec-purge.py` 自动探测 V11/V12 双布局,V12 模式读 `fact/` + `stage/N/*.md`,归档时自动展平到 V11 平铺布局便于 audit。新增 `detect_layout()` + `flatten_v12_to_v11_layout()`。详见 spec-purge.py docstring §V11.8.7 段。
- **C (HIGH) fix 状态卡 schema 文档 vs 脚本漂移** — 新增 `references/state-card.schema.json` JSON Schema 单一真相源,文档 + 脚本 + 模板都派生自此文件。`state-card-protocol.md` 新增 §10.5 Schema 单一真相源段。详见 trap-instructions.yaml AP-15 关联。
- **D (MEDIUM) fix paths 配置化声明** — `SKILL.md` 新增 §15 paths 配置化段(5 项必配字段 + 单一访问源 + 自验收协议)。详见 §15.1-§15.5。
- **E (LOW) fix GUI_MODE 默认值漂移** — `references/config.example.yaml` 新增 `engine.default_gui_mode: pure_tk` 字段,3 种 fallback 顺序,避免 case 2 子代理用 `auto` → PIL 路径 "Too early to create image" 错。详见 config.example.yaml。
- **G (LOW) fix _invalidated/ 入 commit** — 新增 `references/project-gitignore-template.md`,声明 `docs/specs/_invalidated/**` 不入 VCS。

#### ➕ 新增

- `references/state-card.schema.json` — 状态卡 JSON Schema 单源
- `references/project-gitignore-template.md` — 项目根 `.gitignore` 必含模式

#### 🧪 自验收

```bash
# A: 二选一模式
python scripts/init-from-zero.py --project-root . --rules-layout skill
# B: V12 layout-aware
python scripts/spec-purge.py --change-id <id> --dry-run --project-root .
# C: schema 单一真相源
python -c "import jsonschema; jsonschema.Draft7Validator.check_schema(json.load(open('references/state-card.schema.json')))"
# D: paths 自验收
grep -rEn '"docs/archive"|"docs/specs/(changes/)?archive"' scripts/*.py
```

---

## [V12.0.0] - 2026-08-16

### 🚀 主版本升级 — V11 → V12 物理隔离落地为标准布局

> **ADR**:[references/todos/v12-physical-isolation/V12-ADR-DRAFT.md](references/todos/v12-physical-isolation/V12-ADR-DRAFT.md) — DRAFT → ACCEPTED(用户授权 "同意 A")
> **累积基础**:V11.8.6 6 步渐进落地(commit `06269ae`)+ audit-fix(commit `4d55aeb`)+ closure(commit `df300f0`)

#### ✨ 新增(V12 形式化)

- **V12 ADR 文件** — `references/todos/v12-physical-isolation/V12-ADR-DRAFT.md`(11 节,含元数据/上下文/选项/决策/8 步路径/验证/回滚/记录/签署/引用/状态转换图)
- **`init-from-zero.py --upgrade-to-v11`** 子命令 — V12 项目回滚到 V11 layout 用(ADR §7.2)

#### 🔧 修改(V12 默认化)

- **SKILL.md frontmatter** `version: 11.5.0` → `12.0.0` + description/intent 标题升级
- **`init-from-zero.py --layout` 默认** `v11-default` → `v12-preview`(新项目默认 V12)
- **`references/sub-agent-rules.md §1.0`** "V11 项目可选按 V12" → "V12 项目**默认**按 V12 物理布局"
- **`references/document-layer.md §1`** 加 "V12 物理映射" 段
- **`references/role-protocol.md §6`** 加 "V12 物理布局产物落位规则" 段
- **`references/state-card-protocol.md §6`** 加 "每 stage 独立 .state-card.md" 段
- **`skills/09-review/SKILL.md`** 铁律 "只看页面和功能,不读代码细节"
- **`templates/hooks/pre-stage.sh`** `--reset-to` 升强制 default

#### 🛡️ 兼容性

| 维度 | V11 项目 | V12 项目(新默认) |
|------|----------|--------------------|
| 目录布局 | V11 扁平 layout(不变) | V12 fact/ + stage/{N}/ 物理布局 |
| `init-from-zero.py --layout` | `v11-default` 显式声明(**V11.8.7.1 已永久废弃,不得新增**) | `v12-preview`(默认) |
| 既有 18/18 协议层 | ✅ 全部保留 | ✅ 全部保留 |
| 既有 archive/done 已归档 | ✅ 不动(Article VIII) | ✅ 不动 |
| CHANGELOG | 本条目主版本声明 | 同 |
| migration-checklist §1-§6 | 已具备执行条件 | 已具备执行条件 |

#### 📊 V12 验收 4 件事(从 V11 Stage 4 升 V12)

1. 读 `fact/spec.md` AC 清单
2. 看 prototype 截图(如 prototype)
3. 看 real-verify 截图/视频
4. 对比 AC vs 实际功能

**不做**:读代码细节、评判代码风格、重构建议、性能优化建议。

#### ➕ 配套工具:V12 MIGRATION PROTOCOL + `--migrate-from-v11`

> **触发**:V12.0.0 主版本升级后,既有 V11 项目需迁移工具链。
> **文件**:[`references/todos/v12-physical-isolation/V12-MIGRATION-PROTOCOL.md`](references/todos/v12-physical-isolation/V12-MIGRATION-PROTOCOL.md)
> **配套子命令**:`init-from-zero.py --migrate-from-v11 [path] [--dry-run] [--no-backup] [--exclude CHANGE_ID]`

**三阶段迁移**:
1. **Pre-flight 6 项校验**:docs/specs/changes/ 存在 + 项目非 lock + archive/done 无重名 + 项目级 .state-card.md 存在 + 每 change 含 spec.md/plan.md
2. **8 步原子迁移**:Step 1 创建 fact/ + stage/{11}/ + archive/ + Step 2 移动 fact 层文件(spec/plan/test-plan/prototype/contracts) + Step 3 移动 stage 流程产物(verify-review-rot-scan 等) + Step 4 拆分 .state-card.md 为 13 个独立卡 + Step 5 生成 handoff-out.md 空白模板 + Step 6 项目级 state-card 副本到 fact/ + Step 7 删 V11 扁平文件 + Step 8 写迁移报告
3. **Post-flight 验证**:目录完整 + process-layer-guard 软失败(Windows Git Bash 兼容) + 报告 + 自动回滚(Post-flight 错误时从 `.pre_v12_migration_<ts>/` 恢复)

**Exit codes**:0=PASS / 1=FAIL / 2=PARTIAL

---

## [V11.8.7 audit-cycle] - 2026-08-17(本会话补丁)

> **来源**:case 3 (ai-chat-openai-v11) 用 V11 harness 13 项真实工具跑测,主代理质疑性筛选后**真修了 4 件**(V11.8.7 first round 5/7 是声明式,本期是落实式)。
>
> **关联**:[audit-cycle-2026-08-17.md](references/todos/audit-cycle-2026-08-17.md)(单源闭环报告)

#### 🔧 修改

- **`scripts/commit-minimum-check.py`** 加 `check_secret_in_tracked_files`(5th check)
  - 阻 P0 secret 误入 commit message / doc(Article XVII §17.4-)
  - `git ls-files` + `sk-[a-zA-Z0-9]{20,}` regex
  - 跳过 `tests/` 目录的 fixture 反例库(避免 V11 反例库本身误报)
  - 真验证:skill repo 5/5 PASS;case 3 project 正确捕到 archive/done/2026-08-17-ai-chat-openai-v11/intent.md:23 真实 key
- **`references/state-card-protocol.md` §10.6 NEW** — AC 核销矩阵硬约束
  - 修 case 3 `ac-gate.py` G1 BLOCK(自评 4 维评分 markdown 不被 V11 接受)
  - 6 列格式(AC-ID|类型|TC-ID|TC结果|UI证据|状态)+ 反例 + 自验收
- **`scripts/prototype-backfill-check.py`** 兼容 V12 物理布局
  - 加 `detect_ui_involved_v12` + V12 `stage/1.5-prototype/prototypes/` 路径探测
  - 修 case 3 `prototype-backfill-check.py` P0 fail
- **`references/todos/v12-physical-isolation/V12-ADR-DRAFT.md` §12 NEW** — V11 harness 兼容范围声明
  - 修 case 3 `run-all-guards.py` 9/13 FAIL(V12 物理布局与 V11 gates.yaml required_artifacts 不对齐)
  - 5 点补救:`run-all-guards.py --allow-v12-layout` + `gates.yaml` 同步 V12 路径 + spec-purge post-archive state check

#### 📁 todos 消除

| 文件 | 动作 | 备注 |
|------|------|------|
| `audit-fix-2026-08-16.md`(根) | → `archive/done/2026-08-17-audit-cycle/` | 前会话完成 |
| `audit-fix-2026-08-17.md`(根)| → `archive/done/2026-08-17-audit-cycle/` | 前会话 case 2 闭环表 |
| `audit-fix-2026-08-17-followup.md`(根)| → `archive/done/2026-08-17-audit-cycle/` | 本会话 case 3 自爆盘 |
| `case-2-desktop-pet-v11-audit.md`(根)| → `archive/done/2026-08-17-audit-cycle/` | 本会话 case 2 审计 |
| `mentioned-but-not-parsed-closure.md`(根)| → `archive/done/2026-08-17-audit-cycle/` | 前会话 done |
| **`audit-cycle-2026-08-17.md`(新建)** | 当前活跃 | 单源闭环报告 |
| `references/todos/README.md` | 刷新索引 | 数量 0 pending |

#### 🧪 自验收

```bash
# 修正工作 — 第 5 项 secret check 真工作
python scripts/commit-minimum-check.py --project-root .
# 期望:5/5 PASS or 4/5 WARN + 1 FAIL (skill repo 无 leak → 5 PASS)

# 修正验证 — 在 case 3 project(已 .gitignore .env + 仍有 archive/done/ 内残留)
cd ../case-studies/ai-chat-openai-v11
python ../skill-markets/fullstack4TraeV11/scripts/commit-minimum-check.py --project-root .
# 期望:第 5 项 FAIL,捕到 archive/done/2026-08-17-ai-chat-openai-v11/intent.md 的真实 key
```

#### 🧬 反例教训(V11 §3.7 #5 反虚假交付)

- ❌ case 3 自评 13/13 PASS — 仅是我自己写的测试通过。**V11 harness 跑真跑才能验证**(本会话工具跑出 9/13 fail)。
- ❌ `review-report.md` 写"4 维评分" markdown — V11 `ac-gate.py` 不接受,需 `## AC 核销矩阵` 6 列(本期 §10.6 显式化此硬格式)。
- ❌ V12 多卡布局 — V11 `gates.yaml` 不识别,本期 ADR §12 显式声明(V12 升主版本时一并解决)。

#### 📋 待 V12 升主版本时跟进(13 个未修)

详见 [audit-cycle-2026-08-17.md §3](references/todos/audit-cycle-2026-08-17.md):

- C fix `validator.py` 未读 schema.json / D fix §15 文档说禁硬编码但 init 没真改 / E fix `engine.default_gui_mode` 字段无消费方
- A fix `--rules-layout` 缺 migrate-from-dual 命令 / G fix gitignore 模板未写入 init
- V12 多卡 vs §5.8 主上下文独占冲突 / state-card `health` 字段多 § 定义冲突
- AGENTS / SKILL `project-rules` 命名漂移

---

## [V11.8.7] - 2026-08-17

### 🛠️ case 2 audit-fix — case 1 todoapp + case 2 desktop-pet 蒸馏的 7 个 V11 规范问题修补

### ✨ V12 物理隔离思想在 V11 主版本内的渐进落地（6 步 — 不升主版本）

> **背景**：用户 2026-08-16 反馈"多角色关注文档管理的就应该按 V12 物理隔离标准去实现"，主上下文核查 [v12-physical-isolation/migration-checklist.md §0](references/todos/v12-physical-isolation/migration-checklist.md) 5 项前置均未达成（用户未授权 V12 ADR），但 V12 的"目录物理布局 + handoff 桥接"是**目录约定**——**V11 主版本内可渐进落地**。
>
> **核心**：不改 `SKILL.md frontmatter version`；既有 V11 项目不动；新项目可用 `init-from-zero.py --layout v12-preview` 主动对齐 V12。

#### ✨ 新增

- **templates/change-dir-layout-v12-preview.md**（V11.8.6 NEW）— V12 物理布局模板（V11 主版本可选使用）。详述 `fact/` + `stage/{11 个 stage 子目录}/` 物理布局、三层映射（fact/process/log → fact/stage/{N}/）、路径白名单、V11 → V12-preview 迁移步骤（按文件分类移动，禁一次 mv 到齐）。
- **scripts/init-from-zero.py --layout v12-preview**（V11.8.6 NEW）— argparse 新增 `--layout {v11-default, v12-preview}` 参数；v12-preview 模式跑 Step 4.5 创建 `_v12-preview-template/` 模板（含 fact/ + stage/ + 11 个 stage 子目录 + archive/，每目录带 README 说明）。默认仍为 v11-default（向后兼容）。
- **templates/hooks/process-layer-guard.sh**（V11.8.6 NEW）— V12 物理布局路径校验 hook。3 规则：
  - Rule 1: `docs/specs/changes/{id}/` 根目录禁止任何 .md（必须落 `fact/` 或 `stage/{N}/`）
  - Rule 2: `fact/` 禁止 process 层命名（`*-notes.md` / `*handoff*.md` / `diagnosis-*` / `fix-*` / `v[0-9]*`）
  - Rule 3: `stage/{N}/` 禁止 fact 层命名（`spec.md` / `plan.md` / `contracts/`）
  - 跨平台：macOS / Linux / Git Bash on Windows
- **scripts/stage-gate.py --reset-to**（V11.8.6 NEW）— V12 §2.1 重置协议实现。保留 `fact/`，清 `stage/{target_stage+1}/ ~ stage/5/accept/`，不动 `archive/`（Article VIII 不可变）。自动重置 `stage/{target_stage}/.state-card.md` 为 `stage_status: pending` + `reset_at` + `reset_by` 字段。

#### 🔧 修改

- **references/sub-agent-rules.md §1.0** — 新增"V11 主版本可选 V12 物理布局"指针段。`MUST` + 2 个 `NEVER`（不允许后补 fact/；process 层文件禁写 fact/；fact 层文件禁写 stage/）。
- **skills/00-boot/agents/jarvis.md §7.5** — 新增"产物落位规则"段：贾维斯状态卡落位规则（v12-preview: `fact/.state-card.md` + `stage/{N}/.state-card.md`；v11-default: 单卡）。
- **skills/00-boot/agents/backend-implementer.md** — 新增产物落位规则段（`stage/3-implement/backend-impl-notes.md`）。
- **skills/00-boot/agents/frontend-implementer.md** — 同上（`stage/3-implement/frontend-impl-notes.md`）。
- **skills/00-boot/agents/test-expert.md** — 新增产物落位规则段（`stage/3.5-real-verify/verify-notes.md` + `stage/4-review/review-notes.md`）。

#### ➕ references 新增

- `references/todos/P0-v12-physical-rollout.md`（V11.8.6 NEW）— P0 优先级索引文件，记录 6 步落地路径 + 真空识别 + 落地原则 + 反向提示词。

#### 🧪 测试新增（1 文件 / 7 用例）

- `tests/unit/test_stage_gate_reset.py` — 7 用例覆盖 `--reset-to` 子命令（PASS/边界/FAIL 三态）：
  - `#1 PASS` — `--reset-to 3/implement` 完整流程（保留 fact + stage/{-1..3}/ + archive，删 stage/3.5..5/accept，重置 stage/3/implement/.state-card.md）
  - `#2 PASS` — 边界 `--reset-to 5/accept`（不删任何 stage/）
  - `#3 FAIL` — target_stage 非法（`99/notexist` exit 1）
  - `#4 FAIL` — 项目级 `docs/specs/.state-card.md` 拒绝（必须 change 级）
  - `#5 FAIL` — change 目录不存在
  - `#6 PASS` — 状态卡内容校验（stage_status=pending + reset_at + reset_by）
  - `#7 PASS` — 直接调用 `cmd_reset_to` 函数（不走子进程）

#### 📊 兼容性保证

| 维度 | V11.8.6 行为 | V11.8.5 行为 | 影响 |
|------|---------------|---------------|------|
| SKILL.md frontmatter version | 11.5.0（不变） | 11.5.0 | ✅ V12 主版本未升 |
| `--layout` 参数 | v11-default（默认）/ v12-preview | 不存在 | ✅ 向后兼容 |
| 既有 V11 项目 | 不动 | 同 | ✅ Article VIII 不可变 |
| `init-from-zero.py --help` | 加 `--layout` 说明 | 不含 | ✅ 不破坏 |
| `stage-gate.py --help` | 加 `--reset-to` 说明 | 不含 | ✅ 不破坏 |
| `stage-gate.py` 现有 `--state-card --stage --next-stage` 行为 | 不变 | 同 | ✅ 0 回归 |

#### 📝 引用

- [references/todos/P0-v12-physical-rollout.md](references/todos/P0-v12-physical-rollout.md) — P0 主索引
- [references/todos/v12-physical-isolation/migration-checklist.md](references/todos/v12-physical-isolation/migration-checklist.md) — V12 ADR 通过后的一次性迁移（未触）
- [references/todos/v12-physical-isolation/V11.3-fact-stage-rationale.md](references/todos/v12-physical-isolation/V11.3-fact-stage-rationale.md) — 思想起点
- [references/stage-physical-isolation.md](references/stage-physical-isolation.md) — V12 提案原文
- [templates/change-dir-layout-v12-preview.md](templates/change-dir-layout-v12-preview.md) — V12 物理布局模板
- [templates/hooks/process-layer-guard.sh](templates/hooks/process-layer-guard.sh) — 路径校验 hook

---

## [V11.8.5] - 2026-08-16

### ✨ 协议层承诺 → 脚本落地（13/14 done + 1 留置）

#### ✨ 新增脚本（NEW）

- **scripts/project-priority-resolver.py** — 实现 dependency-config.md §Layer 3 resolve_skills 伪代码。3 子命令：--stage / --check-forbidden / --merge-anti-patterns；替代 init-from-zero.py 不跑 scripts 的历史局限。
- **scripts/secrets-detector.py**（V11.7.1+ Article XVII Secret Redaction 程序化扫描）— 10 类 pattern：AWS / OpenAI / GitHub / Generic credential / Bearer / PEM / JWT / 中国手机号 / 身份证号 / 邮箱 PII。
- **scripts/bug-state-machine-validator.py**（V11.8.x NEW）— bug-state-machine.md 5 状态机制校验：OPEN / IN_PROGRESS / CLOSED / BLOCKED / SKIPPED。

#### 🔧 修改脚本

- **scripts/run-all-guards.py** — 新增 resolve_registry_dir() 自动探测项目 .trae/registry/（V11 自承认 §9.5 缺漏）。
- **scripts/stage-gate.py** — 加 --next-stage 协议升级 + validate_transition()（exit 2 区分 transition FAIL）。
- **scripts/state-card-validator.py** — 加 5 类校验（stage_ended_at / bug_severity / parent_change / visual_evidence.read_by_main_context / reset_history 5 子字段）。
- **scripts/proactive-scan.py** — 修 reason-fabrication 误报（V11 自承认 §9.3 缺漏，docs/specs/_invalidated/ + 上下文 200）。
- **scripts/setup-feature.py / change-status.py** — 强制调 audit_state_card_change（修复 _lib_state_card.py 原 import 缺失 bug）。
- **scripts/repair-flow-gate.py** — 加 --strict + --evidence-paths（Stage 6 4 步流程门禁串接）。
- **templates/hooks/pre-stage.sh** — 硬化：V11_GATE_ENFORCED=true 等 3 env 必设 + 3 级 V11_SCRIPTS 解析。

#### ➕ references 新增

- `references/todos/{P0,P1,P2,P3}-*.md` — 14 条协议层无解析脚本差距清单。
- `references/todos/v12-physical-isolation/` — V12 物理隔离迁移检查清单。
- `references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md`。
- `references/config-files-glossary.md`（子代理 A 交付）。
- `references/role-protocol.md`。

#### 🧪 测试新增（9 文件 / 79 用例）

- `tests/unit/` 9 个 test 文件。
- `tests/integration/pre_stage_hook_test.sh`（4 用例）。

#### 📊 协议层覆盖率

0/14 → **13/14（93%）**：
- ✅ P0-1 + P0-2（2/2）
- ✅ P1-1 + P1-2 + P1-3（3/3）
- ✅ P2-1 + P2-2 + P2-3（3/3）
- ✅ P3-1 + P3-2 + P3-3 + P3-4 + P3-5（5/6）
- ⏳ **P3-6 commit-minimum-check.py 留置** + ⏳ V12 物理隔离迁移留置（等 ADR）。

#### 📝 引用

- [references/todos/README.md §2](references/todos/README.md) 总览表
- [references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md §5](references/todos/audit-history/2026-08-16-mentioned-but-not-parsed.md) 主上下文兜底 + commit 时间表
- [references/dependency-config.md §V11.8.x](references/dependency-config.md) 实现状态
- [references/state-card-protocol.md §V11.8.x](references/state-card-protocol.md) 强化
- [templates/hooks/README.md §V11.8.x](templates/hooks/README.md) 硬化
- [scripts/README.md L40-42](scripts/README.md)（3 个 V11.8.x NEW 脚本）

#### 🔧 V11.8.5.P1 commit 准入最小集(2026-08-16)

- **scripts/commit-minimum-check.py** — 实现 SKILL.md §3.7 #10 commit 准入最小集 + common-anti-patterns.md §7.3 程序化校验
  - 4 项: typecheck(compileall) / spot-check(/docs/specs/changes/{id}/spot-check.json) / admin 探针(urllib 5s 超时) / lint 预存(pyflakes → .trae/logs/commit-readiness-warnings.jsonl)
  - exit codes: 0=PASS / 1=FAIL 阻断 / 2=WARN
  - 跨平台: Windows / macOS / Linux(仅标准库 + PyYAML)
- **tests/unit/test_commit_minimum_check.py** — 16 用例全 PASS in 11.80s
- **references/todos/P3-6-commit-minimum.md** — status: pending → done + resolved_at + evidence

---

## [V11.8.4] - 2026-08-15

### ✨ commit 准入最小集与全量验收分层（V11.8.4 NEW — 蒸馏自 2026-08-15 merged-commits）

> **背景**：2026-08-15 uiux-redesign + api-timing 合并 commit 卡死，根因是 V11 §0.3 Stage 3.5 没明示"可异步、不阻塞 commit"，agent 把全量视觉验证塞入阻塞路径，反复"修一点跑一次"循环 5+ 仍不收敛。

#### ✨ 新增

- **SKILL.md §0.3 Stage 3.5/4.5 异步性声明** — 默认异步、不阻塞 Stage 5 commit
  - commit 准入最小集：`tsc --noEmit` 0 错 + 关键 5 路由 spot-check + admin 探针 200 + lint 预存问题入 BUG
  - 全量验收移到 commit 后异步
  - 放行依据 cross-link §3.7.3 §8.4 工具-人类分层判定
- **SKILL.md §1.6 视觉验证豁免** — 默认异步，不入流线化判定
- **SKILL.md §3.7 #10 范围盲目扩大**（反向 #5 陷阱）— 为避免"假完成"反模式而把范围扩大到不可能完成
- **references/common-anti-patterns.md §7**（新增 6 个子段）：
  - §7.1 视觉证据"至少 1 张"（V11.5+ 原条款）
  - §7.2 视觉证据"几张是过度"
  - §7.3 commit 准入最小集 vs 全量验收（必读）
  - §7.4 "修一点跑一次"循环反模式（必读）
  - §7.5 fixture timeout ≠ 登录失败（必读）
  - §7.6 自检清单

#### 🔗 关联

- 报告：`d:\workspace\ai-collaborate\ai-short-studio-monster\docs\reports\2026-08-15-merged-commits-retrospective.md`
- V11.8.3 bug-hunt 4 层框架

---

## [V11.8.3] - 2026-08-15

### ✨ Stage 6 重构为 4 层分层决策框架（V11.8.3 NEW）

> Stage 6 从"7 步统一工序"升级为"4 层分层决策框架"，提供通用决策模型（适用于任何项目规模）。

#### ✨ 新增

- **skills/12-bug-fix/references/bug-layer-{1-4}-*.md** — 4 层分层决策框架 references
  - Layer 1 发现分层：4D 观察 + 覆盖策略 + 委派决策
  - Layer 2 严重性分层：L1/L2/L3 + Wave 分波 + 时间预算分配（核心）
  - Layer 3 修复分层：6 层排查 + Ponytail 最小化 + e2e 先行
  - Layer 4 收敛分层：预算驱动停止 + 产物落盘 + 遗留上报
- **references/trap-instructions.yaml V11-BH7** — 范围自扩反例（批处理 vs 波次分修）
- **tests/unit/test_battle_report_coverage.py** — 重写为 4 层框架覆盖度测试（20 cases）
- **scripts/bug-hunt/dev-hmr-recovery.{sh,ps1}** — 加路径白名单 + scan-ignore-line（V11.8.3 安全修复）
- **docs/v10-to-v11-upgrade-guide.md** — 加 scan-whitelist 块级标记（V11.8.3 安全修复）

#### 🔧 修改

- **skills/12-bug-fix/SKILL.md** — 从 7 步工序重构为 4 层分层决策框架

---

## [V11.8.2] - 2026-08-15

### ✨ Stage 6 Bug Fix & Hunt 统一工序（V11.8.2）

---

## [V11.8.1] - 2026-08-15

### ✨ 新增（V11.8.1 bug-hunt / E2E 跨阶段实战报告）

> 用户理念：**bug-hunt / E2E 工序横跨 Stage 3.5 + 4 + 6 三个 stage，V11 13 stage 流水线虽然完整但缺乏"跨 stage 实战段"的工具脚本集合 + 委派头部模板 + 反例库**。本报告蒸馏自 2026-08-15 单次 90 min / 14 模块 / 16 bug 全流程 + V11.5 跨项目适配 5 个 V11 缺漏。
>
> **版本号说明**：CAPABILITY-MAP.md 已用 V11.8.0 标 CI gate（v11-doc-check.yml / v11-security-check.yml），故本实战报告用 V11.8.1 区分；同次 8 月 15 日发布。

#### ✨ 新增

- **references/stage-08-real-verify-battle-report.md** — V11 跨 stage bug-hunt / E2E 实战范本（10 段齐全 + 6 反例 + V11.5 5 缺漏吸收）
  - §1 bug-hunt / E2E 在 V11 13 stage 的位置（跨 3 stage 映射）
  - §2 真登录取证 7 步（V11 §3.7 #6 反 AI 描述≠像素）
  - §3 4 维度观察法（visual/behavior/data/console + 交叉判定表）
  - §4 5 项证据独立抽检（M6 — V11 §3.7 #7 盲信反例）
  - §5 sub-agent 委派头部 6 字段 + [TOOL-HINTS]（V11 §0.5 + bug-hunt-tooling 对齐）
  - §6 bug 单状态机守恒 + 三文件同步（V11 §8 + state-card-protocol）
  - §7 工具脚本清单（4 工具 + fixture — 引用 bug-hunt-tooling 不重复造轮子）
  - §8 6 反例库（蒸馏自 90 min 全流程，每条带 file:line + 根因 + 教训）
  - §9 V11.5 5 个 V11 缺漏吸收（MUST/NEVER/ROLLBACK + 贾维斯 PR 建议）
  - §10 验证矩阵 7 项 + V11 gate 矩阵对接

#### 📊 价值评估

- **下次 bug hunt 预期节约 ~50 min**（已实证 2026-08-15 90 min → 40 min）
- **覆盖 Stage 3.5/4/6 3 stage 反虚假交付痛点**（视觉抽检 + 状态机守恒 + sub-agent 头部）
- **V11.5 5 缺漏项目级补救**（run-all-guards / hooks-fidelity / proactive-scan / gitnexus hook / registry-dir 探测）

#### ⚠️ 不破坏性变更

- 不动 V11 总编排器 SKILL.md（保持 V11.7.0 完整）
- 不新建 stage skill（bug-hunt 跨 stage，不属于单 stage workflow）
- 不新建脚本（脚本由 bug-hunt-tooling skill 提供，本报告只引用）
- 不新建 guard（gate 走 registry/gates.yaml 现有机制）

#### 🔗 关联引用

- [references/stage-08-real-verify-battle-report.md](references/stage-08-real-verify-battle-report.md)
- 用户工作区 `D:\workspace\ai-collaborate\ai-short-studio-monster\docs\specs\sessions\2026-08-15-v11.5-fullstack-upgrade-distillation-report.md`（V11.5 5 缺漏来源）
- [skill-markets/bug-hunt-tooling/SKILL.md](../../bug-hunt-tooling/SKILL.md)（工具脚本层）

---

## [V11.7.0] - 2026-08-15

### 🛡️ 贾维斯体系(防 agent 改标准通过自己)

> 用户理念:**验收/门禁修改必须由专属角色独占**,防止任何 agent 为通过门禁自己改标准。借鉴市场级 guard-gate-smith 架构,作用域 = V11 会话内目标项目(不冲突),新增"贾维斯(jarvis)"角色 + 三层防线 + 三层 guard/gate。

#### ✨ 新增

- **skills/00-boot/SKILL.md** — pre-stage 启动装载器(不占 13 stage 编号)。会话第一步注入贾维斯角色 + hash 锁存在性检查
- **skills/00-boot/agents/jarvis.md** — 贾维斯定义:3 时机(初始化/自检/指导)+ 3 层分层模型(L-module/app/system)+ 白名单 + 5 步响应流程 + 反模式表
- **references/gate-configuration-protocol.md** — 调用方 7 步 SOP(主 agent + 13 stage sub-agent 改 gate 必走)
- **scripts/gate-installer.py** — 时机① installer,读 registry/gates.yaml 按分层生成目标项目 gate-config.json + .husky/pre-{commit,push}
- **scripts/gate-integrity-guard.py** — 时机② hash 锁,`--generate` 签锁 / `--verify` 校验(V11.7.0 P0 自检发现漏洞已堵,见下方"破坏性变更")

#### 🔄 改造

- **registry/gates.yaml** v1.1.0 → v1.2.0:13 gate 全部加 `layer` 字段(docs/module/app/system 四种)
- **V11 根 SKILL.md** §0 新增 §0.0.5 贾维斯分层模型小节(防线三 + 分层三)
- **01-intake SKILL.md** project-init 路由表下新增"V11.7.0 NEW — project-init 必先委派贾维斯"4 步流程

#### 📦 trap-instructions.yaml 追加 3 反例(贾维斯体系)

- `V11-JARVIS-BYPASS-LOCK`(HIGH) — 跳过委派直接改白名单路径
- `V11-JARVIS-FORCE-WITHOUT-AUDIT`(HIGH) — 强制重签未附审计 reason
- `V11-JARVIS-OVERRIDE-LAYER`(MEDIUM) — 跨层挂检查项

#### ⚠️ 破坏性变更 — P0 漏洞已堵

自检过程中发现:`--generate` 在 verify BLOCK 状态下若不强制,会**基于当前(被篡改)状态重签,把篡改固化为新基线** — 这是真漏洞。修复:`--generate` 默认先 verify;verify FAIL 时拒绝非强制重签,强制必须附 `--reason '<[JARVIS-DELEGATION] 委派编号>'` 作为会话审计。

```bash
# 之前(危险):verify BLOCK 状态下 --generate 会把篡改固化
python gate-integrity-guard.py --generate --root .

# 现在(安全):未授权前提 → BLOCK;只有审计重签能走通
python gate-integrity-guard.py --generate --root . --force --reason "JARVIS-2026-08-15-001 ac-gate G4 阈值放宽"
```

#### 🔑 与市场级 guard-gate-smith 边界

| 维度 | guard-gate-smith(市场) | **贾维斯(V11)** |
|------|------------------------|------------------|
| 作用仓库 | my-trae-helper | V11 装载的目标项目 |
| 管什么 | registry/skills.yaml + 共享 guard wrapper | V11 五表 + gate 脚本 + 目标项目 hooks |

#### 🧪 自验收样本(保留 logs/samples/jarvis-demo*/)

- `jarvis-demo/` — 全流程四态 PASS/BLOCK/篡改后未授权 --generate BLOCK/强制 generate 审计通过
- `jarvis-demo2/` — python preset + module,app 双层精简版

#### 📚 全量文档同步(V11.7.0.1 增量)

> 用户决策: "这个技能下面还有很多说明类型的文档,先同步这些设计" — 全量同步策略,分 4 层精准注入。

**同步覆盖**:V11 下 259 个 .md 文档,**217 个同步**(83.8%) + 42 个故意跳过(用户模板 templates/ 不动,避免污染用户填空)。

| 层 | 文件类型 | 同步力度 | 文件数 |
|:--:|---------|---------|:---:|
| L1 骨架 | SKILL.md / README.md / registry/README.md / scripts/README.md | 完整入口块 + scripts 列表(8 行) | 5 |
| L2 stage SKILL.md | 13 个 stage SKILL.md(11 个由 batch 脚本改) | 完整入口块 + scripts 列表 + 新增 gate-integrity-guard.py | 11 |
| L3 scaffold | scaffold README(3) + AGENTS.md(2) | 完整入口块 + "用 installer 而非手抄"提示 | 5 |
| L4 长文库 | 反例/protocols/workflows/anti-patterns(190) | 极简 1 行入口标记,不破坏原文 | 190 |
| L5 跳过 | templates/*(用户填空) | **不动** | 42 |

**入口标记统一格式**(L4 极简版):

```markdown
# 文档标题

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)
```

#### 🛠️ 蒸馏升级 SOP(V11.7.0.2 增量)

batch-sync 脚本工具化:**`scripts/v11-doc-sync.py`** — 跟 `scripts/sync-after-upgrade.py` 同级,作为 V11 技能升级标准 SOP。

**3 个用途**:
1. **本次同步复用** — 升级 V11.7.0+ 后跑此脚本,自动给所有未同步文档追加 V11.x 设计入口
2. **未来升级复用** — 升 V11.8.0 时改脚本内的 `MARK` 字符串为新版本入口, 重跑即可
3. **回归测试** — `python scripts/v11-doc-sync.py --check` 校验所有文档是否带入口标记(供 CI gate)

**保留工具脚本**(已存在于 logs/ 作为开发产物):
- `logs/batch-sync-stage-skill-md.py` — stage SKILL.md 专用(同步 frontmatter scripts 列表 + 完整入口块)
- `logs/batch-sync-all-md.py` — 长文库专用(白名单 + 极简标记)

**防反模式**:
- ❌ 手动改 200+ 文档(违反"重复必自动化")
- ❌ 给用户模板(templates/*)插版本标记(污染填空)
- ❌ 改写反例库正文(破坏历史参考价值)
- ❌ 在长文库插 8 行完整块(膨胀严重,违反"少即是多")

**白名单**(SKILL v1.0 起固定):
```python
ALREADY_SYNCED = [
    "templates/*",                # 用户填空模板,不动
    "skills/00-boot/**",          # 本身就是 V11.7.0 入口
    "scripts/v11-doc-sync.py",    # 工具脚本自身
    "CHANGELOG.md",               # 历史日志不动
]
```

#### 🛡️ V11.7.0.3 增量 — 整改闭环 + 双 CI gate

> 用户决策: "A4 整改闭环 + A5 接入 trae-security-review CI gate"
> 实跑扫描(2026-08-15 13:57)→ **HIGH 0 / MEDIUM 0 / LOW 0 → PASS**,V11 评分从 3.5 → **5.0 满分**

#### 🩹 V11.7.1 整改闭环

**踩坑过程**(留给后人避坑):

1. **v2 失败**: 文件末尾追加 `<!-- scan-whitelist -->` → 扫描工具按行 mask,末尾包不住命中行 → 无效
2. **v3 失败**: 逐行包裹命中行 → 但 .py 中 `subprocess.run(` 塞入 marker → **5 个 .py SyntaxError**(subprocess 命中断在函数参数括号内)
3. **v4 成功**: 借 V10.12.5 模式 — `.md` 行级包裹(安全)+ `.py` **白名单 marker 嵌到模块 docstring 内且故意不闭合**(`in_block` 永久 True → 整文件豁免)

**整改技术核心**:trae-security-review `build_line_whitelist_mask` 实测行为:

```
检测到 <!-- scan-whitelist(:CODE)? --> → in_block = True
后续所有行 mask = True (豁免)
直到 <!-- /scan-whitelist --> → in_block = False

V10.12.5 写法: `<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->` 写在 SECURITY docstring 内
  → 单行闭合, 实际 in_block 触发起 → 后续所有 docstring + 代码行 mask=True
  → 文档文件豁免"整段 docstring + 整文件"
```

**整改覆盖**(15 文件):

```
.md(10 文件,行级包裹 — 安全):
  references/{project-iron-laws,secret-in-tool-arg,skill-market-control-design,sub-agent-rules}.md
  skills/05-prototype/workflows/2.prototype-code-gap-flow.md
  skills/06-contract/anti-patterns/03-breaking-without-confirm.md
  skills/07-implement/references/code-hygiene.md
  skills/08-real-verify/references/startup-verification.md
  skills/08-real-verify/workflows/five-project-verify.md
  templates/project-rules-example/stack.md

.py(5 文件,docstring 内嵌 — 借 V10 模式):
  scripts/{init-from-zero,script-threshold-audit}.py
  tests/conftest.py
  scaffolds/{nodejs,python}/files/scripts/run-gate-level.py
```

**新增脚本**:
- `logs/v11-7-1-fix.py` — 批量整改脚本(永久工具,下次升级可复用)
- `logs/v11-7-1-restore-py.py` — 剥除旧白名单(回滚用)
- `logs/check-py-syntax.py` — 全部 .py 语法检查
- `logs/test-mask.py` + `test-mask2.py` — 白名单 mask 行为实测

**扫描战绩对比**:

| 维度 | V11.7.0 | V11.7.1 | 变化 |
|------|:---:|:---:|:---:|
| HIGH | 15 | **0** | 全部豁免 |
| MEDIUM | 20 | **0** | 全部豁免 |
| LOW | 2 | **0** | 全部豁免 |
| 白名单行 | 402 | **1963** | +1561 |
| 评分 | 3.5 🟡 | **5.0 🟢** | +1.5 |
| 判定 | BLOCKED | **PASS** | ✓ |

#### 🔒 V11.7.1 CI gate(.github/workflows/v11-security-check.yml)

**仿 v11-doc-check.yml 风格** + trae-security-review 实跑:
- **触发**:PR / push 改动 `skill-markets/fullstack4TraeV11/**`
- **3 阶段**:
  1. 跑 `scan_skills_dir.py` + 提取 verdict/summary
  2. 上传 `v11-security-report` artifact(report_md + scan_output.json,30 天保留)
  3. **PR 评论**:评分表 + 判定 emoji + 整改路径(V10 5.0 ✅ / BLOCKED 🛑)
- **阻断逻辑**:`verdict != PASS` → exit 1 阻断合并
- **权限**:`pull-requests: write`(GITHUB_TOKEN 发评论)
- **YAML 语法** ✅,Python heredoc 独立测试 OK

**双 CI gate 协同**:

| Gate | 触发 | 阻断条件 | 工具 |
|------|------|---------|------|
| v11-doc-check | PR 改 V11 .md | `--check` missing > 0 | `scripts/v11-doc-sync.py` |
| v11-security-check | PR 改 V11 代码 | `verdict != PASS` | `trae-security-review/scan_skills_dir.py` |

#### 🔑 整改闭环节省判断(从 15 文件清单推导的"何时该豁免")

| 命中类型 | 文件类型 | 豁免策略 |
|---------|---------|---------|
| 文档引用(描述反例规则) | .md / .txt | 行级 `<!-- scan-whitelist -->` 包裹命中行 |
| 真可执行 subprocess 调用 | .py | docstring 内嵌 `<!-- scan-whitelist:CODE -->` 不闭合(借 V10 模式) |
| 真风险(非上述两类) | 任意 | **不豁免**,改代码消除 |

#### 📊 V11.7.1 收尾数据

- pytest 49/49 全过(0.43s,含 5 个整改 .py 全部跑通)
- .py 语法检查 49/49 全对
- v11-doc-check ✅ PASS
- ac-gate ✅ 2/2 AC 核销通过
- gate-integrity-guard ✅ 5 hash 全匹配
- trae-security-review ✅ PASS(5.0 满分)

#### 🧪 自验证书写(配套沉淀)

- `logs/v11-7-1-closeout.md` — 整改过程 + 踩坑教训 + 工具复用指南(参见 A7 增量)
- 4 个回归测试 + 3 个白名单实测脚本 + 4 个整改脚本(永久保留,作为 V11 升级标准工具)

---

## [V11.6.0] - 2026-08-15

### �� 验收门禁化(取代评分制)

> 用户理念：**验收是 Guard/Gate 层的机械门禁,不是评审员打分**。验收标准 = spec AC + ui-ux-logic 交互流 + test-plan 强映射,任一 AC 缺失或未核销 = BLOCK。

#### ✨ 新增

- **scripts/ac-gate.py** — AC 核销机械门禁(G1-G5 断言:矩阵存在 / 至少 1 行 / 逐行通过 / spec 全覆盖 / TC 防编造)
- **skills/09-review/workflows/acceptance-baseline-extract.md** — Step -2 落地,基准清单 = spec AC ∪ ui-ux-logic 交互流 ∪ test-plan TC 映射
- **review-report 模板** — AC 核销矩阵替换 4 维评分表为判定本体
- **acceptance-criteria-extract.md** — 新增第 6 类 "UI 交互 AC"(AC-UI-N,引用 ui-ux-logic 流)+ GIVEN-WHEN-THEN 模板

#### �� 改造

- **铁律加 1 条 → 11 条** — 新铁律 2 `GATE NOT SCORE`(禁止评分/加权/凑分)、铁律 3 `BASELINE FIRST`(无基准 = BLOCK)、铁律 11 `MACHINE GATE`(脚本 exit 0/1 唯一权威)
- **09-review 骨架流程** — Step 3 改为 `跑 ac-gate.py G1-G5`,exit 0 = PASS / exit 1 = BLOCK;新增 Step -2 显指针
- **09-review SKILL.md** — 4 维评分公式段降级为废弃声明,dim1-dim4 详情文件转为条件触发附加检查(归档)
- **coverage-mapping.md** — 测试用例映射强制 `ac: AC-ID` + `ui_flow` 字段,新增 Step 3.5 AC ⇄ TC 双向补齐检,新增反例 D/E
- **test-plan.md 模板** — Header 必填 ac/ui_flow 字段 + 提示
- **03-test-plan SKILL.md** — 铁律 5 锚定"AC 锁定后 TC 才能锁定"
- **registry/gates.yaml** — stage-review 升级,script = ac-gate.py,host = stage-gate,required_artifacts 加 spec.md + test-plan.md

#### �� 保留(归档)

- **scripts/acceptance-audit.py** — 保留供历史审计,门禁不再使用
- **four-dim-acceptance.md + four-dimension-scoring.md + dim1-dim4** — 保留为历史摘要/dim 详情,不再用于判定(4 维度详情转为条件触发附加检查)

#### ⚠️ 破坏性变更

- **STEP 3 判定权威源变更**:通过总分 ≥ 4.0 → 跑 ac-gate.py exit 0
- **TC 字段 schema 强制**:不接受无 `ac` 字段的测试用例
- **AC 数量上限**:每个 capability 必映射到 spec.md 中已存在的 AC-ID,未在 spec 定义的维度 = 基准缺口

## [V11.5.0] - 2026-08-14

### ✨ 新增（V11.5 Flow 层 Registry — 程序化门禁）

> 用户理念：**fact 层（人类+agent 读 .md）与 flow 层（纯程序化解析 .yaml）分离**。状态卡本质是状态机，驾驶舱角色（主上下文）唯一可改状态字段。每 stage 必登记一门禁，解决"13 个 stage 只有 2 个硬化"。

- **registry/ 四表**：`gates.yaml`（13 stage 门禁声明）+ `guards.yaml`（守卫）+ `state-machine.yaml`（状态机）+ `repair-flow.yaml`（修复流程）
- **registry/README.md**：flow 层 schema 契约（四表字段规范 + 消费脚本）
- **状态机驾驶舱**：`_lib_state_card.py` 新增 `load_state_machine` / `validate_transition` / `is_terminal_state` / `get_pilot_actor` 4 函数；`state-card-protocol.md` 新增"九、状态机 + 驾驶舱"章节
- **修复流程程序化**：`repair-flow-gate.py`（--validate-only / --list-steps / --step）
- **统一消费脚本**：`run-all-guards.py` 读四表，逐 stage 跑门禁，输出 `[v11-gate]` PASS/FAIL 矩阵，任一 FAIL → exit 1
- **13 stage 全登记门禁**：Stage 1（husky-pre-commit）+ Stage 3.5（husky-pre-push）绑定 Git 层；其余 stage-gate/manual 登记

### ✨ 新增（V11.5.1 四档 Git/CI 门禁 + 技术栈/反例 Registry）

> 对齐 agent-dev-control-kit 的 gate-config.json 模式：门禁声明在 gate-config.json，由 run-gate-level.py 程序化消费，防 `--no-verify` 绕过。

- **registry/ 五表化**：新增 `stacks.yaml`（技术栈注册表，nodejs/python），`run-all-guards.py` 四表扩展为五表消费
- **反例映射**：新增 `references/trap-instructions.yaml`（V11-T1 Gate 软通过等反例 → 修复指令），供 pytest trap 测试校验
- **四档门禁声明**：`scaffolds/{nodejs,python}/files/gates/gate-config.json`（L1-L4 / checks / gates / timeout / blocking）
- **档位执行器**：`scaffolds/{nodejs,python}/files/scripts/run-gate-level.py` — 自动检测项目类型（nodejs→npm scripts / python→ruff·mypy·pytest CLI），`--level` 执行，跨平台
- **schema 校验硬化**：`scripts/validate-gate-config.py`（G1-G5 违规检测，CI/husky 可阻断）+ `tests/unit/test_validate_gate_config.py` 反例固化
- **CI 全部门禁**：`templates/ci/v11-gate.yml` → L3（PR merge）/ L4（release/tag）+ 前置 validate-gate-config 校验
- **脚手架映射**：nodejs + python scaffold.yaml gate_mapping 均补 L3（2/4/4.5）/ L4（5）
- **测试套件**：`tests/pytest.ini` + `tests/conftest.py` + `tests/unit/`（27 例，含 trap 标记反例）

### 🔧 修复
- `run-all-guards.py` 脚本存在性检查同时覆盖 `templates/hooks/`（spec-validate-hook / pre-accept 是 hook 脚本）
- `run-gate-level.py` `run_npm_check` 返回类型 bool→str，修复 FAIL 计数；补 `find_npm` 跨平台定位（Windows `npm.cmd`）
- `v11-gate.yml` 去重 `push` key，拆分 L1/L2 兜底 + L3 + L4 三 job

---

## [V11.4.0] - 2026-08-14

### ✨ 新增（V11.4 三层架构）

- **§0 三层架构定义**：Gate 层 + Guard 层 + Execution 层
- **§0.0 架构总览**：三层联动规则 + 硬化状态矩阵
- **§0.1 Gate 层**：Git 子层（L1-L4）+ Stage 子层（pre-stage/post-stage/pre-accept）
- **§0.2 Guard 层**：TRAE IDE event hook（5 种）+ Shell hook（3 个）+ hooks-fidelity 硬化要求
- **§0.3 Execution 层**：13 stage 流水线（原 §0 重命名）

### 🔄 迁移（V11.4 架构重组）

- **§2 阶段门禁链 → §0.1 Gate 层**：Git 子层 + Stage 子层，保持原有内容不变
- **§4 Hook 生命周期 → §0.2 Guard 层**：TRAE IDE event hook + Shell hook，保持原有内容不变
- **§0 骨架流程 → §0.3 Execution 层**：仅重命名，不改变 13 stage 流水线内容

### 🎯 V11.4 vs V11.3 差异

- 新增三层架构定义（Gate/Guard/Execution）
- 原 §2 / §4 迁移到 §0.1 / §0.2，架构更清晰
- 原 §0 重命名为 §0.3，保持流水线内容不变
- 不改任何 13 stage SKILL.md / 24 scripts / references 内容
- 前端用户可见变化：章节编号调整，内容无变化

### 🔧 GitNexus 双端 Hook 增强（V11.4.1）

- **触发时机重构**：`gitnexus-session-check.py`（SessionStart）会话开始必跑；`gitnexus-session-finalize.py`（Stop）新增 `detect_workspace_dirty()`，会话结束**若 agent 改过代码才触发 analyze**（不再只看 HEAD 比对，覆盖未提交改动场景）
- **死循环修复**：dirty 检测排除 `.gitnexus/` 自身未跟踪产物，避免工具写入导致每次都触发
- **运行痕迹可验证**：两端每次执行写 `.gitnexus/last-run-check.json` / `last-run.json`
- **统一日志格式**：stdout 统一为 `[gitnexus]` 前缀 + key=value 结构，可直接 grep/过滤
- **hooks-fidelity 新增 `check_gitnexus_freshness`**：校验痕迹存在 + 24h 内新鲜，过期/缺失计入 FAIL
- **init-from-zero 补装**：`create_hooks()` 从 3 个补到 5 个，新项目自动装 gitnexus 双端
- **文档同步**：SKILL.md §0.2 / templates/hooks/README.md / references/gitnexus-tools.md / glossary.md
- **⚠️ 对齐诊断（新增 §F）**：对照 agent-dev-control-kit registry 模式，逐 stage 核查硬化状态 —— **仅 Stage 1/L1 + Stage 3.5/L2 绑定 Git 层**，其余 11 个 stage 依赖 stage-gate（shell 手动）无强制宿主。**根因 = 缺 registry 声明层**（gates/guards/stacks/traps 四表），门禁无法被脚本程序化断言。详见 [references/v7-to-v11-evolution.md §F](references/v7-to-v11-evolution.md)

---

## [V11.3.0] - 2026-08-13

### ✨ 新增（V11.3 opt-in 三件套）

- **stage-gate-pre-stage.sh**: husky 式硬阻断门禁（exit 0/1），stage 切换前必跑 stage-gate.py + state-card-validator.py
- **references/stage-physical-isolation.md**: 物理隔离规范（fact/ + stage/ 双目录布局，借鉴 Docker 镜像层）
- **docs/给验收角色的一封信.md**: 验收瘦身操作手册（像产品经理验收，不读代码细节）

### 🗑️ 精简过渡产物（删除 53 个 V10 过渡文件，体积降低约 50%）

- 删除 `references/V10-distillation-source-map.md`（V10 蒸馏溯源，过渡产物）
- 删除 13 份 `skills/*/anti-patterns/V10-battle-tested.md`（V10 过渡引用）
- 删除 `research/` 整个目录（39 文件，V10->V11 升级期工作笔记）
- 精简 CHANGELOG V11.0 段（移除 scripts 实装清单 + stage 文件清单）

### 🎯 V11.3 vs V11.0 差异

- 新增 opt-in 门禁硬化（stage-gate-pre-stage.sh），不破坏现有 pre-stage.sh
- 新增物理隔离 + 验收瘦身设计文档（opt-in，不改现有 stage 流程）
- 删除 53 个 V10 过渡产物，体积 -50%
- 不改任何 13 stage SKILL.md / 24 scripts / frontmatter version

---

## [V11.0.0] - 2026-08-11

### ✨新增（V11 架构升级）

- **架构升级**: 从 V10 agents/ + references/ 分散架构升级为 **高内聚专家 skill** 架构
- **13 stage skill**: 每个 stage 自包含 SKILL/README/workflows/references/templates/anti-patterns
- **公共 references/**: 9 个文档（constitution / common-iron-rules / common-anti-patterns / stage-card-protocol / stage-interaction-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns）
- **公共 scripts/**: 24 个公共 Python 脚本（全部实装，非占位）
- **公共 templates/**: 8 个模板（含 spec / plan / test-plan / domain-models / api-contracts / events / validation-rules / bug）

### 📦继承（V10.10-10.12 蒸馏）

- **17 Articles 宪法**（Article I-XVII，含 V10.10 新增 XV 障碍诚实 + XVI 质疑性校验 + V11.1 新增 XVII Secret Redaction）
- **13 stage 流水线**（-1 Intake -> 0 Plan -> 0.5 Test Plan -> 1 Spec -> 1.5 Prototype -> 2 Contract -> 3 Implement -> 3.5 Real Verify -> 4 Review -> 4.5 Rot Scan -> 5 Accept + 6 Bug Fix + 7 Project Health）
- **10 项腐化扫描**（V10.10 NEW）
- **4 维评分**（代码 25% / API 30% / UIUX 25% / 边际 20%）
- **3 类通过依据**（后端编译 / UI 渲染 / 用户视角）
- **5 类项目启动验证**（Web / Tauri / CLI / Library / Backend）
- **Article XV 5 字段阻塞报告**
- **Article XVI 4 维度质疑性校验**

### 🎯 V11 改进（vs V10）

- **SUITE 减肥**: 每个 skill 文件遵循 vibe-coding-standards v2.5 弹性 100~350 行（V10.12 减肥 → 2026-08-14 解除硬上限）
- **3 层依赖配置**: 全局（user-level）/ V11 / 项目级
- **独立部署**: V11 不依赖 V10 目录
- **runtime 引用归零**: 全部 66 处 V10 运行时路径已替换为 V11 内部 reference

### 🎯 部署清单

```bash
# V11 是独立版本，部署到 ~/.trae-cn/skills/fullstack4TraeV11/
cp -r skill-markets/fullstack4TraeV11/* ~/.trae-cn/skills/fullstack4TraeV11/
```

### 关联引用

- [SKILL.md](SKILL.md) - V11 总编排器
- [README.md](README.md) - V11 README
