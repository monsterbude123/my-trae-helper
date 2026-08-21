# CI Gate Stack — 4 层强制链

> 来源:thedocumentation.org markdownlint-cli CI/CD + Red Hat PR #271 + Vale.sh 用户案例 + fullstack4TraeV11 §14 Stage 8 v11-doc-check.yml 模式。
> SKILL.md §6 摘要。本文件给完整 4 层强制链(每层含具体工具 + 配置文件 + 触发时机 + 阻断规则)。

---

## §1 4 层强制链(完整架构)

```
L1 编辑器              markdownlint VSCode 扩展 / Vale VSCode 扩展
   │ (开发时实时反馈)
   ↓ commit
L2 pre-commit           pre-commit v3+ 框架
   │ (本地拦截)
   ↓ push
L3 CI                   GitHub Actions docs-guard.yml
   │ (云端阻断)
   ↓ 定期
L4 监控                 cron + Slack/Email 告警
   (持续守护)
```

---

## §2 L1 — 编辑器层

### §2.1 VSCode 配置(`.vscode/settings.json`)

```json
{
  // markdownlint 实时反馈
  "markdownlint.config": {
    "MD013": false,
    "MD025": { "level": 1 },
    "MD026": { "punctuation": ".,;:!" }
  },

  // Vale 实时反馈
  "vale.valeCLI.path": "${workspaceRoot}/.vale/vale",
  "vale.configPath": ".vale.ini",

  // 保存时触发(可选,慢)
  "editor.formatOnSave": false
}
```

### §2.2 推荐扩展

| 扩展 | 用途 |
|------|------|
| `DavidAnson.vscode-markdownlint` | Markdown 语法 |
| `errata-ai.vale-server` | 散文风格 |
| `yzhang.markdown-all-in-one` | 通用 Markdown |
| `foam.foam-vscode` | 笔记型反向链接(可选) |

---

## §3 L2 — pre-commit 层

### §3.1 安装

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg  # 可选
```

### §3.2 .pre-commit-config.yaml(完整版)

```yaml
# .pre-commit-config.yaml
default_install_hook_types: [pre-commit]
default_stages: [commit]

repos:
  # ── lychee 死链 ──
  - repo: local
    hooks:
      - id: lychee-internal
        name: lychee internal link check (offline)
        entry: lychee --offline --config lychee.toml
        language: system
        types_or: [markdown]
        pass_filenames: false
        files: '^docs/.*\.md$'

  # ── markdownlint-cli2 ──
  - repo: https://github.com/DavidAnson/markdownlint-cli2
    rev: v0.13.0
    hooks:
      - id: markdownlint-cli2
        args: ['--config', '.markdownlint.yaml']

  # ── Vale 风格 ──
  - repo: https://github.com/errata-ai/vale
    rev: v3.0.0
    hooks:
      - id: vale
        args: ['--config', '.vale.ini', '--no-exit']

  # ── 本 skill frontmatter 校验 ──
  - repo: local
    hooks:
      - id: qdm-frontmatter
        name: QDM frontmatter check (quadrant / doc_status / last_verified)
        entry: python scripts/check-frontmatter.py
        language: python
        types_or: [markdown]
        pass_filenames: true
        files: '^docs/.*\.md$'

  # ── SSOT 铁律 3 — 防止复制粘贴(检测可疑重复段落)──
  - repo: local
    hooks:
      - id: qdm-redundancy-hint
        name: QDM redundancy hint (informational only)
        entry: python scripts/check-redundancy-hint.py
        language: python
        types_or: [markdown]
        pass_filenames: true
        files: '^docs/.*\.md$'
        # 注:此 hook 只警告,不阻断(避免误报)
```

### §3.3 scripts/check-redundancy-hint.py(本 skill 推荐,可选)

```python
"""
QDM SSOT §铁律 3 检测 — 找 >50 字符重复段落(只警告,不阻断)
"""
import sys, re
from pathlib import Path
from collections import defaultdict

MIN_PARA_LEN = 50  # 段落最小长度(字符)

para_to_files = defaultdict(list)
for path in sys.argv[1:]:
    text = Path(path).read_text(encoding="utf-8")
    # 提取 markdown 段落(连续非空行)
    paras = re.split(r'\n\s*\n', text)
    for p in paras:
        p = p.strip()
        if len(p) < MIN_PARA_LEN: continue
        # 去掉链接和格式,只比对纯文本
        plain = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', p)
        plain = re.sub(r'[*_`]', '', plain)
        para_to_files[plain].append(path)

warnings = 0
for para, files in para_to_files.items():
    if len(set(files)) > 1:
        print(f"[REDUNDANCY-HINT] 段落出现在 {len(set(files))} 个文件:")
        for f in set(files): print(f"  - {f}")
        print(f"  段落预览: {para[:80]}...")
        print()
        warnings += 1

if warnings:
    print(f"[REDUNDANCY-HINT] 总 {warnings} 处可疑重复,考虑用相对引用(见 SKILL.md §2 铁律 3)")
    sys.exit(0)  # 不阻断,只警告
```

---

## §4 L3 — CI 层

### §4.1 .github/workflows/docs-guard.yml(完整版)

```yaml
name: docs-guard

on:
  pull_request:
    paths:
      - 'docs/**/*.md'
      - '.markdownlint.yaml'
      - '.vale.ini'
      - 'lychee.toml'
      - 'scripts/check-frontmatter.py'
  push:
    branches: [main]
    paths: ['docs/**/*.md']

concurrency:
  group: docs-guard-${{ github.ref }}
  cancel-in-progress: true

jobs:
  docs-guard:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python(frontmatter 校验用)
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python deps
        run: pip install pyyaml

      # ── Step 1: lychee 死链(内链 100%)──
      - name: Lychee Link Check(internal)
        uses: lycheeverse/lychee-action@v2
        with:
          args: --config lychee.toml --offline --no-progress
          fail: true
          jobSummary: true

      # ── Step 2: markdownlint-cli2 ──
      - name: markdownlint-cli2
        uses: DavidAnson/markdownlint-cli2-action@v17
        with:
          globs: |
            docs/**/*.md

      # ── Step 3: Vale 风格 ──
      - name: Vale Prose Linter
        uses: errata-ai/vale-action@v1
        with:
          files: docs/**/*.md
          config: .vale.ini

      # ── Step 4: frontmatter 强制字段 ──
      - name: QDM Frontmatter Check
        run: |
          python scripts/check-frontmatter.py $(find docs -name '*.md')

      # ── Step 5: SSOT 铁律 3 — 段落重复检测(警告)──
      - name: QDM SSOT Redundancy Hint
        continue-on-error: true  # 警告不阻断
        run: |
          python scripts/check-redundancy-hint.py $(find docs -name '*.md')
```

### §4.2 阻断规则矩阵

| 检查 | L2 pre-commit | L3 CI | 阻断条件 |
|------|--------------|-------|---------|
| 内链死链 | ✅ | ✅ | 任意失败 |
| 外链死链 | ❌ | ✅ | retry × 2 后仍失败 |
| Markdown error | ✅ | ✅ | error 级必清零 |
| Vale error | ✅(退出非零) | ✅ | error 级必清零(warning 允许) |
| quadrant 缺失 | ✅ | ✅ | 缺失 = BLOCK |
| doc_status 缺失 | ✅ | ✅ | 缺失 = BLOCK |
| last_verified 缺失 | ✅ | ✅ | 缺失 = BLOCK |
| 段落重复 | 警告 | 警告 | 仅提示,不阻断 |

---

## §5 L4 — 监控层

### §5.1 每日全量外链扫描

```yaml
# .github/workflows/docs-daily.yml
name: docs-daily-monitor
on:
  schedule:
    - cron: '0 2 * * *'  # 每天 UTC 02:00
  workflow_dispatch:

jobs:
  daily-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lychee Daily External Scan
        uses: lycheeverse/lychee-action@v2
        with:
          args: --config lychee.toml --no-progress
          fail: false   # 监控模式,不阻断
          jobSummary: true

      - name: Slack Notify
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "📚 docs-daily 外链扫描失败:${{ github.workflow }} ${{ github.run_id }}"}
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

### §5.2 每周 freshness 报告

```yaml
# .github/workflows/docs-weekly-freshness.yml
name: docs-weekly-freshness
on:
  schedule:
    - cron: '0 9 * * 1'  # 每周一 UTC 09:00

jobs:
  freshness-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }

      - name: Generate freshness report
        run: |
          pip install pyyaml
          python scripts/freshness-report.py > .trae/tmp/freshness-weekly.md

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: freshness-weekly
          path: .trae/tmp/freshness-weekly.md

      - name: Slack Notify (🔴 文档清单)
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "📊 本周 freshness 报告:🔴 / ⚫ 文档清单见 artifact"}
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

### §5.3 季度 ROT 审计触发

```yaml
# .github/workflows/docs-quarterly-rot.yml
name: docs-quarterly-rot-audit
on:
  schedule:
    - cron: '0 9 1 */3 *'  # 每季度第 1 天 UTC 09:00

jobs:
  rot-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }

      - name: ROT audit
        run: |
          pip install pyyaml
          python scripts/rot-audit.py > .trae/tmp/rot-quarterly.md

      - name: Create ROT tracking issue
        uses: peter-evans/create-issue-from-file@v4
        with:
          content-filepath: .trae/tmp/rot-quarterly.md
          title: "📚 ROT 季度审计 - $(date +%Y-%m)"
```

---

## §6 与 fullstack4TraeV11 §14 关系

| 维度 | V11 §14 | 本 skill §6 |
|------|--------|-----------|
| CI workflow 文件 | `v11-doc-check.yml` | `docs-guard.yml` |
| Stage | Stage 8 doc-sync | 通用(L4 监控是异步支线) |
| 触发时机 | PR 合并前 | PR / 每日 / 每周 / 季度 |
| 阻断力度 | error 必清零 | 本 skill §4.2 矩阵(细分) |

**关系**:V11 用户复用本 skill §3 工具栈 + §4 CI 模板;非 V11 用户直接用本 skill。

---

*完整规范见 [SKILL.md §6](../SKILL.md) 摘要;配置文件详细见 [docs-as-code-toolchain.md](docs-as-code-toolchain.md)。*
