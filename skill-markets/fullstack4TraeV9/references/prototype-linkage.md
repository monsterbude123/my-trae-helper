# 原型 ↔ HTML 联动层

> 当项目有外部 Designer（人或 Trae Work）交付 HTML 原型页面时生效。
> 无外部 Designer → 跳过本章，走标准 [prototype.md](prototype.md) 正向流程。

---

## §1 章节契约 — `## 引用的 HTML 文件`

每份 `prototypes/{design-prompt,ui-ux-logic}.md` 必须在 H1 之后首个章节位置包含此章节。

### 1.1 4 列表格

```markdown
## 引用的 HTML 文件

| 角色 | 文件 | <title> | 用途 |
|------|------|---------|------|
| 主页面 | xxx.html | 模块名 — 产品名 | 一句话功能定位 |
| 辅助 | yyy.html | 子组件 — 产品名 | 一句话功能定位 |
```

### 1.2 字段约束

| 字段 | 约束 |
|------|------|
| 角色 | 仅「主页面 / 辅助」二值 |
| 文件 | 仅文件名（不含路径），与 HTML 源文件名逐字一致 |
| `<title>` | 必须与 HTML 文件 `<title>` 标签内容逐字匹配 |
| 用途 | ≤ 30 字 |

### 1.3 校验规则（机械化）

```
[1] 每份 prototype 文件必须含此章节
[2] 主页面行数 = 1
[3] 辅助行数 ≥ 0（跨模块共享时可多行）
[4] <title> 与对应 HTML 文件实际 <title> 完全一致
[5] 主页面 + 辅助行去重 ⊆ HANDOFF 索引
```

---

## §2 HTML 归属决策树

当 Designer 交付一组 HTML 页面时，按此树判定每个 HTML 归属哪个 spec 的 prototypes/：

```
HTML 页面 → 归属决策
├─ 主题是主业务页面 → 主页面，归属对应 spec，prototypes/ 表头列出
├─ 主题是子组件（弹窗/扫描进度/侧栏/拆分视图/错误回退等）
│   └─ → 辅助页面，绑定到主 spec，原型头部 + 引用表格
├─ 主题是跨模块可视化（依赖图/时序图/架构图）
│   └─ → 绑定到当前最相关 spec（推荐）或暂不实现
├─ 无匹配 spec → 反向缺失，记录到 HANDOFF 缺失清单
└─ spec 存在但无对应 HTML → Stub P0（见 §3）
```

---

## §3 三态处理：完整 / Stub / 缺失

| 状态 | 判定 | 处理 |
|------|------|------|
| **完整** | design-prompt.md + ui-ux-logic.md + HTML 全部齐备 | HANDOFF 列入，校验通过 |
| **Stub (P0)** | spec/define 已声明 UI 需求，HTML 已交付但 prototypes/ 为空 | 主上下文创建 prototypes/ 目录 + 占位文件（含 §1 章节占位 + 状态标注）；阻塞 spec-writer 继续，直到 Designer 确认 HTML 后填充 |
| **反向缺失 (P2)** | spec 存在但 Designer 未交付对应 HTML | HANDOFF 列入缺失清单，Designer 决策：新建 HTML / 合并 / 暂不实现 / 共享页 |

**Stub 文件模板**：

```markdown
# {Feature} — {文档类型}（Stub）

> ⚠️ 占位文件 — Designer 交付 HTML 后由 spec-writer 填充。

## 引用的 HTML 文件

| 角色 | 文件 | <title> | 用途 |
|------|------|---------|------|
| 主页面 | 待确认 | 待确认 | 待确认 |

---
状态: P0 阻塞 — 等待 Designer 交付 HTML
```

---

## §4 注入 spec-writer 的强制检查

spec-writer 在 Step 5（UI 原型触发）之前，必须执行以下检查：

```
[ ] Step 5.0: 外部 HTML 交接检查
  涉及 UI 且项目存在外部 Designer HTML?
    ├─ 是 → 查找 HANDOFF 索引
    │       ├─ 找到对应 HTML → 正常产出 prototypes/，写入 §1 章节
    │       ├─ Stub 模式 → 只写占位文件，标注 P0 阻塞
    │       └─ 未找到 → 🛑 P0 阻塞，不允许继续 spec 编写
    └─ 否 → 跳过，走标准 prototypes/ 正向流程
```

---

## §5 禁止项

- 禁止 prototypes/ 无 §1 章节就移交 downstream
- 禁止 spec-writer 跨过 HANDOFF 索引自行假设 HTML 对应关系
- 禁止在 `<title>` 字段写入非 HTML 源文件实际标题的内容
- 禁止将辅助 HTML 标记为「主页面」
