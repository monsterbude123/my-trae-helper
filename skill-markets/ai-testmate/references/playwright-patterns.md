# playwright-patterns — Playwright UI 端到端范式

## §1 登录态复用

```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context(browser, env):
    context = browser.new_context(base_url=env["APP_BASE_URL"])
    # 登录一次,保存 cookies
    page = context.new_page()
    page.goto("/login")
    page.fill('[name="email"]', env["TEST_USER_A_EMAIL"])
    page.fill('[name="password"]', env["TEST_USER_A_PASSWORD"])
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard")
    context.storage_state(path=".auth/state.json")
    yield context

@pytest.fixture
def logged_in_page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()
```

## §2 截图脱敏(AP-5 必做)

```python
def mask_password_fields(page):
    """截图前注入 CSS mask 所有密码字段"""
    page.add_style_tag(content="""
        input[type="password"],
        input[name*="secret"],
        input[name*="token"],
        input[name*="key"],
        [data-sensitive="true"] {
            -webkit-text-security: disc !important;
            color: transparent !important;
            background: #333 !important;
        }
    """)

@pytest.fixture(autouse=True)
def screenshot_on_failure(logged_in_page, request):
    yield
    if request.node.rep_call.failed:
        case_id = request.node.callspec.id
        # 截图前脱敏
        mask_password_fields(logged_in_page)
        timestamp = datetime.now().strftime("%H%M%S")
        out = SCREENSHOTS_DIR / f"{case_id}-failure-{timestamp}.png"
        logged_in_page.screenshot(path=str(out), full_page=True)
```

## §3 用例骨架

```python
@pytest.mark.ui
@pytest.mark.parametrize("case_id", [
    cid for cid, c in test_cases.items() if c["type"] in ("ui", "both")
])
def test_ui_flow(case_id, test_cases, logged_in_page):
    case = test_cases[case_id]
    page = logged_in_page
    for step in case["steps"]:
        action, selector, value = step["action"], step["selector"], step.get("value")
        if action == "goto":
            page.goto(selector)
        elif action == "fill":
            page.fill(selector, value)
        elif action == "click":
            page.click(selector)
        # ... 更多 action
    # 断言
    for expected in case["expected"]:
        assert_selector_present(page, expected)
```

## §4 浏览器选择

```python
# 默认 chromium(三核中最小、最快)
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

# 跨浏览器矩阵(可选)
# pytest --browser chromium webkit firefox
```

## §5 反模式(AP-5 / AP-1)

- ❌ 截图前未 mask 密码字段 → 报告泄露凭据
- ❌ base_url 硬编码 `https://example.com`
- ❌ 失败截图不带时间戳 → 与历史混淆
- ❌ 浏览器路径硬编码 `/usr/bin/chromium`
- ❌ 登录脚本重复执行(应 fixture scope=session)