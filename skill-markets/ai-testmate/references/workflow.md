# workflow — 流水线详细协议

## §1 6 步流水线

```
Step 1 [planner]
  输入:<workspace>/docs/prds/<app>-prd.md
  动作:解析 PRD + 调 zentao-cli(只读)
       zentao product story list --product $ZENTAO_PRODUCT_ID
       zentao testcase list --product $ZENTAO_PRODUCT_ID
  输出:<workspace>/tests/<app>/test-cases.yaml

Step 2 [credential-keeper]
  输入:<project>/.agents/.env
  动作:校验必填变量(见 env-config-spec.md §1)
  输出:env dict(内存对象)

Step 3a [api-tester] ∥ Step 3b [ui-tester]   ← 并行异步
  输入:test-cases.yaml + env dict
  动作:分别跑 pytest-playwright 与 pytest-requests
  输出:
    api-tester → reports/<ts>/api-report.json
    ui-tester  → reports/<ts>/ui-report.json + screenshots/

Step 4 [reporter]
  输入:api-report.json + ui-report.json + test-cases.yaml + env dict
  动作:
    4.1 聚合统计(总/通过/失败/跳过/P0~P2 分组)
    4.2 失败根因建议(匹配 trap-instructions.yaml)
    4.3 禅道回写(testtask create + bug create)
    4.4 飞书推送(lark_im_message send)
  输出:
    reports/<ts>/report.html
    reports/<ts>/report.md
    reports/<ts>/junit.xml
    reports/<ts>/manifest.json
```

## §2 test-cases.yaml 字段规范

```yaml
- id: TC-001                              # 全局唯一
  story_ref: ZT-STORY-1234                # 禅道需求 ID(可选,planner 自动填)
  existing_ref: ZT-CASE-5678              # 禅道已有用例 ID(可选)
  name: 用户登录                          # 用例名
  type: ui                                # ui | api | both
  priority: P0                            # P0 | P1 | P2
  preconditions:                          # 前置条件
    - "测试用户 A 已注册"
  steps:                                  # 步骤(自然语言)
    - "打开 /login"
    - "输入账号密码"
    - "点击登录"
  expected:                               # 预期
    - "跳转到 /dashboard"
  data:                                   # 用例数据(可选)
    user_pool: TEST_USER_A
```

## §3 时间戳目录规范

```
reports/YYYYMMDD_HHMMSS/
├── api-report.json
├── ui-report.json
├── report.html
├── report.md
├── junit.xml
├── manifest.json
└── screenshots/
    ├── TC-001-before.png
    ├── TC-001-failure.png
    └── ...
```

时间戳生成:`$(date +%Y%m%d_%H%M%S)`(Linux/macOS)或 `Get-Date -Format "yyyyMMdd_HHmmss"`(Windows)

## §4 子代理并行(主代理必读)

```
api-tester 与 ui-tester 必须并发启动(主代理 Task 工具 async fire-and-forget)
主代理等待两者都 done 后才进 reporter
禁止串行(浪费时间)
```

## §5 失败回退

| 阶段失败 | 行为 |
|---------|------|
| planner 失败 | 整单停,标 BLOCK |
| credential-keeper 失败 | 整单停,标 BLOCK |
| api-tester 失败 | 标记继续,reporter 报告 |
| ui-tester 失败 | 标记继续,reporter 报告 |
| reporter 部分失败 | 标记 + 降级 webhook 写 logs/ |