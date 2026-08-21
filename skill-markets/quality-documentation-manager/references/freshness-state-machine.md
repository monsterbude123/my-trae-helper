# Freshness 状态机 + 修复时限协议

> 来源:doc-map-manager v2 freshness 评分 + Write the Docs WEP + DITA 5 态。
> SKILL.md §5 摘要。本文件给完整 4 态状态机 + freshness 4 档 + outdated 时限红线 + ROT 季度审计 SOP。

---

## §1 文档状态机(完整版)

```
                评审通过
   draft  ─────────────────→  stable
     │                          │
     │ 评审不通过               │ 检测到内容过期
     ↓                          ↓
   (回炉)                    outdated
                                │
                                │ 时限红线超时
                                ↓
                           deprecated
                                │
                                │ 文档归档 / 删除
                                ↓
                          (删除)
```

### §1.1 4 态定义

| 状态 | frontmatter `doc_status` | 含义 | 行为 |
|------|------------------------|------|------|
| **draft** | `draft` | 草稿,未稳定 | 不入索引 / 不被引用 |
| **stable** | `stable` | 已发布,当前有效 | 正常检索 + 引用 |
| **outdated** | `outdated` | 已知与代码不一致,待修复 | 入索引但标⚠,触发时限红线 |
| **deprecated** | `deprecated` | 已废弃,不再维护 | 入索引但显示警告 banner |

---

## §2 outdated 时限红线(P0~P2 完整版)

| 优先级 | 模块类型 | 修复时限 | 超时动作 | 告警通道 |
|--------|---------|---------|---------|---------|
| **P0** | 计费 / 安全 / 鉴权 | ≤ 24h | 强制降级为 `deprecated` | Slack #docs-critical + Email |
| **P1** | 核心 API / 架构 | ≤ 7 天 | 升级 P0 跟踪 | Slack #docs |
| **P2** | 边缘功能 / 教程 | ≤ 30 天 | 合并到下一季度 ROT 审计 | 季度报告 |

### §2.1 超时降级协议

```
outdated 文档超 P0 24h 未修复
  → 自动降级为 deprecated(Script 自动改 frontmatter)
  → 触发 Slack #docs-critical 告警
  → 关联 PR / Issue 自动 @ 责任人
  → CI 拒绝后续引用此文档的合并
```

### §2.2 P0 模块识别

```yaml
# .docs-config.yaml(本 skill 推荐)
priority_overrides:
  - path: "docs/modules/billing/**"
    priority: P0
    reason: "计费 — 金额错误直接影响收入"
  - path: "docs/modules/auth/**"
    priority: P0
    reason: "鉴权 — 安全相关"
  - path: "docs/modules/payment/**"
    priority: P0
    reason: "支付 — 资损风险"
  - path: "docs/architecture/**"
    priority: P1
    reason: "架构 — 影响核心 API"
```

---

## §3 freshness 4 档(完整版,与 doc-map-manager 对齐)

| 距 last_verified | 评分 | 图标 | doc-map-manager --grab 输出 | 本 skill 动作 |
|-----------------|------|------|------------------------|------------|
| 0~7 天 | 1.0→0.7 | 🟢 | 高置信,可直接引用 | 无 |
| 7~30 天 | 0.7→0.3 | 🟡 | 中置信,标"可能不是最新" | agent 二次验证 |
| 30~90 天 | 0.3→0.1 | 🔴 | 低置信,必须交叉验证 | 触发 ROT O(Outdated)审计 |
| 90+ 天 | ≤0.1 | ⚫ | 过时,必须验证 | 强制标 `outdated` + 时限红线启动 |

### §3.1 freshness 评分算法

```python
# 本 skill 推荐算法(与 doc-map-manager v2 对齐)
def freshness(last_verified: str, now: str = None) -> tuple[float, str]:
    """返回 (评分, 图标)"""
    from datetime import date, datetime
    lv = date.fromisoformat(last_verified)
    today = date.today() if now is None else date.fromisoformat(now)
    days = (today - lv).days
    if days <= 7:   return max(1.0 - days * 0.043, 0.7), "🟢"
    if days <= 30:  return max(0.7 - (days - 7) * 0.017, 0.3), "🟡"
    if days <= 90:  return max(0.3 - (days - 30) * 0.003, 0.1), "🔴"
    return 0.1, "⚫"
```

---

## §4 ROT 季度审计 SOP(完整版)

> **ROT** = **R**edundant / **O**utdated / **T**rivial 三态文档审计。
> 来源:[InstantDocs IA for Technical Writing](https://instantdocs.com/blog/information-architecture-for-technical-writing)
> ⚠️ **缩写冲突**:fullstack4TraeV11/skills/10-rot-scan 的 ROT = "腐化扫描",同缩写异义。本 skill 不重命名(改破坏触发词)。

### §4.1 ROT 三态定义

| ROT | 含义 | 检测方法 | 修复动作 |
|-----|------|---------|---------|
| **R**edundant | 冗余:两篇文档讲同一件事 | `grep -l "关键词" docs/**/*.md` + 概念相似度 | 删除副本,改相对引用(SSOT §铁律 2+3) |
| **O**utdated | 过期:描述的功能已变更 | freshness 🔴 + GitNexus context() 对比 | 标 outdated,启动 §2 时限红线 |
| **T**rivial | 琐碎:没有实际价值 | 流量低(无引用 + 无点击) + 作者评审 | 删除 |

### §4.2 季度审计流程

```
每季度(3/6/9/12 月)
  │
  ├─ Step 1: 数据采集
  │   ├── doc-map-manager --grab 全部文档(统计 freshness)
  │   ├── grep 同概念多文档(找 R 候选)
  │   └── 分析引用图谱(找低流量 T 候选)
  │
  ├─ Step 2: 分类
  │   ├── R 候选清单(redundant)
  │   ├── O 候选清单(outdated)
  │   └── T 候选清单(trivial)
  │
  ├─ Step 3: 责任分派
  │   ├── 每个文档 → 责任人(从 git blame 取)
  │   └── 优先级 → P0 / P1 / P2
  │
  ├─ Step 4: 修复时限
  │   ├── P0 R/O/T → 1 周
  │   ├── P1 R/O/T → 2 周
  │   └── P2 R/O/T → 下季度前
  │
  └─ Step 5: 验证 + 报告
      ├── 修复后跑 verify.py
      └── 输出季度报告 → Slack #docs + AGENTS.md §5 附录
```

### §4.3 R/O/T 修复脚本(本 skill 推荐,可选)

```bash
# 找同概念多文档(粗糙但有效)
grep -l "亲和性路由" docs/**/*.md
# 期望:每概念 ≤ 2 个文件(定义 + 1 引用)

# 找 freshness 🔴 文档
python -c "
import yaml, glob, sys
sys.path.insert(0, 'scripts')
from freshness import freshness
for f in glob.glob('docs/**/*.md', recursive=True):
    text = open(f).read()
    import re; m = re.match(r'^---\n(.+?)\n---', text, re.S)
    if not m: continue
    fm = yaml.safe_load(m.group(1)) or {}
    lv = fm.get('last_verified')
    if not lv: print(f'{f}: no last_verified'); continue
    score, icon = freshness(lv)
    if icon == '🔴' or icon == '⚫':
        print(f'{f}: {icon} {score:.2f} (last_verified={lv})')
"
```

---

## §5 修复 SOP(按优先级)

### §5.1 P0 outdated(≤ 24h)

```
1. 检测:CI 跑 freshness 算法 → 🔴
2. 责任:git blame → 最近 30 天 commit 作者
3. 修复:
   a. 跑 doc-map-manager --impact(找下游)
   b. 同步修改文档以匹配代码(SSOT §铁律 1)
   c. 更新 last_verified → 今天
   d. 跑 verify.py 验证
4. 兜底:超 24h 未修 → 自动降级 deprecated + Slack 告警
```

### §5.2 P1 outdated(≤ 7 天)

```
1. 检测:每周一 CI 自动扫描
2. 责任:模块 owner(从 .docs-config.yaml priority_overrides 取)
3. 修复:同 §5.1(可放宽到 7 天)
4. 兜底:超 7 天 → 升级 P0 跟踪
```

### §5.3 P2 outdated(≤ 30 天)

```
1. 检测:季度审计(Slack 自动提醒)
2. 责任:原作者
3. 修复:同 §5.1(可放宽到 30 天)
4. 兜底:超 30 天 → 合并到下一季度 ROT 审计
```

---

## §6 状态迁移自动化

### §6.1 自动降级脚本(L4 监控 cron)

```python
"""
scripts/auto-deprecate.py — L4 监控 cron 用
依赖:pyyaml
"""
import yaml, re, glob, subprocess, sys
from pathlib import Path
from datetime import date, timedelta

P0_PATHS = ["docs/modules/billing", "docs/modules/auth", "docs/modules/payment"]
P1_PATHS = ["docs/architecture", "docs/api"]

def priority(path: str) -> str:
    for p in P0_PATHS:
        if path.startswith(p): return "P0"
    for p in P1_PATHS:
        if path.startswith(p): return "P1"
    return "P2"

def days_since(date_str: str) -> int:
    return (date.today() - date.fromisoformat(date_str)).days

TIMELINES = {"P0": 1, "P1": 7, "P2": 30}

for f in glob.glob("docs/**/*.md", recursive=True):
    text = Path(f).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.+?)\n---", text, re.S)
    if not m: continue
    fm = yaml.safe_load(m.group(1)) or {}
    if fm.get("doc_status") != "outdated": continue
    lv = fm.get("last_verified")
    if not lv: continue
    d = days_since(lv)
    limit = TIMELINES[priority(f)]
    if d > limit:
        # 强制降级为 deprecated
        new_text = text.replace('doc_status: outdated', 'doc_status: deprecated')
        new_text = re.sub(r'last_verified: \S+', f'last_verified: {date.today().isoformat()}', new_text)
        Path(f).write_text(new_text, encoding="utf-8")
        print(f"[AUTO-DEPRECATED] {f} (P{priority(f)[1]} 超 {d}d > {limit}d)")
        # Slack 告警(略)
```

---

## §7 与 doc-map-manager 关系

| 本 skill 概念 | doc-map-manager 对应 | 说明 |
|-------------|--------------------|------|
| freshness 4 档 | doc-map-manager --grab 新鲜度评分 | 算法对齐(§3.1) |
| doc_status 4 态 | doc-map-manager frontmatter 兼容 | 字段名 `doc_status`,不冲突 |
| ROT 审计 | doc-map-manager --detect-changes | 提供变更检测,本 skill 给 ROT 维度分类 |

**不重复造**:doc-map-manager 已有 build-index.py / query-index.py,本 skill 不复制。

---

*完整规范见 [SKILL.md §5](../SKILL.md) 摘要;SSOT 铁律交叉引用见 [ssot-protocol.md §6](ssot-protocol.md)。*
