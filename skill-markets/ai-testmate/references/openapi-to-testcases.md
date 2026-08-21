# openapi-to-testcases — OpenAPI → test-cases.yaml 映射

> v1.1 增量。`scripts/openapi-extractor.py` 读 openapi.json/yaml,产出 test-cases.yaml 片段。

---

## §1 openapi 字段映射

| OpenAPI 字段 | test-cases.yaml 字段 | 说明 |
|-------------|---------------------|------|
| `operationId` | `name` | 缺 operationId → 用 `${method} ${path}` |
| `path` + `method` | `data.url` + `data.method` |  |
| `tags[0]` | `priority` | "core"→P0,"admin"→P2,其他→P1 |
| `summary` | 追加到 `preconditions` |  |
| `parameters[].name` + `in=path` | `data.path_params` | 必填参数放第一项 |
| `parameters[].name` + `in=query` | `data.query_params` |  |
| `requestBody.required` | `preconditions` 追加 |  |
| `responses` | `data.expected_status` | 取 200/201 优先 |
| `responses['4xx']` | `data.negative_cases` | 见 §2 |
| `security` | `preconditions` 追加"需 auth" | **V2-AP-1 必检测** |
|  | `id` 前缀 | `TC-API-${operationId 转 kebab-case}` 或 `TC-API-${序号}` |

---

## §2 负例生成规则

每个 operation 自动生成 **1 正例 + 1 负例**(防用例爆炸):

| 正例期望 | 自动生成的负例 |
|---------|--------------|
| 200     | 缺必填参数 → 400/422 |
| 201     | 重复创建 → 409 |
| 204     | -                |
| 4xx     | 取最大 4xx      |

**不生成的负例**:
- 不生成鉴权失败的负例(那是 auth 测试范畴,不是本 operation 的责任)
- 不生成超过 3 步的链路负例(超出单 operation 边界)

---

## §3 生成的 test-cases.yaml 示例

```yaml
# openapi.json 一段:
# paths:
#   /users/{id}:
#     get:
#       operationId: getUser
#       tags: [core]
#       security: [{bearerAuth: []}]
#       parameters: [{name: id, in: path, required: true}]
#       responses:
#         '200': {...}
#         '404': {...}

# 生成的 test-cases.yaml:
- id: TC-API-get-user
  story_ref: null
  name: getUser
  type: api
  priority: P0
  source: openapi
  preconditions:
    - 需 auth(bearer)
    - 存在 user_id
  steps:
    - "GET /users/{id} 传有效 id"
    - "GET /users/invalid-id 触发 4xx"
  expected:
    - "200 + user 字段"
    - "4xx 错误响应"
  data:
    method: GET
    url: /users/{id}
    path_params: {id: 1}
    expected_status: 200
    negative_cases:
      - url: /users/invalid
        expected_status: 404
    auth_required: true
```

---

## §4 openapi-extractor.py 调用范式

```bash
# 主代理调用
python scripts/openapi-extractor.py \
  --input docs/openapi/app-openapi.json \
  --output tests/app/test-cases.openapi.yaml \
  --mode auto  # auto = 每 op 1 正 +1 负,full = 全状态码穷举
```

---

## §5 反例(V2-AP-1)

- ❌ openapi 有 `security` 字段但提取器不写 `auth_required: true`
  → 修复:openapi-extractor.py 必须检测 security 字段,任何 operation 必带
- ❌ path 参数 `{id}` 不替换占位 → 测试用例 url 是字面量
  → 修复:path_params 必填,生成用例时填占位值
- ❌ operation 没标 method → 全用 GET(假通过)
  → 修复:extractor 必须按 method 严格断言
- ❌ tags 没解析 → 所有用例 priority=P1
  → 修复:tag → priority 映射表(见 §1)
- ❌ 负例只生成 success 路径(用户要求"自动化",生成了空集)
  → 修复:每 op 强制生成至少 1 个负例

---

## §6 与现有 references 的衔接

- 用例落到 `test-cases.yaml` 后,api-tester 按 [pytest-patterns.md](pytest-patterns.md) 跑
- 安全相关用例(api-tester §1 fixture 注入 token)
- 鉴权失败用例不在本 skill 范围,仅生成 happy-path