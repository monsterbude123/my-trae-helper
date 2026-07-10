---
name: comfyui-api
description: 连接运行中的 ComfyUI 实例、提交工作流、监听执行、获取结果。支持在线（REST 接口）和离线（JSON 导出）两种模式。用于执行 ComfyUI 工作流或查看服务状态时调用。
user-invocable: true
metadata: {"openclaw":{"emoji":"🔌","os":["darwin","linux","win32"],"requires":{"anyBins":["curl","wget"]},"primaryEnv":"COMFYUI_URL"}}
---

# ComfyUI 接口技能

通过 ComfyUI 的 REST 接口执行工作流、监听进度、获取结果。

## 配置

所有可调参数集中在 `.env`，完整说明见 [`foundation/配置.md`](../../foundation/配置.md)。

| 参数 | 占位符 | 默认 |
|------|--------|------|
| 服务地址 | `{{COMFYUI_URL}}` | `http://127.0.0.1:8188` |
| 接口超时 | `{{COMFYUI_API_TIMEOUT}}` | `30` 秒 |
| 轮询间隔 | `{{COMFYUI_POLL_INTERVAL}}` | `5` 秒 |
| 轮询总超时 | `{{COMFYUI_POLL_TIMEOUT}}` | `600` 秒 |
| 客户端 ID | `{{COMFYUI_CLIENT_ID}}` | `comfyui-api-skills` |

## 两种模式

### 在线模式（ComfyUI 正在运行）

完整接口访问。交互式工作首选。

1. **测试连接**：`GET {{COMFYUI_URL}}/system_stats`
2. **探查能力**：使用 `comfyui-inventory` 技能
3. **提交工作流**：`POST {{COMFYUI_URL}}/prompt`
4. **轮询结果**：`GET {{COMFYUI_URL}}/history/{prompt_id}`，每 `{{COMFYUI_POLL_INTERVAL}}` 秒一次
5. **取回输出**：`GET {{COMFYUI_URL}}/view?filename=...`

### 离线模式（无服务）

导出工作流 JSON 供用户在 ComfyUI 中手动加载。

1. 按 ComfyUI 格式生成工作流 JSON
2. 存到 `projects/{项目}/workflows/{名称}.json`
3. 指导用户拖入 ComfyUI

## 接口操作

> 以下示例使用占位符 `{{COMFYUI_URL}}`；执行时替换为 `.env` 中的实际值。

### 查看服务状态

```bash
curl {{COMFYUI_URL}}/system_stats
```

**响应字段**：
- `system.os`：操作系统
- `system.comfyui_version`：版本字符串
- `devices[0].name`：GPU 名称
- `devices[0].vram_total`：总显存（字节）
- `devices[0].vram_free`：剩余显存（字节）

### 提交工作流

```bash
curl -X POST {{COMFYUI_URL}}/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": WORKFLOW_JSON, "client_id": "{{COMFYUI_CLIENT_ID}}"}'
```

**WORKFLOW_JSON 格式**：

```json
{
  "1": {
    "class_type": "LoadCheckpoint",
    "inputs": { "ckpt_name": "flux1-dev.safetensors" }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "photorealistic portrait...",
      "clip": ["1", 1]
    }
  }
}
```

- 节点用字符串 ID 索引
- 输入引用上游节点：`["{节点 ID}", {输出下标}]`

**响应**：

```json
{"prompt_id": "abc-123-def", "number": 1}
```

### 轮询完成情况

```bash
curl {{COMFYUI_URL}}/history/abc-123-def
```

- **未完成**：返回 `{}`（空对象）
- **已完成**：返回含 outputs 的执行数据：

```json
{
  "abc-123-def": {
    "outputs": {
      "9": {
        "images": [{"filename": "ComfyUI_00001.png", "subfolder": "", "type": "output"}]
      }
    },
    "status": {"completed": true}
  }
}
```

### 取回输出图像

```bash
curl "{{COMFYUI_URL}}/view?filename=ComfyUI_00001.png&subfolder=&type=output" -o output.png
```

### 上传参考图

```bash
curl -X POST {{COMFYUI_URL}}/upload/image \
  -F "image=@reference.png" \
  -F "subfolder=input" \
  -F "type=input"
```

### 中断当前生成

```bash
curl -X POST {{COMFYUI_URL}}/interrupt
```

### 释放显存

```bash
curl -X POST {{COMFYUI_URL}}/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true}'
```

## 轮询策略

ComfyUI 在 CLI 场景不支持 WebSocket。使用 REST 轮询：

1. 通过 `POST {{COMFYUI_URL}}/prompt` 提交工作流 → 得到 `prompt_id`
2. 每 `{{COMFYUI_POLL_INTERVAL}}` 秒轮询一次 `GET {{COMFYUI_URL}}/history/{prompt_id}`
3. 响应为空：生成中，继续轮询
4. 响应非空：检查 `status.completed`
5. `completed: true` → 提取 outputs
6. status 含错误 → 转交 `comfyui-troubleshooter`

**超时**：轮询超过 `{{COMFYUI_POLL_TIMEOUT}}` 秒时提醒用户。视频生成（Wan 14B）可能需 15-30 分钟。

## 工作流校验

提交任何工作流前：

1. 读取 `state/inventory.json`（通过 `comfyui-inventory`）
2. 对每个节点：确认 `class_type` 已在已装节点中
3. 对每个模型引用：确认文件在已装模型中
4. 标记缺失项：
   - 节点：建议用 ComfyUI-Manager 安装
   - 模型：提供 `references/模型清单.md` 中的下载链接
   - 版本不匹配：建议更新

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| 连接被拒 | ComfyUI 未运行 | 切离线模式，保存 JSON |
| 400 错误请求 | 工作流 JSON 非法 | 校验节点连线 |
| 500 内部错误 | ComfyUI 崩溃 | 建议重启并查日志 |
| 超时（无响应） | 服务过载 | 等待后重试一次 |

## 参考

- 完整接口表：[`foundation/接口速查.md`](../../foundation/接口速查.md)
- 环境变量与占位符：[`foundation/配置.md`](../../foundation/配置.md)
