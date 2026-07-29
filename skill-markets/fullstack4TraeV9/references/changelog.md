# CHANGELOG

## v9.2.0

**Stage 1: OpenSpec 思想内化**
- **哲学段**：SKILL.md 新增 "fluid not rigid / specs grow / delta over rewrite / enablers not gates" 五原则
- **Delta Spec**：spec-writer 改为 Brownfield 场景写 ADDED/MODIFIED/REMOVED/RENAMED
- **Spec 累积生长**：reviewer Step 6 "Spec 累积合并"（delta → 主 spec）
- **Fluid 工作流**：工件依赖定义为"使能器"（新 references/artifact-schema.md）
- **机械化流程吸收**：`#### Scenario:` 格式铁律、MODIFIED 完整复制铁律、tasks.md checkbox 格式、proposal 模板

**Stage 2: 确定性脚本**
- `scripts/spec-validate.py` — Spec 格式机械验证
- `scripts/spec-merge.py` — Delta 机械合并到主 Spec
- `scripts/change-status.py` — 文件系统真相读取

**Stage 3: Hook 体系移植与安装脚本**
- `scripts/install-hooks.py` — 从技能包安装 hooks 到目标项目（**新增核心脚本**）
- 移植 8 个 .ps1 Hook 脚本到 `templates/hooks/`: session-start / doc-sync-gate / contract-gate / spec-validate-hook / auto-test / drift-detect / tasks-integrity / complexity-guard
- 移植 3 个 .py 支持脚本到 `templates/scripts/`: env-init / render-cockpit / log-agent-prompt
- 移植 hooks.json + README.md 到 `templates/hooks/`
- 所有移植文件已更新版本引用: V8→V9, fullstack4traev8→fullstack4traev9, docs/specs/changes→docs/specs, proposal.md→define.md

- `scripts/migrate-v8-to-v9.py` — V8 项目一键迁移到 V9.2（hooks 安装 + 目录拍平 + state-card 转换 + 清理）

**修改文件**: SKILL.md（35 处 + §6.1 Hook 安装段 + §6 脚本表）+ 4 个 agent + intake + changelog
**新增文件**: references/artifact-schema.md + 5 个 scripts/ + 13 个 templates/（8 hooks + 1 json + 1 readme + 3 scripts）+ scenarios/v9.2-scenario-walkthrough.md
**版本号**: 9.1.0 → 9.2.0

## v9.1.0
- 回补 5 项 V8 核心协议（面向 Trae Work 适配，内嵌而非新建文件）：
  - **Completion Report 协议**：每个 Agent 末尾强制产出结构化交付报告（§4），主上下文机械验证
  - **AOP 移交自检**：每个 Agent 末尾 3 项移交前自问清单
  - **委派注入模板**：SKILL.md §1.5 委派注入表，主上下文委派时强制注入 [MUST] 项
  - **Report-Growth 错误升级**：§3 禁止项新增"Agent 异常写入 `.trae/logs/report-growth.jsonl`"
  - **Refactor 回流隔离**：implementer 追加 L1 物理隔离旧产物到 `_invalidated/`
- intake agent：Completion Report 含 `dedup_result` 字段，AOP 自检强制去重搜索
- SKILL.md 版本号 9.0.0 → 9.1.0，描述更新为"面向 Trae Work 优化，保留 V8 核心协议"
- 文件数不变（30），总行数增加约 220 行（均在已有文件末尾）

## v9.0.0
- 采用 OpenSpec 格式替代自定义 Spec 格式
- 6→7 阶段流水线：新增 Define 阶段（合并 Proposal+Plan+Closure）
- 子代理 6→7：新增 definer agent
- references 9→16：新增 define-format / bug-workflow / artifact-lifecycle，增强 acceptance-gates / drift-detect
- SKILL.md 从 84 行扩至 121 行，铁律 4→8 条，禁止项 4→8 条
- 补齐核心门禁：5 维度量化打分、Visual Gate、归档 3 门禁、回流判定树、Bug 快速链、Cockpit 启动感知、DELTA ONLY、工件生命周期
- 保留 V8 核心能力的 90%+，文件数较 V8 减少 31%
