# 原型设计规则（完整版）

> 触发条件：spec 的 BDD 场景涉及用户可见的界面时生效。
> 定位：spec 阶段的扩展产出。管"开发前的低保真原型"，视觉验收管"开发后的高保真验收"。两者用同一套 ASCII 字符（┌┐└┘├┤│┬┴┼─）形成闭环。

---

## §0 触发判断

```
spec 的 BDD 场景涉及用户可见的界面？
  ├── 是 → MUST 产出 prototypes/
  │     ├── prototypes/README.md（索引）
  │     ├── prototypes/{page-name}.md（每个页面一个独立文件）
  │     └── prototypes/{component-name}.md（共享组件单独一个文件）
  │
  ├── 否（纯后端/纯 API/纯 CLI）→ 跳过原型
  │
  └── 不确定（如 API 响应驱动 UI 动态渲染）
        └── 默认视为涉及 UI → 产出低保真原型
```

---

## §1 4 条原型铁律（违反任一条 → 退回重画）

```
1. UI MUST HAVE PROTOTYPE       涉及 UI 必先画原型
2. REAL TEXT NOT PLACEHOLDER    线框图标实际文字，禁止 [按钮] [输入框] 等占位符
3. ALL STATES DRAWN             4 状态齐全（默认/加载中/空数据/错误）
4. MODULAR NOT MONOLITHIC       每个页面/模块一个独立文件，不塞单文件
```

---

## §2 三层次原型分工

```
层次 1: ASCII 线框图         fullstack-prototype-writer 负责
                                用 ┌┐└┘├┤│┬┴┼─ 画页面布局，标实际文字
层次 2: 交互说明 + 样式说明   fullstack-prototype-writer 负责
                                每个可交互元素的行为 + 布局方式（flex/grid）+ 响应式断点
层次 3: 详细视觉设计          移交 ui-ux-pro-max 技能
                                配色/组件库/间距/动效/响应式细节
```

**铁律**：fullstack 阶段只做层次 1+2。在 fullstack 阶段做配色/动效 → 越界，退回。

---

## §3 每个原型文件 5 段必须内容

| 段 | 内容 | 缺一段 → 退回 |
|----|------|-------------|
| 1. 线框图 | 4 个状态各画一张 ASCII 图，标实际文字和按钮 | ❌ 不通过 |
| 2. 交互说明 | 每个可交互元素：行为 + 触发条件 + 关联 spec Scenario | ❌ 不通过 |
| 3. 样式说明 | 布局方式（flex/grid）+ 响应式断点 + z-index 层级 | ❌ 不通过 |
| 4. 状态变化 | 状态名 / 触发条件 / 线框图差异 / 数据需求 | ❌ 不通过 |
| 5. 移交清单 | 移交 ui-ux-pro-max 的设计决策清单（配色/间距/动效等待定项） | ❌ 不通过 |

---

## §4 与下游衔接

```
prototype-writer 产出 prototypes/{module}.md
    │
    ├─▶ contract-writer：从原型推导接口数据需求
    │     └→ 如对话区域需要 messages[] → contract 加对应接口
    │
    ├─▶ ui-ux-pro-max：接收 prototypes/ + 移交清单 → 做高保真视觉设计
    │
    └─▶ implementer：编码前 MUST 读取 prototypes/{module}.md
          └→ 布局/交互/状态 1:1 对照实现
```

---

## §5 异常分支

| 异常 | 处理 |
|------|------|
| 页面极少（只有 1 个页面） | 仍需 prototypes/README.md + 1 个 page 文件，不可省略目录结构 |
| 原型与实现发现矛盾 | implementer 不自行修改原型 → 回流 spec-writer 更新 |
| 某个状态的 UI 在设计时不确定 | 画"最佳猜测"，标注【待确认】，不跳过该状态 |
| ASCII 字符在目标显示环境中乱码 | 改用 + - | = 等基础字符替代，保持结构不变 |
| contract-writer 无法从原型推导字段 | 标记缺失项，回流 spec-writer 补充交互说明中的字段信息 |

---

## §6 反面范例

```
❌ 涉及 UI 但只写 BDD 场景不画原型
   → contract-writer 猜数据需求 → 接口字段缺失/冗余 → implementer 凭空实现

❌ 原型用 [按钮] [输入框] 占位符
   → implementer 不知道按钮上写什么文字 → 实现走样

❌ 只画默认状态
   → 加载/空/错误状态由 implementer 自由发挥 → 体验割裂

❌ 所有页面塞一个 prototypes/all.md
   → 文件臃肿 → 修改一处影响全局 → 难以维护

❌ fullstack 阶段做配色/动效
   → 越界 → 应移交给 ui-ux-pro-max
```
