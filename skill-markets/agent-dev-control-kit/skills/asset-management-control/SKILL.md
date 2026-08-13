---
name: asset-management-control
description: 资产管理控制技能。规范大文件、二进制、媒体资产生命周期（上传、去重、引用追踪、清理），防止磁盘爆炸与重复资产。当用户提到"资产管理"、"asset"、"大文件上传"、"媒体资源"、"二进制资源"、"asset management"、"dedupe"时主动加载。
version: 1.0.0
requires:
  skills: [execution-control]
  optional: [data-change-control]
---

# Asset Management Control

## 触发词

- 资产管理 / 资产控制 / asset management / 大文件 / 二进制资源 / 媒体资源 / 重复资产 / asset dedupe

## 功能说明

资产管理控制技能为不可文本 diff 的资产（二进制、媒体、模型、压缩包）提供标准化的全生命周期管理，覆盖**上传、校验、去重、引用追踪、版本、清理**六大环节。确保资产可溯源、空间可控、不重复、不丢失。

## 适用场景

| 场景 | 典型资产 | 典型风险 |
|------|---------|---------|
| 影视/游戏制作 | 角色图、背景图、音频、模型、粒子 | 磁盘爆炸、命名混乱、版本错位 |
| 模型与训练 | checkpoint、LoRA、数据集 | 重复训练、引用断开 |
| Web 静态资源 | 图片、字体、PDF、视频 | CDN 缓存失效、404 |
| 文档资料 | 大 PDF、zip、ISO | 备份遗漏、引用失效 |

## 输入规范

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `asset_path` | string | 资产源路径 | `./raw/character_v1.png` |
| `asset_type` | string | 资产类型 | `image`, `video`, `audio`, `model`, `binary`, `dataset`, `archive` |
| `operation` | string | 操作 | `upload`, `dedupe`, `link-check`, `cleanup`, `version-bump` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `target` | string | — | 目标位置（OSS/CDN/本地仓库） |
| `hash` | string | — | 已知哈希，跳过重新计算 |
| `force` | boolean | `false` | 强制执行（覆盖已有版本） |
| `retention_days` | integer | `90` | 清理保留天数 |
| `dry_run` | boolean | `false` | 仅报告不执行 |

## 核心流程

```
资产请求 → 类型识别 → 哈希计算 → 查重(本地+远端) → 上传/引用登记 → 版本化 → 引用追踪 → 周期性清理
```

## 5 个关键控制点

### CP-1 类型识别与大小阈值（HIGH）

- 资产类型必须与 `asset_type` 一致（MIME / magic bytes 校验）
- 单文件大小阈值：默认 1MB 以上视为"大资产"，必须走哈希索引
- 拒绝路径穿越：`asset_path` 必须落在白名单目录内

### CP-2 哈希计算与去重（HIGH）

- 算法优先级 `sha256 > sha1 > md5`，统一使用小写 hex
- 大文件（>1GB）使用分块哈希，避免内存溢出
- 命中已有哈希 → 直接复用，不重新上传，节省带宽
- 哈希冲突（极低概率）→ 追加 `content_size + mtime` 二次判定

### CP-3 引用追踪（HIGH）

- 资产上传成功后，必须在 `assets/INDEX.json` 登记：

```json
{
  "asset_id": "ast_8f3a2b",
  "hash": "sha256:8f3a2b...",
  "type": "image",
  "size": 245132,
  "uploaded_at": "2026-08-13T10:30:00Z",
  "uploaded_by": "agent:asset-uploader",
  "references": ["scenes/01/character.json#image", "docs/casting.md"],
  "versions": [
    {"version": "v1", "created_at": "...", "superseded": false}
  ]
}
```

- 引用关系必须在写入/删除文档、配置、场景文件时同步更新
- 删除资产前必须先解除全部引用（reference_count = 0）

### CP-4 备份与版本化（MEDIUM）

- 同一资产支持 `vN` 版本递增，旧版本默认保留 N 天后清理
- 备份位置与生产位置物理隔离（OSS / 独立磁盘分区）
- 关键资产支持跨区域复制（DR）

### CP-5 周期清理（LOW）

- 周期任务：扫描 `last_accessed_at > retention_days` 的资产
- 清理前必须输出待清理清单，进入 pending 状态（7 天宽限期）
- 宽限期内可撤回，逾期自动归档至冷存储
- 清理日志写入 `logs/asset-cleanup-YYYY-MM-DD.log`

## 输出规范

### 成功输出

```json
{
  "status": "success",
  "data": {
    "asset_id": "ast_8f3a2b",
    "operation": "upload",
    "hash": "sha256:8f3a2bc91d...",
    "size": 245132,
    "deduped": false,
    "references": 2,
    "version": "v1",
    "stored_at": "s3://bucket/assets/2026/08/ast_8f3a2b.png"
  },
  "metrics": {
    "duration": "1.2s",
    "hash_time": "180ms",
    "upload_time": "850ms",
    "index_time": "40ms"
  }
}
```

### 去重命中

```json
{
  "status": "success",
  "data": {
    "asset_id": "ast_existing_42",
    "operation": "upload",
    "deduped": true,
    "original_uploaded_at": "2026-07-12T08:21:00Z",
    "bytes_saved": 245132
  }
}
```

### 失败输出

```json
{
  "status": "error",
  "error": {
    "code": "E301",
    "message": "Reference still exists",
    "phase": "cleanup",
    "context": "asset_id=ast_8f3a2b has 3 active references, must unlink first"
  }
}
```

## 验收标准

1. **可溯源**：每个资产有唯一 `asset_id` + `hash` + `uploaded_by`
2. **零重复**：同一内容只存储一份（hash 索引保证）
3. **引用一致**：资产删除前 `reference_count = 0`，否则拒绝
4. **空间可控**：磁盘使用率 < 80%，超阈值告警
5. **清理可逆**：清理进入 pending 状态，宽限期内可恢复
6. **审计完整**：`assets/INDEX.json` 可还原任何资产的完整轨迹

## 错误处理

### 错误分级

| 级别 | 代码前缀 | 处理方式 |
|------|---------|---------|
| CRITICAL | E1xx | 立即终止，资产不可写入 |
| ERROR | E2xx | 终止当前操作，触发补偿 |
| WARNING | E3xx | 记录警告，提交审核后继续 |
| INFO | E4xx | 记录信息，不影响执行 |

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|---------|
| E101 | 路径穿越检测失败 | 检查 `asset_path` 是否在白名单内 |
| E102 | 资产类型不匹配 | MIME 与 `asset_type` 必须一致 |
| E201 | 上传失败 | 检查网络/权限/存储配额 |
| E202 | 索引写入失败 | 检查 `assets/INDEX.json` 锁 |
| E301 | 引用未解除 | 先解引用再清理 |
| E302 | 哈希冲突 | 切换更细粒度判定（size+mtime） |

## 示例用法

### 示例 1：上传角色立绘

```markdown
**用户请求**：上传 character_main.png 到 OSS

**执行过程**：
1. 类型识别：image/png, 245KB → 走哈希索引
2. 哈希计算：sha256:8f3a2bc91d...（180ms）
3. 去重查询：未命中 → 新上传
4. 上传到 s3://bucket/assets/2026/08/ast_8f3a2b.png
5. INDEX.json 登记：references=[scenes/01/character.json#image]
6. 返回结果：asset_id=ast_8f3a2b, version=v1, references=2
```

### 示例 2：去重命中

```markdown
**用户请求**：上传同一份 character_main.png（重复上传）

**执行过程**：
1. 类型识别：image/png, 245KB
2. 哈希计算：sha256:8f3a2bc91d...（180ms）
3. 去重查询：命中 ast_existing_42（2026-07-12 上传）
4. 跳过上传 → bytes_saved=245132
5. 更新 references 字段
6. 返回结果：deduped=true, bytes_saved=245132
```

### 示例 3：清理未引用资产

```markdown
**用户请求**：清理 90 天未引用的资产

**执行过程**：
1. 扫描 INDEX.json：找到 23 个 last_accessed_at > 90d 的资产
2. 校验引用：reference_count 全部 = 0
3. 生成待清理清单 → 进入 pending（7 天宽限期）
4. 写入 logs/asset-cleanup-2026-08-13.log
5. 返回结果：pending_count=23, hard_deleted=0
```

## 示例代码

### Python：资产上传核心逻辑

```python
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

INDEX_PATH = Path("assets/INDEX.json")

def calc_hash(file_path: Path, algo: str = "sha256") -> str:
    """大文件分块哈希，避免内存溢出"""
    h = hashlib.new(algo)
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return f"{algo}:{h.hexdigest()}"

def find_existing(asset_hash: str) -> dict | None:
    """去重查询"""
    if not INDEX_PATH.exists():
        return None
    index = json.loads(INDEX_PATH.read_text())
    return next((a for a in index["assets"] if a["hash"] == asset_hash), None)

def upload_asset(asset_path: str, asset_type: str, references: list[str]) -> dict:
    """受控上传：识别 → 哈希 → 去重 → 上传 → 登记"""
    src = Path(asset_path)

    # CP-1 类型识别
    if not src.is_file():
        return {"status": "error", "error": {"code": "E101", "message": "asset not found"}}

    # CP-2 哈希 + 去重
    h = calc_hash(src)
    existing = find_existing(h)
    if existing:
        existing["references"] = list(set(existing["references"] + references))
        return {"status": "success", "data": {**existing, "deduped": True}}

    # CP-3/4 上传 + 登记（伪代码：实际对接 OSS SDK）
    asset_id = f"ast_{h[7:13]}"
    stored_at = f"s3://bucket/assets/{datetime.now(timezone.utc):%Y/%m}/{asset_id}{src.suffix}"

    entry = {
        "asset_id": asset_id,
        "hash": h,
        "type": asset_type,
        "size": src.stat().st_size,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": "agent:asset-uploader",
        "stored_at": stored_at,
        "references": references,
        "versions": [{"version": "v1", "created_at": datetime.now(timezone.utc).isoformat(), "superseded": False}]
    }

    # 写索引（生产应加文件锁）
    index = json.loads(INDEX_PATH.read_text()) if INDEX_PATH.exists() else {"assets": []}
    index["assets"].append(entry)
    INDEX_PATH.write_text(json.dumps(index, indent=2))

    return {"status": "success", "data": {**entry, "deduped": False}}
```

### Bash：清理任务

```bash
#!/usr/bin/env bash
# cleanup-unused-assets.sh — 清理 N 天未引用的资产
set -euo pipefail

RETENTION_DAYS=${RETENTION_DAYS:-90}
INDEX="assets/INDEX.json"
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

NOW=$(date -u +%s)
PENDING_FILE="$LOG_DIR/asset-cleanup-pending-$(date +%Y%m%d).json"

jq -r --arg now "$NOW" --arg days "$RETENTION_DAYS" \
   '.assets[] | select(.references | length == 0) | select(
       (.uploaded_at | fromdateiso8601) < ($now | tonumber - ($days | tonumber) * 86400)
   ) | .asset_id' "$INDEX" > "$LOG_DIR/asset-cleanup-candidates.txt"

COUNT=$(wc -l < "$LOG_DIR/asset-cleanup-candidates.txt")
echo "[$(date -Iseconds)] pending_cleanup_count=$COUNT retention_days=$RETENTION_DAYS" \
     | tee -a "$LOG_DIR/asset-cleanup-$(date +%Y%m%d).log"
```

## 依赖说明

### 必需依赖

- 对象存储服务（OSS / S3 / MinIO）：用于资产持久化
- 文件哈希库：`hashlib`（Python）/ `crypto`（Node）

### 可选依赖

- CDN：用于加速分发
- 病毒扫描服务：用于上传前检测

## 注意事项

1. 永远不直接 `rm` 资产，必须走 cleanup 流程（pending → grace period → delete）
2. 资产 ID 必须基于哈希生成，避免随机 ID 导致索引膨胀
3. 大文件（>1GB）必须分块哈希，避免 OOM
4. 删除资产前必须验证 `reference_count == 0`
5. 索引文件 `assets/INDEX.json` 必须有文件锁，避免并发写入冲突
6. 跨项目复制要保留原始 `uploaded_by`，避免溯源链断裂

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | 2026-08-13 | 初始版本（补齐 5 大 Execution Skill 之一） |