# Anti-patterns — Stage 5 Accept 反例库

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 跳过知识沉淀直接归档 | [01-skip-knowledge-extract.md](01-skip-knowledge-extract.md) |
| 2 | 修改归档文件 | [02-modify-archive.md](02-modify-archive.md) |
| 3 | 删归档目录 | [03-delete-archive.md](03-delete-archive.md) |

## 反例自检清单(archive-agent 必走)

```yaml
archive_agent_checklist:
  knowledge_extract:    # 对应铁律 2 + 反例 1
    - [ ] spec-knowledge-extract.py 已跑(api/domain/events 三类型产出)?
    - [ ] docs/api-endpoints/ + domain-models/ + events/ 非空?
  archive_immutable:    # 对应铁律 1 + 8 + 反例 2/3
    - [ ] spec-purge.py 已跑 → docs/archive/done/{change-id}/ 存在?
    - [ ] 归档文件未修改?（git diff docs/archive/done/ 空输出）
    - [ ] 归档目录未删除?(ls docs/archive/done/ 非空)
  archive_required_artifacts:   # 对应铁律 6
    - [ ] spec.md + plan.md + contracts/(domain-models/api-contracts/events/validation-rules) + review-report.md + rot-scan-{date}.md + verify-report.md 齐全?
  state_card_archived:   # 对应铁律 7
    - [ ] current_stage = "5/accept" + stage_status = "completed" + health = "🟢 on-track"?
```
