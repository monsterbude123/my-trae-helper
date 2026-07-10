# Vision-Audit 提示词速查本

> 活文档。每次发现 VL 误判/漏判/计数错误，追加到 §1，并在 §2 沉淀改进后的 prompt 模板。
> 配合 `SKILL.md` 的"Prompt 编写原则"使用。

---

## §1 已知 VL 限制（按场景）

### P01 — Naive UI 按钮 disabled 状态

**症状**：VL 把 Naive UI disabled 按钮误判为"可点击"。

**根因**：Naive UI 不用 HTML `disabled` 属性表示禁用，而是加 CSS 类 `n-button--disabled`。视觉上 disabled 按钮只是颜色稍浅（type="primary" 时是浅紫色），VL 容易误判。

**复现**：
- 截图 `sub-02-create-modal.png` — 新建弹窗名称为空时"保存"按钮 disabled，VL 说"可点击状态（未禁用）"
- 截图 `sub-open-import.png` — 导入弹窗未选包时"预览提取结果"按钮 disabled，VL 说"可点击"

**正确做法**：
- 不要让 VL 判断按钮 disabled
- 改用 Playwright DOM 检测：`buttonLocator.getAttribute('class')` 包含 `n-button--disabled`
- 或：`await expect(buttonLocator).toHaveClass(/n-button--disabled/)`

**改进 prompt**：
- ❌ "保存按钮当前是可点击还是禁用状态？"
- ✅ "保存按钮的文字颜色是深色还是浅色？背景色是什么？" — VL 描述视觉事实，由 Agent 结合 DOM 判断

---

### P02 — Input 文本溢出（水平滚动）

**症状**：VL 说"文字完整显示"，但实际 `scrollWidth > clientWidth`，输入框有水平滚动。

**根因**：`<input type="text">` 超长文本默认显示开头部分，VL 看到的"完整"是视觉完整，但用户实际需要滚动才能看到末尾。

**复现**：
- 截图 `sub-long-name.png` — 48 个中文字符，scrollWidth=672, clientWidth=592
- VL 说"文字完整显示，没有被截断"

**正确做法**：
- 不要让 VL 判断 input 文本是否溢出
- 改用 Playwright DOM 检测：
  ```js
  await input.evaluate((el) => ({
    scrollWidth: el.scrollWidth,
    clientWidth: el.clientWidth,
    isOverflow: el.scrollWidth > el.clientWidth,
  }))
  ```

**改进 prompt**：
- ❌ "输入框文字是否完整显示，还是被截断？"
- ✅ "输入框里可见的文字内容是什么？"（让 VL 只描述可见文字，不判断是否截断）

---

### P03 — 表单计数不准

**症状**：VL 说"5 个表单项"，实际只有 4 个（类型/名称/内容条目/标签）。

**根因**：VL 对结构化元素的计数不稳定，特别是当有嵌套或动态行时。

**复现**：
- 截图 `sub-02-create-modal.png` — 新建弹窗
- VL 说"5 个表单项"

**正确做法**：
- 不要让 VL 做精确计数
- 改用 Playwright：`await page.locator('.n-form-item').count()`
- 或：让 VL 列出"看到的表单标签文字"，由 Agent 自己计数

**改进 prompt**：
- ❌ "弹窗内有几个表单项？"
- ✅ "列出弹窗内所有可见的表单标签文字（按从上到下顺序）"

---

### P04 — Toast 通知描述

**观察**：VL 能识别 toast 通知，但描述位置可能不准（说"顶部中央"，实际可能在不同位置）。

**复现**：截图 `sub-save-filled.png` — VL 说"位于页面顶部中央的提示框"，实际 Naive UI useMessage 默认在顶部中央，这次正确。

**结论**：暂时不需要 DOM 补充，但建议 prompt 改为：
- ✅ "页面上的 toast/通知文字是什么？出现在页面的什么位置（顶部/底部/中央/角落）？"

---

## §2 改进后的 Prompt 模板（按场景）

### 场景 A：分析弹窗内容

```
客观描述：
1) 是否出现弹窗？弹窗标题文字是什么？
2) 列出弹窗内所有可见的表单标签文字（按从上到下顺序，不计数）
3) 每个表单字段当前的值或占位文字
4) 底部按钮的文字（按从左到右顺序）
5) 弹窗外背景是否被遮罩
6) 任何看起来不一致的间距、对齐、颜色问题
注意：不要判断按钮是否禁用，只描述按钮文字和颜色
```

### 场景 B：分析列表页

```
客观描述：
1) 顶栏文字和按钮
2) 标题和副标题文字
3) 当前激活的 Tab 名称（高亮显示的那个）
4) 列表显示"几个条目"的提示文字
5) 列出每个条目的实际文字（名称、内容、标签）
6) 是否有空白区域、加载态、错误占位
7) 任何看起来不一致的间距、对齐、颜色问题
```

### 场景 C：分析表单填写后状态

```
客观描述：
1) 弹窗内每个表单字段当前的值
2) 输入框里可见的文字内容
3) 标签区域是否有标签，标签文字是什么
4) 是否有 toast/通知，文字和位置
5) 弹窗整体布局有没有被撑破或错位
注意：不要判断按钮是否禁用，不要判断输入框文字是否被截断
```

---

## §3 Agent 侧 DOM 检测补充清单

> 当 VL 分析涉及以下场景时，Agent 必须额外用 Playwright DOM 检测补充：

| 场景 | VL 不可靠 | DOM 检测方式 |
|------|-----------|--------------|
| 按钮 disabled | ❌ | `class` 包含 `n-button--disabled` |
| Input 文本溢出 | ❌ | `scrollWidth > clientWidth` |
| 元素计数 | ❌ | `locator.count()` |
| Hover 状态 | ❌ | `:hover` CSS 伪类，需要 `page.hover()` 后截图 |
| Loading 状态 | ⚠️ | `class` 包含 `n-button--loading` 或 `is-loading` |
| 焦点元素 | ❌ | `await page.evaluate(() => document.activeElement)` |
| Modal 是否打开 | ⚠️ | `.n-modal-container .n-modal` count > 0 |
| Toast 是否显示 | ⚠️ | `.n-message` count > 0 |

---

## §4 改进 SKILL.md 的建议

1. **"Prompt 编写原则"** 段落新增"VL 不可靠场景"小节，指向本速查本
2. **"人类交互工作流"** 第 3 步加入：VL 返回后，对照 §3 清单判断是否需要 DOM 补充
3. **screenshot.mjs** 可扩展支持 `--fill` / `--measure` 参数，避免每次写临时脚本
4. 建议新增 `scripts/dom-check.mjs`：常用 DOM 检测的封装（disabled / overflow / count）

---

## §5 待观察（尚未定论）

- VL 对中文长文本的截断描述是否稳定
- VL 对 ECharts / 复杂图表的识别准确度
- VL 对深色主题 vs 浅色主题的差异
- 4B thinking 模型 vs 8B instruct 的差异

发现新问题时，按 P01-P03 格式追加到 §1。
