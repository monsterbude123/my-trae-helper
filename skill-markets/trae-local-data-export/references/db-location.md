# Trae 数据库定位

> 跨平台查找 `ModularData/ai-agent/database.db` 的指南。

---

## §1 标准路径

| 平台 | 路径 | 备注 |
|------|------|------|
| **Windows** | `%APPDATA%\Trae CN\ModularData\ai-agent\database.db` | `APPDATA = C:\Users\<USER>\AppData\Roaming` |
| **macOS** | `~/Library/Application Support/Trae CN/ModularData/ai-agent/database.db` | — |
| **Linux** | `~/.config/Trae CN/ModularData/ai-agent/database.db` | XDG 规范 |

> Trae 还有"Trae"（不带 CN）的实验版，路径中 Trae 字符串可能不同——以实际安装目录名为准。

---

## §2 自动发现脚本

### 2.1 Windows（PowerShell）

```powershell
$base = $env:APPDATA
$patterns = @("Trae CN", "Trae", "trae", ".trae")
foreach ($p in $patterns) {
    $db = Join-Path $base $p "ModularData\ai-agent\database.db"
    if (Test-Path $db) { Write-Output "FOUND: $db"; break }
}
```

### 2.2 macOS / Linux（Python）

```python
from pathlib import Path
import platform, os

def find_trae_dbs():
    home = Path.home()
    if platform.system() == "Darwin":
        bases = [home / "Library/Application Support"]
    elif platform.system() == "Windows":
        bases = [Path(os.environ.get("APPDATA", home / "AppData/Roaming"))]
    else:
        bases = [home / ".config", home / ".local/share"]

    found = []
    for base in bases:
        for pattern in ["Trae CN", "Trae", "trae", ".trae"]:
            dbs = list((base / pattern).rglob("ModularData/ai-agent/database.db"))
            found.extend(dbs)
    return found
```

---

## §3 验证文件存在

```python
import os
db = ".../ModularData/ai-agent/database.db"
print(f"size: {os.path.getsize(db) / 1024 / 1024:.1f} MB")
# 期望: 200MB ~ 600MB（取决于聊天量）
# 警告: < 50MB → 几乎无聊天；> 2GB → 异常
```

---

## §4 常见陷阱

| 陷阱 | 现象 | 解决 |
|------|------|------|
| 多版本并存 | `Trae CN` + `Trae` 都存在 | 用最新 + 容量最大的 |
| WAL/SHM 旁路 | `database.db-wal` / `database.db-shm` 未读 | 关闭 Trae 后再读，否则读到旧快照 |
| OneDrive 重定向 | 路径在 OneDrive 而非 APPDATA | 用 `dir %APPDATA%` 反查真实位置 |
| 容器化 | WSL2 / Docker 内运行 Trae | 进容器内查 `/root/.config/...` |

---

## §5 不在标准位置时的深度搜索

```powershell
# Windows: 5 分钟内全盘找
Get-ChildItem -Path C:\ -Recurse -Filter "database.db" -ErrorAction SilentlyContinue -Depth 8 |
    Where-Object { $_.FullName -like "*ModularData*ai-agent*" }
```

```python
# macOS / Linux: 5 分钟超时
import subprocess
subprocess.run(
    ["find", str(Path.home()), "-name", "database.db",
     "-path", "*ModularData*", "-not", "-path", "*/node_modules/*"],
    timeout=300
)
```

> 命中后必须排除以下误报：① 临时解压的副本 ② git lfs 缓存 ③ Docker volume 挂载
