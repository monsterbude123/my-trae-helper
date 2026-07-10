# §13 工具链推荐

> 每类问题对应的工具/库，含"解决什么问题 + 替代方案 + 接入难度"。

---

## Python 测试栈

| 工具 | 解决什么问题 | 替代方案 | 接入难度 |
|------|------------|---------|---------|
| `pytest` | 测试框架 | unittest | ⭐ |
| `pytest-asyncio` | 异步测试支持 | 异步 unittest | ⭐ |
| `pytest-cov` | 覆盖率 | coverage.py | ⭐ |
| `pytest-xdist` | 并行测试 | pytest-parallel | ⭐⭐ |
| `pytest-timeout` | 测试超时控制 | 自定义装饰器 | ⭐ |
| `pytest-mock` | Mock fixture | 直接用 unittest.mock | ⭐ |
| `pytest-httpserver` | HTTP mock | responses / httpx_mock | ⭐⭐ |
| `freezegun` / `time-machine` | 时间冻结 | 自定义 monkeypatch | ⭐ |
| `faker` | 测试数据生成 | 手写 fixture | ⭐ |
| `hypothesis` | 属性测试 | parametrize | ⭐⭐⭐ |

---

## TypeScript / JavaScript 测试栈

| 工具 | 解决什么问题 | 替代方案 | 接入难度 |
|------|------------|---------|---------|
| `vitest` | 测试框架 | jest | ⭐ |
| `@testing-library/react` | React 组件测试 | enzyme | ⭐⭐ |
| `msw` | HTTP mock | nock / fetch-mock | ⭐⭐ |
| `happy-dom` / `jsdom` | DOM 模拟 | - | ⭐ |
| `@vitest/coverage-v8` | 覆盖率 | c8 | ⭐ |
| `vitest-teamcity-reporter` | CI 报告 | - | ⭐ |

---

## E2E 测试栈

| 工具 | 解决什么问题 | 替代方案 | 接入难度 |
|------|------------|---------|---------|
| `Playwright` | E2E 框架（推荐） | Cypress / Selenium | ⭐⭐ |
| `@playwright/test` | Playwright 测试 runner | - | ⭐ |
| `playwright-tracer` | 失败时录制 trace | - | ⭐ |
| `reg-suit` | 视觉回归对比 | Percy / BackstopJS | ⭐⭐ |
| `axe-core` | 无障碍检测 | - | ⭐⭐ |

---

## 性能测试栈

| 工具 | 解决什么问题 | 替代方案 | 接入难度 |
|------|------------|---------|---------|
| `k6` | HTTP 负载测试（推荐） | Locust / JMeter | ⭐⭐ |
| `pytest-benchmark` | Python 微基准 | timeit | ⭐ |
| `Lighthouse CI` | 前端性能 | WebPageTest | ⭐⭐ |
| `py-spy` | Python 火焰图 | Austin | ⭐ |
| `Clinic.js` | Node.js 性能诊断 | 0x | ⭐⭐ |
| `EXPLAIN ANALYZE` | SQL 慢查询分析 | - | ⭐ |

---

## 安全测试栈

| 工具 | 解决什么问题 | 替代方案 | 接入难度 |
|------|------------|---------|---------|
| `bandit` | Python SAST | pylint-security | ⭐ |
| `Semgrep` | 多语言 SAST | SonarQube | ⭐⭐ |
| `pip-audit` | Python SCA | safety | ⭐ |
| `npm audit` / `Snyk` | JS SCA | - | ⭐ |
| `Gitleaks` | 密钥扫描 | TruffleHog | ⭐ |
| `Trivy` | 容器镜像扫描 | Grype / Clair | ⭐⭐ |
| `OWASP ZAP` | DAST（动态扫描） | Burp Suite | ⭐⭐⭐ |

---

## 日志与诊断栈

| 工具 | 解决什么问题 | 替代方案 | 接入难度 |
|------|------------|---------|---------|
| `structlog` | 结构化日志 | loguru | ⭐ |
| `Sentry` | 错误监控 + APM | Datadog / NewRelic | ⭐⭐ |
| `OpenTelemetry` | 分布式追踪 | Jaeger / Zipkin | ⭐⭐⭐ |
| `pytest-logger` | 测试日志 | - | ⭐ |

---

## CI/CD 栈

| 工具 | 解决什么问题 | 替代方案 | 接入难度 |
|------|------------|---------|---------|
| `GitHub Actions` | CI runner | GitLab CI / Jenkins | ⭐ |
| `pre-commit` | 本地 hook | husky + lint-staged | ⭐ |
| `act` | 本地跑 GH Actions | - | ⭐⭐ |
| `Allure` | 测试报告可视化 | ReportPortal | ⭐⭐ |

---

## 工具链选型原则

1. **优先选维护活跃的开源工具**——避免工具自身成为债务
2. **优先选有公共标准的工具**——pytest / Playwright / k6 都是行业标准
3. **每个工具引入前评估 3 个替代方案**——避免随意选型
4. **工具链随团队规模演进**——10 人团队和 100 人团队的工具栈不同
5. **不要追求"全栈工具"**——一个工具搞定所有事通常意味着每件事都做不好
