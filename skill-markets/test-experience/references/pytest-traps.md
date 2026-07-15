# Pytest 陷阱速查

> 来源: 多轮 agent 并行开发中反复踩坑的真实教训。
> 技术栈: pytest + asyncio/anyio + uv + conftest autouse fixtures

---

## §1 环境就绪决策树

```
需要运行测试？
  ├── 新增了依赖？ → 先 uv sync，确认 .venv 已更新
  ├── 需要数据库/外部服务？ → 检查服务是否运行中
  ├── 涉及真实 LLM 调用？ → 必须被 autouse mock 覆盖，否则禁止运行
  └── 环境就绪 → 运行测试
```

---

## §2 外部调用检测

```
新增代码涉及以下任何 → 检查是否被 autouse mock 覆盖：
  - 网络请求（httpx, aiohttp, requests, urllib）
  - LLM API（openai, anthropic, 任何 model provider）
  - 文件系统写入（非临时目录的读写）
  - 子进程调用（subprocess, asyncio.create_subprocess_exec）

覆盖规则：
  ├── autouse fixture 已 mock → 安全，测试不会触发真实调用
  ├── 无 autouse 覆盖 → 新增 mock fixture 或扩展现有 autouse
  └── 不确定 → grep 调用链，追踪到最外层
```

---

## §3 Import-time 常量陷阱

```
模块定义了 import-time 计算的常量（如路径、配置值）？
  ├── grep 所有引用该常量的下游模块
  ├── 确认需要测试不同常量值的场景
  └── 需要变化 → conftest monkeypatch 循环中加入
       策略: autouse fixture 在 import 前设置环境变量/配置
       注意: 已 import 的模块不会重新执行 import-time 逻辑
```

---

## §4 Fixture 选择决策树

```
需要新增 fixture？
  ├── 需要数据库？ → 显式声明依赖 DB fixture
  ├── 不需要数据库 → 不声明 DB fixture，保持纯函数速度
  ├── 每个测试都需要的环境初始化（零耗时） → autouse=True
  ├── 每个测试都需要但有开销的初始化 → 评估是否可以 autouse
  │     ├── 开销 < 0.1s → 可以 autouse
  │     └── 开销 > 0.1s → 不 autouse，显式声明
  ├── 重建成本 > 0.5s 且无状态修改 → scope="module"
  └── 严重依赖数据库初始化 → 必须声明 DB fixture
```

---

## §5 Autouse Fixture 纪律

```
autouse fixture 内容规则：
  ├── ✅ 允许：重置单例（_instance = None）
  ├── ✅ 允许：清除环境变量副作用
  ├── ✅ 允许：设置 ContextVar 默认值（零耗时）
  ├── ✅ 允许：Mock 外部服务（零网络调用）
  ├── ❌ 禁止：数据库初始化（init_db / create_tables）
  ├── ❌ 禁止：文件 I/O（读配置、写日志）
  └── ❌ 禁止：网络请求（健康检查、服务发现）
```

---

## §6 Marker 决策树

```
这个测试是否需要特殊 marker？
  ├── 涉及真实网络调用（LLM API / MCP / HTTP 外部服务） → @pytest.mark.slow
  ├── 需要跳过 autouse user context → @pytest.mark.no_auto_user
  ├── 需要允许阻塞 IO（在 blocking_io/ 子目录下） → @pytest.mark.allow_blocking_io
  ├── 纯函数 / Pydantic 模型 / 纯逻辑 → 不加 marker
  └── Mock 了 LLM 但走了完整管线 → 不加 slow（autouse 已降级）
```

### 运行策略

本地: `uv run pytest -m "not slow"` | CI 全量: `uv run pytest` | 仅单元: `uv run pytest -m "not slow" tests/unit/`

---

## §7 测试编写自检清单

```
[ ] 真实网络请求？ → grep openai/anthropic/httpx/aiohttp/requests
[ ] 需要数据库？ → 显式声明 DB fixture；不需要 → 不声明
[ ] from X import Y 引用？ → grep 检查所有下游 mock 覆盖
[ ] 单例/工厂？ → autouse fixture 中加入重置逻辑
[ ] 耗时 > 1s？ → 检查是否意外调用真实 LLM/外部服务
[ ] import-time 常量？ → 确认 conftest monkeypatch 已覆盖
[ ] 异步 + Windows？ → 确认不依赖 signal-based timeout
[ ] autouse fixture？ → 确认内容符合 §5 纪律
[ ] 测试顺序依赖？ → 确认单例/全局状态已重置
```

---

## §8 异步超时规避（Windows 特有）

Windows + asyncio → 不要依赖 pytest-timeout 硬杀。需要超时 → 用 asyncio.wait_for() 在代码层控制。全局超时 → marker 分级跳过，不依赖 signal-based timeout。
