# Anti-patterns — Stage 4.5 Rot Scan 反例库

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 跳过 rot-scan 直接 Accept | [01-skip-rot-scan.md](01-skip-rot-scan.md) |
| 2 | 扫完不改（fix-list.json 空）| [02-fix-list-empty.md](02-fix-list-empty.md) |
| 3 | rot-detector 自身腐烂未检测 | [03-rot-detector-rotten.md](03-rot-detector-rotten.md) |

## 反例自检清单（rot-detector-agent 必走）

```yaml
rot_scan_self_check:
  - [ ] Stage 4 Review PASS 后必跑 proactive-scan.py 10 项？(反例 1)
  - [ ] fix-list.json 含 type/severity/fix_action 且非空？(反例 2)
  - [ ] self-diagnose.py 30 天内跑过？(反例 3)
  - [ ] rot-detector 自身规则版本对齐？(反例 3)
  - [ ] Stage 5 Accept 前置 rot-scan PASS 验证？(反例 1)
```

## reset_history 适用边界

> rot-scan **不写状态卡字段**（产物路径 `docs/reports/` 而非 `docs/specs/`），不在 `reset_history` 字段记录范围。`force-reset-protocol §7.2` 删除清单中的 `rot-scan-*.md` 是反向操作（force-reset 删除 rot-scan 产物），不是 rot-scan 自身写 reset_history。
> 类比：rot-scan 是质疑工具（被下游 Stage 5 Accept 验证），不是被质疑对象。
