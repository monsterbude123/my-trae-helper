"""
02_security.py — 委托 trae-security-review/scan_skills_dir.py 做静态安全扫描

subprocess.run 调用 V2.1 扫描器，解析 JSON 报告并映射到统一三态。
仅依赖标准库，不复制扫描逻辑（与 AGENTS.md §5 一致）。

CLI:    python 02_security.py --target <skill-path> [--json]
退出码: 0=PASS  2=WARN  4=BLOCK  5=ARG_ERROR  6=INTERNAL_ERROR
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


CHECK_ID = "02_security"
SCAN_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "trae-security-review"
    / "scripts"
    / "scan_skills_dir.py"
)


def run_scan(skill: Path, tmp_dir: Path):
    if not SCAN_SCRIPT.is_file():
        return None, f"scan_skills_dir.py 不存在: {SCAN_SCRIPT}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(SCAN_SCRIPT),
        str(skill),
        str(tmp_dir),
        "--quiet",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, shell=False, timeout=60
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"subprocess 启动失败: {exc}"

    if proc.returncode != 0 and not proc.stdout.strip().startswith("{"):
        return None, f"扫描器非零退出 (rc={proc.returncode}): {proc.stderr[:300]}"

    out = proc.stdout.strip()
    # 部分扫描器会在 JSON 后附带额外 stdout 行，取首行 JSON
    first = next((line for line in out.splitlines() if line.startswith("{")), "")
    if not first:
        return None, "扫描器未产出 JSON（首行非对象）"
    try:
        return json.loads(first), None
    except json.JSONDecodeError as exc:
        return None, f"JSON 解析失败: {exc}; 原始: {first[:200]}"


def evaluate(target: Path, tmp_root: Path):
    if not target.is_dir():
        return {
            "id": CHECK_ID,
            "status": "BLOCK",
            "score": 0,
            "issues": [
                {
                    "code": "TARGET_NOT_DIR",
                    "severity": "HIGH",
                    "message": f"目标不是目录: {target}",
                    "file": str(target),
                    "line": None,
                }
            ],
        }

    tmp_dir = tmp_root / f"sa-scan-{int(time.time() * 1000)}"
    report, err = run_scan(target, tmp_dir)
    if report is None:
        return {
            "id": CHECK_ID,
            "status": "BLOCK",
            "score": 0,
            "issues": [
                {
                    "code": "SCAN_FAILED",
                    "severity": "HIGH",
                    "message": err or "扫描失败",
                    "file": str(target),
                    "line": None,
                }
            ],
        }

    rc = report.get("risk_counts", {})
    high = int(rc.get("high", 0))
    medium = int(rc.get("medium", 0))
    low = int(rc.get("low", 0))

    issues = []
    for f in report.get("findings", []):
        sev = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}.get(
            f.get("severity", ""), "LOW"
        )
        issues.append(
            {
                "code": f.get("code", "UNKNOWN"),
                "severity": sev,
                "message": f.get("message", ""),
                "file": f.get("file", str(target)),
                "line": f.get("line"),
            }
        )

    if high >= 1:
        status, score = "BLOCK", max(0, 50 - 15 * high)
    elif medium >= 3:
        status, score = "WARN", max(40, 100 - 8 * medium)
    elif medium > 0 or low > 0:
        score = 100 - 2 * medium - low
        score = max(0, min(100, score))
        status = "PASS"
    else:
        status, score = "PASS", 100

    return {
        "id": CHECK_ID,
        "status": status,
        "score": score,
        "issues": issues,
        "scan_summary": report.get("summary", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="委托 security scan")
    parser.add_argument("--target", required=True, help="skill 目录路径")
    parser.add_argument(
        "--tmp",
        default=str(Path(__file__).resolve().parents[3] / ".trae" / "tmp"),
        help="扫描报告输出目录",
    )
    parser.add_argument("--json", action="store_true", help="强制 JSON 输出")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    tmp_root = Path(args.tmp).resolve()

    t0 = time.time()
    try:
        result = evaluate(target, tmp_root)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(
            json.dumps(
                {
                    "id": CHECK_ID,
                    "status": "INTERNAL_ERROR",
                    "score": 0,
                    "issues": [
                        {
                            "code": "EXCEPTION",
                            "severity": "HIGH",
                            "message": f"内部异常: {exc}",
                            "file": str(target),
                            "line": None,
                        }
                    ],
                    "duration_ms": int((time.time() - t0) * 1000),
                },
                ensure_ascii=False,
            )
        )
        sys.stdout.write("\n")
        sys.exit(6)

    result["duration_ms"] = int((time.time() - t0) * 1000)
    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.write("\n")
    code_map = {"PASS": 0, "WARN": 2, "BLOCK": 4}
    sys.exit(code_map.get(result["status"], 4))


if __name__ == "__main__":
    main()
