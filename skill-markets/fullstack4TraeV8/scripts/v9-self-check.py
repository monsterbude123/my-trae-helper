"""V9 精密化改动快速自检。

检查技能包中所有关键约束是否存在（结构完整性验证）。
对应 v9-validation-protocol.md 的 Step A-C 层面检查。

用法:
    python v9-self-check.py [--verbose]
"""

import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
MYTRAE_ROOT = SKILL_ROOT.parent.parent
RULES_DIR = MYTRAE_ROOT / ".trae" / "rules"
AGENT_PROTOCOL = RULES_DIR / "agent协调协议.md"
STRICT_RULES = RULES_DIR / "strict.md"

INJECTION_TEMPLATE = SKILL_ROOT / "references" / "delegation-injection-template.md"
COMPLETION_REPORT = SKILL_ROOT / "references" / "completion-report-protocol.md"
QUANTITATIVE = SKILL_ROOT / "references" / "quantitative-acceptance.md"
REVIEWER = SKILL_ROOT / "agents" / "reviewer.md"
DOC_UPDATER = SKILL_ROOT / "agents" / "doc-updater.md"
IMPLEMENTER = SKILL_ROOT / "agents" / "implementer.md"
SESSION_START = SKILL_ROOT / "templates" / "hooks" / "session-start.ps1"
HOOKS_JSON = SKILL_ROOT / "templates" / "hooks" / "fullstack-hooks.json"

pass_count = 0
fail_count = 0


def check(label: str, result: bool) -> None:
    global pass_count, fail_count
    if result:
        print(f"  [PASS] {label}")
        pass_count += 1
    else:
        print(f"  [FAIL] {label}")
        fail_count += 1


def file_contains(path: Path, pattern: str) -> bool:
    """检查文件是否包含指定正则模式。"""
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return bool(re.search(pattern, text))


def file_contains_count(path: Path, pattern: str) -> int:
    """返回文件匹配指定模式的次数。"""
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    return len(re.findall(pattern, text))


def main() -> int:
    print(f"Skill Root:  {SKILL_ROOT}")
    print(f"MyTrae Root: {MYTRAE_ROOT}")
    print()
    print("=== V9 Precision Self-Check ===")

    # ── P0-1: 主上下文禁止直接编辑文档索引 ──
    check("P0-1 文档索引 delegation rule in agent-protocol",
          file_contains(AGENT_PROTOCOL, r"文档索引"))

    # ── P0-2: gitignore 误杀检测 ──
    p02a = file_contains(AGENT_PROTOCOL, r"git check-ignore")
    p02b = file_contains(COMPLETION_REPORT, r"gitignore")
    check("P0-2 gitignore silent-kill detection", p02a and p02b)

    # ── P0-3: N/A 验证 + 非阻塞废除 ──
    p03a = file_contains(QUANTITATIVE, r"Step 5")
    p03b = file_contains(REVIEWER, r"N/A")
    check("P0-3 N/A pre-declaration verify + Step5", p03a and p03b)

    # ── P1-1: Completion Report 协议 + 硬门禁 ──
    p11a = COMPLETION_REPORT.exists()
    p11b = file_contains(AGENT_PROTOCOL, r"Completion Report")
    check("P1-1 Completion Report protocol + hard gate", p11a and p11b)

    # ── P1-2 / P2-2: doc-updater 完整性清单 ──
    p12 = file_contains_count(DOC_UPDATER, r"文档索引")
    check("P1-2/P2-2 doc-updater 文档索引 coverage (>=2)", p12 >= 2)

    # ── P2-1: Doc-Sync Confirm 门禁 ──
    p21a = file_contains(STRICT_RULES, r"Doc-Sync Confirm")
    p21b = file_contains(AGENT_PROTOCOL, r"git diff --stat -- docs/")
    check("P2-1 Doc-Sync diff confirm gate", p21a and p21b)

    # ── P2-3: docs/ 目录规范 ──
    check("P2-3 docs/ path convention authority",
          file_contains(STRICT_RULES, r"## docs/"))

    # ── P2-4: Hook 自证 ──
    p24a = file_contains(SESSION_START, r"hook-session-start")
    p24b = file_contains(HOOKS_JSON, r'"enabled"\s*:\s*true')
    p24c = file_contains(AGENT_PROTOCOL, r"(?i)hook")
    check("P2-4 Hook self-proving (log+enabled+trigger)", p24a and p24b and p24c)

    # ── V9.2-1: implementer 编码前 GitNexus impact() ──
    va = file_contains(IMPLEMENTER, r"GITNEXUS IMPACT")
    vb = file_contains(IMPLEMENTER, r"步骤 0\.8")
    check("V9.2-1 Implementer GitNexus impact() step", va and vb)

    # ── V9.2-2: Completion Report 含 GitNexus 验证段 + 机械验证 Step 0.5 ──
    v2a = file_contains(IMPLEMENTER, r"GitNexus 验证")
    v2b = file_contains(AGENT_PROTOCOL, r"Step 0\.5")
    check("V9.2-2 GitNexus verification in CR + Step 0.5 gate", v2a and v2b)

    # ── V9.2-3: doc-updater 拒绝直接 python build-index.py ──
    v3a = file_contains(DOC_UPDATER, r"REJECT DIRECT COMMAND")
    v3b = file_contains(AGENT_PROTOCOL, r"python build-index\.py")
    check("V9.2-3 doc-updater reject direct build-index", v3a and v3b)

    # ── V9.3-1: 委派注入模板存在 + agent协调协议引用 ──
    d1a = INJECTION_TEMPLATE.exists()
    d1b = file_contains(AGENT_PROTOCOL, r"委派注入协议")
    check("V9.3-1 Delegation injection template + protocol ref", d1a and d1b)

    # ── V9.3-2: implementer 铁律 12-14（前端测试/集成测试/端口） ──
    d2a = file_contains(IMPLEMENTER, r"FRONTEND TEST REQUIRED")
    d2b = file_contains(IMPLEMENTER, r"INTEGRATION TEST REQUIRED")
    d2c = file_contains(IMPLEMENTER, r"NO HARDCODED CONFIG")
    check("V9.3-2 Implementer iron laws 12-14", d2a and d2b and d2c)

    # ── V9.3-3: implementer 步骤 0.8.5（编码前自检） ──
    d3 = file_contains(IMPLEMENTER, r"步骤 0\.8\.5")
    check("V9.3-3 Implementer step 0.8.5 pre-code check", d3)

    # ── V9.3-4: reviewer 合规性回溯验证 + __tests__ 质量阈值 ──
    d4a = file_contains(REVIEWER, r"合规性回溯验证")
    d4b = file_contains(REVIEWER, r"为空目录")
    check("V9.3-4 Reviewer compliance back-trace + threshold", d4a and d4b)

    print()
    print(f"=== Result: {pass_count} PASS / {fail_count} FAIL ===")
    if fail_count > 0:
        print("Gaps exist. See v9-validation-protocol.md for details.")
        return 1
    print("All passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
