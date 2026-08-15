# {Feature} — UI/UX 交互逻辑（给开发者）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> **位置**: `docs/specs/changes/{id}/prototypes/ui-ux-logic.md`
> **编制依据**: V11.2 NEW 双产物机制，蒸馏自 V10 prototype.md §文档二
> **必含门禁**: 组件树 ≥ 1 + 交互流 ≥ 2 + 状态表 ≥ 3 + 错误处理 ≥ 3
> **模板说明**: 复制此模板到目标路径，按 `{占位符}` 填写实际内容。

---

## 引用的 HTML 文件

| 角色 | 文件 | <title> | 用途 |
|------|------|---------|------|
| 主页面 | xxx.html | 模块名 — 产品名 | 一句话功能定位 |

---

## 组件树

{从页面顶层到最小可交互单元的层级关系}

```
例:
<App>
  ├─ <Header>
  │   ├─ <Logo />
  │   ├─ <Breadcrumb items={[...]} />
  │   └─ <UserAvatar />
  ├─ <Sidebar>
  │   └─ <NavMenu items={[...]} />
  └─ <MainContent>
      ├─ <FilterBar>
      │   ├─ <SearchInput />
      │   └─ <DateRangePicker />
      └─ <DataTable>
          ├─ <TableHeader columns={[...]} />
          └─ <TableBody>
              └─ <TableRow onClick={...}>
                  └─ <ActionMenu />
```

## 交互流

### 流 1: {操作名称}

- 触发: {用户行为，如点击按钮/键盘快捷键/拖拽}
- 前置条件: {状态条件，如已选中/已登录/数据已加载}
- 执行步骤:
  1. {步骤描述}
  2. {步骤描述}
- 后置结果: {状态变化/页面跳转/数据变更}
- 异常处理: {网络失败/权限不足/数据异常时的行为}

### 流 2: {操作名称}

- 触发: ...
- 前置条件: ...
- 执行步骤: ...
- 后置结果: ...
- 异常处理: ...

### 流 3: {操作名称}（可选）

- 触发: ...

## 状态管理

| 状态名 | 类型 | 初始值 | 变化触发 | 影响范围 |
|--------|------|--------|---------|---------|
| {state} | {string/boolean/object} | {default} | {事件} | {组件列表} |
| selectedIds | string[] | [] | 用户多选操作 | DataTable / BulkActions |
| filterValue | string | "" | SearchInput.onChange | DataTable 数据源 |
| isLoading | boolean | false | fetchData() 调用 | Skeleton / Spinner |
| error | Error \| null | null | API 调用失败 | ErrorBanner |

## 组件行为规格

### 组件: {组件名}

- 显示条件: {什么时候渲染 / 什么时候隐藏}
- 交互行为:
  - {行为1}: {描述}
  - {行为2}: {描述}
- 禁用条件: {什么时候不可交互}
- 键盘快捷键: {如有}

### 组件: SearchInput

- 显示条件: FilterBar 始终可见
- 交互行为:
  - onChange: debounce 300ms 后触发 filterValue 更新
  - onClear: 清空 filterValue 并触发重新加载
  - onKeyDown(Enter): 立即触发搜索（绕过 debounce）
- 禁用条件: isLoading=true 时禁用输入
- 键盘快捷键: "/" 全局聚焦

## 错误与边界处理

| 场景 | 行为 |
|------|------|
| 网络失败 | {重试策略/降级展示/用户提示} |
| 超长数据 | {截断方式/省略号/展开收起} |
| 并发操作 | {防重复提交/乐观锁/排队提示} |
| 权限不足 | {禁用态/隐藏/引导授权} |
| 加载超时 | {超时阈值/超时提示/取消请求} |

```
例:
- 网络失败: 显示 "网络异常，请重试" Toast，自动重试 3 次（指数退避）
- 超长数据: 标题超过 50 字截断 + 悬浮 tooltip 显示完整
- 并发操作: 按钮 disabled + "提交中..." 文字，乐观锁防重复
- 权限不足: 按钮置灰 + 悬浮提示 "无权限"
- 加载超时: 30s 超时显示 "请求超时" + 取消按钮
```

---

## 关联引用

- 配套文档: [design-prompt.md](design-prompt.md)（同目录，给 Trae Work 的视觉提示词）
- 协议文档: [../references/prototype-dual-source.md](../references/prototype-dual-source.md) §3
- 联动协议: [../references/prototype-linkage.md](../references/prototype-linkage.md)
- 蒸馏来源: fullstack4TraeV10/references/prototype.md §文档二
