# Bug 单状态机 + 编号规则

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage -1 Intake 创建 Bug 单 + Stage 6 Bug Fix 全程维护的状态机。

---

## 状态机（3 个状态）

```
[OPEN] ──→ [IN_PROGRESS] ──→ [CLOSED]
   ↑              │                │
   │              │                │
   └──────────────┴────────────────┘
            (用户拒绝 / 验证失败可回退)
```

| 状态 | 含义 | 触发条件 | 维护者 |
|------|------|---------|--------|
| **OPEN** | Bug 已录入，等待 Stage 6 处理 | Stage -1 Intake 创建 | 主上下文 |
| **IN_PROGRESS** | Stage 6 Bug Fix 进行中 | e2e 先行 FAIL 验证通过 | debugger |
| **CLOSED** | Bug 修复 + 回归通过 + 用户确认 | TDD 修复 PASS + 用户签字 | debugger |

---

## 状态转换矩阵

| From → To | 触发动作 | 必要条件 | 写入字段 |
|-----------|---------|---------|---------|
| (无) → OPEN | Stage -1 Intake 创建 Bug 单 | Bug 单 6 字段齐全 + 用户同意 | `stage_status=pending`, `bug_severity=P0/P1/P2` |
| OPEN → IN_PROGRESS | Stage 6 加载 + e2e 先行 FAIL | e2e 测试初始 FAIL 验证 | `stage_status=working`, `stage_started_at=now` |
| IN_PROGRESS → CLOSED | TDD 修复 + 回归 PASS + 用户确认 | TDD GREEN + 全量回归 PASS + 用户书面签字 | `stage_status=completed`, `stage_ended_at=now`, `health=🟢 on-track` |
| IN_PROGRESS → OPEN | e2e 初始 PASS（说明 bug 不存在）| 6 层排查证明无 bug | `stage_status=pending`, `notes: e2e 初始 PASS → 不是 bug → 回退 OPEN` |
| IN_PROGRESS → OPEN | TDD 修复 FAIL | 重做 TDD 循环 | `gate_result.status=FAIL`, `blocked_by=5 字段` |
| CLOSED → OPEN | 回归发现新问题 | 用户反馈 + 重新录入 bug 单（不修改原 bug 单）| **新建** Bug 单 + 引用原 bug-id |

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
  │   └─→ 回退: IN_PROGRESS → OPEN + notes 标注 + 用户确认
  │
  ├─ 6 层排查超 5 轮（仍找不到根因）
  │   └─→ 升级: 状态 = blocked + 5 字段阻塞报告 + 用户决策
  │
  └─ TDD 修复 PASS + 回归通过
      └─→ 升级: 状态 = CLOSED + bug 单回写 + 用户签字
```

---

## 状态机反例

### 反例 A：跳过 OPEN 状态直接到 IN_PROGRESS

```
主上下文: 创建 bug 单 → 立即进入修复  # ❌ 跳过 OPEN 状态
正确: OPEN → e2e 先行 FAIL 验证 → IN_PROGRESS
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
状态卡: 还是 IN_PROGRESS  # ❌ 违反铁律 9
正确: 同步更新两份
```

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage -1 入口
- [bug-intake-flow.md](../workflows/bug-intake-flow.md) — Bug 录入 6 字段工作流
- [bug-template.md](../templates/bug-template.md) — Bug 单模板
- Stage 6 Bug Fix: [../../12-bug-fix/SKILL.md](../../12-bug-fix/SKILL.md)
- 状态卡协议: [../../../references/state-card-protocol.md](../../../references/state-card-protocol.md)
- 文档分层: [../../../references/document-layer.md](../../../references/document-layer.md)
