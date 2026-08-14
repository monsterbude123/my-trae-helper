# Changelog - V11

> V11 独立 skill 版本 changelog。V10 -> V11 蒸馏 + 架构升级。

---

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
