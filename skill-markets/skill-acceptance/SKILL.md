---
name: skill-acceptance
version: "0.1.0"
description: Skill 包合规验收门禁 — CI/pre-release 钩子。自动跑 6 项检查（frontmatter 合规 / 安全扫描 / CAPABILITY-MAP 去重 / scripts 边界 / references 体积 / 决策层级标注），任意 1 项 HIGH 阻断，MEDIUM 累计 ≥3 警告。供 skill-markets 任何新装/升级/发布的 skill 准入审查使用。
requires:
  skills: [trae-security-review]
  optional: [agent-dev-control-kit]
triggers:
  - skill 验收
  - skill 准入
  - skill 发布
  - skill audit
  - skill verify
  - skill acceptance
  - skill pre-release
---

# skill-acceptance — Skill 包合规验收门禁

## §0 定位

> **本 skill 是元项目独有**的 L4 pre-release 钩子，**不是**通用验收体系。

| 维度 | acceptance-discipline | trae-security-review | **skill-acceptance（本）** |
|------|----------------------|----------------------|---------------------------|
| 范围 | 通用项目交付（PR/E2E/性能） | Skill 安全风险扫描 | Skill 包元数据合规准入 |
| 触发 | 提 PR / E2E 回归 | 审查可疑代码 | 新装 / 升级 / 发布 Skill |
| 产物 | 测试报告 + 门禁决策 | 安全 findings | 6 维 PASS/WARN/BLOCK 矩阵 |
| 位置 | 全栈流水线阶段 | agents/ 双引擎 | CI/pre-commit 独立钩子 |

**核心命题**：发布任何新 Skill 前必须先经 `verify.py` 自验；CI 上新 PR 引入 `skill-markets/<new>/` 必跑一次 6 项检查。

---

## §1 6 项检查维度清单

| ID | 检查 | 阻断条件（HIGH） | 警告条件（MEDIUM） | 实现位置 |
|----|------|------------------|--------------------|----------|
| `frontmatter` | YAML frontmatter 完整性 | `name` 缺失 / ≠ 目录名 | `version` 缺失 | `verify.py::check_frontmatter` |
| `security` | 危险命令 / 动态执行 / 密钥 | 任意 HIGH finding | 累计 ≥ 3 MEDIUM | `verify.py::check_security` |
| `capability_map` | CAPABILITY-MAP.md 注册 | 未注册且非 `--new-skill` | 注册项缺少能力摘要 | `verify.py::check_capability_map` |
| `scripts_boundary` | scripts/ 子目录纪律 | 脚本 ≥ 150 行 | 脚本散落根目录 | `verify.py::check_scripts_boundary` |
| `references_size` | SKILL.md / references/ 体积 | SKILL.md > 500 行 | references 总和 > 200KB | `verify.py::check_references_size` |
| `decision_layer_tag` | 决策层级标注 | 完全缺失关键词 | 关键词命中 ≤ 1 个 | `verify.py::check_decision_layer_tag` |

详细规范：[references/checks.md](references/checks.md)

---

## §2 触发方式

### 2.1 Husky pre-release（本地）

```bash
# .husky/pre-release
npx -y python D:/workspace/my-trae-helper/skill-markets/skill-acceptance/scripts/verify.py \
    --target D:/workspace/my-trae-helper/skill-markets/$SKILL_NAME \
    --strict || exit 4
```

### 2.2 GitHub Actions（CI）

```yaml
# .github/workflows/skill-acceptance.yml
name: skill-acceptance
on:
  pull_request:
    paths: ['skill-markets/**']
jobs:
  verify:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: run verify.py
        run: |
          python skill-markets/skill-acceptance/scripts/verify.py `
            --target skill-markets/${{ matrix.skill }} `
            --json --report .trae/tmp/report.json
```

---

## §3 调用方式

```bash
python scripts/verify.py --target <skill-path> [OPTIONS]

OPTIONS:
  --target PATH        # 必填，待验收 skill 目录
  --json               # 输出 JSON 格式（脚本自身 stdout）
  --report PATH        # 落盘 JSON 报告（默认不写）
  --fail-on LEVEL      # 触发退出的最低严重度（BLOCK|WARN|PASS），默认 BLOCK
  --strict             # 启用 MEDIUM ≥3 警告阻断（默认关闭）
  --new-skill          # 跳过 CAPABILITY-MAP 注册校验（首次发布用）
  --quiet              # 仅打印汇总表（无进度）
  -h / --help          # 帮助
```

### 3.1 最小用法

```bash
# 验收自己（自验）
python scripts/verify.py --target ../skill-acceptance

# 验收 trae-security-review（自验）
python scripts/verify.py --target ../trae-security-review --json

# 完整报告
python scripts/verify.py --target ../<new-skill> \
    --json --report .trae/tmp/sa-<new-skill>.json --strict
```

---

## §4 退出码矩阵

详细定义：[references/exit-codes.md](references/exit-codes.md)

| Code | 语义 | 触发条件 | CI 建议 |
|:----:|------|----------|---------|
| 0 | PASS | 6 项全过 | ✅ 准入 |
| 2 | WARN | MEDIUM ≥3 或单检查 score<60 | ⚠️ 警告放行 |
| 4 | BLOCK | 任一 HIGH finding | 🛑 阻断 PR |
| 5 | ARG_ERROR | 参数错误 / 路径不存在 | 🔧 修复命令 |
| 6 | INTERNAL_ERROR | verify.py 自身 bug | 🐛 修脚本 |

---

## §5 与现有 skill 的关系

```
依赖：
  trae-security-review  ── 提供 scan_skills_dir.py（security 检查的子调用）
  agent-dev-control-kit ── 可选，提供 stage 标签嵌入（可选优化）

不重复：
  - acceptance-discipline  ── 项目级交付验收，本 skill 是 skill 包准入
  - trae-security-review   ── 单点安全扫描，本 skill 是元数据合规 + 安全打包
```

### 5.1 调用栈

```
verify.py
├── check_security
│   └── subprocess.run("python trae-security-review/scripts/scan_skills_dir.py")
└── check_capability_map
    └── 读取 skill-markets/CAPABILITY-MAP.md（仅读，不改）
```

---

## §6 准入判定

```
总体状态映射：
  任意检查 status=BLOCK  → overall=BLOCK  → exit=4
  否则 累加 MEDIUM ≥3    → overall=WARN   → exit=2
  否则                   → overall=PASS   → exit=0

判定失败处理：
  exit=4 (BLOCK)  → 修复 skill 包后重跑
  exit=2 (WARN)   → 阅读 .trae/tmp/report.json 决定是否放行（--strict 模式下升级为 BLOCK）
  exit=5 (ARG_ERROR) → 检查参数拼写
  exit=6 (INTERNAL_ERROR) → 提交 issue（verify.py 自身崩溃）
```

### 6.1 失败回退

- 单检查 `INTERNAL_ERROR` → 该检查判 BLOCK（不影响其他 5 项）
- JSON 解析失败 → `capability_map` 视为 WARN
- `--target` 路径不存在 → exit=5

### 6.2 报告位置

- 默认：`stdout`（人读）+ 可选 `--report` 落盘
- 落盘约定：`.trae/tmp/sa-<skill-name>-<timestamp>.json`
- 报告 24h 后由 `prepare-publish.mjs` 清理

---

## §7 Gate 自验收协议(V2.2 新增 — 2026-08-14)

> **核心命题**:写完任何 Gate / Guard 脚本后,必须用**真反例**验证其能真阻断,否则 Gate 是"演戏"。

### 7.1 触发场景

写完以下任一脚本后必须执行本协议:

| 触发项 | 验证责任 |
|--------|---------|
| `.husky/pre-commit` / `pre-push` | 故意加违规 commit,验证 exit ≠ 0 |
| `scripts/*-guard.py`(security/structure/capability/dependency)| 造 tmp 违规样本,验证 BLOCK |
| `package.json scripts.lint / test:unit / build` | 删除脚本名,验证 Gate 报错 |
| GitHub Actions workflow | 故意 push 失败,验证 CI 阻断 |
| 新增 `node --check` 文件列表 | 加 TS 语法错误文件,验证发现 |

### 7.2 自验收三态验证

```
PASS  态: 干净样本        → 期望 exit=0
BLOCK 态: 违规样本(反例) → 期望 exit≠0 + 错误信息
边界态: 边界样本(如 .md 单文件 / 空目录 / tmp 名含特殊字符)
```

### 7.3 自验收脚本模板

```python
import subprocess, tempfile
from pathlib import Path

GUARD = Path("scripts/skill-structure-guard.py")

passed = failed = 0

def test(name, fn):
    global passed, failed
    try: fn(); passed += 1
    except AssertionError as e: failed += 1

# ❶ PASS 态
def t_pass_clean():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "SKILL.md").write_text("---\nname: ok\n---\n")
        code, _, _ = run(GUARD, tmp)
        assert code == 0

# ❷ BLOCK 态(反例)
def t_block_bad_name():
    bad = Path(tmpfile) / "BadName_2026"
    bad.mkdir()
    (bad / "SKILL.md").write_text("---\nname: x\n---\n")
    code, out, _ = run(GUARD, bad)
    assert code != 0
    assert "目录名不合规" in out

test("干净技能 → PASS", t_pass_clean)
test("大写目录名 → BLOCK", t_block_bad_name)
```

### 7.4 反例样本库(必跑清单)

写完任何新 Gate 后,**至少跑 3 个反例**:

| Gate 类型 | 必跑反例 |
|----------|---------|
| 安全守卫 | 硬编码 `api_key = "sk-..."` / 硬编码 `password = "..."` |
| 结构守卫 | 缺 YAML frontmatter / 铁律 > 10 条 / 目录名大写 |
| 能力守卫 | 与已注册脚本 basename 重复 / 不存在的脚本名参数 |
| 依赖守卫 | 不存在的技能名 / 缺硬依赖 |
| Lint | TS 类型注解混入 JS / 未声明导出 |
| Build | 缺 bin/cli.mjs / package.json 缺 scripts |

### 7.5 失败处理

```
Gate 自验收失败时:
  1. 不能直接修 Gate,先识别失败模式:
     ├─ "反例未被检测"  → Guard 缺检查项(本会话 capability guard bug)
     ├─ "exit code 错"   → main 块未触发(本会话 dependency guard bug)
     ├─ "脚本静默跳过"  → if grep -q 包住 npm run(本会话 pre-commit bug)
     └─ "硬编码文件列表" → lint 未 glob 扫描(本会话 lint bug)
  2. 修复后重跑全部反例,直到 100% 通过
  3. 把反例样本固化进 tests/unit/test_*.py(不能跑一次就丢)
```

### 7.6 已固化的反例样本

本项目已落地(参考,不复制):

- `tests/unit/test_skill_acceptance.py` — 13 用例(4 守卫 × 多反例)
- `tests/unit/test_structure_guard.py` — 4 用例
- `tests/unit/test_security_guard.py` — 4 用例

详见 [references/gate-self-check.md](references/gate-self-check.md)

---

## §8 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.0 | 2026-08-XX | 初始版本:6 项检查 + verify.py |
| 0.2.0 | 2026-08-14 | **新增 §7 Gate 自验收协议**(本会话蒸馏) |