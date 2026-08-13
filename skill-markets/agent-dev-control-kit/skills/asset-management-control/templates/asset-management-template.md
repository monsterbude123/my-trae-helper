# 资产管理执行模板

## 资产信息

- **资产路径**: [源文件绝对/相对路径]
- **资产类型**: [image / video / audio / model / binary / dataset / archive]
- **大小**: [bytes / KB / MB / GB]
- **执行人**: [Agent / 人工]
- **预计时间**: [YYYY-MM-DD HH:MM]

## 1. 影响评估

### 风险等级

- [ ] HIGH — 影响生产资产/跨项目引用/无引用追踪
- [ ] MEDIUM — 单项目资产/有明确引用范围
- [ ] LOW — 临时资产/测试样本

### 影响范围

```
引用该资产的文件/场景/文档:
- [引用1]: [引用说明]
- [引用2]: [引用说明]

受影响系统:
- [对象存储 / CDN / 备份系统]
```

## 2. 哈希与去重

```bash
# 计算哈希
sha256sum [asset_path]
# 输出: 8f3a2bc91d...  asset.png

# 查重（命中即跳过上传）
grep "[hash]" assets/INDEX.json
```

| 状态 | 动作 |
|------|------|
| 未命中 | 上传 + 登记 INDEX.json |
| 已命中 | 更新 references，跳过上传 |

## 3. 上传与登记（HIGH/MEDIUM 必须）

### 上传目标

- [ ] OSS / S3 / MinIO: `[bucket]/[path]/[asset_id][ext]`
- [ ] 备份位置: `[dr_bucket]/[path]`

### INDEX.json 登记项

```json
{
  "asset_id": "ast_xxxxxx",
  "hash": "sha256:xxxxx",
  "type": "image",
  "size": 245132,
  "uploaded_at": "2026-08-13T10:30:00Z",
  "uploaded_by": "agent:asset-uploader",
  "stored_at": "s3://bucket/path",
  "references": ["scenes/01/character.json#image"]
}
```

## 4. 引用追踪

| 操作 | 文件 | 引用更新 |
|------|------|---------|
| 新增引用 | [path/to/ref.json] | append references |
| 删除引用 | [path/to/ref.json] | remove from references |
| 验证引用 | grep -r [asset_id] [codebase] | 应有 ≥1 个引用 |

## 5. 执行记录

| 时间 | 操作 | 结果 | 备注 |
|------|------|------|------|
| HH:MM | 计算哈希 | SUCCESS/FAIL | sha256:xxx |
| HH:MM | 去重查询 | HIT/MISS | — |
| HH:MM | 上传存储 | SUCCESS/FAIL | — |
| HH:MM | 登记 INDEX | SUCCESS/FAIL | — |

## 6. 验证结果

- [ ] 哈希计算正确
- [ ] 去重索引已更新
- [ ] 引用关系一致
- [ ] 备份位置已同步（如适用）
- [ ] 资产可正常访问（CDN/OSS）

## 7. 清理预案（如需）

```bash
# 验证引用为 0
jq '.assets[] | select(.asset_id == "ast_xxxxxx") | .references | length' assets/INDEX.json
# 必须为 0

# 进入 pending 状态（7 天宽限期）
echo '{"asset_id":"ast_xxxxxx","pending_at":"YYYY-MM-DD","delete_at":"YYYY-MM-DD+7"}' \
  >> logs/asset-cleanup-pending-YYYY-MM-DD.json

# 宽限期后正式删除（先冷归档再 hard delete）
aws s3 mv s3://bucket/path s3://cold-bucket/path
aws s3 rm s3://bucket/path
```

## 8. 回滚方案

```bash
# 回滚上传：从备份恢复
aws s3 cp s3://backup-bucket/path s3://bucket/path --recursive

# 回滚 INDEX：恢复上一版本
cp assets/INDEX.json.bak assets/INDEX.json
```