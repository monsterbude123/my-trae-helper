# V12 MIGRATION PROTOCOL(2026-08-16 — V11 → V12 主版本迁移协议)

> **定位**:V11 项目(扁平 layout,单卡模式)→ V12 物理布局(fact/ + stage/{N}/ + 多卡模式)的官方迁移协议
>
> **核心设计**:**非破坏性 + 三阶段 + 强制验证 + 自动回滚**
>
> **当前状态**:V12.0.0 commit `8913af3` 已落地,本文档是 V12 ADR §5 Step 8 的补全 — 提供完整迁移路径(之前只有 V12→V11 回滚子命令)

---

## §0 协议元数据

```yaml
protocol_id: V12-MIGRATION
version: 1.0.0
date: 2026-08-16
author: 主上下文(2026-08-16 V12 ADR 实施补全)
prerequisites:
  - V12.0.0 主版本升级(commit 8913af3)
  - SKILL.md frontmatter version = 12.0.0
  - scripts/init-from-zero.py --migrate-from-v11 子命令可用
related_adr:
  - V12-ADR-DRAFT.md §5 Step 8
  - migration-checklist.md §1-§6(迁移骨架,本文档是其程序化补全)
related_commits:
  - 8913af3 (V12.0.0 主版本升级)
  - 06269ae (V11.8.6 V12 渐进落地)
  - df300f0 (mentioned-but-not-parsed closure)
---

## §1 三阶段迁移路径(强制)

### 1.1 迁移前(Pre-flight)

**目标**:校验项目可迁移性 + 备份 + 风险评估

```
MUST 主上下文在跑 --migrate-from-v11 前:
  1. 校验项目根存在 docs/specs/changes/{id}/ 目录(V11 layout 标志)
  2. 校验项目不在以下状态(migration-checklist.md §6):
     - Stage 3.5 进行中(verify-report 未完)
     - GitNexus 索引跑分析中
     - 任何 stage agent 持 5 protected 字段未落库
  3. 校验 archive/done/{id}/ 不与 change 重名(Article VIII 不可变)
  4. 自动生成 V11 备份(.pre_v12_migration_<ts>/ 整个 docs/specs/ 副本)
  5. 生成迁移报告:每个 change-id 的文件清单(行数、字节数、修改时间)
  6. 校验报告完整(每个 change 的 spec.md / plan.md / contracts/ 必须存在)
```

**Pre-flight 失败 → 立即终止,不开始迁移**。

### 1.2 迁移中(Execution)

**目标**:文件级原子操作 + 幂等性 + 失败回滚

```
V11 → V12 文件映射(按文件分类,绝不全 mv 到齐):

docs/specs/changes/{change-id}/
├── .state-card.md                    # 单卡 → 多卡
├── spec.md                           → fact/spec.md
├── plan.md                           → fact/plan.md
├── test-plan.md                      → fact/test-plan.md
├── prototype.md                      → fact/prototype.md(若有)
├── contracts/                        → fact/contracts/
├── verify-report.md                  → stage/3.5-real-verify/verify-notes.md
├── review-report.md                  → stage/4-review/review-notes.md
├── rot-scan-{date}.md                → stage/4.5-rot-scan/rot-notes.md
├── impl-notes.md                     → stage/3-implement/{actor}-impl-notes.md
└── ...(其他)

迁移步骤(8 步,原子操作):
  Step 1: 创建 docs/specs/changes/{id}/fact/ + stage/{11 个子目录}/
  Step 2: 移动 fact 层文件(spec/plan/contracts/test-plan/prototype → fact/)
  Step 3: 移动 stage 流程产物(verify-report → stage/3.5/notes.md 等)
  Step 4: 拆分 .state-card.md 单卡为 13 个独立卡(每 stage 一张)
  Step 5: 生成每 stage 的 handoff-out.md(≤200 字,从原卡 history 提取)
  Step 6: 项目级 .state-card.md → 副本到 fact/.state-card.md(只读)
  Step 7: 删除 V11 扁平文件(根目录的 spec.md / plan.md 等)
  Step 8: 生成 .migration_v11_to_v12_<ts>.md 报告(每 change 含原文件清单 + 目标位置)
```

**每步都验证(md5sum 对比 V11 备份)**,失败立即回滚。

### 1.3 迁移后(Post-flight)

**目标**:验证迁移完整性 + 注册表守卫 + 归档标记

```
MUST 主上下文在 --migrate-from-v11 后:
  1. 校验每个 change 的 fact/ + stage/{N}/ 目录完整(对比 V11 备份)
  2. 校验每个 change 的 .state-card.md 数量 = 1(fact/) + 11(stage/)= 12
  3. 跑 process-layer-guard.sh → 期望 PASS(无路径违规)
  4. 跑 stage-gate.py --validate-only → 期望 PASS(state-machine 解析)
  5. 跑 state-card-validator.py --strict-audit → 期望 PASS(17 字段校验)
  6. 更新 INDEX.md / CHANGELOG.md 标记"已迁移 V12"
  7. 保留 .pre_v12_migration_<ts>/ 备份(30 天后可删除)
  8. 不动 archive/done/(Article VIII 不可变)
```

**Post-flight 失败 → 自动回滚**(从 .pre_v12_migration_<ts>/ 恢复)。

---

## §2 工具函数签名

### 2.1 `init-from-zero.py --migrate-from-v11 [path] [--dry-run] [--no-backup]`

```
usage: init-from-zero.py --migrate-from-v11 [path]

V11 → V12 项目物理布局迁移(V12.0.0 NEW — 主版本升级配套)

positional arguments:
  path                  项目根目录(默认 .)

optional arguments:
  --dry-run             仅校验,不实际移动(报告每个文件的目标位置)
  --no-backup           不创建 .pre_v12_migration_<ts>/ 备份(危险,默认开)
  --force               跳过 §1.1 Pre-flight 校验(危险)
  --exclude CHANGE_ID   排除特定 change-id 不迁移(逗号分隔)

Exit codes:
  0 = PASS(迁移成功 + 全部验证通过)
  1 = FAIL(pre-flight 失败 / 备份创建失败 / 文件校验失败)
  2 = PARTIAL(部分 change 迁移成功,部分跳过 — 用户需手动复核)
```

### 2.2 函数接口

```python
def cmd_migrate_from_v11(args) -> int:
    """V11 项目 → V12 物理布局的迁移主函数。

    Args:
        args: argparse 解析结果(含 --project-root / --dry-run / --no-backup / --exclude)

    Returns:
        int: 0=PASS / 1=FAIL / 2=PARTIAL
    """

def pre_flight_check(project_root: Path) -> tuple[bool, list[str]]:
    """§1.1 Pre-flight 6 项校验。返回 (ok, error_list)。"""

def create_backup(project_root: Path, ts: str) -> Path:
    """创建 .pre_v12_migration_<ts>/ 备份整个 docs/specs/ 目录。"""

def migrate_change(change_dir: Path) -> tuple[bool, str]:
    """§1.2 8 步迁移单个 change-id。返回 (ok, report_path)。"""

def post_flight_verify(project_root: Path) -> tuple[bool, list[str]]:
    """§1.3 Post-flight 8 项验证。返回 (ok, error_list)。"""

def rollback_from_backup(backup_dir: Path, project_root: Path) -> bool:
    """从 .pre_v12_migration_<ts>/ 恢复(自动回滚)。"""
```

---

## §3 单文件分类映射表

| V11 文件 | V12 目标位置 | 映射规则 |
|----------|-------------|----------|
| `docs/specs/changes/{id}/.state-card.md` | `fact/.state-card.md`(副本只读) | 单卡 13 stage 数据拆分到 13 个独立卡 |
| `docs/specs/changes/{id}/spec.md` | `fact/spec.md` | 路径移位,内容不变 |
| `docs/specs/changes/{id}/plan.md` | `fact/plan.md` | 同上 |
| `docs/specs/changes/{id}/test-plan.md` | `fact/test-plan.md` | 同上 |
| `docs/specs/changes/{id}/prototype.md` | `fact/prototype.md`(若有) | 同上 |
| `docs/specs/changes/{id}/contracts/*.md` | `fact/contracts/*.md` | 整体迁移 |
| `docs/specs/changes/{id}/verify-report.md` | `stage/3.5-real-verify/verify-notes.md` | 改名 |
| `docs/specs/changes/{id}/review-report.md` | `stage/4-review/review-notes.md` | 改名 |
| `docs/specs/changes/{id}/rot-scan.md` | `stage/4.5-rot-scan/rot-notes.md` | 改名 |
| `docs/specs/changes/{id}/impl-notes.md` | `stage/3-implement/{actor}-impl-notes.md` | 改名 + 加 actor 前缀 |
| `docs/specs/changes/{id}/verify-notes.md` | `stage/3.5-real-verify/verify-notes.md` | 改名 |
| `docs/specs/changes/{id}/acceptance-notes.md` | `stage/5-accept/accept-notes.md` | 改名 |

**state-card 拆分规则**(单卡 → 13 卡):

```yaml
# 从 V11 单卡提取
current_stage: "3/implement"          # 拆分后保留在 fact/.state-card.md
stage_status: "completed"
history:                                  # 拆分后每 stage 提取
  - stage: "0/plan"
    actor: "tech-planner"
    duration_minutes: 30
    notes: "..."
  - stage: "3/implement"
    actor: "backend-implementer"
    duration_minutes: 120
    notes: "TDD 全绿..."

# 拆分后输出:13 个独立卡,每个 stage 一张
# stage/0/plan/.state-card.md:
current_stage: "0/plan"
stage_status: "completed"
actor: "tech-planner"
duration_minutes: 30
notes: "..."
reset_history: []

# stage/3/implement/.state-card.md:
current_stage: "3/implement"
stage_status: "completed"
actor: "backend-implementer"
duration_minutes: 120
notes: "TDD 全绿..."
handoff_out:
  - stage: "3.5/real-verify"
    note: "TDD 全绿,等真实验证"
```

---

## §4 失败处理矩阵

| 失败阶段 | 失败类型 | 处理 |
|----------|---------|------|
| Pre-flight | V11 layout 不规范 | FAIL,不迁移(返回 1) |
| Pre-flight | 项目处于"不迁移标志"状态 | FAIL,不迁移(返回 1) |
| Pre-flight | archive/done/ 重名 | FAIL,不迁移(返回 1) |
| Backup | 备份目录创建失败 | FAIL,不迁移(返回 1) |
| Migration | 单个 change 文件移动失败 | **回滚该 change 的所有步骤**,标记 PARTIAL,继续其他 change |
| Migration | md5sum 校验失败 | **回滚该 change**,记录到 .migration_v11_to_v12_<ts>.md 错误段 |
| Migration | >50% change 失败 | 全局回滚(从备份恢复),返回 FAIL |
| Post-flight | process-layer-guard FAIL | 标记,但不自动回滚(可能需要手工修复,如 process-layer-guard 的豁免) |
| Post-flight | stage-gate.py / state-card-validator FAIL | 自动回滚(从备份恢复) |

---

## §5 安全不变量(必读)

- **archive/done/{id}/ 内容不可变**(Article VIII — V11/V12 都遵守)
- **主仓 .git/info/exclude 屏蔽 docs/ 不变**(docs 子仓独立跟踪)
- **备份保留 ≥30 天**(避免误删)
- **每 change 一份迁移报告**(可追溯)
- **迁移不改任何 .md 文件的字节内容**(只移动路径,不改内容)
- **迁移不改 .state-card.md 的 history 字段**(只拆分到多卡)

---

## §6 关联引用

- [V12-ADR-DRAFT.md](V12-ADR-DRAFT.md) — V12 ADR §5 Step 8 实施路径
- [migration-checklist.md](migration-checklist.md) — V12 ADR 通过前的人工迁移骨架
- [stage-physical-isolation.md](../stage-physical-isolation.md) — V12 物理布局设计哲学
- [document-layer.md](../document-layer.md) — V12 物理映射段
- [role-protocol.md](../role-protocol.md) §10 — V12 产物落位规则
- [state-card-protocol.md](../state-card-protocol.md) §10 — V12 多卡字段定义
- [SKILL.md §3.7 #5 evidence_required](../../SKILL.md) — 任何数字声明必带证据