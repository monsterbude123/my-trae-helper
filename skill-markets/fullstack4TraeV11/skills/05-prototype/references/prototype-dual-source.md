# Prototype 双产物机制（V11.2 NEW — 蒸馏自 V10）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> **来源**: fullstack4TraeV10/references/prototype.md（V10.9 蒸馏保留，V11.2 NEW 强化）
> **部署时不依赖 V10**：内容已完整内化到 V11
> **关联**: [prototype-linkage.md](prototype-linkage.md)（HANDOFF 联动）+ ⚠️ V10 来源溯源,部署前可删:[designer-handoff.md](../../../../fullstack4TraeV10/references/designer-handoff.md)（外部 Designer 协议）

---

## §1 双产物机制总览

涉及 UI 变更时，**spec-writer 必产 2 份文档**到 `docs/specs/changes/{id}/prototypes/`：

| 文档 | 用途 | 读者 |
|------|------|------|
| `design-prompt.md` | Trae Work 生成视觉原型的结构化提示词 | Trae Work（AI） |
| `ui-ux-logic.md` | 交互逻辑、状态、组件行为 | 开发者（implementer） |

**核心理念**：需求确认后 AI 设计提示词 + 交互逻辑，后续阶段以此为稳定真相源，不变更。

**触发条件**：spec.md 含 UI 声明（页面/组件/视觉/交互任一）。

> **Article 锚定**: Article II Spec First(spec 是契约来源)+ Article V Verifiable Claims(双产物必含可视化证据)+ Article IX Cross-Session Verify(实施者 vs 设计者双向交叉)。

---

## §2 design-prompt.md 结构（给 Trae Work）

### 2.1 必含骨架（V10 prototype.md §文档一）

```markdown
# {Feature} — 设计提示词

## 引用的 HTML 文件
| 角色 | 文件 | <title> | 用途 |
|------|------|---------|------|
| 主页面 | xxx.html | 模块名 — 产品名 | 一句话功能定位 |
| 辅助 | yyy.html | 子组件 — 产品名 | 一句话功能定位 |

---

## 页面描述
- 页面名称: {name}
- 页面目标: {一句话描述用户要完成什么任务}
- 所属模块: {module}

## 布局骨架
{用自然语言描述页面区域划分，标注每个区域的作用}

## 核心组件清单
| 组件 | 类型 | 位置 | 关键属性 |
|------|------|------|---------|
| {组件1} | {按钮/输入框/列表/...} | {区域} | {placeholder/default/...} |

## 视觉风格
- 色彩: {主色调 / 辅助色 / 状态色}
- 间距: {描述间距风格，如紧凑/宽松}
- 字体: {层级关系，如标题/正文/辅助文字}

## 5 状态要求
每个页面必须覆盖以下 5 种状态的视觉表现：
1. **加载中**: {骨架屏/loading 动画/进度条}
2. **空数据**: {空状态插画 + 引导文案}
3. **正常态**: {正常数据展示的完整页面}
4. **错误态**: {错误提示样式 + 重试入口}
5. **边界态**: {极限数据场景，如超长文本/大量数据/极端缩略图}

## 响应式断点
| 断点 | 宽度 | 布局变化 |
|------|------|---------|
| Desktop | ≥1280px | {描述} |
| Tablet | 768-1279px | {描述} |
| Mobile | <768px | {描述} |

## 特殊交互视觉
{拖拽效果/动画过渡/弹窗/右键菜单 等的视觉描述}
```

### 2.2 编写原则

- **自然语言描述视觉**，不是技术实现 — Trae Work 需要理解"长什么样"，不是"怎么写代码"
- **状态描述要具体** — 不是"显示错误信息"，而是"页面中央红色卡片，左侧错误图标 + 右侧错误文字 + 重试按钮"
- **组件属性标注清楚** — placeholder 文案、默认值、禁用态

---

## §3 ui-ux-logic.md 结构（给开发者）

### 3.1 必含骨架（V10 prototype.md §文档二）

```markdown
# {Feature} — UI/UX 交互逻辑

## 引用的 HTML 文件
| 角色 | 文件 | <title> | 用途 |
|------|------|---------|------|
| 主页面 | xxx.html | 模块名 — 产品名 | 一句话功能定位 |

---

## 组件树
{从页面顶层到最小可交互单元的层级关系}

## 交互流
### 流 1: {操作名称}
- 触发: {用户行为，如点击按钮/键盘快捷键/拖拽}
- 前置条件: {状态条件，如已选中/已登录/数据已加载}
- 执行步骤:
  1. {步骤描述}
  2. {步骤描述}
- 后置结果: {状态变化/页面跳转/数据变更}
- 异常处理: {网络失败/权限不足/数据异常时的行为}

## 状态管理
| 状态名 | 类型 | 初始值 | 变化触发 | 影响范围 |
|--------|------|--------|---------|---------|
| {state} | {string/boolean/object} | {default} | {事件} | {组件列表} |

## 组件行为规格
### 组件: {组件名}
- 显示条件: {什么时候渲染 / 什么时候隐藏}
- 交互行为:
  - {行为1}: {描述}
  - {行为2}: {描述}
- 禁用条件: {什么时候不可交互}
- 键盘快捷键: {如有}

## 错误与边界处理
| 场景 | 行为 |
|------|------|
| 网络失败 | {重试策略/降级展示/用户提示} |
| 超长数据 | {截断方式/省略号/展开收起} |
| 并发操作 | {防重复提交/乐观锁/排队提示} |
| 权限不足 | {禁用态/隐藏/引导授权} |
```

### 3.2 编写原则

- **面向开发者** — 描述行为逻辑，不描述视觉效果
- **状态表要完整** — implementer 需要知道所有可能状态
- **异常路径写清楚** — "网络失败怎么办" 是最常见的遗漏点
- **组件行为能用伪代码表达就用伪代码**

---

## §4 产出流程

```
spec-writer 判断涉及 UI
  ↓
产出 design-prompt.md（AI 可读的视觉描述）
  ↓
产出 ui-ux-logic.md（开发者可读的交互逻辑）
  ↓
用户确认 → Trae Work 按 design-prompt.md 生成视觉原型
  ↓
visual gate: reviewer 对比实现截图 vs ui-ux-logic.md 行为规格
```

---

## §5 最低门禁（机械化 — prototype-backfill-check.py）

- [ ] **design-prompt.md**: 5 状态全部覆盖 + 响应式断点 ≥ 2
- [ ] **ui-ux-logic.md**: 组件树 ≥ 1 + 交互流 ≥ 2 + 状态表 ≥ 3 + 错误处理 ≥ 3
- [ ] 两份文档不能有空占位符（如 "TODO"/"待补充"）
- [ ] 纯后端/API → 跳过，不产出 prototypes/ 目录

门禁脚本：`python scripts/prototype-backfill-check.py --change-id {id}`

---

## §6 反向补全（Backfill）— 已有设计但缺 prototypes/ 文档

> 场景：项目已有 Trae Work 生成的视觉原型 + spec.md，但缺少 `prototypes/design-prompt.md` 和 `prototypes/ui-ux-logic.md`。

### 6.1 触发条件

```
1. docs/specs/changes/{id}/spec.md 存在（有 Spec）
2. docs/specs/changes/{id}/prototypes/ 不存在 或 缺任一份文档
3. spec.md 涉及 UI（含前端页面/组件描述）
→ 触发 backfill
```

> **工作目录锁**: backfill 全程只读写 `docs/specs/changes/{id}/` 目录。不得读取或写入项目级文件。

### 6.2 Backfill 流程

```
Step 1: 从 spec.md 提取交互逻辑 → 生成 ui-ux-logic.md
  输入: spec.md 的 Scenarios + Acceptance + Invariants + E2E
  方式: 从 BDD 场景反向拆解:
    - WHEN → 触发条件
    - THEN → 后置结果
    - 多个 Scenario → 交互流
    - Acceptance 条目 → 状态表
    - Invariants → 错误与边界处理

Step 2: 从 Trae Work 设计反向描述 → 生成 design-prompt.md
  输入: 已有的 Trae Work 生成的视觉原型页面
  方式: 观察实际设计，反向填空模板:
    - 页面区域划分 → 布局骨架
    - 可见组件 → 核心组件清单
    - 用色/间距/字体 → 视觉风格
    - 各状态截图 → 5 状态要求
  注意: 此时 design-prompt.md 的角色从"生成提示词"变为"视觉规格"

Step 3: 用户确认两份文档 → prototypes/ 就位 → 后续验收正常执行
```

### 6.3 Backfill 产出门禁

与正向流程相同：
- [ ] `design-prompt.md`: 5 状态全部覆盖 + 响应式断点 ≥ 2
- [ ] `ui-ux-logic.md`: 组件树 ≥ 1 + 交互流 ≥ 2 + 状态表 ≥ 3 + 错误处理 ≥ 3
- [ ] 两份文档不能有空占位符
- [ ] `design-prompt.md` 描述的是实际设计（非理想化设计）

---

## §7 禁止项

- ❌ 禁止用 ASCII 线框图替代 design-prompt.md
- ❌ 禁止在 spec.md 末尾内联原型内容（两份文档独立存放）
- ❌ 禁止在 prototypes/ 中放实际图片（图片由 Trae Work 生成，不纳入 git）
- ❌ 禁止跳过 design-prompt.md / ui-ux-logic.md 任一份（仅限 UI 涉及 change；纯后端/API/CLI 跳过整个 prototypes/ 目录，V11.2 铁律 7）
- ❌ 禁止使用占位符（如 "TODO"/"待补充"/"TBD"）— 必须填实际内容

---

## §8 关联引用

- [prototype-linkage.md](prototype-linkage.md) — HANDOFF 联动协议（章节契约 + 归属决策树 + 三态处理）
- [../templates/design-prompt.md](../templates/design-prompt.md) — design-prompt 模板
- [../templates/ui-ux-logic.md](../templates/ui-ux-logic.md) — ui-ux-logic 模板
- ⚠️ V10 来源溯源,部署前可删:[../../../../fullstack4TraeV10/references/designer-handoff.md](../../../../fullstack4TraeV10/references/designer-handoff.md) — Designer ↔ 主上下文 ↔ spec-writer 交接协议
- 门禁脚本：`scripts/prototype-backfill-check.py`
