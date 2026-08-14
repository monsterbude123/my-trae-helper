# agent-dev-control-kit — 测试体系

> 由 my-trae-helper 2026-08-14 会话蒸馏补充。
> 对应反例:`references/traps.md §AP-2 / §AP-3 / §AP-4 / §AP-7`。
> 落实 §11.1 三件套铁律:**写完 Gate/Guard 必须用真反例跑自验收**。

## 一键跑

```bash
# 全部测试(102 用例,~3.6s)
python -m pytest tests

# 仅反例(34 用例,~1.4s,改动 Gate/Guard 后必跑)
python -m pytest tests -m trap -v

# 仅单元(< 50ms/用例,日常开发)
python -m pytest tests/unit -v

# 仅集成(对真 subprocess,~5s/用例)
python -m pytest tests/integration -v
```

## 分层(对应 acceptance-discipline §1 + test-experience §3)

| 层 | 目录 | 路径 | 速度预算 | 内容 |
|----|------|------|---------|------|
| **Unit** | `tests/unit/` | 文件/进程内 | < 50ms/用例,全量 < 2s | 解析器、模板、registry、fixtures |
| **Integration** | `tests/integration/` | 真 subprocess | < 5s/用例,全量 < 5s | 对真脚本跑真反例 — 必须 exit ≠ 0 |
| **Trap** | 任意 + `@pytest.mark.trap` | 任选 | 与所在层一致 | 蒸馏自 `references/traps.md §AP-*` 的固化反例 |

## 必须固化的反例(本会话蒸馏)

| AP | 描述 | 阻断文件 | 测试 |
|----|------|---------|------|
| AP-2 | Gate 静默跳过不存在脚本 | `validate-gate-integrity.check_nodejs` | `TestCheckNodejs::test_v2_echo_skip_script_blocked` |
| AP-3 | Guard 缺 CLI 自执行入口 | 全部 `scripts/*.py` | `test_cli_runs_against_tmp` 等 4 个 |
| AP-4 | Lint 硬编码文件列表 | `registry/*.yaml` 一致性 | `TestScaffoldConsistency` 参数化 |
| AP-7 | Guard 正则覆盖不足 | `is_fake_gate_script` 模式 | `TestIsFakeGateScript::test_fake_hook_flagged` |

## 跑通记录

| 时间 | 用例总数 | trap 数 | 失败 | 备注 |
|------|--------:|-------:|-----:|------|
| 2026-08-14 round 1 | 102 | 34 | 0 | 初始蒸馏版 |
| 2026-08-14 round 2 | 147 | 71 | 0 | + Catalog 守门(catalog / hint / guard / trap-instructions) |
| 2026-08-14 round 3(新增 catalog 5 类) | 147 | 71 | 0 | 5 类"主动给 agent 提示":doc / section / schema / script / cross-ref |

## 新增:Catalog 主动指引机制(M1+M2+M3)

### 痛点对应

| ai-short-studio-monster 触发面 | 本 skill 对应 | 实现位置 |
|---|---|---|
| `route-catalog.ts`(应有什么) | [skill-catalog.yaml](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/tests/catalogs/skill-catalog.yaml) | 声明"应有尽有" |
| 缺文档阻断 | `TestRequiredDocs` | [test_catalog_coverage.py](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/tests/catalogs/test_catalog_coverage.py) |
| 缺 page 元素 | `TestRequiredSections` | 同上 |
| 缺 schema | `TestRequiredSchemaFields` | 同上 |
| `docs-sync-guard.mjs` 阻断 | [catalog-guard.py](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/scripts/catalog-guard.py) | commit 时阻断 |
| `.learnings/ERRORS.md` 沉淀 | [trap-instructions.yaml](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/references/trap-instructions.yaml) | 结构化反例 + fix_template |
| 聚合可读 | [agent-hint-emit.py](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/scripts/agent-hint-emit.py) | 按 trap 分组 |

### 触发场景示例

```bash
# 1. happy-path:现状必通过(clean state)
python scripts/catalog-guard.py
# → ✅ catalog guard passed

# 2. 反例演示:在 catalog 加一个不存在的文档
python -c "
import yaml
p = 'tests/catalogs/skill-catalog.yaml'
d = yaml.safe_load(open(p, encoding='utf-8'))
d['required_docs'].append({'path': 'MISSING.md', 'purpose': 'demo'})
yaml.safe_dump(d, open(p, 'w', encoding='utf-8'), allow_unicode=True)
"
python scripts/catalog-guard.py
# → 1 catalog test fail
# → 🛑 HINT-AP-CAT-001:agent 应当创建 MISSING.md / 在 catalog 移除
# → 🛑 CATALOG GUARD 阻断 commit (banner)

# 3. 聚合当前 hints(配合 pytest -m trap 跑过后的输出)
python scripts/agent-hint-emit.py --group-by trap
```

### 加新反例流程

1. 在 [references/trap-instructions.yaml](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/references/trap-instructions.yaml) 加 AP-N 条目
2. 在 [tests/catalogs/skill-catalog.yaml](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/tests/catalogs/skill-catalog.yaml) 声明触发点
3. 在 [tests/catalogs/test_catalog_coverage.py](file:///d:/workspace/my-trae-helper/skill-markets/agent-dev-control-kit/tests/catalogs/test_catalog_coverage.py) 加 pytest 用例 + `emit_hint(...)`
4. 跑 `python -m pytest tests -m trap -v` 全绿

## 与已有 unittest 套件并存

`scripts/install-husky.test.py` 是 2026 早期基于 `unittest` 的轻量套件,**继续保留**,与 pytest 互补:

```bash
# 跑经典 unittest
python scripts/install-husky.test.py -v
```

两个套件覆盖不同维度,合并跑 ≈ 117 用例。

## 新增反例的流程(对应 §2 反例新增流程)

1. 写出会话中真实发生的踩坑(放 `references/traps.md §AP-N+1`)
2. 在 `tests/unit/` 或 `tests/integration/` 加 `@pytest.mark.trap` 用例固化
3. 跑 `pytest -m trap -v` 全绿
4. 在 SKILL.md §11.3 加引用
