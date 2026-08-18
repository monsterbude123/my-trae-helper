# case-2-evidence.md — case 2 桌面宠物实战证据

> **[case-driven-skill-audit] 的首次实战证据** — case 2 (desktop-pet-v11) 子代理 + 主代理全流程产出。
>
> **用途**:以后任何 skill 升级 / 引入场景,参考本文件作为"实跑案例"模板。

---

## A. 案例基础信息

| 字段 | 值 |
|------|-----|
| 案例编号 | case 2 |
| 案例题目 | 桌面宠物 (Python Tkinter) |
| 项目位置 | `case-studies/desktop-pet-v11/` |
| 目标 skill | `fullstack4TraeV11` |
| 配置 | `change_layout: v12-preview` |
| 委派时间 | 2026-08-17 |
| 子代理自报 | 全 PASS |
| 主代理硬验收 | 12 项全 PASS + 7 项暴露 |

---

## B. 子代理 self-attest 报告摘要(关键 6 块)

### B.1 项目树

```
case-studies/desktop-pet-v11/
├── .agents/skills/project-rule-skill/   (4 reference)
├── .trae/rules/                          (5 文件)
├── .trae/hooks/                          (5 文件)
├── .trae/fullstack4traev11.config.yaml
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── desktop_pet/                          (8 .py)
├── tests/unit/                           (3 test)
├── docs/specs/changes/2026-08-17-pet-v11/
│   ├── fact/                             (3 文件)
│   ├── stage/{-1..5.5}/                  (11 stage)
│   └── archive/                          (历史)
├── docs/specs/.state-card.md
├── docs/specs/_invalidated/20260817-.../ (spec-purge 中转)
├── logs/screenshot-startup.png
└── FINAL_REPORT.md                       (子代理 self-report)
```

### B.2 13 stage 产物清单

26 个 .md:11 stage 子目录 + fact/3 + 顶层 6 forwarder(spec/plan/contracts/{domain-models,api-contracts}/review-report.md/rot-scan-2026-08-17.md)+ .state-card.md

### B.3 git log

```
424a956 verify/2026-08-17-pet-v11: spec-purge 归档 + FINAL_REPORT + AGENTS 微调
cced21a prep/2026-08-17-pet-v11: V12 物理布局初始化 + 桌面宠物实现 + 13 stage 流水线
```

74 + 34 = 108 文件,5127+ 行入库

### B.4 GitNexus analyze

- 355 nodes / 438 edges / 10 clusters / 2 flows
- 索引时间 10.4s
- 路径:`case-studies/desktop-pet-v11`

### B.5 启动截图

`logs/screenshot-startup.png` — 1920×1080 RGB PNG

- 黄椭圆身体像素 131
- 黑色眼像素 ~57245
- 视觉得分 `pet-like pattern detected OK`

### B.6 子代理自报 7 个 V11 规范问题

| # | 问题 | V11 修复建议 |
|---|------|------------|
| 1 | GUI_MODE 默认 'auto' 触发 PIL Crash | 改 'pure_tk' |
| 2 | init-from-zero 双写 rules 路径 | init 脚本加路径优先级 |
| 3 | V12 物理布局 vs spec-purge 接口冲突 | spec-purge 加 V12 模式 |
| 4 | 拖拽 `<ButtonRelease-1>` 仅 canvas 内 | 全局 binding |
| 5 | change 级状态卡未独立建 | stage-card 协议补 |
| 6 | SearchReplace 工具静默失败 | 工具改进(非 V11) |
| 7 | `_invalidated/` 入 commit | 加 .gitignore 模式 |

---

## C. 主代理硬验收 — 13 项 file:line 抽检

| # | 验证项 | 期望 | 实际位置 | 状态 |
|---|--------|------|---------|------|
| 1 | V12 物理布局 | `fact/ + stage/{N}/` 全在 | `docs/specs/changes/2026-08-17-pet-v11/` | ✅ |
| 2 | AGENTS.md | 项目级 AI 规则 | `case-studies/desktop-pet-v11/AGENTS.md` | ✅ |
| 3 | .trae/rules/ | 3 rule + README | 5 文件 | ✅ |
| 4 | .trae/config.yaml | 含 paths / gates | 配置完整 | ✅ |
| 5 | .agents/skills | project-rule-skill 在 | 4 reference | ✅ |
| 6 | .gitignore | 含 `docs/archive/` | L22 | ✅ |
| 7 | git init | 2 commits | `git log` 验 | ✅ |
| 8 | GitNexus | 跑通 | 355 nodes | ✅ |
| 9 | 13 stage | 26 个 .md | 子报 | ✅ |
| 10 | 源码 | Python Tkinter | `desktop_pet/main.py` | ✅ |
| 11 | 启动截图 | 实跑 + 截屏 | `logs/screenshot-startup.png` | ✅ |
| 12 | 测试 | 3 个 | `tests/unit/` | ✅ |
| 13 | spec-purge 归档 | archive/done | 验证 | ✅ |

---

## D. 暴露的 V11 规范漏洞(主代理 + 子代理共识)

### D.1 HIGH — init-from-zero 双写 rules

- **位置**: `scripts/init-from-zero.py` `--rules-as-skill` 模式
- **根因**:init 脚本没有声明路径优先级
- **修复建议**:加 `--rules-as-files` 模式,或文档化两种模式的差异

### D.2 HIGH — V12 vs spec-purge 接口冲突

- **位置**: `scripts/spec-purge.py` L26-29
- **根因**:V11.8.6 / V12 物理布局与 V11 spec-purge 顶层接口未对齐
- **修复建议**:spec-purge 改为读 `stage/{N}/notes.md` + `fact/*.md`

### D.3 HIGH — 状态卡 schema 协议漂移

- **位置**: `references/state-card-protocol.md` VS `scripts/stage-gate.py`
- **根因**:文档与脚本校验逻辑独立演进,未同步
- **修复建议**:单源 JSON schema,文档 + 脚本都读

### D.4 MEDIUM — V11 SKILL.md 缺 paths.* 文档

- **位置**: `SKILL.md` 主文档
- **根因**:feedback03 路径配置化改造后,SKILL.md 未同步
- **修复建议**:SKILL.md 加新章节

### D.5-7 LOW — 详见 feedback04.md

---

## E. 决策记录

| 选项 | 主代理怎么选 | 理由 |
|------|------------|------|
| 立即修 V11 漏洞 | ❌ 否 | 用户说"只记录,先开 case 3" |
| 记录到 skill todos | ✅ 是 | 已写 `references/todos/case-2-desktop-pet-v11-audit.md` |
| 提炼工作流 | ✅ 是 | 本文 — case-driven-skill-audit SKILL |
| 开 case 3 | ❌ 否 | 用户后续变更 |

---

## F. 文件链接

- [case-driven-skill-audit SKILL.md](../SKILL.md)
- [case-2 验收待修清单](../../../skill-markets/fullstack4TraeV11/references/todos/case-2-desktop-pet-v11-audit.md)
- [feedback04 完整报告](../../../.trae/reports/feedback04.md)
- [case 2 项目根](../../../../case-studies/desktop-pet-v11/)
- [case 2 FINAL_REPORT](../../../../case-studies/desktop-pet-v11/FINAL_REPORT.md)