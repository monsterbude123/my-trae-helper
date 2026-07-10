---
name: "test-experience"
description: "测试开发与质量经验库 — 编写/修改测试代码时加载，覆盖 mock 策略、fixture 设计、异步陷阱、超时控制和 bad-test 反模式。适用 Python + pytest + asyncio 技术栈。"
triggers:
  - "写测试"
  - "加测试"
  - "补测试"
  - "测试失败"
  - "测试超时"
  - "test timeout"
  - "测试卡"
  - "mock 不生效"
  - "fixture"
  - "测试慢"
  - "新增测试"
  - "测试报错"
---

# Test Experience — 通用测试开发质量标准

**避免 agent 在多轮并行开发中重复踩坑。**

---

## §1 核心原则

```
测试不是"能跑就行"。测试代码的设计复杂度不亚于生产代码。
坏测试 > 没有测试（因为坏测试给虚假信心）。
```

| 原则 | 含义 |
|------|------|
| **隔离性** | 测试不依赖外部环境（网络、真实 API、文件系统固定路径） |
| **确定性** | 同一测试 10 次跑结果完全相同 |
| **速度** | 单测 < 50ms，集成测试 < 5s，全量 < 30s（无外部依赖时） |
| **可维护** | 新增外部依赖时只需改 fixture，不改 test body |

---

## §2 测试速度定律

### 2.1 耗时根源分类

| 耗时源 | 典型耗时 | 解决策略 |
|--------|---------|---------|
| 真实 LLM/网络调用 | 20-60s | Mock 降级 |
| 数据库初始化 | 0.5-1s/次 | 仅集成测试使用 |
| 文件 I/O（ZIP 创建） | 20-50ms | 可接受 |
| 事件循环创建/销毁 | 10-30ms | 使用 session scope |

### 2.2 speed budget 模型

```
假设 250 个测试：
- 如果每个测试额外 0.5s DB init → 125s 浪费
- 如果每个测试额外 30s LLM 调用 → 7500s 浪费
- 如果只有 10 个测试调 LLM → 300s 浪费
```

**结论：一个真实网络调用的集中式代价，足以毁掉整个测试套件的可用性。**

### 2.3 分层策略

```
Layer 1: Pure Unit（无 IO）          → autouse fixture 只关外部服务 → < 10s 全量
Layer 2: Mocked Integration（DB）   → 显式声明 temp_data_dir         → < 30s 全量  
Layer 3: Real Integration（LLM）    → @pytest.mark.slow               → 需要时才跑
```

---

## §3 Mock 策略矩阵

### 3.1 三种 mock 手段对比

| 手段 | 适用场景 | 成本 | 风险 |
|------|---------|------|------|
| `monkeypatch.setattr` | 替换模块级函数/属性 | 低 | 不穿透 `from X import Y` |
| `monkeypatch.setenv` | 控制环境变量触发降级 | 低 | 依赖代码内有降级分支 |
| provider/factory 替换 | 整个外部系统替身 | 中 | 需维护 Mock 实现 |

### 3.2 Mock 生效性检查清单

在写 mock 之后，写测试断言之前，MUST 确认：

```
[ ] 被 mock 的函数名在目标模块中确实存在？
[ ] 目标模块是通过 import 导入的还是 from X import Y 导入的？
    → from X import Y 需要 patch 下游模块的 attr，不是源头
[ ] mock 函数签名（参数、返回值类型）与真函数兼容？
[ ] 异步函数用了 AsyncMock？
[ ] 单例/工厂是否需要显式重置？
```

### 3.3 反模式：部分 Mock

```python
# ❌ 只 mock 了 embedding，忘了 chroma_store 引用链
monkeypatch.setattr(embedding_service, "embed", mock_embed)

# ✅ autouse fixture 统一处理所有外部依赖
# 不要在每个测试文件里重复写 mock
```

---

## §4 异步测试陷阱

### 4.1 sync fixture 里调用 asyncio.run()

```python
# ❌ 每个测试创建一个新事件循环
@pytest.fixture(autouse=True)
def init_db_every_test():
    asyncio.run(database.init_db())  # 157 tests × 1 event loop = 大量开销

# ✅ 只在需要 DB 的 fixture 里调用一次
@pytest.fixture
def temp_data_dir():
    asyncio.run(database.init_db())
    yield
```

### 4.2 asyncio + mock 排序

```python
# 问题：asyncio_mode = "auto" 时，sync fixture 在 event loop 外执行
# monkeypatch.setattr 对 async 函数的 mock 可能不生效

# ✅ 确保 mock 在事件循环启动前已设置
```

### 4.3 async generator 不能直接用 returns/rejects

```python
# ❌ Mock 了一个 async generator，但 mock 返回了 coroutine
mock.chat.return_value = {"content": "fake"}  # async generator expects __aiter__

# ✅ MockProvider 完整实现了 __aiter__ / __anext__
```

---

## §5 Fixture 设计范式

### 5.1 命名约定

```
_temp_dir    → scope=function, 每个测试独立
_global_conf → scope=session, 全局共享
mock_xxx     → 明确的 mock fixture
real_xxx     → 明确的真实环境 fixture
```

### 5.2 依赖图可视化原则

```
一个 fixture 依赖链超过 3 层 → 考虑拆分
一个 fixture 做了两件事 → 拆成两个（SRP）
```

### 5.3 teardown 保证

```python
# ✅ 使用 yield 确保清理
@pytest.fixture
def tmp():
    path = create()
    yield path
    shutil.rmtree(path, ignore_errors=True)  # 即使测试崩溃也会清理

# ❌ 在 fixture 开头 delete 旧数据然后创建新数据
#    如果创建失败，旧数据已被删除
```

---

## §6 Bad Test 识别与处理

### 6.1 Bad Test 特征

| 特征 | 表现 | 处理 |
|------|------|------|
| Test Eater | 卡住整个测试套件，其他测试无法执行 | 立即标记 `skip` 或修复 |
| Flaky Test | 时过时不过，无模式 | 重写，加确定性断言 |
| Slow Test | 单用例 > 10s 且无外部调用 | 分析 fixture 链，剪枝 |
| Mockless Test | 调用真实 API 但没有标记 slow | 加 mock 或加 slow mark |
| Assertion-Free | `await some_func()` 无 assert | 删除或加断言 |
| Copy-Paste Cascade | 复制其他测试只改了一行 | 提取公共 fixture/parametrize |

### 6.2 处理流程

```
发现 Bad Test →
  ├── 核心功能？→ 修复（加 mock / 优化 fixture / 重写断言）
  ├── 重复测试？→ 合并
  ├── 废弃功能？→ 删除
  └── 不确定？→ 标记 @pytest.mark.skip(reason="NEEDS REVIEW")
```

---

## §7 新增测试模板

```python
"""测试 <模块名> — <一句话概括>"""
import pytest

# ============================================================================
# Layer 1: Pure Unit（无 IO）
# ============================================================================

class Test<Module>Pure:
    """纯函数/模型验证：无 fixture 依赖，无 IO"""

    def test_<scenario>(self):
        """简短的中文描述"""
        result = some_pure_function(input)
        assert result == expected


# ============================================================================
# Layer 2: Mocked Integration（有 DB，无外部服务）
# ============================================================================

class Test<Module>Integration:
    """集成测试：需要 DB 但 LLM/ChromaDB/Embedding 已由 autouse mock"""

    @pytest.mark.asyncio
    async def test_<scenario>(self, temp_data_dir):
        """需要 DB 的测试，显式声明 temp_data_dir"""
        ...


# ============================================================================
# Layer 3: Real Integration（真实 LLM / 外部服务）
# ============================================================================

class Test<Module>Live:
    """真实 LLM 测试：用环境变量 SHUXIA_TEST_REAL_LLM=1 开启"""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_<scenario>(self, temp_data_dir):
        """仅在需要验证真实 LLM 行为时手动跑"""
        ...
```

---

## §8 测试运行命令速查

```bash
# 日常开发（默认 Mock，全量 250 测试，~16s）
uv run pytest

# 跳过 LLM 测试（~14s）
uv run pytest -m "not slow"

# 显示最慢 10 个测试
uv run pytest --durations=10

# 真实 LLM 验证（~197s，需网络 + API Key）
$env:SHUXIA_TEST_REAL_LLM="1"; uv run pytest

# 单文件
uv run pytest tests/test_api.py -v

# 只跑失败的
uv run pytest --lf

# 覆盖率
uv run pytest --cov=. --cov-report=term-missing
```

---

## §9 ShuXia 项目专项避坑

> 来源：多轮 agent 并行开发中反复踩坑的真实教训。已在 `.trae/rules/测试避坑.md` 中有要点版，此处为完整版。

### 9.1 LLM 调用陷阱

- `_test_env` autouse fixture 默认清空 API Key + Mock Provider/Fallback，**新增 LLM 调用路径时必须确认被覆盖**
- `provider_factory._factory` 是模块级单例，MockProvider 仅在 API Key 为空时创建 → 重置：`monkeypatch.setenv("OPENAI_API_KEY", "")` + `pf._factory = None`
- `@pytest.mark.slow` 标记真实 LLM/API 调用；`-m "not slow"` 跳过（日常 ~14s vs 含 slow ~197s）
- `SHUXIA_TEST_REAL_LLM=1` 启用真实 LLM 验证

### 9.2 monkeypatch 引用链陷阱

`from X import Y` 在模块顶部执行后，monkeypatch 原始模块 X 不会更新下游模块的引用：

```python
# ❌ 只 patch 了 chroma_store.search
monkeypatch.setattr(chroma_store, "search", mock_search)

# ✅ 必须同时 patch 所有 from chroma_store import search 的下游模块
monkeypatch.setattr(chroma_store, "search", mock_search)
monkeypatch.setattr(document_service, "chroma_search", mock_search)
monkeypatch.setattr(ctx_builder, "chroma_search", mock_search)
```

**已知引用链**：`document_service.chroma_search`、`import_service.add_documents`、`package_service.chroma_delete`、`ctx_builder.chroma_search` ← 均来自 `chroma_store`。新增引用模块时跑 `rg "from.*chroma_store" engine/` 检查。

### 9.3 DB_PATH 污染

`database.DB_PATH` 被 12+ 个模块在 import 时复制到自身属性。新增 DB_PATH 持有者 → 必须加入 `conftest.py temp_data_dir` 的 monkeypatch 循环。

### 9.4 Windows + asyncio 限制

- pytest-timeout 在 Windows + asyncio 下无效（不支持 signal）→ 使用 marker 分级跳过，不依赖 timeout 硬杀
- venv 路径污染：`uv run` 可能指向父项目的 `.venv`，安装新依赖后确认 `uv sync` 同步到 cwd
- 异步 generator mock 不能直接用 `returns/rejects`，需实现 `__aiter__/__anext__`（MockProvider 已完整实现）

### 9.5 Fixture 经验值

- `temp_data_dir` 创建临时目录 + 初始化 SQLite（`asyncio.run(init_db())`）→ 仅 API 集成测试需要
- autouse `_test_env`：仅关停外部服务（零耗时），不放 `init_db`（157 次调用 = 大量时间）
- 新增 fixture 自问：依赖 temp_data_dir？需要 event loop？重建 > .5s → `scope="module"`
