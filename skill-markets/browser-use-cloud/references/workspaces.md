# Workspaces & Files — 文件管理

Workspace 为 agent 提供持久文件存储。两种核心模式：

1. **你上传文件 → agent 读取**
2. **Agent 创建文件 → 你下载**

## 上传文件

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()
workspace = await client.workspaces.create(name="my-workspace")

# 上传单个文件
await client.workspaces.upload(workspace.id, "people.csv")

# 上传多个文件
await client.workspaces.upload(workspace.id, "data.csv", "config.json", "image.png")

# Agent 读取文件
result = await client.run(
    "Read people.csv and tell me who works at Google",
    workspace_id=workspace.id,
)
print(result.output)
```

```typescript
import { BrowserUse } from "browser-use-sdk/v3";

const client = new BrowserUse();
const workspace = await client.workspaces.create({ name: "my-workspace" });

// 上传
await client.workspaces.upload(workspace.id, "people.csv");

// Agent 使用
const result = await client.run(
  "Read people.csv and tell me who works at Google",
  { workspaceId: workspace.id },
);
console.log(result.output);
```

## Agent 创建文件

Agent 在 workspace 中创建的文件通过 session messages 获取：

```python
client = AsyncBrowserUse()
workspace = await client.workspaces.create(name="reports")

result = await client.run(
    "Generate a sales report PDF from the data in data.csv",
    workspace_id=workspace.id,
)

# 列出 workspace 中的文件
files = await client.workspaces.files(workspace.id)
for f in files:
    print(f.name, f.size)
```

## Workspace 管理

```python
# 列出所有 workspace
workspaces = await client.workspaces.list()

# 获取单个 workspace 信息
ws = await client.workspaces.get(workspace.id)

# 删除 workspace
await client.workspaces.delete(workspace.id)
```

## 使用场景

| 场景 | 示例 |
|------|------|
| 数据分析 | 上传 CSV → agent 分析 → 生成图表 |
| 表单批量填充 | 上传 Excel → agent 逐行填写网页表单 |
| 文档处理 | 上传 PDF → agent 提取关键信息 |
| 报告生成 | Agent 抓取数据 → 生成报告文件 |
| 图片处理 | 上传截图 → agent 识别内容 |
