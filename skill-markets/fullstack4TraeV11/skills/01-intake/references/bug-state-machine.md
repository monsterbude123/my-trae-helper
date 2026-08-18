# Bug 单状态机 + 编号规则

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage -1 Intake 创建 Bug 单 + Stage 6 Bug Fix 全程维护的状态机。

---

## 状态机（7 个状态）

```
[OPEN] ──→ [IN-FIX] ──→ [FIXED] ──→ [VERIFIED] ──→ [CLOSED]
   ↑           │             │             │
   │           │             └─→ [REOPENED] ─→ [IN-FIX] (复测失败回退)
   │           │
   │           └──(回退)──→ [OPEN]   (e2e 初始 PASS / 修复失败)
   │
   └───→ [OBSOLETE]   (功能变更致过时，OPEN/FIXED/VERIFIED 任一均可)
```

| 状态 | 含义 | 触发条件 | 维护者 |
|------|------|---------|--------|
| **OPEN** | Bug 已录入，等待 Stage 6 处理 | Stage -1 Intake 创建 | 主上下文 |
| **IN-FIX** | Stage 6 Bug Fix 进行中（6 层排查 + TDD 修复）| e2e 先行 FAIL 验证通过 | debugger / 代码提测 |
| **FIXED** | 已修复，待测试专家复测 | TDD GREEN + 回归 PASS + 已填 Fix | 代码提测（写权）|
| **VERIFIED** | 测试专家复测通过，再观察无 regression | 亲自跑 + 截图 + 4 维度观察 | 测试专家（裁定权）|
| **REOPENED** | 测试专家复测 FIXED 失败回退 | 附复现证据 | 测试专家 |
| **OBSOLETE** | 功能变更致过时（终态）| 仅测试专家可标 + 附过时理由 | 测试专家 |
| **CLOSED** | 关闭归档（终态）| 代码提测申请 + 测试专家会签 + 用户确认 | 三方确认 |

> **权威源**: [../../12-bug-fix/references/bug-state-machine.md](../../12-bug-fix/references/bug-state-machine.md)
> 01-intake 必须与 12-bug-fix 保持 7 态完全一致（OPEN/IN-FIX/FIXED/VERIFIED/CLOSED/REOPENED/OBSOLETE）。

---

## 状态转换矩阵

| From → To | 触发动作 | 必要条件 | 写入字段 |
|-----------|---------|---------|---------|
| (无) → OPEN | Stage -1 Intake 创建 Bug 单 | Bug 单 7 字段齐全（含 source）+ 用户同意 | `stage_status=pending`, `bug_severity=P0/P1/P2` |
| OPEN → IN-FIX | Stage 6 加载 + e2e 先行 FAIL | e2e 测试初始 FAIL 验证 | `stage_status=working`, `stage_started_at=now` |
| IN-FIX → FIXED | TDD 修复 + 回归 PASS | TDD GREEN + 回归 PASS + 已填 Fix | `stage_status=working`, `qa_submitted_at=now` |
| FIXED → VERIFIED | 测试专家复测通过 | 亲自跑 + 截图 + 4 维度观察无 regression | `stage_status=verifying`, `qa_verified_at=now` |
| FIXED → REOPENED | 测试专家复测失败 | 附复现证据；同一单 REOPENED ≥ 2 次 → 升级仲裁 | `stage_status=pending`, `reopen_reason=...` |
| VERIFIED → CLOSED | 代码提测申请 + 测试专家会签 + 用户确认 | 三方确认 + bug 单回写 + 用户签字 | `stage_status=completed`, `stage_ended_at=now`, `health=🟢 on-track` |
| REOPENED → IN-FIX | 回到修复队列 | 代码提测接手 | `stage_status=working` |
| IN-FIX → OPEN | e2e 初始 PASS（说明 bug 不存在）| 6 层排查证明无 bug | `stage_status=pending`, `notes: e2e 初始 PASS → 不是 bug → 回退 OPEN` |
| IN-FIX → OPEN | TDD 修复 FAIL | 重做 TDD 循环 | `gate_result.status=FAIL`, `blocked_by=5 字段` |
| OPEN/FIXED/VERIFIED → OBSOLETE | 功能变更致过时 | 仅测试专家可标 + 附过时理由 + 功能变更引用 | `stage_status=obsolete`, `obsolete_reason=tech-plan/spec diff` |

---

## Bug 单编号规则

### 格式

```
{module}-{NNN}-{slug}
```

| 段 | 含义 | 规则 |
|----|------|------|
| `module` | 模块名 | kebab-case，与项目模块对齐（如 `settings` / `api` / `auth` / `ui`） |
| `NNN` | 3 位数字 | 自增，从 `001` 开始，每个 module 独立计数 |
| `slug` | 短描述 | kebab-case，3-5 个单词 |

### 示例

| Bug-id | 模块 | 编号 | 描述 |
|--------|------|------|------|
| `settings-009-config-key-case-mismatch` | settings | 009 | 前后端 config key 大小写不一致 |
| `api-001-rate-limit-not-triggered` | api | 001 | 速率限制未触发 |
| `auth-003-token-refresh-concurrency-500` | auth | 003 | token 并发刷新报 500 |
| `ui-015-modal-z-index-overlap` | ui | 015 | 模态框 z-index 重叠 |

### 编号扫描命令

```bash
# 当前 module 最大编号
ls docs/bugs/{module}-*.md 2>/dev/null | wc -l

# 或更精确
ls docs/bugs/{module}-*.md 2>/dev/null | grep -oE "{module}-[0-9]{3}" | sort -u | tail -1
```

### 幂等性测试场景(V11.2 NEW — 蒸馏自 01-intake 自检报告)

| 场景 | 输入 | 期望行为 | 失败后果 |
|------|------|---------|---------|
| **A: 重名** | module=auth,已有 auth-001.md / auth-001.md(误复制) | `ls` 命令重复统计 +1,`grep -oE | sort -u` 去重后 NNN 不变 → 自动跳到下一个编号(不会撞号) | 若误用 wc -l 而非 sort -u,会跳号(留空 bug-002) |
| **B: 模块重命名** | 原 module=user 重命名为 account,旧 bugs/user-001.md 仍存在 | 旧 bug 单不会出现在新 module 扫描结果中(grep -oE 锚定 module 名) | 用户手动迁移或保留旧 module 名,避免丢 bug |
| **C: 编号格式漂移** | 部分 bug 用 2 位编号(auth-1.md)部分用 3 位(auth-001.md) | `grep -oE "{module}-[0-9]{3}"` 只匹配 3 位,**2 位编号被遗漏**(防漂移强制 3 位) | 必须在 bug 录入阶段强制 3 位编号(intent-types.md L145) |

### 编号冲突处理

| 冲突类型 | 处置 |
|---------|------|
| 同一 module 编号已存在 | 自动 +1，跳过已用编号 |
| 编号与已归档 bug 重叠 | 新建独立 bug 单，引用原 bug-id |
| 用户自定义 bug-id | 校验唯一性，不冲突才接受 |

---

## Bug 单生命周期

```
[创建]                                [销毁]
   │                                     │
   ↓                                     ↓
docs/bugs/{bug-id}.md   ──→   修复完成 + CLOSED   ──→   保留（事实层）
docs/bugs/{bug-id}/
  .state-card.md         ──→   状态 = CLOSED    ──→   保留（事实层）
```

**禁止**:
- ❌ 修改已 CLOSED 的 Bug 单（除非追加注释，不改原内容）
- ❌ 删除 Bug 单（违反 Article XII 文档诚实 + 可追溯性）

---

## 状态机与文档分层

| 文档 | 层级 | 子代理可读性 |
|------|------|------------|
| `docs/bugs/{bug-id}.md` | fact（修复后） | ✅ debugger / implementer 必读 |
| `docs/bugs/{bug-id}-draft.md` | process（修复中） | ❌ 主上下文摘要注入（不直接读） |
| `docs/bugs/{bug-id}/.state-card.md` | fact | ✅ debugger 必读 |

**详细分层规则**: [../../../references/document-layer.md](../../../references/document-layer.md)

---

## 状态机与回退路径

```
Stage 6 Bug Fix 执行中
  ├─ e2e 初始 PASS（说明无 bug）
  │   └─→ 回退: IN-FIX → OPEN + notes 标注 + 用户确认
  │
  ├─ 测试专家复测 FIXED 失败
  │   └─→ FIXED → REOPENED → IN-FIX（附复现证据 + 同单 ≥ 2 次升级仲裁）
  │
  └─ VERIFIED 通过 + 三方确认
      └─→ VERIFIED → CLOSED + bug 单回写 + 用户签字
```

---

## 状态机反例

### 反例 A：跳过 OPEN 状态直接到 IN-FIX

```
主上下文: 创建 bug 单 → 立即进入修复  # ❌ 跳过 OPEN 状态
正确: OPEN → e2e 先行 FAIL 验证 → IN-FIX
```

### 反例 B：未验证 e2e 初始 FAIL

```
debugger: 写 TDD 修复 → 直接 GREEN  # ❌ 违反铁律 "e2e 先行"
正确: 先写失败测试 → 确认 FAIL → 写实现 → GREEN
```

### 反例 C：CLOSED 后又修改

```
bug 单状态 = CLOSED 后又修改 symptom 字段  # ❌ 违反 Article XII
正确: 追加 comment 段，不改原内容；如需新 bug 单则新建
```

### 反例 D：状态卡与 Bug 单不同步

```
Bug 单: 标记 CLOSED
状态卡: 还是 IN-FIX  # ❌ 违反铁律 9
正确: 同步更新两份
```

### 反例 E：状态机三方不一致

```
01-intake 文档: 用旧 V11 命名(无 IN-FIX)
12-bug-fix 权威源: IN-FIX(V12 标准)
→ 三方 7 态收敛: 12-bug-fix 是唯一状态集合  # ❌ 任意一处仍用 V11 残留名
正确: 7 态完全一致 = OPEN/IN-FIX/FIXED/VERIFIED/CLOSED/REOPENED/OBSOLETE
```

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage -1 入口
- [bug-intake-flow.md](../workflows/bug-intake-flow.md) — Bug 录入 6 字段工作流
- [bug-template.md](../templates/bug-template.md) — Bug 单模板
- Stage 6 Bug Fix: [../../12-bug-fix/SKILL.md](../../12-bug-fix/SKILL.md)
- 状态卡协议: [../../../references/state-card-protocol.md](../../../references/state-card-protocol.md)
- 文档分层: [../../../references/document-layer.md](../../../references/document-layer.md)
