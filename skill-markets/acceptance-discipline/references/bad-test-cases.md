# §11 坏测试案例库

> 本节收录从三份原始资料提炼 + 行业常见 + 实战高频的 12 类 Bad Test 反模式。每条均含**症状 / 根因 / 修复 diff / 预防措施**，可直接作为团队培训教材与代码 review 检查项。

---

## 案例索引

| # | 类型 | 严重度 | 影响范围 | 来源 |
|---|------|-------|---------|------|
| 1 | Test Eater（套件阻塞） | 🔴 HIGH | 全套件卡死 | test-experience |
| 2 | Flaky Test（时过时不过） | 🔴 HIGH | 虚假信心 / 浪费排查时间 | test-experience |
| 3 | Mock 路径错配 | 🔴 HIGH | 测试无意义 / 调真实 API | test-partition-runner |
| 4 | Async Generator 当 Promise | 🟡 MED | 测试假通过 | test-partition-runner |
| 5 | ReadableStream 类型错误 | 🟡 MED | 流式接口测试失败 | test-partition-runner |
| 6 | Native Module 未编译 | 🟡 MED | 测试启动即崩 | test-partition-runner |
| 7 | Sync Fixture 调 asyncio.run() | 🟡 MED | 全量测试慢 17× | test-experience |
| 8 | 部分 Mock（引用链断裂） | 🟡 MED | Mock 看似生效实际没生效 | test-experience |
| 9 | Assertion-Free Test | 🟢 LOW | 测试永远通过，无价值 | test-experience |
| 10 | Copy-Paste Cascade | 🟢 LOW | 维护成本爆炸 | test-experience |
| 11 | 截图无日志（E2E 假验收） | 🔴 HIGH | "页面有问题"反复猜改 | e2e-module-audit |
| 12 | 修复不重验证 | 🔴 HIGH | "声称修好"实际未修 | e2e-module-audit |

---

## 案例 1：Test Eater — 卡死整个套件

**症状**：跑 `pytest` 后某个测试开始就一直不动，`Ctrl+C` 后看到卡在 `test_chat_with_llm`。

**根因**：测试调用了真实 LLM API，没有 mock，等待 60s 超时。

```python
# ❌ BEFORE
@pytest.mark.asyncio
async def test_chat_with_llm():
    response = await llm.chat("hello")  # 真实调用 OpenAI，60s 超时
    assert response is not None
```

```python
# ✅ AFTER
@pytest.mark.asyncio
async def test_chat_with_llm(mock_llm):
    mock_llm.chat.return_value = {"content": "fake response"}
    response = await llm.chat("hello")
    assert response["content"] == "fake response"

# conftest.py
@pytest.fixture
def mock_llm(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("app.services.llm.provider", mock)
    return mock
```

**预防**：
- autouse fixture hook socket 层，禁止真实网络调用（见 metrics.md）
- LLM 相关测试默认带 `@pytest.mark.slow`，日常回路跳过

---

## 案例 2：Flaky Test — 时过时不过

**症状**：`test_search_with_timestamp` 在 CI 上时绿时红，本地 10 次有 3 次失败。

**根因**：测试用了 `datetime.now()` 作为输入，跨秒时结果不同。

```python
# ❌ BEFORE
def test_search_with_timestamp():
    result = search(created_after=datetime.now() - timedelta(days=1))
    assert len(result) == 10  # 跨秒时数据库行数可能变化
```

```python
# ✅ AFTER
def test_search_with_timestamp(freezer):
    freezer.move_to("2026-06-25 12:00:00")
    # 固定时间，数据确定性
    result = search(created_after=datetime(2026, 6, 24, 12, 0, 0))
    assert len(result) == 10

# conftest.py
@pytest.fixture
def freezer(time_machine):
    return time_machine
```

**预防**：
- 任何用 `now()` / `uuid()` / `random()` 的测试必须 freeze
- CI 上跑 10 次连测，加入 Flaky Score 监控（见 metrics.md）

---

## 案例 3：Mock 路径错配

**症状**：测试明明 mock 了 `fetchWithProxy`，但实际跑时还是发了真实请求。

**根因**：代码里实际调用的是 `fetchWithRetry`（在另一个模块），mock 路径错了。

```typescript
// ❌ BEFORE：mock 了错误的模块
vi.mock('@/lib/serverUtils', () => ({
  fetchWithProxy: vi.fn(),  // 实际代码用的是 fetchWithRetry
}));

// 测试中
const result = await fetchData();  // 内部调 fetchWithRetry，未 mock → 真实请求
```

```typescript
// ✅ AFTER：mock 实际调用方
vi.mock('@/lib/concurrency-limiter', () => ({
  fetchWithRetry: vi.fn().mockResolvedValue({ ok: true, data: 'fake' }),
}));
```

**预防**：
- 写完 mock 后，**故意改 mock 返回值**确认测试会失败（验证 mock 生效）
- Mock 生效性检查清单必须逐项过

---

## 案例 4：Async Generator 当 Promise

**症状**：测试用 `expect(...).rejects.toThrow()`，但 generator 抛出的错误没被捕获，测试假通过。

**根因**：`adapter.chat()` 返回 `AsyncGenerator`，不是 `Promise`，`rejects.toThrow` 无效。

```typescript
// ❌ BEFORE
await expect(adapter.chat([...])).rejects.toThrow('429');
// generator 抛错发生在迭代时，不是调用时，这个 expect 永远不会触发
```

```typescript
// ✅ AFTER：消费 generator 才能捕获错误
let error: Error | null = null;
try {
  for await (const _ of adapter.chat([...])) {
    // 消费所有 chunk
  }
} catch (e) {
  error = e as Error;
}
expect(error).toBeTruthy();
expect(error?.message).toContain('429');
```

**预防**：
- 写 mock 前确认返回类型：`Promise<T>` / `AsyncGenerator<T>` / `AsyncIterator<T>`
- 团队内共享"async generator 测试模板"

---

## 案例 5：ReadableStream 类型错误

**症状**：Mock SSE 流式响应时，`response.text()` 拿到的是 `[object Object]` 而非真实文本。

**根因**：`ReadableStream.from([string])` 创建的是 `ReadableStream<string>`，但 fetch 期望 `ReadableStream<Uint8Array>`。

```typescript
// ❌ BEFORE
const sseBody = "data: hello\n\n";
const mockResponse = new Response(ReadableStream.from([sseBody]));
// 实际读取时拿到的是字符串 toString，不是 ArrayBuffer
```

```typescript
// ✅ AFTER
function createMockStreamBody(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  let index = 0;
  return new ReadableStream<Uint8Array>({
    pull(controller) {
      if (index < chunks.length) {
        controller.enqueue(encoder.encode(chunks[index]));
        index++;
      } else {
        controller.close();
      }
    }
  });
}

const mockResponse = new Response(createMockStreamBody(["data: hello\n\n"]));
```

**预防**：
- 流式接口测试必须有"端到端"的 chunk 拼接验证
- 在 helper 库里固化 `createMockStreamBody` 函数

---

## 案例 6：Native Module 未编译

**症状**：`npm install` 后跑测试，`better-sqlite3` 报 `Module did not self-register`。

**根因**：`better-sqlite3` 是 native module，依赖 Node ABI 版本，更换 Node 版本后需 rebuild。

```bash
# ❌ 错误做法：删除 node_modules 重装（不解决 ABI 问题）

# ✅ 正确做法
npm rebuild better-sqlite3
npx prisma generate  # prisma 同理
```

**预防**：
- `.nvmrc` 锁定 Node 版本
- `package.json` 加 `postinstall: npm rebuild && prisma generate`
- README 文档化"换 Node 版本后必须 rebuild"

---

## 案例 7：Sync Fixture 调 asyncio.run()

**症状**：250 个测试全量跑 125s，但单测都 < 50ms。

**根因**：autouse sync fixture 里调 `asyncio.run(database.init_db())`，每个测试都新建事件循环。

```python
# ❌ BEFORE
@pytest.fixture(autouse=True)
def init_db_every_test():
    asyncio.run(database.init_db())  # 250 测试 × 0.5s = 125s 浪费
```

```python
# ✅ AFTER
@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """只在需要 DB 的测试里显式声明"""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    asyncio.run(database.init_db())  # 仅在需要的测试调用
    yield db_path
```

**预防**：
- `pytest --durations=10` 应该作为日常命令，发现慢测试立即排查
- autouse fixture 慎用，特别是涉及 IO 的

---

## 案例 8：部分 Mock（引用链断裂）

**症状**：mock 了 `embedding_service.embed`，但测试时 `chroma_store` 内部还是调了真 embedding。

**根因**：`chroma_store` 在初始化时已 import embedding，mock 时 embedding 引用已固化。

```python
# ❌ BEFORE：只 mock 了一处
monkeypatch.setattr(embedding_service, "embed", mock_embed)
# chroma_store.embed 已经在模块加载时绑定到原 embed
```

```python
# ✅ AFTER：autouse fixture 统一 mock 所有外部依赖
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """统一 mock，避免引用链遗漏"""
    monkeypatch.setattr("app.services.embedding.embed", mock_embed)
    monkeypatch.setattr("app.services.vector_store.ChromaClient",
                        InMemoryChroma)
    monkeypatch.setattr("app.services.llm.provider", MockLLMProvider())
```

**预防**：
- 不在每个测试文件里重复写 mock，统一在 conftest.py autouse fixture
- Mock 覆盖率监控（见 metrics.md）

---

## 案例 9：Assertion-Free Test

**症状**：测试代码只有 `await some_func()`，没有 `assert`。测试永远通过。

**根因**：开发者写测试是为了"跑过"，不是为了"验证"。

```python
# ❌ BEFORE
@pytest.mark.asyncio
async def test_create_user():
    user = await create_user("alice@test.com")
    # 没 assert，永远通过
```

```python
# ✅ AFTER
@pytest.mark.asyncio
async def test_create_user(temp_data_dir):
    user = await create_user("alice@test.com")
    assert user.id is not None
    assert user.email == "alice@test.com"
    assert user.created_at is not None
    # 验证 DB 持久化
    db_user = await get_user(user.id)
    assert db_user.email == "alice@test.com"
```

**预防**：
- lint 规则：测试函数必须包含 `assert` 关键字
- Code review 时检查"测试是否真的能 catch bug"——故意改坏代码看测试是否失败

---

## 案例 10：Copy-Paste Cascade

**症状**：一个测试文件里有 20 个测试，结构几乎相同，只差一个参数。

**根因**：复制粘贴方便，但维护成本爆炸——改一个所有都要改。

```python
# ❌ BEFORE：20 个相似测试
def test_login_with_email(): ...
def test_login_with_phone(): ...
def test_login_with_username(): ...
# ... 还有 17 个
```

```python
# ✅ AFTER：parametrize
@pytest.mark.parametrize("identifier_type,identifier_value", [
    ("email", "alice@test.com"),
    ("phone", "+8613800000000"),
    ("username", "alice"),
    # ...
])
def test_login(identifier_type, identifier_value):
    result = login(identifier_type, identifier_value)
    assert result.success
```

**预防**：
- 看到 3 个以上相似测试就重构为 parametrize
- Code review 时质疑"这段代码是否可以参数化"

---

## 案例 11：截图无日志（E2E 假验收）

**症状**：E2E 截图显示页面空白，AI 直接说"页面渲染有问题"，开始猜各种原因改了一下午。

**根因**：只截图不拉日志，没有证据链。

```typescript
// ❌ BEFORE：只截图
await page.goto("/dashboard");
await page.screenshot({ path: "screenshots/dashboard.png" });
// 然后开始猜——是路由错了？是 API 挂了？是 JS 报错？
```

```typescript
// ✅ AFTER：截图 + 日志 + 控制台 + 网络请求
await page.goto("/dashboard");
await page.screenshot({ path: "screenshots/dashboard.png" });

// 并行收集证据
const [consoleLogs, networkLogs] = await Promise.all([
  page.evaluate(() => window.__e2e_console_logs),
  page.evaluate(() => window.__e2e_network_logs),
]);
const backendLogs = await queryRecentLogs("dashboard", 100);

// 关联诊断
if (consoleLogs.some(l => l.level === 'error')) {
  // 定位 JS 错误
}
if (networkLogs.some(n => n.status >= 500)) {
  // 定位后端 API
}
```

**预防**：
- E2E 必须遵守"截图是线索，日志是证据"铁律
- Workflow B 的 6 步协议必须完整走完

---

## 案例 12：修复不重验证

**症状**：AI 修复了"按钮点击没反应"的 bug，提交了代码，说"已修复"。下次发版重爆。

**根因**：修完没重跑用户场景验证。

```
# ❌ BEFORE
用户：注册按钮点了没反应
AI：根因是 services/auth.ts:32 未处理 500，已修复
AI：完成 ← 没有重跑验证

# ✅ AFTER
用户：注册按钮点了没反应
AI：根因是 services/auth.ts:32 未处理 500，已修复
AI：重新执行注册流程 → 截图显示"该邮箱已注册" → 前后端无 ERROR/WARNING
AI：完成 ✅（带验证证据）
```

**预防**：
- Workflow B 硬约束：修复后必须重新导航 + 操作 + 截图
- "完成标志 = 操作正常 + 截图正常 + 前后端无 ERROR/WARNING"

---

## 案例库的维护

- 新发现的 Bad Test 必须按 blockage-resolver-agent.md 的 Bad Test 反馈模板记录到案例库
- 每季度 review 案例库，删除已通过工具自动检测的项
- 案例库作为新人入职必读材料
