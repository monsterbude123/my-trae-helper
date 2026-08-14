# 云端运行环境

> 自定义云端运行环境，让云端智能体在隔离环境中执行代码、运行与调试。解决本地环境不一致、资源受限等问题。
> 仅 Code 模式可用。

## 入口

界面左下角 → **头像 → 设置** → **云端运行环境** → **创建**。

## 配置参数

| 参数 | 说明 |
|------|------|
| **环境名称** | 标识和区分不同开发环境 |
| **预装依赖** | 基础镜像 + 预装的语言版本（详见下表） |
| **环境变量** | 普通配置（接口地址、运行模式等）；最多 100 个 |
| **敏感变量** | KMS 加密存储，API 返回仅返回 key 列表；最多 50 个 |
| **运行方式** | 启动命令（如 `npm run dev`） |

### 预装语言与版本（来自官方 `all-in-one` 通用镜像）

| 语言 | 字段 | 支持版本 |
|------|------|----------|
| Python | `python_version` | 3.10 / 3.11 / 3.12 / 3.13 / 3.14 |
| Node.js | `node_version` | 18 / 20 / 22 / 24 |
| Go | `go_version` | 1.22.12 / 1.23.8 / 1.24.3 / 1.25.1 |
| Rust | `rust_version` | 1.83.0 ~ 1.92.0 |
| Java | `java_version` | 11 / 17 / 21 / 22 / 23 / 24 / 25 |
| Ruby | `ruby_version` | 3.2.3 / 3.3.8 / 3.4.4 |
| PHP | `php_version` | 8.2 / 8.3 / 8.4 / 8.5 |
| Swift | `swift_version` | 5.10 / 6.1 / 6.2 |

> 暂不支持用户自定义容器镜像（如 `container_image`）。可通过 `GET /api/v1/environment_configs/supported_versions` 获取最新支持版本。

## 敏感变量 vs 环境变量

| 维度 | 敏感变量 | 环境变量 |
|------|----------|----------|
| 存储 | KMS 加密 | 明文 JSON |
| API 返回 | 仅 key 列表 | 完整 key-value |
| 适用 | API 密钥、数据库密码、访问令牌 | DEBUG 开关、LOG_LEVEL、端口号 |
| 数量上限 | 50 | 100 |

## 运行时配置

| 参数 | 作用 | 限制 |
|------|------|------|
| **install** | 环境启动时执行的命令（安装依赖），阻塞执行 | 命令长度 ≤ 10KB；触发时机：代码 clone 完成后 |
| **start** | 依赖装完后执行的命令（启动项目），后台执行 | 命令长度 ≤ 10KB |
| **terminals** | 与主程序并行的后台任务（数据库、测试监听、日志监控） | 最多 10 个并行终端；每条命令长度 ≤ 4KB |

### 脚本执行顺序

```
环境启动
    ↓
1. install（阻塞等待）
    ↓
2. start（后台运行，不阻塞）
    ↓
3. terminals（并行打开所有）
    ↓
环境就绪
```

> install 失败会阻断后续步骤；start 与 terminals 是长时进程；terminals 并行无顺序。

## 网络策略（仅官方预置白名单）

> 暂不支持用户自定义网络策略。

`network_policy` 固定参数：

| 参数 | 描述 |
|------|------|
| `mode` | 固定 `1`（启用） |
| `allowlist_policy` | 固定 `0`（使用 `common_dependencies` 列表） |
| `common_dependencies` | 字符串数组，可选 `npm` / `pypi` / `maven` / `goproxy` / `rubygems` / `packagist` / `crates` / `docker` / `github` / `gitlab` |

## 完整示例（React + FastAPI 全栈）

```json
{
  "name": "Full Stack Dev Environment",
  "preinstalled_packages": { "python_version": "3.12", "node_version": "20" },
  "runtime_config": {
    "install": "npm install && pip install -r requirements.txt",
    "start": "npm run dev",
    "terminals": [
      { "name": "Backend Server", "command": "uvicorn main:app --reload --port 8000" },
      { "name": "Test Runner", "command": "pytest --watch" }
    ]
  },
  "secrets": { "API_KEY": "...", "DB_PASSWORD": "..." },
  "environment_variables": { "DEBUG": "true", "LOG_LEVEL": "info" },
  "network_policy": { "mode": 1, "allowlist_policy": 0, "common_dependencies": ["npm","pypi","github"] }
}
```

## 使用方式

| 端 | 入口 |
|----|------|
| **网页版** | 对话框右下方直接选择所需自定义云端环境 |
| **桌面版** | 打开 GitHub 拉取的远程项目 → 输入框左下角选 **云端** 模式 → 选择所需环境 |