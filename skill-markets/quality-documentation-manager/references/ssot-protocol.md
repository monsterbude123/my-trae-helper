# SSOT 协议 — 详细规范

> 来源:[Docsie SSOT](https://www.docsie.io/blog/glossary/single-source-of-truth-ssot/) + TapTap 实战(Code as SSOT) + DevFlow 反例库(coupled invariant tax)。
> SKILL.md §2 6 条铁律摘要。本文件给完整 6 条铁律执行细节 + 字段命名避坑 + 4 类反例。

---

## §1 SSOT 本质 — 协议而非工具

**核心洞察**(多源印证):

```
SSOT 不是"一个数据库",而是一种协议
├── 所有人用同样的定义、规则、ID
├── "真理" = 数据准确 + 时效 + 完整 + 可追溯
└── 一旦重复存在,所有副本必须字节一致,否则 = 真相污染
```

**SSOT 在 docs/ 的应用原则**(TapTap 实战):

```
代码是权威(Code as SSOT)
文档是派生物,不是独立存在
冲突时代码赢,永远不反过来
```

---

## §2 6 条铁律(完整执行版)

### 铁律 1 — 代码是权威(Code as SSOT)

```
触发场景:文档描述与代码实现不一致
执行:
  1. 先确认代码 git HEAD 是 stable(非 WIP 分支)
  2. 跑 doc-map-manager --impact <doc> 找出反向引用
  3. 修改文档以匹配代码(不反过来)
  4. 触发 doc_status: stable(若原 outdated)
```

### 铁律 2 — 一概念一定义

```
触发场景:同概念在 ≥2 篇文档独立定义
执行:
  1. ROT 审计:R(Redundant)命中
  2. 选一篇作 SSOT(选 explanation 象限优先)
  3. 其他文档改为相对引用
  4. 删除原定义段落(不留"副本")
```

### 铁律 3 — 相对引用替代复制粘贴

```markdown
❌ 复制粘贴(违反 SSOT)
## Redis 配置
Redis 是高性能 KV 存储,支持多种数据结构...
(整段复制自 explanation/redis-choice.md)

✅ 相对引用(SSOT 合规)
## Redis 配置
> Redis 原理与选型 → [Redis 选型原理](../explanation/redis-choice.md)
> 命令参考 → [Redis 命令清单](../reference/redis-commands.md)
(本文档聚焦"如何配置",不重复原理)
```

**强制纪律**:任何 markdown 段落复制粘贴到另一文档 = 触发 SSOT 违规,标 HIGH 反例(见 [trap-instructions.yaml §AP-3](trap-instructions.yaml))。

### 铁律 4 — 反向引用图谱必构建

```
触发场景:修改任何文档前
执行:
  1. 跑 doc-map-manager --impact <doc>
  2. 拿到下游文档清单 + 风险等级
  3. 评估修改是否会触发下游 SSOT 违规
  4. 同步修改下游或留 issue 跟踪
```

**反例**:不知道下游就动手 → 真相污染(coupled invariant tax)。

### 铁律 5 — "真理"四要素必须齐

| 要素 | 检测 | 工具 |
|------|------|------|
| 数据准确 | 文档描述与代码对比 | GitNexus context() |
| 时效 | last_verified 距今 ≤ 30 天 | doc-map-manager --grab |
| 完整 | frontmatter 必填字段齐 | L3 CI |
| 可追溯 | git log + 文档变更记录 | git blame |

**缺任一要素** → 该文档标 `outdated`,启动 §5 时限红线。

### 铁律 6 — 副本必须字节一致

```
触发场景:必须保留副本(例如多语言版本 / 离线分发)
执行:
  1. 用构建工具自动生成(避免人工维护多副本)
  2. CI 检查副本一致性(差异 = BLOCK)
  3. 副本必须带"自动生成,勿编辑"标记
```

**反例**:人工维护多副本 → 必然漂移 → 真相污染。

---

## §3 字段命名避坑(全局 self-improving-agent 冲突)

> 必读:.agents/rules/learning.md §3 铁律(`severity` / `what_is_wrong` / `detect_signal` / `see_also`)。
> 本节扩展到 SSOT frontmatter 字段命名。

### §3.1 SSOT 字段命名表

| ❌ 不用(全局 self-improving-agent schema) | ✅ 用(本 skill SSOT 字段) | 备注 |
|----------------------------------------|------------------------|------|
| `Logged` / `Logged At` | `last_verified` | YYYY-MM-DD,人工核验日 |
| `Priority` | `freshness_tier` | 🟢/🟡/🔴 4 档映射,与 doc-map-manager 对齐 |
| `Status` | `doc_status` | draft / stable / outdated / deprecated |
| `Reproducible` | `verify_method` | manual / ci / gitnexus-cross-check |
| `Related Files` / `Related` | `backlinks` | 由 doc-map-manager --context-mode 自动生成 |
| `Source` | `upstream_ref` | 上游代码/设计文档相对路径 |
| `Notes` | `ssot_notes` | SSOT 特殊说明(如副本关系) |

### §3.2 命名铁律

```
1. MUST 不用全局 schema 命名(避免冲突)
2. MUST 字段语义清晰(读名知义,不依赖注释)
3. MUST 与 doc-map-manager v2 freshness 4 档对齐
4. MUST 用相对路径(违反 = 触发 §铁律 3)
```

---

## §4 4 类反例(常见违反模式)

### §4.1 类型 A — 复制粘贴(违反铁律 3)

```markdown
❌ how-to/configure-redis.md
"Redis 是开源的高性能 KV 存储,使用 ANSI C 编写..."
(完整复制自 explanation/redis-choice.md)
```

**检测**:`grep -l "ANSI C 编写" docs/**/*.md` → 期望 ≤1 个文件。

### §4.2 类型 B — 副本漂移(违反铁律 6)

```markdown
❌ docs/zh-CN/configure-redis.md 与 docs/en/configure-redis.md
内容不一致(一段已更新,另一段未更新)
```

**检测**:CI 用 `diff` 比对 → 差异 → BLOCK。

### §4.3 类型 C — 改前不查下游(违反铁律 4)

```
❌ 修改 docs/architecture.md 后,未跑 doc-map-manager --impact
→ 不知道 docs/modules/payment/{business,tech}.md 引用了 §3.2
→ payment 文档仍描述旧架构 → 真相污染
```

**检测**:git commit hook → 检查是否跑过 `query-index.py --impact`。

### §4.4 类型 D — 文档当 SSOT(违反铁律 1)

```
❌ 文档描述 API 行为,代码实现不同
按文档"修复"代码 → 代码逻辑崩
```

**检测**:PR review 检查项 → "代码改动是否被文档反向驱动"。

---

## §5 去重的可执行工具(业界现状)

| 工具 | 类型 | 用法 | 限制 |
|------|------|------|------|
| **Grep + 人工审查** | 关键字搜索 | `grep -l "关键词" docs/**/*.md` | 不可扩展 |
| **Vale** | 风格检查 | 词汇规范化(术语统一) | 不能查"概念重复" |
| **Spectral** | OpenAPI 规则 | 检查 API 重复定义 | 仅 OpenAPI |
| **mkdocs-material** | 构建时检查 | 构建时验证所有链接 | 需建站 |
| **自定义脚本** | 关键字 + 余弦相似度 | 找相似段落 | 误报高 |

**推荐组合**(本 skill 不重复造脚本):

```
L2 pre-commit  →  Grep 同概念多文档(粗糙但有效)
L3 CI          →  Vale 术语统一 + Spectral OpenAPI 检查
L4 季度审计    →  ROT R(Redundant)人工 review
```

---

## §6 ROT 审计的 SSOT 维度(交叉引用)

ROT(Redundant / Outdated / Trivial)三态文档审计与 SSOT 铁律交叉:

| ROT | SSOT 铁律命中 | 修复动作 |
|-----|--------------|---------|
| **R**edundant | 铁律 2 + 3 | 删除副本,改相对引用 |
| **O**utdated | 铁律 5 | 标 doc_status: outdated,启动 §5 时限红线 |
| **T**rivial | — | 删除(无 SSOT 价值) |

详见 [freshness-state-machine.md §ROT 季度审计 SOP](freshness-state-machine.md)。

---

## §7 业界反例库(DevFlow)

> 来源:[DevFlow Autopilot SSOT Policy](https://github.com/The01Geek/devflow-autopilot/issues/762)
> 术语:**coupled invariant tax**(耦合不变性税)

```
一旦重复存在,所有副本必须保持字节一致
否则 = coupled invariant tax

成本构成:
  ├── 维护成本:每次更新 × 副本数
  ├── 验证成本:diff 比对
  ├── 风险成本:副本漂移 → 真相污染
  └── 教学成本:新成员不知哪个为准
```

**结论**:能不副本就不副本;必须副本则强制自动化生成。

---

*完整规范见 [SKILL.md §2](../SKILL.md) 摘要;反例库见 [trap-instructions.yaml](trap-instructions.yaml)。*
