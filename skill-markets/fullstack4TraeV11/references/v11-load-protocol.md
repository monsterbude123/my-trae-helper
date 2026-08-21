# V11 Skill 加载协议(§0.5)

> **来源**:V12 SKILL.md §0.5(防首次产物偏离 + canvas-asset-folders 实战蒸馏)
> **蒸馏日期**:2026-08-19(vibe-coding-standards v2.5 瘦身 — 从 SKILL.md §0.5 抽出)
> **适用对象**:主上下文收到 "Use Skill: fullstack4traev11" 后,9 步加载顺序 + 加载后 3 项验证 + 同类约定 10 项清单

---

## §0.5 Skill 加载协议(V12 升级 — 防首次产物偏离)

主上下文收到 "Use Skill: fullstack4traev11" 后,**必须**按顺序执行:

1. 加载本 SKILL.md(含 frontmatter `stage_config`)
2. **必读** 12 个公共 references:constitution / common-iron-rules(含 Article XVII Secret Redaction)/ common-anti-patterns(含 §19-22 反例)/ stage-interaction-protocol / state-card-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns / **agent-error-diagnosis** / **sub-agent-rules** / **project-structure**
3. **强制调 Skill(name="project-rules")** — 拿项目级 rules 路由表,按需加载项目惯例(V12 NEW — 防违反项目级 rules 协议)
   - **若 `.trae/skills/project_rules_skills/SKILL.md` 已存在** → 直接调用
   - **若不存在** → 必先跑 `python ~/.trae-cn/skills/fullstack4TraeV11/scripts/init-from-zero.py --project-root . --rules-as-skill`(默认开)创建入口,再调用 Skill(name="project-rules")
4. **Glob 1 次** 项目自身约定:`AGENTS.md` / `docs/` / `.trae/rules/` / `.trae/fullstack4traev11.config.yaml` + **项目目录结构**(见 §0.5.1 同类约定清单)
5. **核对 V11 标准路径** — 状态卡应在 `docs/specs/.state-card.md`(项目级)/ `docs/specs/changes/{id}/.state-card.md`(change 级)/ `docs/bugs/{id}/.state-card.md`(bug 级)。**禁止用 `.trae/state-card.md`**(V10 残留,已迁移出 `.trae/`)
6. **如有项目级覆盖** → 按 3 层优先级合并(项目级 > 编排器 stage_config > stage skill depends_on)
7. **列出"我不能踩的雷"清单**(反例 §19-22 + 现有 Article V/IX/XI 必逐项)— 必走(V12 沿用)
8. **Bug 录入触发词识别**(见 SKILL.md §10)→ 询问用户是否录入 bug 单
9. 然后才进入 Stage -1 Intake 工作模式

**反例**:只加载 SKILL.md 主文件就立即进入 stage → 不知项目惯例 → 命名/编号/结构偏离 → 用户 4+ 轮返工。

**反例(V12 沿用 V11.1)**:未列"我不能踩的雷"清单就直接做工作 → 反复踩同一雷 → 见 [unread-rule-pass.md](unread-rule-pass.md) §21

**反例(V12 沿用 V11.2 — 蒸馏自 canvas-asset-folders 实战)**:
- ❌ 跳过 Skill(name="project-rules") 而用 grep/Glob 搜项目 rules → 违反项目级 rules 协议
- ❌ 把状态卡写到 `.trae/state-card.md`(V10 残留路径)→ 未核对 [state-card-protocol.md §1.1](state-card-protocol.md) 必走协议

---

## §0.5.2 加载后验证(V12 沿用 V11.2)

加载协议 9 步走完后,**主上下文必跑 3 项验证**(不进入主流程前):

```bash
# 1. hooks-fidelity.py: 验证 hooks 链路完整
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .

# 2. project-rules skill 入口存在性 LS 验证
ls .trae/skills/project_rules_skills/SKILL.md
# → 不存在 = 反例 §23 触发,必先跑 init-from-zero.py --rules-as-skill

# 3. state-card 路径核对
ls docs/specs/.state-card.md
# → 不存在 = 初始化未完成或路径错误
```

**反例**: 跳过 §0.5.2 验证 = "看似加载成功但 hooks/rules/state-card 三件套某项缺失 → 主流程跑挂"。这是 V11.2 蒸馏的 canvas-asset-folders 实战教训。

---

## §0.5.1 同类约定强制清单(V12 沿用 V11.1)

**第 3 步"Glob 1 次"具体 Glob 哪些目录**——按任务类型激活强制清单(不分类型 = 漏 Glob = 🛑 FAIL):

| # | 类别 | 必 Glob 目录 / skill | 触发关键词 |
|:--:|------|---------------------|-----------|
| 1 | **截屏** | `.trae/skills/screenshot/` 或 `.trae-cn/skills/screenshot/` | screenshot / 截图 / 视觉证据 |
| 2 | **视觉验证** | `.trae/skills/visual-evidence-discipline/` 或 `.trae-cn/skills/visual-evidence-discipline/` | UI 验收 / 像素验证 / 通过依据 |
| 3 | **浏览器自动化** | `.trae/skills/browser-use-cloud/` 或 `.trae-cn/skills/browser-use-cloud/` | browser-use / 网页抓取 / 表单填写 |
| 4 | **UI 测试** | `.trae/skills/playwright-best-practices/` 或 `.trae-cn/skills/playwright-best-practices/` | Playwright / E2E / page object |
| 5 | **E2E 框架** | `.trae/skills/e2e-module-audit/` 或 `.trae-cn/skills/e2e-module-audit/` + **[skills/12-bug-fix/references/bug-hunt-battle-report.md](../skills/12-bug-fix/references/bug-hunt-battle-report.md)**(V11.8.2 NEW Stage 6 Phase A 实战段) | e2e / 端到端回归 / 视觉审计 / bug-hunt / 受 auth 保护路由 / 真登录 7 步 |
| 6 | **录屏** | `.trae/skills/screenshot/` §录屏模式 + `.trae-cn/skills/screenshot/` | 录屏 / 操作回放 / 失败重演 |
| 7 | **a11y** | `.trae/skills/ui-ux-pro-max/` + 项目 `docs/a11y/` | 可访问性 / WCAG / a11y |
| 8 | **性能** | `.trae/skills/ui-ux-pro-max/` + 项目 `docs/perf-budget.md` | 性能 / 帧率 / FCP / Web Vitals |
| 9 | **契约对齐** | `.trae/skills/frontend-backend-contract-alignment/` 或 `.trae-cn/skills/frontend-backend-contract-alignment/` | 前后端契约 / SSE / datetime 格式 |
| 10 | **时间/时区** | `.trae-cn/skills/` 内含 datetime / tz 的 skill | datetime / 时区 / IANA / 时间戳 |

**强制声明格式**(加载协议第 3 步完成后,主上下文回复必须含):

```markdown
§0.5 Step 3 同类清单激活情况:
  - [1] 截屏: ✅/⚠️/N/A — 理由
  - [2] 视觉验证: ✅/⚠️/N/A — 理由
  - [3] 浏览器自动化: ✅/⚠️/N/A — 理由
  - ... (10 项全列)
```

**反模式(V12 沿用 V11.1 禁止)**: "我只 Glob 1-2 项就够了" / "同类理解见仁见智" / "清单太长记不住"。