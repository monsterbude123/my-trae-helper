---
name: trae-security-review
description: 双引擎安全审查能力包 — Agent 驱动的代码安全审查 + 本地 Skill 目录静态扫描 + 严谨用词扫描。当用户需要代码安全审计、项目安全扫描、依赖漏洞检查、密钥泄露检测、三方 Skill 准入审查、文档用词严谨性检查时加载。
requires:
  optional: [acceptance-discipline]
---

# TRAE Security Review — 双引擎安全审查

## 架构概览

```
trae-security-review/
├── SKILL.md                    ← 本文件：编排入口
├── agents/
│   ├── code-security-reviewer   ← Agent 1：AI 驱动的代码安全审查（diff 级）
│   └── skill-scanner            ← Agent 2：本地 Skill 目录静态扫描（准入审查）
├── references/
│   ├── checklists.md            ← 安全审查清单
│   ├── risk-patterns.md         ← 高/中/低风险模式库
│   ├── rigor-patterns.md        ← 严谨用词模式库（10 类）
│   └── report-template.md       ← 报告模板
└── scripts/
    ├── scan_skills_dir.py V2.1  ← 技术安全扫描（8 类风险 + 三层白名单 + 词边界）
    ├── scan_rigor.py            ← 严谨用词扫描（10 类模式 + 词库豁免 + 量化阈值）
    ├── rigor_scanner.py         ← 严谨扫描核心库
    ├── rigor_reporter.py        ← 严谨扫描报告输出
    └── lib/
        ├── rigor_patterns.py    ← 严谨用词词表（10 类 × 中英文）
        └── platform_detector.py ← Skill 平台兼容性识别（19 类平台）V2.2 NEW
```

## 双引擎工作流

```
用户需求安全审查
    │
    ├─ "审查这段代码/这个 diff/这个 PR"
    │   └─▶ code-security-reviewer Agent
    │        ├─ 确定范围（diff / 文件 / 全程）
    │        ├─ 收集上下文
    │        ├─ 5 维度漏洞分析
    │        ├─ 置信度评分
    │        └─ 结构化报告 + Mermaid 可视化
    │
    ├─ "扫描这个 Skill 目录/做准入审查"
    │   └─▶ skill-scanner Agent
    │        ├─ 运行 scan_skills_dir.py V2.1
    │        ├─ 8 类风险静态检测（HIGH ×3 + MEDIUM ×3 + LOW ×2）
    │        ├─ 三层白名单机制（文件级 .scanignore + 区块级 HTML 注释 + 行级 ignore-line）
    │        ├─ 平台兼容性识别
    │        └─ JSON + Markdown 双格式报告（含白名单豁免透明段）
    │
    └─ "项目全面安全评估"
        └─▶ 先跑 code-security-reviewer → 再跑 skill-scanner
              合并报告 → 输出完整安全审计
```

## scan_skills_dir.py V2.1 能力（V10.12.5 NEW）

### 8 类风险检测

| 级别 | Code | 模式 | V2.1 关键变更 |
|------|------|------|--------------|
| HIGH | `CMD_RM_RF` | `\brm\s+-rf\b` | 无变化 |
| HIGH | `DYN_EVAL` | `\beval\s*\(|\bexec\s*\(` | 无变化 |
| HIGH | `HARDCODED_SECRET` | `(api[_-]?key|token\|secret\|password\|private_key)\s*[:=]\s*['\"\`].{8,}['\"\`]?` | 无变化 |
| MEDIUM | `SHELL_EXEC` | `subprocess/child_process/os.system` | 无变化 |
| MEDIUM | `HTTP_INSECURE` | `http://` | 无变化 |
| MEDIUM | `SUDO_OPERATION` | `\bsudo\b` | 无变化 |
| LOW | `STACK_LEAK` | `print\(.*\btraceback\b\|print\(.*\bstack\b\|...` | **V2.1 加 `\b` 词边界**（修复 "Fullstack" 项目名误判）|
| LOW | `WEAK_CRYPTO` | `\b(MD5\|SHA1\|DES\|RC4)\b` | 无变化 |

### 三层白名单机制

| 层级 | 语法 | 用途 | 示例 |
|------|------|------|------|
| 文件级 | `.scanignore`（gitignore 格式）| 跳过整个文件 | `risk-patterns.md` |
| 区块级 | `<!-- scan-whitelist[:CODE1,CODE2] -->` ... `<!-- /scan-whitelist -->` | 文档引用豁免（HTML 注释）| `<!-- scan-whitelist:CMD_RM_RF -->` |
| 行级 | `<!-- scan-ignore-line -->` 或 `# scan-ignore-line` | 单行豁免 | `# scan-ignore-line` |

**特性**：文档文件（.md/.txt）自动忽略 CODE 限定（默认全部豁免）；代码文件（.py/.js/.ts）按 CODE 过滤。

**透明报告**：报告新增"白名单豁免段"展示文件级跳过 + 行/区块级豁免数 + 按 CODE 统计豁免数。

## 外部互补工具

本包是 AI Agent 层的能力。以下 CLI 工具可作为互补，通过 Agent 调用来集成：

| 工具 | 用途 | 安装 |
|------|------|------|
| `github/awesome-copilot@security-review` | AI 驱动的全代码库安全扫描 | `npx skills add github/awesome-copilot@security-review` |
| ~~`skills-security`（Damond-Fung）~~ | ~~纯本地 Skill 目录静态扫描~~ | **已整合**：能力（5 类风险 + 平台识别）已迁入本 skill `scripts/lib/platform_detector.py` + `scan_skills_dir.py V2.1`。原仓库保留 DEPRECATED 兼容壳 |

## 与 acceptance-discipline 的协作

本技能包的审查结果可集成到 `acceptance-discipline` 的发版门禁流程：

```
code-security-reviewer 输出
    → 安全维度打分 ≥ 4.0 才能通过
    → 移交 gate-keeper-agent 汇总
    → 与 unit-test / integration-test / perf 结果合并
```

---

## scan_rigor.py 严谨用词扫描（V2.2 NEW）

### 10 类风险模式

| Code | 类别 | 严重度 | 触发示例（应避免） |
|------|------|--------|-------------------|
| `EMOTIONAL_TONE` | 情绪化用词 | LOW | 非常好用 / 极致 / 完美 / awesome / perfect |
| `ABSOLUTE_CLAIM` | 绝对断言 | LOW | 100% / 零风险 / absolutely safe / guaranteed |
| `VAGUE_QUANTIFIER` | 模糊量化 | LOW | 大量 / 少量 / many / several |
| `INCLUSIVE_HEDGE` | 兜底模糊 | MEDIUM | 等等 / 诸如此类 / 以此类推 |
| `UNDEFINED_TERM` | 未定义术语 | MEDIUM | 特殊情况 / 极端情况 / edge cases |
| `DEAD_ANGLE_MARKER` | 死角提示词 | MEDIUM | 一般情况下 / 通常情况下 / generally / typically |
| `PERSONAL_OPINION` | 主观判断 | LOW | 我觉得 / 我认为 / I think |
| `PROHIBITED_PHRASE` | 禁用短语 | LOW | 显而易见 / 显然 / obviously / clearly |
| `OVER_PROMISE` | 过度承诺 | MEDIUM | 一键搞定 / 轻松实现 / one-click / effortlessly |
| `UNMEASURED_BENEFIT` | 不可量化收益 | LOW | 提升效率 / 改善体验 / improve performance |

### 设计原则

- **可证伪**：每条规则都给出具体触发模式 + 替换建议
- **豁免**：代码块（` ``` `）/ 行内代码（` ` `）/ Python 原始字符串（`r"..."`）自动豁免
- **三层白名单**：复用 `scan_skills_dir.py` 的文件级 / 区块级 / 行级白名单语法
- **量化阈值**：总命中 ≥ 30 / EMOTIONAL+PROHIBITED ≥ 10 / 其它类别 ≥ 5 → WARNING

### 用法

```bash
# 自检（验证词表 + 阈值）
python scripts/scan_rigor.py --self-test

# 扫描目录
python scripts/scan_rigor.py skill-markets/<pkg> audit_reports
python scripts/scan_rigor.py skill-markets/<pkg> audit_reports --quiet   # 单行 JSON
```

### 与 .husky 集成

仓库根 `.husky/pre-commit` 已绑定双扫描：

```
每次 git commit
  ├── 1. scan_skills_dir.py → HIGH 阻断 commit
  └── 2. scan_rigor.py → WARNING 仅提示，不阻断
```

启用方式：`git config core.hooksPath .husky`（已配置）
跳过方式：`git commit --no-verify`（不推荐）


