#!/usr/bin/env python3
"""
V11 project-priority-resolver.py — P1-1 + P1-3 实现

实现 §14.5 项目级 rules > V11 通用层优先级 + 读 .trae/fullstack4traev11.config.yaml
字段(forbidden_paths / stage_config.skills / required_stages)。

Usage:
    # 输出某 stage 的合并 skill 列表(3 层优先级,JSON)
    python project-priority-resolver.py --project-root <path> --stage <id> --json

    # 校验 path 是否在 forbidden_paths 命中 → exit 1 阻断
    python project-priority-resolver.py --project-root <path> --check-forbidden <path>

    # 合并 V11 通用层 + 项目级 anti-patterns.md
    python project-priority-resolver.py --project-root <path> --merge-anti-patterns --output <file>

Exit codes:
    0 = PASS / 合法的路径 / 合并成功
    1 = FAIL / forbidden 命中 / 输入非法
    2 = N/A(标注理由)
"""
import argparse
import fnmatch
import json
import pathlib
import sys

try:
    import yaml
except ImportError:
    print("[v11-priority] FATAL: PyYAML 未安装", file=sys.stderr)
    sys.exit(1)


CONFIG_FILENAME = "fullstack4traev11.config.yaml"
PROJECT_ANTI_PATTERNS = (
    ".trae/skills/project_rules_skills/references/anti-patterns.md"
)
V11_ANTI_PATTERNS = "references/common-anti-patterns.md"
V11_STAGE_GATE_FILE = "scripts/stage-gate.py"
V11_REPO_MARKER = "fullstack4TraeV11"  # 用于在 skill_root 路径中识别 V11 仓库根


def find_project_config(project_root: pathlib.Path) -> pathlib.Path | None:
    """定位项目级配置文件 <project_root>/.trae/fullstack4traev11.config.yaml。"""
    candidate = project_root / ".trae" / CONFIG_FILENAME
    return candidate if candidate.is_file() else None


def load_project_config(project_root: pathlib.Path) -> dict:
    """加载项目级 config.yaml;不存在返回空 dict。

    PyYAML safe_load 自动过滤掉注释与 None 字段;字段缺失则 dict.get() 兜底 None。
    """
    path = find_project_config(project_root)
    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[v11-priority] config 解析失败: {e}", file=sys.stderr)
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def load_v11_stage_skills(skill_root: pathlib.Path, stage_id: str) -> list:
    """Layer 2: 从 V11 SKILL.md depends_on.skills 读对应 stage 的 skill 列表。

    返回 list[str]。未找到或 stage 不存在返回 []。
    """
    # V11 约定:stage id "3/implement" → skill 目录 "03-implement"
    # 跳过数字前缀的 ordinal,只保留阶段名
    parts = stage_id.split("/", 1)
    if len(parts) != 2:
        return []
    raw = parts[1].strip()
    # "real-verify" / "rot-scan" 已是短名;目录命名约定 N-stage-name
    candidates = [
        f"01-intake", f"02-plan", f"03-test-plan", f"04-spec", f"05-prototype",
        f"06-contract", f"07-implement", f"08-real-verify", f"09-review",
        f"10-rot-scan", f"11-accept", f"12-bug-fix", f"13-project-health",
    ]
    short_to_dir = {
        "intake": "01-intake",
        "plan": "02-plan",
        "test-plan": "03-test-plan",
        "spec": "04-spec",
        "prototype": "05-prototype",
        "contract": "06-contract",
        "implement": "07-implement",
        "real-verify": "08-real-verify",
        "review": "09-review",
        "rot-scan": "10-rot-scan",
        "accept": "11-accept",
        "bug-fix": "12-bug-fix",
        "health": "13-project-health",
    }
    target_dir = short_to_dir.get(raw)
    if target_dir is None:
        # 模糊匹配
        for c in candidates:
            if raw in c:
                target_dir = c
                break
    if target_dir is None:
        return []
    skill_md = skill_root / "skills" / target_dir / "SKILL.md"
    if not skill_md.is_file():
        return []
    try:
        with open(skill_md, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return []
    # YAML frontmatter 解析
    if not text.startswith("---"):
        return []
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return []
    fm = text[3:end]
    try:
        data = yaml.safe_load(fm) or {}
    except Exception:
        return []
    depends = data.get("depends_on", {}) or {}
    skills = depends.get("skills", []) or []
    return [s for s in skills if isinstance(s, str)]


def load_global_skills(skill_root: pathlib.Path) -> list:
    """Layer 1: 占位返回 V11 推荐预装 user-level skills。

    返回 V11 reference/dependency-config.md §Layer 1 列出的 skill 名单。
    """
    return [
        "gitnexus4Trae",
        "ponytail4Trae",
        "visual-evidence-discipline",
        "screenshot",
        "playwright-best-practices",
        "frontend-backend-contract-alignment",
        "acceptance-discipline",
        "goal-mode",
        "doc-map-manager",
        "browser-use-cloud",
    ]


def resolve_skills(stage_id: str, project_config: dict, skill_root: pathlib.Path) -> list:
    """3 层优先级解析(实现 dependency-config.md L107-125 算法)。

    Layer 3 项目级覆盖 > Layer 2 V11 内置 > Layer 1 全局。
    """
    skills = []
    skills.extend(load_global_skills(skill_root))           # Layer 1
    skills.extend(load_v11_stage_skills(skill_root, stage_id))  # Layer 2
    project_overrides = (
        (project_config.get("stage_config") or {}).get(stage_id, {}) or {}
    )
    project_skills = project_overrides.get("skills", []) or []
    skills = list(project_skills) + skills                  # 项目级前置于 V11 通用
    return list(dict.fromkeys(skills))


def resolve_skill_root() -> pathlib.Path:
    """V11 skill 根目录(脚本所在目录的上一级)。"""
    return pathlib.Path(__file__).resolve().parent.parent


def check_forbidden(project_root: pathlib.Path, target_path: str) -> tuple:
    """校验 target_path 是否命中项目 forbidden_paths 任何一条 glob 规则。

    返回 (blocked: bool, matched_rule: str | None, reason: str)。
    """
    project_config = load_project_config(project_root)
    forbidden = (project_config.get("forbidden_paths") or [])
    if not isinstance(forbidden, list):
        return (False, None, "forbidden_paths 不是 list")
    # 统一用 / 分割便于跨平台匹配
    target_norm = target_path.replace("\\", "/").lstrip("./")
    for rule in forbidden:
        if not isinstance(rule, str):
            continue
        rule_norm = rule.replace("\\", "/").lstrip("./")
        # fnmatch 支持 ** 递归语法;为简化,把 ** 视为 *
        rule_simple = rule_norm.replace("**", "*")
        if fnmatch.fnmatch(target_norm, rule_simple) or fnmatch.fnmatch(target_path, rule):
            return (True, rule, f"命中禁读规则: {rule}")
    return (False, None, "未命中 forbidden_paths")


def merge_anti_patterns(project_root: pathlib.Path, skill_root: pathlib.Path) -> dict:
    """合并 V11 通用层 + 项目级 anti-patterns.md。

    返回 {"v11_path": str|None, "project_path": str|None, "merged_size": int}。
    """
    v11_path = skill_root / V11_ANTI_PATTERNS
    project_path = project_root / PROJECT_ANTI_PATTERNS

    merged_content = []
    if v11_path.is_file():
        merged_content.append(f"<!-- source: V11通用层 {V11_ANTI_PATTERNS} -->\n")
        merged_content.append(v11_path.read_text(encoding="utf-8"))
        merged_content.append("\n\n---\n\n")
    if project_path.is_file():
        merged_content.append(f"<!-- source: 项目级 {PROJECT_ANTI_PATTERNS} -->\n")
        merged_content.append(project_path.read_text(encoding="utf-8"))

    return {
        "v11_path": str(v11_path) if v11_path.is_file() else None,
        "project_path": str(project_path) if project_path.is_file() else None,
        "merged_size": sum(len(c) for c in merged_content),
        "merged_content": "".join(merged_content),
    }


# ============================================================================
# CLI
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="V11 项目级优先级解析(Layer 3 > 2 > 1)")
    parser.add_argument("--project-root", required=True, help="项目根目录")
    parser.add_argument("--stage", help="目标 stage id(如 3/implement)")
    parser.add_argument("--check-forbidden", metavar="PATH",
                        help="校验 PATH 是否命中 forbidden_paths(命中 exit 1)")
    parser.add_argument("--merge-anti-patterns", action="store_true",
                        help="合并 V11 + 项目级 anti-patterns.md 到 --output")
    parser.add_argument("--output", help="合并输出文件路径(--merge-anti-patterns 时必填)")
    parser.add_argument("--json", action="store_true", help="JSON 输出(--stage 时)")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(f"[v11-priority] 项目根不存在: {project_root}", file=sys.stderr)
        return 2

    skill_root = resolve_skill_root()

    # --check-forbidden
    if args.check_forbidden:
        blocked, rule, reason = check_forbidden(project_root, args.check_forbidden)
        if blocked:
            print(f"[v11-priority] BLOCKED: {reason}", file=sys.stderr)
            return 1
        else:
            print(f"[v11-priority] ALLOW: {args.check_forbidden} ({reason})")
            return 0

    # --merge-anti-patterns
    if args.merge_anti_patterns:
        if not args.output:
            print("[v11-priority] --merge-anti-patterns 必须配合 --output", file=sys.stderr)
            return 1
        result = merge_anti_patterns(project_root, skill_root)
        out = pathlib.Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result["merged_content"], encoding="utf-8")
        print(f"[v11-priority] merged → {out}")
        print(f"  - v11 source: {result['v11_path'] or '(not found)'}")
        print(f"  - project source: {result['project_path'] or '(not found)'}")
        print(f"  - merged size: {result['merged_size']} bytes")
        return 0

    # --stage
    if args.stage:
        project_config = load_project_config(project_root)
        skills = resolve_skills(args.stage, project_config, skill_root)
        if args.json:
            print(json.dumps({
                "stage": args.stage,
                "skills": skills,
                "project_config_used": find_project_config(project_root) is not None,
                "layers": {
                    "layer1_global": load_global_skills(skill_root),
                    "layer2_v11": load_v11_stage_skills(skill_root, args.stage),
                    "layer3_project": (
                        (project_config.get("stage_config") or {})
                        .get(args.stage, {})
                        .get("skills", [])
                    ),
                },
            }, ensure_ascii=False, indent=2))
        else:
            print(f"[v11-priority] stage={args.stage} merged skills ({len(skills)}):")
            for s in skills:
                print(f"  - {s}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())