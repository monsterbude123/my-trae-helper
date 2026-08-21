# pytest-patterns — pytest 端点测试范式

## §1 用例骨架

```python
import pytest, requests, json
from pathlib import Path

# conftest.py 提供 fixture
@pytest.fixture(scope="session")
def api_session(env):
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {env['API_TOKEN']}",
        "Content-Type": "application/json",
    })
    return s

@pytest.fixture(scope="session")
def test_cases(workspace):
    yaml_path = Path(workspace) / "tests" / "test-cases.yaml"
    return yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

@pytest.mark.api
@pytest.mark.parametrize("case_id", [
    cid for cid, c in test_cases.items() if c["type"] in ("api", "both")
])
def test_endpoint(case_id, test_cases, api_session):
    case = test_cases[case_id]
    resp = api_session.request(
        method=case["method"],
        url=case["url"],
        headers=case.get("headers", {}),
        json=case.get("body"),
        timeout=10,
    )
    assert resp.status_code == case["expected_status"], \
        f"[{case_id}] status: {resp.status_code}, expected: {case['expected_status']}"

    body = resp.json()
    for field in case["expected_fields"]:
        assert field in body, f"[{case_id}] missing field: {field}"
```

## §2 夹具复用

```python
# conftest.py
@pytest.fixture(scope="session")
def env():
    """由 credential-keeper 注入的 env dict"""
    from ai_testmate.credential import load_env
    return load_env()

@pytest.fixture(scope="session")
def workspace():
    return os.environ["TESTMATE_WORKSPACE_ROOT"]
```

## §3 失败响应落盘

```python
@pytest.fixture(autouse=True)
def save_failure_response(request, api_session, workspace):
    yield
    if request.node.rep_call.failed:
        case_id = request.node.callspec.id
        out = Path(workspace) / "reports" / "<timestamp>" / f"response-{case_id}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        # api_session 最后一请求缓存
        out.write_text(json.dumps(api_session.last_response.json(), indent=2), encoding="utf-8")
```

## §4 报告输出(JUnit XML)

pytest 内置:
```bash
pytest tests/test_api.py \
  --junit-xml=reports/<ts>/junit.xml \
  -v
```

## §5 反模式(对应 AP-1 / AP-7)

- ❌ 硬编码 base_url(应从 env 注入)
- ❌ 跳过鉴权夹具(失败用例不可信)
- ❌ 用例间共享可变状态(顺序耦合)
- ❌ 报告无时间戳(覆盖历史)
- ❌ 失败响应体不落盘(根因缺失)