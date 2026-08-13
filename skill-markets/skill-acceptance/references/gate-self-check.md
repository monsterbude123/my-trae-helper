# Gate 自验收 — 反例库与失败模式诊断

> **核心命题**:"看起来通过" ≠ "真通过"。任何 Gate / Guard 脚本写完必须用真反例跑一次,确认能真阻断。

---

## §0 为什么需要 Gate 自验收?

```
常见错误路径:
  1. 写完 pre-commit → 自评"对" → 提交 → 用户发现 Gate 假通过
  2. 写完 lint → 加白名单 → 提交 → 漏掉了新文件类型
  3. 写完 guard → 跑干净样本 → 提交 → 但反例根本未被检测

后果:Gate 名义上存在,实际失效,所有提交"看起来通过"
     直到生产事故或用户手动验证才暴露
```

---

## §1 Gate 自验收 5 大反例

### R-1: Gate 静默跳过不存在脚本(本会话真实发生)

```
触发场景:
  pre-commit 写了 if grep -q '"lint"' package.json; then npm run lint; fi
  package.json 实际没 lint 脚本

失败路径:
  grep 返回 false → 进入 if 块的 else 分支 → 什么都不做 → exit 0
  → "L1 Commit Gate 通过" 假象

正确写法:
  if ! grep -q '"lint"' package.json; then
    echo "❌ Gate 配置错误: package.json 缺少 lint 脚本"
    exit 1
  fi
  npm run lint

自验收反例:
  1. 删除 package.json 的 lint 脚本
  2. git commit --allow-empty
  3. 期望: Gate 在 lint 阶段 exit 1 并打印 "缺少 lint 脚本"
  4. 恢复 lint 脚本
```

### R-2: Guard 缺 CLI 自执行入口(本会话真实发生)

```
触发场景:
  skill-dependency-guard.mjs 只有 `export async function runDependencyGuard`
  没有 `if (import.meta.url === ...)` main 块

失败路径:
  node src/guards/skill-dependency-guard.mjs never-existed-zzz
  → 仅加载模块,什么都不做 → exit 0

正确写法:
  // CLI 自执行入口
  const isMain = import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`;
  if (isMain) {
    runDependencyGuard(process.argv.slice(2));
  }

自验收反例:
  1. node src/guards/skill-dependency-guard.mjs never-existed-zzz
  2. 期望: 输出 JSON + 报错 + exit 1
  3. 如果 exit 0 → 立即补 main 块
```

### R-3: Guard 正则覆盖不足(本会话真实发生)

```
触发场景:
  capability guard 用 `r'scripts/([^`]+)'` 提取 CAPABILITY-MAP.md 中的脚本
  只能匹配 `scripts/xxx.py`,漏掉 `vision-audit/scripts/vision-audit.mjs`

失败路径:
  测试用例 `重复 vision-audit.mjs` → guard 通过(假)
  → 实际生产中 vision-audit.mjs 重复 → 不被检测

正确写法:
  re.findall(r'`([^`]*\.(?:py|mjs|sh|ps1))`', content)
  改为通用路径正则,返回 (完整路径列表, basename 列表) 二元组

自验收反例:
  1. 在 tmp 目录建 scripts/vision-audit.mjs
  2. 跑 guard
  3. 期望: BLOCK + "已存在于共享能力注册表"
```

### R-4: Lint 硬编码文件列表(本会话真实发生)

```
触发场景:
  package.json scripts.lint 写 `node --check bin/cli.mjs && node --check src/add.mjs ...`
  列出 15 个固定文件

失败路径:
  新加 src/foo.mjs 不会触发 lint → 含 TS 语法错误也不被发现

正确写法:
  改为 scripts/lint.mjs:
    walk(root, exclude={node_modules,skill-markets,example,docs,logs,tests,...})
    for file: node --check

自验收反例:
  1. 写 src/_lint_break.mjs 含 `const x: number = ...`
  2. git add src/_lint_break.mjs && git commit -m "test"
  3. 期望: lint 阶段 exit 1 报 TS 语法错
  4. rm src/_lint_break.mjs
```

### R-5: 一次性 commit 巨大违反最小变更

```
触发场景:
  本会话某次 commit 含 172 个文件 / 25051 insertions

失败路径:
  - 一个 commit 跨多个关注点 → 难以 revert
  - Gate 只对最新 commit 校验,前面 commit 没 Gate 保护
  - code review 范围爆炸

正确做法:
  - 按"change ↔ feature 分支 1:1"切分
  - 单 commit < 50 文件 / < 1000 行
  - 每个 commit 一个 stage 标签(prep/design/impl/verify/bug/health)
```

---

## §2 自验收脚本模板(可复制)

```python
"""Gate 自验收 — 反例驱动测试"""

import subprocess
import sys
import tempfile
from pathlib import Path

GUARD = Path("scripts/skill-xxx-guard.py")
passed = failed = 0


def run_guard(skill_path):
    proc = subprocess.run(
        [sys.executable, str(GUARD), str(skill_path)],
        capture_output=True, text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅ {name}")
        passed += 1
    except AssertionError as e:
        print(f"  ❌ {name}: {e}")
        failed += 1


# ━━━ ❶ PASS 态 ━━━
def t_clean_skill():
    """干净技能 → exit 0"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "SKILL.md").write_text("---\nname: clean\ndescription: 测试\n---\n")
        code, _ = run_guard(tmp)
        assert code == 0, f"干净技能应 PASS 但 exit={code}"


# ━━━ ❷ BLOCK 态(反例) ━━━
def t_block_violation():
    """违规技能 → exit ≠ 0 + 错误信息"""
    with tempfile.TemporaryDirectory() as tmp:
        # 根据 Guard 类型造反例
        (Path(tmp) / "SKILL.md").write_text("# 无 frontmatter\n")
        code, out = run_guard(tmp)
        assert code != 0, f"违规应 BLOCK 但 exit={code}"
        assert "frontmatter" in out.lower(), "应报 frontmatter 问题"


# ━━━ ❸ 边界态 ━━━
def t_boundary_md_only():
    """.md 单文件(非技能目录)→ 应识别为非法"""
    md_only = tempfile.NamedTemporaryFile(suffix=".md", delete=False)
    md_only.write(b"---\nname: x\n---\n")
    md_only.close()
    try:
        code, _ = run_guard(md_only.name)
        assert code != 0, ".md 单文件不应被识别为技能"
    finally:
        Path(md_only.name).unlink()


test("干净技能 → PASS", t_clean_skill)
test("违规技能 → BLOCK", t_block_violation)
test(".md 单文件 → 阻断", t_boundary_md_only)

print(f"\n━━━ 通过: {passed} / 失败: {failed} ━━━")
sys.exit(1 if failed > 0 else 0)
```

---

## §3 自验收 Checklist(写完 Gate 后必走)

```
[ ] PASS 态验证:干净样本 → exit 0
[ ] BLOCK 态验证:违规样本 → exit ≠ 0 + 错误信息明确
[ ] 边界态验证:边界样本(如 .md 文件 / 空目录 / 特殊字符名)→ 不被误识别
[ ] 退出码验证:BLOCK 时 exit code ∈ {1, 2, 4, 6}(非 0)
[ ] 输出验证:错误信息出现在 stdout 或 stderr,能被 CI 解析
[ ] 性能验证:守卫运行时间 < 5 秒(不卡 CI)
[ ] 依赖验证:守卫的子进程调用(如 scan_skills_dir.py)路径正确
[ ] 反例固化:tests/unit/test_*.py 含至少 3 个反例
[ ] 集成验证:`npm run test:unit` 含本守卫的自验收
[ ] 文档验证:SKILL.md §触发时机 / §调用方式 含本守卫
```

---

## §4 失败处理决策树

```
Gate 自验收失败
├─ 反例未被检测(guard 假通过)
│   ├─ 检查 guard 正则/逻辑覆盖
│   ├─ 检查子进程调用是否正确
│   └─ 修复后重跑,直到 100%
├─ exit code 错(本应 1,实际 0)
│   ├─ 检查是否有 main 块 / CLI 入口
│   ├─ 检查 if grep -q 写法
│   └─ 修复后重跑
├─ 脚本静默跳过
│   ├─ 检查 if grep -q 包住 npm run
│   ├─ 改为 if ! grep -q 阻断
│   └─ 修复后重跑
└─ 硬编码文件列表
    ├─ 检查 node --check <固定列表>
    ├─ 改为 glob 扫描 scripts/lint.mjs
    └─ 修复后重跑
```

---

## §5 何时不需要 Gate 自验收?

```
豁免条件:
  - 单文件纯新增(参考 agent-dev-control-kit §0.3 "不适用场景")
  - 用户明确要求"快速执行"
  - 临时脚本 / 一次性工具

豁免时仍需:
  - lint 必须通过
  - 至少 1 个 PASS 态验证
```

---

## §6 与本项目自验收脚本的对应关系

本项目已落地(可作为参考实现):

| 守卫 | 自验收文件 |
|------|----------|
| skill-structure-guard.py | tests/unit/test_structure_guard.py (4 用例)|
| skill-security-guard.py | tests/unit/test_security_guard.py (4 用例)|
| skill-capability-guard.py | tests/unit/test_skill_acceptance.py (3 用例)|
| skill-dependency-guard.mjs | tests/unit/test_skill_acceptance.py (2 用例)+ test_dependency_guard.mjs (3 用例)|

合计 13 个反例用例,固化于 `tests/unit/test_skill_acceptance.py`,由 `npm run test:unit` 自动触发。