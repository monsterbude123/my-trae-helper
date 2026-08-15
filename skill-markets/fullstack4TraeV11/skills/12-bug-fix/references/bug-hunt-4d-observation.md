# 4 维度观察法（V11.8.2 NEW Phase A 专属）

> **Stage 6 Phase A Step 2 专属 references**。每个路由观察必须覆盖 4 个维度，**单维度不可证伪**。

---

## §B.0 — 为什么必须 4 维度（铁律 #7）

### 反例：单维度误判 PASS（已发生）

- **BUG-003**：dev server console 报 401 但 visible_text 看 home 页主体仍正常（fallback 占位）→ 主代理只看 visible_text 误判 PASS。
- **BUG-004**：workspace/[projectId] 点击"新建剧集"按钮 → handleCreateEpisode 抛 Unauthorized → 视觉无变化 + 行为失败。
- **BUG-015**：admin/cinema-knowledge/vocabulary → 双倍"加载失败，请重试" → 数据维度失败。

**结论**：4 维度**全过才 PASS**，任一 FAIL 即落 bug 单（按交叉判定表）。

---

## §B.1 — 4 维度定义

| 维度 | 工具 | 检查点 | 失败对应 |
|------|------|--------|----------|
| **视觉（visual）** | `playwright_screenshot` + `playwright_get_visible_text` | 截图含期望关键字/图标/配色；字体未降级（如 emoji 替中文）；布局未塌缩（grid 变纵向 / flex 溢出）；主题色/暗色 token 应用 | L3 视觉走样 |
| **行为（behavior）** | `playwright_click` + `playwright_hover` + `playwright_press_key` | 关键 CTA 点击触发期望动作；hover 显示 tooltip / dropdown；表单提交成功 / 失败状态；路由跳转带预期 query / state | L2 局部不可用 |
| **数据（data）** | `playwright_get_visible_text` + 检查列表条数 / i18n key | mock 列表非空（条数 > 0）；i18n key 已翻译（不能出现 "common.loading" 字面）；数据字段完整（不丢字段、空 stub）；dropdown / select 选项数对齐后端 | L2/L3 |
| **控制台（console）** | `playwright_console_logs` | 0 [error] level；0 401 / 403 / 404 / 500；0 hydration mismatch；0 Unhandled Rejection in Promise | L2（API 401 类）|

### 工具调用模式（每维度）

```yaml
M2.1 视觉维度 (visual):
  工具: mcp__playwright__playwright_screenshot + playwright_get_visible_text
  检查点:
    - 截图是否含期望关键字/图标/配色
    - 字体是否降级（如 emoji 替中文）
    - 布局是否塌缩（grid 变纵向 / flex 溢出）
    - 主题色/暗色 token 是否应用到
  expected_keywords_diff:
    通过: 全部出现
    失败: 1+ 关键字缺失 → 落 L3 视觉走样单
  对应 BUG-003:
    视觉上 home style preset dropdown 仍渲染（仅 fallback 空）
    → 视觉 PASS 但 API 已 401 → 漏判
  关键: 视觉 PASS ≠ API PASS

M2.2 行为维度 (behavior):
  工具: playwright_click + playwright_hover + playwright_press_key
  检查点:
    - 关键 CTA 点击是否触发期望动作
    - hover 是否显示 tooltip / dropdown
    - 表单提交是否成功 / 失败状态
    - 路由跳转是否带预期 query / state
  expected_keywords_diff:
    通过: 跳转 / 状态 / 反馈全部命中
    失败: 静默无响应 / 控制台 unhandled rejection → 落 L2 局部不可用
  对应 BUG-004:
    workspace/[projectId] 点击"新建剧集"按钮 → handleCreateEpisode 抛 Unauthorized
    → 视觉无变化 + 行为失败 → 应落 L2

M2.3 数据维度 (data):
  工具: playwright_get_visible_text + 检查列表条数 / i18n key
  检查点:
    - mock 列表是否非空（条数 > 0）
    - i18n key 是否翻译（不能出现 "common.loading" 字面）
    - 数据字段是否完整（不丢字段、空 stub）
    - dropdown / select 选项数对齐后端
  expected_keywords_diff:
    通过: 列表条数 ≥ 1 + 关键字段非空
    失败: "暂无数据" / "加载失败" / "—" 占位 → 落 L2 / L3
  对应 BUG-015:
    admin/cinema-knowledge/vocabulary → 双倍"加载失败，请重试"
    → 数据维度失败 → 应落 L2

M2.4 控制台维度 (console):
  工具: mcp__playwright__playwright_console_logs
  检查点:
    - 是否有 [error] 级别日志
    - 是否有 401 / 403 / 404 / 500 状态码
    - 是否有 hydration mismatch
    - 是否有 Unhandled Rejection in Promise
  expected_keywords_diff:
    通过: 0 error / 0 fatal / 0 unhandled rejection
    失败: 任一出现 → 必查 dev server log 反查根因
  对应 BUG-003/004:
    [useArtStyles] Failed to fetch art styles: 401 + handleCreateEpisode Unauthorized
    → API 401 触发源头 → 必看此维度
  关键: control plane PASS ≠ UI 集成 PASS
```

---

## §B.2 — 4 维度交叉判定规则

| 视觉 | 行为 | 数据 | 控制台 | 判定 | 操作 |
|:---:|:---:|:---:|:---:|:---:|------|
| ✅ | ✅ | ✅ | ✅ | **PASS** | 不落单，进入下一路由 |
| ✅ | ❌ | * | * | **L2** | 落 bug 单（行为失败） |
| ✅ | * | ❌ | * | **L2** | 落 bug 单（数据失败） |
| ✅ | * | * | ❌ | **L2**（API 401 类）| 落 bug 单（控制台失败） |
| ❌ | * | * | * | **L3** 视觉走样 | 落 bug 单（视觉失败） |
| * | ✅ | ✅ | ❌ | **L2** | API 失败但 UI 集成通过（隐式 bug） |

`*` = 任意（PASS 或 FAIL 不影响本判定）。

---

## §B.3 — 4 维度必备命令（每次观察必跑）

```yaml
# 1. 视觉：截图 + visible_text
mcp__playwright__playwright_screenshot
mcp__playwright__playwright_get_visible_text

# 2. 行为：关键 CTA 点击 + hover
mcp__playwright__playwright_click "button[type='submit']"
mcp__playwright__playwright_hover "[data-testid='nav-item']"

# 3. 数据：列表条数 + i18n key 抽查
# (visible_text 中 grep 关键字)

# 4. 控制台：console_logs
mcp__playwright__playwright_console_logs
```

---

## §B.4 — 反 §05 api-pass-not-ui-pass 反例

> API 200 + 空 fallback → 视觉仍 OK → 误判 PASS。

**破解**：4 维度交叉判定表的第 4 行（视觉 ✅ + 控制台 ❌）会捕获此类——API PASS ≠ UI 集成 PASS。

## §B.5 — 反 §06 fabricate-completed-without-visual 反例

> 4 维度全 ✓ 但已用站外 demo 截图 → 假证据。

**破解**：必走 [bug-hunt-5-check.md](bug-hunt-5-check.md) M6.1 主代理亲自 Read 截图。

---

## 关联引用

- [bug-hunt-phase-a.md](bug-hunt-phase-a.md) — Phase A 整体 3 步流程
- [bug-hunt-5-check.md](bug-hunt-5-check.md) — 5 项证据独立抽检
- [bug-hunt-battle-report.md](bug-hunt-battle-report.md) — V11.8.2 实战报告（含 BUG-003/004/015 失败案例）
- [../SKILL.md §铁律 7](../SKILL.md) — 4 维度观察法铁律
- V11 §3.7 #6 — AI 描述 ≠ 真实像素（视觉抽检必走）