# Docs-as-Code 工具栈 — 完整配置

> 来源:thedocumentation.org markdownlint-cli CI/CD + Red Hat PR #271 + Vale.sh 用户案例。
> SKILL.md §3 摘要 + 决策树。本文件给完整配置文件示例(lychee.toml / .vale.ini / .markdownlint.yaml / .pre-commit-config.yaml / GitHub Actions)。

---

## §1 lychee.toml(链接检查)

```toml
# lychee.toml — 完整配置(本 skill 推荐)
max_concurrency = 8          # 并发请求数(避免 GitHub rate limit)
timeout = 30                 # 单链接超时(秒)
retry_count = 2              # 外链重试次数
retry_wait_time = 5          # 重试等待(秒)

# 排除规则
exclude = [
  "https://github.com/.*/issues/.*",     # GitHub issue 链接易误报
  "https://twitter.com/.*",              # 社交媒体经常改版
  "^mailto:.*",                          # 邮件不检查
]
exclude_link_local = false   # 检查所有本地文件(内链 100% 必须通过)
exclude_path = ["node_modules", ".git", "dist", "build"]

# 行为
include_verbatim = false     # 不检查代码块内的链接
output = "lychee/out.md"     # 报告输出

# 缓存(加速二次运行)
cache = true
```

### §1.1 CLI 用法

```bash
# 内链扫描(必须 100% 通过)
lychee --offline --config lychee.toml 'docs/**/*.md'

# 外链扫描(允许部分失败 + 重试)
lychee --config lychee.toml 'docs/**/*.md'

# 详细输出
lychee --verbose --config lychee.toml 'docs/**/*.md'
```

---

## §2 .vale.ini + styles/(散文风格)

### §2.1 .vale.ini

```ini
# .vale.ini — Vale v3+ 配置
StylesPath = styles

MinAlertLevel = error   # 只阻断 error,警告允许

[*.md]
# 加载内置 + 自定义 styles
BasedOnStyles = Vale, Microsoft, write-the-docs, Google

# 自定义术语(避免拼写误报)
Vocabularies = [
  docs/vocabularies/Tech/accept.txt,
  docs/vocabularies/Tech/reject.txt,
]
```

### §2.2 styles/config/vocabularies/Tech/accept.txt

```
# 允许的术语(不会被 Vale 标记)
Trae
lychee
markdownlint
Diátaxis
SSOT
ROT
GitNexus
```

### §2.3 styles/自定义规则示例 — Write-the-Docs.md

```yaml
# styles/write-the-docs/Write-the-Docs.md
extends: existence
message: "Avoid using '%s' — use more inclusive language"
level: warning
tokens:
  - whitelist
  - blacklist
  - master
  - slave
```

---

## §3 .markdownlint.yaml(Markdown 语法)

```yaml
# .markdownlint.yaml — markdownlint-cli2 v0.13+
default: true

# 规则级别
MD013: false   # 行长度不限制(中文文档常超 80)
MD033: false   # 允许 HTML 内联
MD041: true    # 强制首行是 H1 标题

# 本 skill 强制规则
MD025:         # 单一 H1
  level: 1
MD026:         # H1 末尾禁止标点
  punctuation: ".,;:!"
MD036: false   # 允许段落用引用(本 skill 模板常用)

# 自定义 — frontmatter quadrant 字段必含(配合 CI grep 二次校验)
MD002: false
```

---

## §4 .pre-commit-config.yaml(L2 pre-commit)

```yaml
# .pre-commit-config.yaml — pre-commit v3+
repos:
  - repo: local
    hooks:
      - id: lychee-link-check
        name: lychee link checker
        entry: lychee
        args: ['--config', 'lychee.toml', '--no-progress']
        language: system
        types_or: [markdown]
        pass_filenames: true

  - repo: https://github.com/DavidAnson/markdownlint-cli2
    rev: v0.13.0
    hooks:
      - id: markdownlint-cli2
        args: ['--config', '.markdownlint.yaml']

  - repo: https://github.com/errata-ai/vale
    rev: v3.0.0
    hooks:
      - id: vale
        args: ['--config', '.vale.ini']

  # 自定义 — frontmatter quadrant 字段校验
  - repo: local
    hooks:
      - id: check-quadrant-frontmatter
        name: check quadrant / doc_status in frontmatter
        entry: python scripts/check-frontmatter.py
        language: python
        types_or: [markdown]
        pass_filenames: true
```

### §4.1 scripts/check-frontmatter.py(本 skill 推荐,可选)

```python
"""
本 skill 推荐 — frontmatter quadrant / doc_status 字段校验
依赖:pyyaml
"""
import sys, yaml, re
from pathlib import Path

VALID_QUADRANTS = {"tutorial", "how-to", "reference", "explanation"}
VALID_STATUS = {"draft", "stable", "outdated", "deprecated"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def check(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.+?)\n---", text, re.S)
    if not m: return "no frontmatter"
    try: fm = yaml.safe_load(m.group(1)) or {}
    except: return "frontmatter parse error"
    if "quadrant" not in fm or fm["quadrant"] not in VALID_QUADRANTS:
        return f"missing/invalid quadrant (got {fm.get('quadrant')!r})"
    if "doc_status" not in fm or fm["doc_status"] not in VALID_STATUS:
        return f"missing/invalid doc_status (got {fm.get('doc_status')!r})"
    if "last_verified" not in fm or not DATE_RE.match(str(fm["last_verified"])):
        return f"missing/invalid last_verified (got {fm.get('last_verified')!r})"
    return None

errs = []
for p in sys.argv[1:]:
    e = check(p)
    if e: errs.append(f"{p}: {e}")
if errs:
    print("\n".join(errs), file=sys.stderr); sys.exit(1)
print(f"OK: {len(sys.argv[1:])-len(errs)}/{len(sys.argv[1:])} files")
```

---

## §5 .github/workflows/docs-guard.yml(L3 CI)

```yaml
# .github/workflows/docs-guard.yml — L3 强制链
name: docs-guard

on:
  pull_request:
    paths: ['docs/**/*.md', '.markdownlint.yaml', '.vale.ini', 'lychee.toml']
  push:
    branches: [main]
    paths: ['docs/**/*.md']

jobs:
  docs-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # ── lychee 死链扫描 ──
      - name: Lychee Link Check
        uses: lycheeverse/lychee-action@v2
        with:
          args: --config lychee.toml --no-progress
          fail: true           # 内链 100% 必须通过
          jobSummary: true     # GitHub Job Summary

      # ── markdownlint-cli2 ──
      - name: markdownlint-cli2
        uses: DavidAnson/markdownlint-cli2-action@v17
        with:
          globs: |
            docs/**/*.md

      # ── Vale 风格 ──
      - name: Vale
        uses: errata-ai/vale-action@v1
        with:
          files: docs/**/*.md
          config: .vale.ini

      # ── frontmatter quadrant 校验 ──
      - name: Check frontmatter (quadrant / doc_status / last_verified)
        run: |
          python scripts/check-frontmatter.py $(find docs -name '*.md')
```

---

## §6 工具选型决策树(完整版)

```
校验目标？
│
├── 内链死链(必须 100%)
│   └── lychee --offline --config lychee.toml
│
├── 外链死链(允许 retry × 2 + issue)
│   └── lychee --config lychee.toml
│
├── Markdown 语法(error 必清零)
│   └── markdownlint-cli2 --config .markdownlint.yaml
│
├── 散文风格(术语 / 拼写 / 包容性)
│   └── vale --config .vale.ini
│
├── Frontmatter 强制字段(quadrant / doc_status)
│   └── python scripts/check-frontmatter.py
│
├── Pre-commit hook 编排
│   └── pre-commit v3+ + .pre-commit-config.yaml
│
├── CI 阻断
│   └── GitHub Actions(lychee-action + markdownlint-cli2-action + vale-action)
│
└── 季度审计 + Slack 告警
    └── cron + lychee-action + Slack webhook(L4 监控)
```

---

## §7 业界采纳证据

| 工具 | 采纳项目 |
|------|---------|
| **lychee** | Red Hat / Kubernetes / Rust |
| **Vale** | GitLab / Discord / Docker / Grafana / Datadog |
| **markdownlint-cli2** | David Anson(社区标准) |
| **pre-commit + lychee** | [Red Hat PR #271](https://github.com/red-hat-data-services/agentic-starter-kits/pull/271) |
| **GitHub Actions 完整配置** | [thedocumentation.org CI/CD 指南](https://thedocumentation.org/markdownlint-cli/integration/) |

---

*完整规范见 [SKILL.md §3](../SKILL.md) 摘要 + §6 强制链;CI 完整示例见 [ci-gate-stack.md](ci-gate-stack.md)。*
