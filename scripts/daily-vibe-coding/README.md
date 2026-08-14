# daily-vibe-coding helpers

> 把本次(2026-08-14)调研中的"探查本地项目"的临时指令固化到脚本。
> 下次跑 daily-vibe-coding 时,先跑这套脚本,把基线写到 `_baseline.json`,
> agent 直接读 JSON,不再重复命令。

## 产物

| 脚本 | 用途 | 何时跑 |
|------|------|--------|
| `collect-baseline.py` | 一次性采集 12 项基线 + 历史消化 | **调研前必跑** |
| `generate-templates.py` | 生成 5 份报告骨架(自动填基线数字) | **collect 跑完后跑** |
| `run-precheck.sh` | Windows + Git Bash 一键入口(探测 Python) | 替代直接调 python |

## 工作流(固化前后对比)

### 固化前(本次调研实际跑的命令)
```
ls skill-markets/                                            # 列 skill
python scan_skills_dir.py skill-markets auto_reports          # 安全扫描
Get-Content skill-markets_*.json                            # 解析 JSON
Get-ChildItem skill-markets -Directory | ...                 # 48/42/11/31 计数
Select-String -Pattern '^version:'                          # frontmatter 枚举
git log -1 --format=%ad                                     # 末次 commit
git rev-parse --abbrev-ref HEAD                             # 分支
Read implementation-log.md (if exists)                      # 历史消化
Write 5 个 .md 文件 + 数字手填                              # 报告
```
**耗时**:~8 分钟命令 + ~5 分钟手填数字 = **~13 分钟**

### 固化后(下次调研)
```
bash scripts/daily-vibe-coding/run-precheck.sh --history 2026-08-14
python scripts/daily-vibe-coding/generate-templates.py
# → _baseline.json 已生成, 5 份 .md 骨架已生成(基线自动填)
# → agent 只需 Read JSON + 补充方法论/建议/决策
```
**耗时**:~30 秒命令 + ~3 分钟手填方法论 = **~3.5 分钟**

**节省**:~73%(13 min → 3.5 min)

## 用法

### 1. 每日调研前
```bash
cd d:\workspace\my-trae-helper
bash scripts/daily-vibe-coding/run-precheck.sh
# 等价: python scripts/daily-vibe-coding/collect-baseline.py
# 输出: logs/daily-vibe-coding/<today>/_baseline.json
```

### 2. 生成报告骨架
```bash
python scripts/daily-vibe-coding/generate-templates.py
# 自动读 _baseline.json, 填数字
# 已存在的 .md 跳过(SKIP), 不覆盖手写内容
```

### 3. 选项

```bash
# 二次扫描(快路径, 跳过扫描)
bash scripts/daily-vibe-coding/run-precheck.sh --no-scan

# 含历史消化(必传昨日日期)
bash scripts/daily-vibe-coding/run-precheck.sh --history-date 2026-08-14

# 只生成 1 份报告骨架
python scripts/daily-vibe-coding/generate-templates.py --only self-audit

# 跳过含扫描的步骤, 强制快路径
python scripts/daily-vibe-coding/collect-baseline.py --no-scan
```

## _baseline.json 结构

```json
{
  "baseline_table": {
    "skill_count": 48,
    "skill_md_count": 42,
    "with_version_count": 11,
    "missing_version_count": 31,
    "scan_files": 1247,
    "scan_verdict": "BLOCKED",
    "scan_high": 43,
    "scan_medium": 166,
    "scan_low": 13,
    "scan_whitelist_lines": 3267,
    "last_commit_iso": "2026-08-14 11:44:28 +0800",
    "git_branch": "dev",
    "collect_time_iso": "2026-08-14T13:29:03+08:00",
    "collect_date": "2026-08-14"
  },
  "scan_detail": { ... },
  "frontmatter_detail": {
    "missing_version": ["acceptance-discipline", ...],
    "no_skill_md": ["..."]
  },
  "git_detail": { ... },
  "history_digest": {
    "history_date": "2026-08-14",
    "total_advices": 7,
    "adopted": 7,
    "in_progress": 0,
    "not_started": 0
  }
}
```

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 全部成功 |
| 2 | 扫描器未找到或扫描失败(部分字段为 null, 基线仍可用) |
| 1 | 命令错误(参数/路径错) |

## 反例(防止过度自动化)

- ❌ **不要把方法论生成也自动化** — 方法论是"提炼", 不是"模板填空"
- ❌ **不要把 SUGGESTIONS.md 的 🟢/🟡/🔴/✋ 也自动填** — 这是用户审批入口, agent 替用户打分 = 违反"用户必须决定"
- ❌ **不要把 implementation-log.md ID-08~ID-10 自动填** — 这是采纳方的工作
- ❌ **不要把 self-audit.md 的 HIGH/MED/LOW 自动分类** — 这是"判断", 不是"采集"

固化范围:**只固化"探查本地项目"那 30%**;剩下 70% 留给 agent 推理。