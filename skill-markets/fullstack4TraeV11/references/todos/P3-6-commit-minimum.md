# P3-6(2026-08-16 抽出独立)

> 本条目从 P3-cross-skill-and-doc.md 抽出独立。原 P0-P1-P2-P3 13 条已 done,2026-08-16 物理归档至 [archive/done/2026-08-16-batch-repair/](archive/done/2026-08-16-batch-repair/P3-cross-skill-and-doc.md)。
>
> **本文件保留原因**:状态仍为 pending,等后续会话或用户明确要求时再修。

---

## P3-6 — §3.7 #10 范围盲目扩大反例无程序化检测

```yaml
---
id: AUDIT-#13
title: scripts/commit-minimum-check.py 实现 commit 准入最小集
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: SKILL.md L508 §3.7 #10 commit 准入最小集 ≠ 全量验收
              references/common-anti-patterns.md §7.3
parser_ref: grep `commit.*准入最小集|MINIMUM_COMMIT_CRITERIA` 在 scripts/ 中零命中
fix_path: scripts/commit-minimum-check.py 新建
resolved_at: 2026-08-16T
resolved_by: V11 子代理 + 主上下文兜底验证(2026-08-16)
evidence:
  - scripts/commit-minimum-check.py 新建(21066 字节,4 项准入最小集校验)
  - tests/unit/test_commit_minimum_check.py 新建(14604 字节,16 用例 PASS in 11.80s)
  - 主上下文兜底:
      * clean run → JSON 输出 PASS + 4 checks
      * 故意造语法错 → typecheck FAIL exit 1
      * pytest tests/unit/test_commit_minimum_check.py → 16 passed in 11.80s
---
```

§3.7 #10 反例只在 md 描述,scripts/ 无任何程序化检测(主上下文自觉)。本批次落地。

修复:scripts/commit-minimum-check.py 实现 4 项准入校验——

1. **typecheck 0 错**: `python -m compileall -q scripts/`(Python 等价于 tsc --noEmit)
2. **关键 5 路由 spot-check**: 探测 `docs/specs/changes/{id}/spot-check.json`(允许项目自定义)
3. **admin 探针 200**: 解析 `.trae/fullstack4traev11.config.yaml` 的 `gate.base_url` + 环境变量 `V11_BASE_URL`,curl --max-time 5 {base}/health
4. **lint 预存**: `python -m pyflakes scripts/`,每文件前 5 warning 写 `.trae/logs/commit-readiness-warnings.jsonl`(非阻塞)

Stage 3.5/4.5 默认异步由本脚本显式声明(commit 准入 ≠ 全量验收)。

---

## 关联引用

- 完成 commit `<待本次 commit>` "P3-6 commit-minimum-check.py 实现"
- 前置 commit `45d810f` "references/todos/ 13 done 物理归档" — 本条独立抽出
- 前置 commit `39d4f78` "V11.8.x 协议层承诺 → 脚本落地(13/14 done + 1 留置)" — 本条即"1 留置"
- 本文件归档至 [archive/done/2026-08-16-batch-repair-2/](./archive/done/2026-08-16-batch-repair-2/P3-6-commit-minimum.md)(本批次 commit 后)
