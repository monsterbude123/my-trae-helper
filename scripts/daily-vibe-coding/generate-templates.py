#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-templates.py — 一次性生成 daily-vibe-coding 4 份报告骨架

固化本次调研中重复写的固定模板:
  - external-report.md(空骨架,带历史消化锚点)
  - self-audit.md(基线表 + 12 项检查清单)
  - upgrade-guid.md(3 档优先级骨架)
  - SUGGESTIONS.md(🟢/🟡/🔴/✋ 4 栏骨架)

读取 collect-baseline.py 输出的 _baseline.json 自动填数字,
节省 ~5 分钟/次的手写时间。

用法:
  python scripts/daily-vibe-coding/generate-templates.py
  python scripts/daily-vibe-coding/generate-templates.py --date 2026-08-15 --baseline logs/daily-vibe-coding/2026-08-15/_baseline.json
  python scripts/daily-vibe-coding/generate-templates.py --only self-audit    # 只生成 1 份
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(r"d:\workspace\my-trae-helper")
LOG_DIR = ROOT / "logs" / "daily-vibe-coding"
TZ = timezone(timedelta(hours=8))


def now_str() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %z")


def today_str() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d")


def load_baseline(baseline_path: Path) -> dict:
    if not baseline_path.exists():
        print(f"[gen-tpl] WARN: {baseline_path} 不存在,使用空基线", file=sys.stderr)
        return {}
    try:
        return json.loads(baseline_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[gen-tpl] WARN: 解析 {baseline_path} 失败: {e}", file=sys.stderr)
        return {}


def render_external_report(date: str, baseline: dict, history_date: str | None) -> str:
    """生成 external-report.md 骨架(含基线数据,空方法论部分)"""
    bt = baseline.get("baseline_table", {})
    hist = baseline.get("history_digest", {})
    return f"""# Vibe Coding 每日调研 — {date}

> **运行类型**:{"二次扫描" if history_date == date else "首日全量调研" if not history_date else "日调研"}
> **PART 0 决策**:
> - 历史消化:{hist.get('adopted', 0)} / {hist.get('total_advices', 0)} ✅ ({hist.get('adopted', 0)}/{hist.get('adopted', 0)+hist.get('not_started', 0)} = {((hist.get('adopted', 0) / max(1, hist.get('adopted', 0)+hist.get('not_started', 0))) * 100) if (hist.get('adopted', 0)+hist.get('not_started', 0)) else 0:.0f}%)
> - 7 天去重规则:[按需填写]
> - 本次范围:[按需填写]

---

## 历史消化摘要(PART 0.2 三态分布)

```
✅ 已落地:   {hist.get('adopted', 0)} / {hist.get('total_advices', 0)}
⏳ 进行中:   {hist.get('in_progress', 0)}
❌ 未启动:   {hist.get('not_started', 0)}
⚠️ 已失效:   0
```

[按需展开每条 ID 的采纳细节]

---

## 本日新增方法论:[N] 条(7 天去重规则)

> [按 PART 0.3 决策填写:0 条新方法论 / 5 条新方法论]

### M-01 — [一句话]

- **一句话**: [核心方法论]
- **适用场景**: [何时用]
- **反例**: [常见失败模式]
- **本仓库对接**: [命中技能 + 落地路径]

[按需展开 M-02 ~ M-05]

---

## 来源汇总

| # | 标题 | 作者/机构 | 发布时间 | 链接 | 一句话摘要 |
|---|------|-----------|----------|------|------------|
| 1 | [按需填] | | | | |

---

## 与本仓库的对接点

[按 M-XX 编号逐条列出对应命中技能 + 落地状态]

---

## 不确定 / 待跟进

[按需列出 ⚠️ 条目]

---

## ★实施回写锚点★

| 建议 ID | 建议简述 | 命中技能 | 落地动作 | 回写文件 |
|---------|----------|----------|----------|----------|
| UP-{date}-01 | [按需填] | [路径] | [Write/Edit] | implementation-log.md §ID-01 |
"""


def render_self_audit(date: str, baseline: dict) -> str:
    """生成 self-audit.md(基线表 + 12 项检查清单)"""
    bt = baseline.get("baseline_table", {})
    fm = baseline.get("frontmatter_detail", {})
    scan = baseline.get("scan_detail", {})
    git = baseline.get("git_detail", {})

    # 12 项基线表
    rows = [
        ("1", "skill 目录数", bt.get("skill_count"), "`Get-ChildItem skill-markets -Directory`"),
        ("2", "SKILL.md 文件数(分母)", bt.get("skill_md_count"), "枚举 + 存在性判定"),
        ("3", "含 version 字段的 SKILL.md", bt.get("with_version_count"), "frontmatter 头 10 行"),
        ("4", "缺 version 字段的 SKILL.md", bt.get("missing_version_count"), "同上"),
        ("5", "security scan 文件数", bt.get("scan_files"), "scan_skills_dir.py"),
        ("6", "security verdict", bt.get("scan_verdict"), "同上"),
        ("7", "HIGH 数", bt.get("scan_high"), "解析扫描 JSON"),
        ("8", "MEDIUM 数", bt.get("scan_medium"), "同上"),
        ("9", "LOW 数", bt.get("scan_low"), "同上"),
        ("10", "白名单行数", bt.get("scan_whitelist_lines"), "从 .md 报告抽"),
        ("11", "git log 末次 commit", bt.get("last_commit_iso"), "`git log -1 --format=%ad`"),
        ("12", "git branch", bt.get("git_branch"), "`git rev-parse --abbrev-ref HEAD`"),
    ]
    rows_md = "\n".join(f"| {n} | {label} | `{v}` | {cmd} |" for n, label, v, cmd in rows)

    missing_ver = ", ".join(fm.get("missing_version", [])[:10]) + ("..." if len(fm.get("missing_version", [])) > 10 else "")

    return f"""# 仓库自检 — {date}

> **自检时间**:{now_str()}
> **目的**:固化基线数据 + 12 项检查清单

---

## 体检结果(命令实测)

| # | 检查项 | 值 | 命令 |
|---|--------|----|------|
{rows_md}

**关键发现**:
- version 缺失清单: {missing_ver}
- [按需填:与昨日对比]

---

## 发现的真问题(HIGH/MED/LOW 三档)

### HIGH 级别

[按需填:H-01 / H-02]

### MEDIUM 级别

[按需填:M-01 / M-02]

### LOW 级别

[按需填:L-01]

---

## 不做 / 暂缓的项(附原因)

[按需填]

---

## 给后续 agent 的指令

如果下次自检时发现:
- [触发条件] → [触发动作]
"""


def render_upgrade_guid(date: str, baseline: dict) -> str:
    """生成 upgrade-guid.md 骨架"""
    bt = baseline.get("baseline_table", {})
    hist = baseline.get("history_digest", {})
    return f"""# 本仓库技能升级指导 — {date}

---

## 历史建议处置(来自 PART 0.2)

```
✅ 已落地:   {hist.get('adopted', 0)} / {hist.get('total_advices', 0)}
⏳ 进行中:   {hist.get('in_progress', 0)}
❌ 未启动:   {hist.get('not_started', 0)}
⚠️ 已失效:   0
```

---

## 本日新增升级建议表

| 触发方法论 | 命中技能 | 改动类型 | 优先级 | 具体动作 |
|-----------|----------|----------|--------|----------|
| (空) | — | — | — | 本日无新增升级建议 |

---

## 落地步骤(按优先级降序)

### 1. UP-{date}-01 — [按需填]

- **文件路径**: [路径]
- **预计影响行数**: [行数]
- **风险评估**: [低/中/高]
- **落地步骤**:
  1. [动作 1]
  2. [动作 2]

---

## 不建议做的事(含原因)

- [议题]: [原因] → [替代方案]

---

## 长期演进方向

| 周期 | 方向 |
|------|------|
| **1 周内** | [动作] |
| **1 月内** | [动作] |
| **1 季度内** | [动作] |

---

## ★给后续 agent 的指令★

```
采纳本报告任一"升级建议表"行后,必须追加一行到 logs/daily-vibe-coding/{date}/implementation-log.md:

## ID-<建议ID>
- 采纳时间: <ISO 时间>
- 实际改动: <文件 + 增/改/删 + 行数>
- 验证: <跑了哪个 guard / 自检>
- 结果: ✅ 通过 / ❌ 失败 (原因)
```
"""


def render_suggestions(date: str) -> str:
    """生成 SUGGESTIONS.md 骨架"""
    return f"""# 今日建议清单 ({date})

> 详细调研见 [external-report.md](external-report.md) / [self-audit.md](self-audit.md) / [upgrade-guid.md](upgrade-guid.md)

---

## 🟢 高置信(建议直接采纳)

| 编号 | 建议 | 证据 | 风险 | 一句话理由 |
|------|------|------|------|--------|
| S-01 | [按需填] | [链接] | [低] | [理由] |

---

## 🟡 待核实(采纳前需人工确认)

| 编号 | 建议 | 不确定点 | 建议如何核实 |
|------|------|----------|--------------|
| S-02 | [按需填] | [不确定] | [跑 X 验证] |

---

## 🔴 低置信(本次不强推,记下供下次)

| 编号 | 建议 | 为何低置信 | 何时再议 |
|------|------|-----------|----------|
| S-03 | [按需填] | [原因] | [下次] |

---

## ✋ 用户必须决定(agent 拒绝自动判断)

| 编号 | 议题 | agent 观点 | 等用户回复 |
|------|------|-----------|------------|
| Q-01 | [按需填] | [A/B/C] | "选 X" / "暂缓" |

---

## ★审批工作流★

```
1. 用户读完本文件
2. 对每条建议表态:采纳 / 暂缓 / 拒绝
3. 用户告诉下次会话: "采纳 S-01 / 拒绝 S-02"
4. 采纳方在 implementation-log.md 追加 ID 条目
5. implementation-log.md 是唯一真相源
```
"""


def render_index(date: str, baseline: dict) -> str:
    """生成 INDEX.md(本日目录索引)"""
    return f"""# {date} 目录索引

---

## 产物清单

| 产物 | 路径 | 内容 |
|------|------|------|
| 外部调研 | [external-report.md](external-report.md) | [N 条方法论 + 来源汇总] |
| 仓库自检 | [self-audit.md](self-audit.md) | 12 项基线 + HIGH/MED/LOW 复核 |
| 升级指导 | [upgrade-guid.md](upgrade-guid.md) | 0/3/5 条 UP + 处置步骤 |
| 实施回写 | [implementation-log.md](implementation-log.md) | [N] 项采纳存档 + [M] 个空模板 |
| **建议清单** | [SUGGESTIONS.md](SUGGESTIONS.md) | 🟢/🟡/🔴/✋ 四栏 |

---

## 当日要点

- **方法论**: [N] 条
- **升级建议**: [N] 条
- **自检发现**: HIGH [N] / MED [N] / LOW [N]
- **本会话采纳**: [N] / [N] = [%]

---

## SUGGESTIONS 摘要

| 🟢 高置信 | 🟡 待核实 | 🔴 低置信 | ✋ 用户必须决定 |
|----------|----------|----------|---------------|
| [N] | [N] | [N] | [N] |

---

## 历史消化基线

- [按需填:后续 7 天观察指标]
"""


RENDERERS = {
    "external-report": ("external-report.md", render_external_report),
    "self-audit": ("self-audit.md", render_self_audit),
    "upgrade-guid": ("upgrade-guid.md", render_upgrade_guid),
    "suggestions": ("SUGGESTIONS.md", render_suggestions),
    "index": ("INDEX.md", render_index),
}


def main():
    ap = argparse.ArgumentParser(description="daily-vibe-coding 报告骨架生成器")
    ap.add_argument("--date", default=today_str(), help="今日日期")
    ap.add_argument("--baseline", help="_baseline.json 路径(默认 logs/daily-vibe-coding/<date>/_baseline.json)")
    ap.add_argument("--history-date", help="历史日期(给 external-report 用)")
    ap.add_argument("--only", choices=list(RENDERERS.keys()), help="只生成 1 份")
    args = ap.parse_args()

    baseline_path = Path(args.baseline) if args.baseline else (LOG_DIR / args.date / "_baseline.json")
    baseline = load_baseline(baseline_path)

    out_dir = LOG_DIR / args.date
    out_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for name, (filename, renderer) in RENDERERS.items():
        if args.only and args.only != name:
            continue
        # external-report 需要 history-date
        if name == "external-report":
            content = renderer(args.date, baseline, args.history_date or args.date)
        elif name == "self-audit":
            content = renderer(args.date, baseline)
        elif name == "upgrade-guid":
            content = renderer(args.date, baseline)
        elif name == "suggestions":
            content = renderer(args.date)
        elif name == "index":
            content = renderer(args.date, baseline)
        else:
            continue

        # 检查文件是否已存在(避免覆盖)
        out_file = out_dir / filename
        if out_file.exists():
            print(f"[gen-tpl] SKIP (exists): {out_file}")
            continue
        out_file.write_text(content, encoding="utf-8")
        generated.append(filename)
        print(f"[gen-tpl] OK: {out_file}  ({len(content)} chars)")

    print(f"[gen-tpl] 完成: {len(generated)} 份新文件(已存在的跳过)")
    return 0


if __name__ == "__main__":
    sys.exit(main())