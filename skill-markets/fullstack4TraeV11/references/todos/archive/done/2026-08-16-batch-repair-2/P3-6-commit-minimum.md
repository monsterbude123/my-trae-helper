# P3-6(2026-08-16 抽出独立 → 2026-08-16 batch-repair-2 物理归档)

> 本条目从 P3-cross-skill-and-doc.md 抽出独立。原 P0-P1-P2-P3 13 条已 done,2026-08-16 物理归档至 [archive/done/2026-08-16-batch-repair/](archive/done/2026-08-16-batch-repair/P3-cross-skill-and-doc.md)。
>
> **本文件归档原因**:status 已 done(2026-08-16 本会话执行 commit-minimum-check.py + test_encoding_windows.py + 9 用例全 PASS),物理归档至本目录。

---

## P3-6 — §3.7 #10 范围盲目扩大反例无程序化检测 + Windows PYTHONIOENCODING 兜底

```yaml
---
id: AUDIT-#13
title: scripts/commit-minimum-check.py 实现 commit 准入最小集 + Windows cp1252 兜底
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B + 主上下文补完
protocol_ref: SKILL.md L508 §3.7 #10 commit 准入最小集 ≠ 全量验收
              references/common-anti-patterns.md §7.3
              references/common-anti-patterns.md §7.4 修一点跑一次反模式
parser_ref: grep `commit.*准入最小集|MINIMUM_COMMIT_CRITERIA` 在 scripts/ 中零命中
fix_path: scripts/commit-minimum-check.py 新建 + 测试兜底
resolved_at: 2026-08-16T22:11
resolved_by: V11 子代理 + 主上下文兜底验证(2026-08-16)
evidence:
  - scripts/commit-minimum-check.py 新建(21066 字节,4 项准入最小集校验 + Windows PYTHONIOENCODING=utf-8 L0 兜底)
  - tests/unit/test_commit_minimum_check.py 新建(14604 字节,16 用例 PASS in 11.80s)
  - tests/unit/test_encoding_windows.py 新建(3 用例 PASS,固化 win32 cp1252 兜底行为)
  - references/stage-skill-agent-protocol.md §2 Step 1 [FORBIDDEN] 范例补 6 个全局配置文件(playwright.config.ts/vitest.config.ts/acceptance_manifest.yaml/.trae/fullstack4traev11.config.yaml/.trae/hooks.json/.trae/registry/*.yaml)
  - 主上下文兜底:
      * clean run → JSON 输出 PASS + 4 checks
      * 故意造语法错 → typecheck FAIL exit 1
      * pytest tests/unit/test_commit_minimum_check.py tests/unit/test_encoding_windows.py → 19 passed in 13.36s
      * python scripts/commit-minimum-check.py --help → 含中文输出不崩(win32 兜底生效)
---
```

§3.7 #10 反例只在 md 描述,scripts/ 无任何程序化检测(主上下文自觉)。本批次落地。

修复:scripts/commit-minimum-check.py 实现 4 项准入校验——

1. **typecheck 0 错**: `python -m compileall -q scripts/`(Python 等价于 tsc --noEmit)
2. **关键 5 路由 spot-check**: 探测 `docs/specs/changes/{id}/spot-check.json`(允许项目自定义)
3. **admin 探针 200**: 解析 `.trae/fullstack4traev11.config.yaml` 的 `gate.base_url` + 环境变量 `V11_BASE_URL`,curl --max-time 5 {base}/health
4. **lint 预存**: `python -m pyflakes scripts/`,每文件前 5 warning 写 `.trae/logs/commit-readiness-warnings.jsonl`(非阻塞)
5. **Windows PYTHONIOENCODING=utf-8 L0 兜底**: Python 3.13 win32 默认 cp1252 + 强制 `os.environ["PYTHONIOENCODING"]="utf-8"` + `sys.stdout.reconfigure(encoding="utf-8")`,`print(f"...中文...")` 必崩 UnicodeEncodeError 反例固化

Stage 3.5/4.5 默认异步由本脚本显式声明(commit 准入 ≠ 全量验收)。

---

## 反向提示词(蒸馏)

```yaml
NEVER: 假设 V11 主仓 commit 不需要 typecheck
触发条件: 任何 V11 / 项目侧 commit 前
错误代价: 语法错 commit 进 L1,修复成本翻倍
正确替代: 必跑 commit-minimum-check.py(typecheck + spot-check + admin 探针 + lint 预存)

NEVER: Python 脚本在 Windows console print 中文假设自动 utf-8
触发条件: 任何 V11 / 项目侧 Python 脚本启动
错误代价: print 触发 UnicodeEncodeError → traceback 跌出 → 工具失败无人发现
正确替代: L0 import 阶段强制 PYTHONIOENCODING=utf-8 + sys.stdout.reconfigure(参考 commit-minimum-check.py)
```

---

## 关联引用

- 完成 commit `eed9381`(2026-08-16)"V11.8.5.P1 — §3.7 #10 commit 准入最小集程序化"
- 前置 commit `45d810f` "references/todos/ 13 done 物理归档" — 本条独立抽出
- 前置 commit `39d4f78` "V11.8.x 协议层承诺 → 脚本落地(13/14 done + 1 留置)" — 本条即"1 留置"
- 本文件归档至 [archive/done/2026-08-16-batch-repair-2/](./P3-6-commit-minimum.md)(本批次 commit 后)