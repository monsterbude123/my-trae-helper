# report-templates — 4 份报告模板

## §1 report.html(可视化 + 截图对比)

```html
<!DOCTYPE html>
<html>
<head>
  <title>ai-testmate report <ts></title>
  <style>/* 简洁样式 */</style>
</head>
<body>
  <h1>🤖 ai-testmate 测试报告</h1>
  <p>时间戳:<ts></p>
  <h2>汇总</h2>
  <table border="1">
    <tr><th>总用例</th><th>通过</th><th>失败</th><th>跳过</th><th>错误率</th></tr>
    <tr><td><total></td><td><passed></td><td><failed></td><td><skipped></td><td><error_rate>%</td></tr>
  </table>
  <h2>按优先级分组</h2>
  <table border="1">
    <tr><th>P0</th><th>P1</th><th>P2</th></tr>
    <tr><td>P0: <p0_pass>/<p0_total></td><td>P1: <p1_pass>/<p1_total></td><td>P2: <p2_pass>/<p2_total></td></tr>
  </table>
  <h2>失败用例</h2>
  <ul>
    <li><tc_id>: <name> — 错误: <err>
      <div><before.png> vs <failure.png></div>
      <pre><stacktrace></pre>
    </li>
  </ul>
  <h2>禅道 Bug 链接</h2>
  <ul>
    <li><bug_id>: <bug_title> — <bug_url></li>
  </ul>
</body>
</html>
```

## §2 report.md(可读)

```markdown
# ai-testmate 测试报告 <timestamp>

## 汇总

- 总用例: <total>
- 通过: <passed> ✅
- 失败: <failed> ❌
- 跳过: <skipped>
- 错误率: <error_rate>%

## 按优先级

| P0 | P1 | P2 |
|----|----|----|
| <p0_pass>/<p0_total> | <p1_pass>/<p1_total> | <p2_pass>/<p2_total> |

## 失败用例详情

### TC-001: 用户登录失败
- 复现步骤:...
- 期望:...
- 实际:...
- 错误堆栈:...
- 截图:![before](screenshots/TC-001-before.png)![failure](screenshots/TC-001-failure.png)
- 禅道 Bug:<bug_id> <bug_url>

## 附件

- [JUnit XML](junit.xml)
- [HTML 报告](html)
```

## §3 junit.xml(CI 对接)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="ai-testmate" tests="<total>" failures="<failed>" skipped="<skipped>" time="<duration>">
  <testsuite name="<app>" failures="<failed>" tests="<total>" skipped="<skipped>" time="<duration>">
    <testcase classname="api" name="TC-001" time="<t>">
      <failure type="AssertionError" message="<msg>">
        <stacktrace></stacktrace>
      </failure>
    </testcase>
    <!-- 更多用例 -->
  </testsuite>
</testsuites>
```

## §4 manifest.json(禅道回写元数据)

```json
{
  "timestamp": "<ts>",
  "app": "<app>",
  "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
  "testtask_id": null,
  "bugs_created": [
    {"case_id": "TC-001", "bug_id": "<id>", "url": "<url>"}
  ],
  "lark_pushed": true,
  "lark_card_path": "<workspace>/reports/<ts>/card.json"
}
```

## §5 失败根因建议规则库(trap-instructions.yaml)

```
- rule_id: timeout
  match: "TimeoutError|Read timed out"
  suggestion: "检查网络/服务响应时间,适当增加 timeout"
- rule_id: 401
  match: "401 Unauthorized"
  suggestion: "检查 TEST_USER_* 凭据是否过期"
- rule_id: element_not_found
  match: "ElementNotFound|locator.*not found"
  suggestion: "页面结构可能变更,人工核对 selector"
```