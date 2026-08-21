# Delegation Headers V11 SSOT — 委派头部速查(V11.8.8 NEW)

> **定位**: V11 4 头部 + 5 字段的 SSOT 速查表,主代理委派时**直接复制粘贴**,不凭印象拼装。
>
> **来源**: [role-protocol.md §4](role-protocol.md) 完整协议 + 5 字段必含
> **蒸馏**: 2026-08-19(SPEC-006 uiux-v12-spec-006-assets-templates 反馈,主代理凭印象造简化版头部 ×3 = REJECT)

---

## §0 一句话铁律

```
MUST: 任一委派头部第一行 = [ROLE-DELEGATION]
MUST: 5 字段必含(feature_scope / app_control / bug_dir / constraints / forbidden)
NEVER: [PIPELINE] + [TASK] + [DOC_WHITELIST] + [FORBIDDEN] + [GITNEXUS] 5 简化版头部
```

---

## §1 头部 SSOT(直接复制粘贴)

### 1.1 `[PROTOTYPE-DELEGATION]`(原型设计师)

```
[ROLE-DELEGATION] prototype-designer
[STAGE] 1.5 | 3

uiux_spec: docs/specs/{id}/uiux-spec.md
uiux_logic: docs/specs/{id}/uiux-logic.md
depth: static-html | framework-mock
fidelity: L1 | L2 | L3  (默认 L2)

feature_scope: <产品原型功能点清单, ≤3 行>
app_control: <静态服务命令 + 端口>

constraints:
  - 原型只进 prototypes/**,禁触 src/**
  - mock 数据写死在原型内,零后端依赖
  - 交付必附组件 ID/class 清单(供前端对照 + Stage 3.5 截图校验 + Stage 4 对照表)
  - 发现 UI/UX 双文档不合理 → 退回产品经理,不自行发明设计

forbidden: [src/**, docs/specs/{id}/tech-plan.md]
```

### 1.2 `[QA-SUBMIT-DELEGATION]`(代码提测)

```
[ROLE-DELEGATION] qa-submitter
[STAGE] 3.5 | 6

stage: 3.5 | 6
feature_scope: <功能点清单引用>
app_control: <启动命令 + 端口 + 构建方式>
bug_dir: docs/bugs/{change-id}/
budget: <时间预算>

constraints:
  - 提测通过唯一判据 = 测试专家 PASS + L1/L2 清零,不含自评
  - 每轮修复后重启应用再复测
  - 禁改 tests/**(让测试通过 = REJECT)

forbidden: [tests/**, registry/**, gates/**, 自评提测通过]
```

### 1.3 `[TEST-EXPERT-DELEGATION]`(测试专家)

```
[ROLE-DELEGATION] test-expert
[STAGE] 0.5 | 3.5 | 4 | 6

app_endpoint: <进程信息 + 端口 + 构建 hash>
feature_scope: <功能点清单(产品策划经理产物)>
retest_queue: <待复测 FIXED 单列表>
bug_dir: docs/bugs/{change-id}/
user_feedback: <本轮需消化的用户反馈(如有)>

constraints:
  - 只在给定进程上测试,进程异常报告不重启
  - 新 bug 建单必带 source + severity + 复现步骤
  - 应用侧 + 用户侧至少各 1 处校验每功能点

forbidden: [src/**(应用代码只读不写)]
```

### 1.4 `[JARVIS-DELEGATION]`(type: gate-design,贾维斯)

```
[ROLE-DELEGATION] jarvis (type: gate-design)
[STAGE] 0 | 1 | 2

方案引用: docs/specs/{id}/tech-plan.md §<验收规则章节>
一致性约束: <spec 字段 ↔ 实现符号映射>

constraints:
  - 方案阈值冲突时退回技术策划,不折中
  - 转译 gate 时严禁放宽技术策划方案声明的验收阈值

forbidden: [改动 src/**, 改动 tests/**]
```

---

## §2 通用前置头部块(coding-task 通用 9 项)

> 5 字段之外的"通用包装",适用于所有 `[ROLE-DELEGATION]` 头部之后追加。

```
[MUST-READ] AGENTS.md + .trae/rules/
[DOC_WHITELIST] {whitelist, ≤5 路径}
[GITNEXUS] impact()  # 改前必跑,见 SKILL.md §0.5
[TASK] {≤200 chars}
[OUTPUT] 4 字段: status / evidence / pass_count / next_hook
```

---

## §3 反例(V11.8.8 蒸馏补)

| # | 反例 | 后果 |
|---|---|---|
| A1 | 第一行用 `[PIPELINE]` 而非 `[ROLE-DELEGATION]` | 子代理不知自己是谁,角色越权 |
| A2 | 缺 `feature_scope` | 子代理不知要做什么,功能点漂移 |
| A3 | 缺 `constraints` | 子代理自行发明设计(prototype-designer) |
| A4 | `forbidden` 列过宽(空数组) | 子代理误改 archive/** / registry/** |
| A5 | 头部复制自上一次会话但 stage 已变更 | 旧 stage 字段不适配当前 stage |

---

## §4 自检 checklist(委派前必跑)

```
[ ] 头部第一行 = [ROLE-DELEGATION]?(而非 [PIPELINE])
[ ] 5 字段(feature_scope / app_control / bug_dir / constraints / forbidden)全有?
[ ] feature_scope ≤ 3 行?(超过 = 重新拆分任务)
[ ] doc_whitelist ≤ 5 路径?(超过 = 上下文撑爆)
[ ] forbidden 至少 1 项?(避免子代理误改)
[ ] stage 编号与当前 SPEC 阶段一致?
[ ] 引用 docs/specs/{id}/ 路径已落档?
```

**任一 □ = 修正后再委派,不要凭印象提交。**

---

## §5 历史变更

- **V11.8.8(2026-08-19)**: 4 头部 SSOT 上提 + 5 字段必含 + 反例 5 条 + 自检 checklist 7 项
- 来源: SPEC-006 uiux-v12-spec-006-assets-templates session-distiller-report §4.1