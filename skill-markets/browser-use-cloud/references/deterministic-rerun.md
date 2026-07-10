# Deterministic Rerun — $0 成本重执行

运行一次全 agent 任务后，用缓存脚本即时重执行——零 LLM 成本，最高便宜 99%。

## 快速开始

用 `@{{双括号}}` 标记可变部分。首次运行全 agent，后续调用使用缓存脚本。

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()
workspace = await client.workspaces.create(name="my-scraper")

# 首次：agent 探索并创建脚本 (~$0.10, ~60s)
result = await client.run(
    "Get the top @{{5}} stories from https://news.ycombinator.com as JSON",
    workspace_id=str(workspace.id),
)

# 第二次：直接用缓存脚本 ($0 LLM, ~5s)
result2 = await client.run(
    "Get the top @{{10}} stories from https://news.ycombinator.com as JSON",
    workspace_id=str(workspace.id),
)
```

## 工作原理

1. 发送含 `@{{brackets}}` 的任务 → 系统提取参数创建模板
2. 模板 hash 生成唯一 ID → 检查 workspace 的 `scripts/` 目录
3. **Cache miss** → 全 agent 运行 → agent 保存独立 Python 脚本
4. **Cache hit** → 直接执行脚本，无 agent，无 LLM

## 自动检测

满足两个条件自动激活：
- 任务包含 `@{{` 和 `}}`
- 提供 `workspace_id`

可手动覆盖：
```python
result = await client.run("...", workspace_id=str(ws.id), cache_script=True)   # 强制启用
result = await client.run("...", workspace_id=str(ws.id), cache_script=False)  # 强制禁用
```

## 示例

### 参数化抓取（批量零成本）

```python
# 首次建立脚本
await client.run(
    "Go to @{{https://intro.co/marketplace}} and get all @{{logistics}} experts as JSON",
    workspace_id=str(workspace.id),
)

# 不同关键词零成本重跑
for keyword in ["CEO", "marketing", "finance"]:
    result = await client.run(
        f"Go to @{{{{https://intro.co/marketplace}}}} and get all @{{{{{keyword}}}}} experts as JSON",
        workspace_id=str(workspace.id),
    )
```

### 无参数缓存

末尾加空 `@{{}}` 表示"缓存这个精确任务"：

```python
result = await client.run(
    "Get the current Bitcoin price from coinmarketcap.com @{{}}",
    workspace_id=str(workspace.id),
)
```

### 检查缓存脚本

```python
files = await client.workspaces.files(workspace.id, prefix="scripts/")
for f in files.files:
    print(f"{f.path} ({f.size} bytes)")

# 下载脚本查看
await client.workspaces.download(workspace.id, "scripts/a7f3b2c1.py", to="./my_script.py")
```

## Auto-healing

缓存脚本因网站改版失败时自动修复（1 次限制）：

| 场景 | 成本 |
|------|------|
| 缓存成功 | $0 |
| 缓存失败 → 自动修复 | ~$0.05–1.00 |
| 修复后仍失败 | 同上（返回 best-effort） |

## 成本对比

| | LLM 成本 | Browser+Proxy | 耗时 |
|---|---|---|---|
| 首次（Agent） | ~$0.05–1.00 | ✓ | ~30-120s |
| 缓存命中 | $0 | ✓ | ~3-10s |
