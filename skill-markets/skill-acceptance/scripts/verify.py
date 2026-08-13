"""
skill-acceptance / scripts / verify.py
Skill 包合规验收门禁 — CLI + JSON + 退出码矩阵。
6 项检查：frontmatter / security / capability_map / scripts_boundary /
         references_size / decision_layer_tag
退出码：0 PASS / 2 WARN / 4 BLOCK / 5 ARG_ERROR / 6 INTERNAL_ERROR
用法：
    python verify.py --target <skill-path> [--json] [--report <out.json>]
                     [--fail-on LEVEL] [--strict] [--new-skill] [--quiet]
"""

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, List, Optional

VERSION = "0.1.0"
SCHEMA_VERSION = "1.0.0"
SKILL_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SKILL_ROOT.parent.parent
CAPABILITY_MAP = PROJECT_ROOT / "skill-markets" / "CAPABILITY-MAP.md"
SECURITY_SCANNER = (
    PROJECT_ROOT / "skill-markets" / "trae-security-review"
    / "scripts" / "scan_skills_dir.py"
)
EXIT_PASS, EXIT_WARN, EXIT_BLOCK = 0, 2, 4
EXIT_ARG_ERROR, EXIT_INTERNAL_ERROR = 5, 6
STATUSES = ("PASS", "WARN", "BLOCK")
SEV = ("HIGH", "MEDIUM", "LOW")


@dataclass
class Issue:
    code: str; severity: str; message: str; file: str = ""; line: int = 0


@dataclass
class CheckResult:
    id: str; status: str; score: int
    issues: List[dict] = field(default_factory=list)
    duration_ms: int = 0; note: str = ""

    def to_dict(self): return asdict(self)


def parse_frontmatter(text: str) -> Optional[dict]:
    """极简 YAML frontmatter：顶层 key: value + '- item' 列表。"""
    m = re.match(r"^---\n(.+?)\n---", text, re.S)
    if not m: return None
    out: dict = {}; cur: Optional[str] = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"): continue
        lm = re.match(r"^\s*-\s+(.*)$", line)
        if lm and cur is not None:
            out.setdefault(cur, []).append(lm.group(1).strip().strip('"').strip("'")); continue
        cur = None
        kv = re.match(r"^([A-Za-z_][\w.\-]*)\s*:\s*(.*)$", line)
        if not kv: continue
        key, val = kv.group(1), kv.group(2).split("#", 1)[0].strip().strip('"').strip("'")
        if val == "":
            cur = key; out[key] = []
        else:
            out[key] = val
    return out


def parse_fm(text: str) -> Optional[dict]:
    try:
        import yaml  # type: ignore
        m = re.match(r"^---\n(.+?)\n---", text, re.S)
        return (yaml.safe_load(m.group(1)) if m else None) or None
    except Exception:
        return parse_frontmatter(text)


def now_iso() -> str: return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def dir_name(p: Path) -> str: return p.resolve().name if p.exists() else p.name


def bounded(base: int, issues: List[Issue]) -> int:
    s = base
    for i in issues:
        s -= 40 if i.severity == "HIGH" else 10 if i.severity == "MEDIUM" else 2
    return max(0, min(100, s))


def decide(issues: List[Issue]) -> str:
    """从 issues 推导 check status。"""
    has_h = any(i.severity == "HIGH" for i in issues)
    if has_h: return "BLOCK"
    if any(i.severity == "MEDIUM" for i in issues): return "WARN"
    return "PASS"


def wrap(check_id: str, fn: Callable, p: Path) -> CheckResult:
    t0 = time.monotonic()
    try:
        r = fn(p)
    except Exception as exc:
        r = CheckResult(check_id, "BLOCK", 0, [{
            "code": "INTERNAL_ERROR", "severity": "HIGH",
            "message": f"{type(exc).__name__}: {exc}"}], note="check crashed")
    r.duration_ms = int((time.monotonic() - t0) * 1000); return r


# ---------- 6 项检查 ----------

def check_frontmatter(p: Path) -> CheckResult:
    sm = p / "SKILL.md"; issues: List[Issue] = []
    if not sm.is_file():
        issues.append(Issue("FRONTMATTER_MISSING_SKILLMD", "HIGH", "SKILL.md 不存在"))
        return CheckResult("frontmatter", "BLOCK", 0, [asdict(i) for i in issues])
    fm = parse_fm(sm.read_text(encoding="utf-8", errors="replace"))
    if not fm:
        issues.append(Issue("FRONTMATTER_MISSING_DELIM", "HIGH", "缺 YAML frontmatter", file=str(sm)))
        return CheckResult("frontmatter", "BLOCK", 0, [asdict(i) for i in issues])
    name = (fm.get("name") or "").strip()
    if not name: issues.append(Issue("FRONTMATTER_MISSING_NAME", "HIGH", "缺 name", file=str(sm)))
    elif name != dir_name(p):
        issues.append(Issue("FRONTMATTER_NAME_MISMATCH", "HIGH",
                            f"name={name!r} ≠ 目录 {dir_name(p)!r}", file=str(sm)))
    if not (fm.get("version") or "").strip():
        issues.append(Issue("FRONTMATTER_MISSING_VERSION", "MEDIUM", "缺 version", file=str(sm)))
    desc = (fm.get("description") or "").strip()
    if not desc: issues.append(Issue("FRONTMATTER_MISSING_DESCRIPTION", "HIGH", "缺 description", file=str(sm)))
    elif len(desc) < 30:
        issues.append(Issue("FRONTMATTER_DESCRIPTION_TOO_SHORT", "MEDIUM",
                            f"description 长度 {len(desc)}<30", file=str(sm)))
    return CheckResult("frontmatter", decide(issues), bounded(100, issues),
                       [asdict(i) for i in issues])


def check_security(p: Path) -> CheckResult:
    issues: List[Issue] = []
    if not SECURITY_SCANNER.is_file():
        issues.append(Issue("SECURITY_SCANNER_MISSING", "HIGH",
                            f"未找到 scan_skills_dir.py: {SECURITY_SCANNER}"))
        return CheckResult("security", "BLOCK", 0, [asdict(i) for i in issues])
    try:
        proc = subprocess.run([sys.executable, str(SECURITY_SCANNER), str(p)],
                              capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        issues.append(Issue("SECURITY_TIMEOUT", "HIGH", "scan_skills_dir.py 超时 >60s"))
        return CheckResult("security", "BLOCK", 0, [asdict(i) for i in issues])
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        issues.append(Issue("SECURITY_JSON_PARSE_FAIL", "HIGH", f"JSON 解析失败: {exc}"))
        return CheckResult("security", "BLOCK", 0, [asdict(i) for i in issues])
    for f in (report.get("findings") or []):
        sv = (f.get("severity") or "").lower()
        issues.append(Issue(str(f.get("code") or "SEC_FINDING"),
                            "HIGH" if sv == "high" else "MEDIUM" if sv == "medium" else "LOW",
                            str(f.get("message") or ""), str(f.get("file") or ""),
                            int(f.get("line") or 0)))
    hi = sum(1 for i in issues if i.severity == "HIGH")
    me = sum(1 for i in issues if i.severity == "MEDIUM")
    return CheckResult("security", "BLOCK" if hi else "WARN" if me >= 3 else "PASS",
                       bounded(100, issues), [asdict(i) for i in issues],
                       note=f"findings={len(issues)} (h={hi},m={me})")


def check_capability_map(p: Path, *, new_skill: bool) -> CheckResult:
    issues: List[Issue] = []; name = dir_name(p)
    if not CAPABILITY_MAP.is_file():
        issues.append(Issue("CAPABILITY_MAP_MISSING", "HIGH", f"未找到 {CAPABILITY_MAP}"))
        return CheckResult("capability_map", "BLOCK", 0, [asdict(i) for i in issues])
    text = CAPABILITY_MAP.read_text(encoding="utf-8", errors="replace")
    if not new_skill and not re.search(rf"\b{re.escape(name)}\b", text):
        issues.append(Issue("CAPABILITY_MAP_NOT_REGISTERED", "HIGH",
                            f"{name!r} 未注册（首次发布加 --new-skill）", file=str(CAPABILITY_MAP)))
    note = "new-skill 模式跳过注册" if new_skill else ""
    return CheckResult("capability_map", decide(issues), bounded(100, issues),
                       [asdict(i) for i in issues], note=note)


def check_scripts_boundary(p: Path) -> CheckResult:
    issues: List[Issue] = []; sd = p / "scripts"
    if not sd.is_dir():
        return CheckResult("scripts_boundary", "PASS", 100, [], note="scripts/ 不存在")
    SUFF = (".py", ".sh", ".ps1", ".mjs", ".js", ".bat")
    for e in p.iterdir():
        if e.is_file() and e.suffix in SUFF:
            issues.append(Issue("SCRIPTS_ROOT_POLLUTION", "MEDIUM",
                                f"脚本散落根目录: {e.name}", file=str(e)))
    for e in sd.rglob("*"):
        if e.is_file() and e.suffix in SUFF:
            try:
                n = sum(1 for _ in e.open("r", encoding="utf-8", errors="replace"))
            except OSError:
                continue
            if n > 150:
                issues.append(Issue("SCRIPTS_TOO_LONG", "HIGH",
                                    f"{e.relative_to(p)} 行数 {n} > 150", file=str(e)))
    return CheckResult("scripts_boundary", decide(issues), bounded(100, issues),
                       [asdict(i) for i in issues])


def check_references_size(p: Path) -> CheckResult:
    issues: List[Issue] = []; sm = p / "SKILL.md"; note = ""
    if sm.is_file() and len(sm.read_text(encoding="utf-8", errors="replace").splitlines()) > 500:
        issues.append(Issue("SKILL_MD_TOO_LONG", "HIGH", "SKILL.md > 500 行", file=str(sm)))
    rd = p / "references"; total = 0
    if rd.is_dir():
        total = sum((e.stat().st_size for e in rd.rglob("*.md") if e.is_file()), 0)
        if total > 200 * 1024:
            issues.append(Issue("REFERENCES_TOO_LARGE", "MEDIUM",
                                f"references 总 {total}B > 200KB", file=str(rd)))
        note = f"references_total={total}B"
    return CheckResult("references_size", decide(issues), bounded(100, issues),
                       [asdict(i) for i in issues], note=note)


def check_decision_layer_tag(p: Path) -> CheckResult:
    issues: List[Issue] = []; sm = p / "SKILL.md"
    if not sm.is_file():
        issues.append(Issue("DECISION_TAG_NO_SKILLMD", "HIGH", "SKILL.md 不存在"))
        return CheckResult("decision_layer_tag", "BLOCK", 0, [asdict(i) for i in issues])
    text = sm.read_text(encoding="utf-8", errors="replace")
    kws = ("决策层级", "反例", "铁律", "references/")
    hit = sum(1 for k in kws if k in text)
    if hit == 0:
        issues.append(Issue("DECISION_TAG_MISSING_ALL", "HIGH", "决策关键词 0/4", file=str(sm)))
    elif hit <= 1:
        issues.append(Issue("DECISION_TAG_TOO_FEW", "MEDIUM",
                            f"决策关键词 {hit}/4，建议 ≥2", file=str(sm)))
    return CheckResult("decision_layer_tag", decide(issues), bounded(100, issues),
                       [asdict(i) for i in issues], note=f"keyword_hits={hit}/4")


# ---------- 汇总 + CLI ----------

def aggregate(checks: List[CheckResult], strict: bool) -> tuple:
    if any(c.status == "BLOCK" for c in checks): return "BLOCK", EXIT_BLOCK
    meds = sum(sum(1 for i in c.issues if i.get("severity") == "MEDIUM") for c in checks)
    smin = min((c.score for c in checks), default=100)
    if strict and meds >= 3: return "BLOCK", EXIT_BLOCK
    if meds >= 3 or smin < 60 or any(c.status == "WARN" for c in checks):
        return "WARN", EXIT_WARN
    return "PASS", EXIT_PASS


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="verify.py",
        description="Skill 包合规验收门禁（CI/pre-release 钩子）")
    ap.add_argument("--target", required=True, help="待验收 skill 目录")
    ap.add_argument("--json", action="store_true", help="stdout 输出 JSON")
    ap.add_argument("--report", help="落盘 JSON 报告路径")
    ap.add_argument("--fail-on", choices=STATUSES, default="BLOCK")
    ap.add_argument("--strict", action="store_true", help="MEDIUM≥3 升级 BLOCK")
    ap.add_argument("--new-skill", action="store_true", help="跳过 CAPABILITY-MAP 注册校验")
    ap.add_argument("--quiet", action="store_true", help="仅打印汇总表")
    ap.add_argument("--version", action="version", version=f"verify.py {VERSION}")
    args = ap.parse_args(argv)
    skill_path = Path(args.target).resolve(strict=False)
    if not skill_path.is_dir():
        sys.stderr.write(f"[ARG_ERROR] --target 不存在: {skill_path}\n"); return EXIT_ARG_ERROR
    if not args.quiet: sys.stderr.write(f"==> verify.py v{VERSION} target={skill_path}\n")
    results = [
        wrap("frontmatter", check_frontmatter, skill_path),
        wrap("security", check_security, skill_path),
        wrap("capability_map",
             lambda p: check_capability_map(p, new_skill=args.new_skill), skill_path),
        wrap("scripts_boundary", check_scripts_boundary, skill_path),
        wrap("references_size", check_references_size, skill_path),
        wrap("decision_layer_tag", check_decision_layer_tag, skill_path),
    ]
    overall, exit_code = aggregate(results, strict=args.strict)
    summary = {"block": sum(1 for c in results if c.status == "BLOCK"),
               "warn":  sum(1 for c in results if c.status == "WARN"),
               "pass":  sum(1 for c in results if c.status == "PASS")}
    payload = {"schema_version": SCHEMA_VERSION, "timestamp": now_iso(),
               "target": str(skill_path), "overall_status": overall,
               "checks": [c.to_dict() for c in results], "summary": summary,
               "exit_code": exit_code,
               "tool": {"name": "verify.py", "version": VERSION,
                        "fail_on": args.fail_on, "strict": args.strict}}
    if not args.quiet:
        sys.stderr.write("\n" + "=" * 64 + "\n")
        sys.stderr.write(f" target : {skill_path}\n overall: {overall}  exit={exit_code}\n")
        sys.stderr.write("-" * 64 + "\n")
        for c in results:
            mk = {"PASS": "[OK]  ", "WARN": "[WARN]", "BLOCK": "[BLOCK]"}.get(c.status, "[?] ")
            sys.stderr.write(f" {mk}{c.id:<22s} score={c.score:>3d} {c.duration_ms:>5d}ms {c.note}\n")
        sys.stderr.write("-" * 64 + "\n")
        sys.stderr.write(f" summary: pass={summary['pass']} warn={summary['warn']} "
                         f"block={summary['block']}\n" + "=" * 64 + "\n")
    if args.json: print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.report:
        rp = Path(args.report); rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if not args.quiet: sys.stderr.write(f"[REPORT] {rp}\n")
    th = {"PASS": 0, "WARN": 2, "BLOCK": 4}.get(args.fail_on, 4)
    return exit_code if exit_code >= th else 0


if __name__ == "__main__":
    try: sys.exit(main())
    except KeyboardInterrupt: sys.exit(EXIT_INTERNAL_ERROR)
    except Exception as exc:
        sys.stderr.write(f"[INTERNAL_ERROR] {type(exc).__name__}: {exc}\n")
        sys.exit(EXIT_INTERNAL_ERROR)