# 沙箱安全机制 (Sandbox)

## 支持操作系统

| 系统 | 实现 |
|------|------|
| macOS | sandbox-exec 工具，自动配置 |
| Windows | 原生 + Remote WSL 2 |
| Linux | Debian 10+/Ubuntu 20.04+ (Remote SSH + Bubblewrap) |

## 文件访问控制

| 权限 | 目录 |
|------|------|
| 只读 | `.vscode`、根目录 `/`（默认所有未声明可写的目录） |
| 读写 | 项目目录（除 `.trae`、`.vscode`、`.git` 外）、临时目录、缓存目录、工具依赖目录、语言工具链目录 |

读写权限继承当前用户权限；读写与只读冲突时以只读为准。

## 启用沙箱

设置 → 对话流 → 自动运行命令 → **沙箱运行（支持白名单）** → 配置白名单命令前缀。

## sandbox.json 自定义配置

路径：`~/.trae/sandbox.json`（Win: `%USERPROFILE%\.trae\sandbox.json`）

创建：设置 → 对话流 → 沙箱自定义配置 → 打开配置

```json
{
  "filesystem": {
    "readWrite": [],
    "readOnly": []
  },
  "network": {
    "default": "allow",
    "allow": [],
    "deny": []
  }
}
```

### 文件配置
支持路径格式：绝对路径、`~`、`$VAR`、`$WORKSPACE_FOLDER`。优先级：更长路径 > 更短路径；readOnly > readWrite。

### 网络配置（仅 Windows）
`default`: allow/deny。`allow`/`deny`: 支持 `[ip]`、`[ip/mask]`、`[ip]:port`、`domain`、`domain:port`、`*.domain` 格式。

## 命令运行策略

| 命令类型 | 行为 |
|----------|------|
| 白名单内 | 自动沙箱外运行 |
| 白名单外 | 沙箱内运行，失败询问是否沙箱外重试 |
| 高风险（如 `rm -rf`） | 系统拦截：跳过 / 添加白名单 / 本次沙箱内运行 |
