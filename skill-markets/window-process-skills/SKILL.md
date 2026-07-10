---
name: "window-process-skills"
description: "Windows process and port management toolkit (kill by port/PID/name, query, free port). Invoke when user needs to manage Windows processes, free occupied ports, or perform related Windows system operations."
---

# Window Process Skills

Windows 进程与端口管理工具集。提供常用的 Windows 进程/端口操作命令模板，支持持续扩展。

> 运行环境：PowerShell 7+

## 一、端口管理 (Port)

### 1.1 按端口号 kill 进程

释放被占用的端口（如 8188）。

```powershell
Get-NetTCPConnection -LocalPort <PORT> -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force; Write-Output "Killed PID: $($_.OwningProcess)" }
```

**示例**（释放 8188）：

```powershell
Get-NetTCPConnection -LocalPort 8188 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force; Write-Output "Killed PID: $($_.OwningProcess)" }
```

### 1.2 查询端口占用

```powershell
Get-NetTCPConnection -LocalPort <PORT> -ErrorAction SilentlyContinue | Format-Table -AutoSize
```

### 1.3 查询所有监听端口

```powershell
Get-NetTCPConnection -State Listen | Format-Table LocalAddress,LocalPort,OwningProcess -AutoSize
```

### 1.4 释放端口后验证

```powershell
Get-NetTCPConnection -LocalPort <PORT> -ErrorAction SilentlyContinue | Format-Table -AutoSize; if (-not (Get-NetTCPConnection -LocalPort <PORT> -ErrorAction SilentlyContinue)) { Write-Output "Port <PORT> is now free." }
```

---

## 二、进程管理 (Process)

### 2.1 按 PID kill 进程

```powershell
Stop-Process -Id <PID> -Force
```

### 2.2 按进程名 kill 进程

```powershell
Get-Process -Name <NAME> -ErrorAction SilentlyContinue | Stop-Process -Force; Write-Output "Killed processes named: <NAME>"
```

**示例**（kill 所有 node 进程）：

```powershell
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
```

### 2.3 查询进程（按名称）

```powershell
Get-Process -Name <NAME> -ErrorAction SilentlyContinue | Format-Table Id,ProcessName,Path -AutoSize
```

### 2.4 查询进程（按 PID）

```powershell
Get-Process -Id <PID> -ErrorAction SilentlyContinue | Format-Table Id,ProcessName,Path -AutoSize
```

---

## 三、扩展约定

新增 Windows 进程/端口相关命令时，遵循以下结构：

1. **章节归属**：根据场景归入「端口管理」「进程管理」或新建章节（如「服务管理」「计划任务」）
2. **命令模板**：每个命令一个三级标题，附使用说明 + PowerShell 代码块
3. **示例**：复杂命令补一个真实可运行的示例
4. **参数占位**：使用 `<PORT>` / `<PID>` / `<NAME>` 形式标注需替换的参数
5. **幂等性**：kill 类命令应允许进程不存在（用 `-ErrorAction SilentlyContinue` 抑制报错）
6. **验证**：kill 后建议补一段验证命令，确认资源已释放

---

## 四、常用操作速查

| 需求 | 命令 |
|------|------|
| 释放端口 X | 见 §1.1 |
| 查询端口 X 占用 | 见 §1.2 |
| 查看所有监听 | 见 §1.3 |
| kill PID X | 见 §2.1 |
| kill 所有同名进程 | 见 §2.2 |
| 查找某进程 | 见 §2.3 |
