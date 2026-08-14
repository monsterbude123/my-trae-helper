"""
TRAE Security Review — Skill 平台兼容性检测库

从 skills-security/main.py（DEPRECATED 2026-08-14）迁移而来。
保留独特能力：识别 Skill 类型（trae-skill / claude-skill / json-skill / node-skill / unknown）
+ 推断支持平台（Trae / Claude Code / Cursor / OpenClaw / Codex / Gemini CLI / Aider /
Windsurf / Kilo Code / OpenCode / Augment / Antigravity / GitHub Copilot / Kimi / Cline /
AMP / Warp / 通用）。

被 scan_skills_dir.py V2.1 调用，输出写入 Markdown 报告的"被评估 Skill 基本信息"段。
"""

import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

IGNORE_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__"}

COMMON_PLATFORM_SET = [
    "trae", "claude-code", "cc", "openclaw", "cursor", "codex", "gemini-cli",
    "aider", "windsurf", "kilo-code", "opencode", "augment", "antigravity",
    "universal", "amp", "cline", "github-copilot", "kimi-code-cli", "warp",
]

TYPE_NAME_ZH = {
    "trae-skill": "Trae 技能",
    "claude-skill": "SKILL.md 技能",
    "json-skill": "JSON 技能",
    "node-skill": "Node 技能",
    "unknown": "未知类型",
}

PLATFORM_NAME_ZH = {
    "trae": "Trae",
    "claude-code": "Claude Code",
    "cc": "Claude Code（cc）",
    "cursor": "Cursor",
    "openclaw": "OpenClaw",
    "codex": "OpenAI Codex",
    "gemini-cli": "Gemini CLI",
    "aider": "Aider",
    "windsurf": "Windsurf",
    "kilo-code": "Kilo Code",
    "opencode": "OpenCode",
    "augment": "Augment",
    "antigravity": "Antigravity",
    "github-copilot": "GitHub Copilot",
    "kimi-code-cli": "Kimi Code CLI",
    "cline": "Cline",
    "amp": "AMP",
    "warp": "Warp",
    "universal": "通用（跨平台）",
}


# ---------------------------------------------------------------------------
# 平台识别
# ---------------------------------------------------------------------------

def parse_frontmatter_name(content: str) -> str:
    """从 SKILL.md frontmatter 提取 name 字段"""
    block = re.match(r"^\s*---\s*\n([\s\S]*?)\n---", content)
    if not block:
        return ""
    match = re.search(r"^name:\s*['\"]?([^\r\n'\"]+)['\"]?\s*$", block.group(1), re.M)
    return match.group(1).strip() if match else ""


def classify_skill_type(skill_dir: Path) -> str:
    """按目录结构判断 Skill 类型"""
    if (skill_dir / "SKILL.md").exists():
        normalized_path = str(skill_dir).replace("\\", "/").lower()
        if "/.trae/skills/" in normalized_path:
            return "trae-skill"
        return "claude-skill"
    if (skill_dir / "skill.json").exists():
        return "json-skill"
    if (skill_dir / "package.json").exists():
        return "node-skill"
    return "unknown"


def infer_platforms_from_skill_md(skill_dir: Path) -> set:
    """从 SKILL.md 正文关键词推断支持平台"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return set()
    content = skill_md.read_text(encoding="utf-8", errors="ignore").lower()
    keyword_map = {
        "trae": "trae",
        "claude code": "claude-code",
        "(cc)": "cc",
        " cursor ": "cursor",
        "openclaw": "openclaw",
        "codex": "codex",
        "gemini cli": "gemini-cli",
        "aider": "aider",
        "windsurf": "windsurf",
        "kilo code": "kilo-code",
        "opencode": "opencode",
        "augment": "augment",
        "antigravity": "antigravity",
        "github copilot": "github-copilot",
        "kimi code cli": "kimi-code-cli",
        "cline": "cline",
        "amp": "amp",
        "warp": "warp",
        "skill.md-style": "universal",
        "跨平台": "universal",
    }
    detected = set()
    normalized = f" {content} "
    for keyword, platform_code in keyword_map.items():
        if keyword in normalized:
            detected.add(platform_code)
    return detected


def infer_platforms(skill_dir: Path, skill_type: str) -> list:
    """综合路径 + SKILL.md + skill.json 推断平台列表"""
    platforms = set()
    normalized_path = str(skill_dir).replace("\\", "/").lower()
    if "/.trae/skills/" in normalized_path:
        platforms.add("trae")
    if "/.agents/skills/" in normalized_path:
        platforms.add("universal")
    skill_json = skill_dir / "skill.json"
    if skill_json.exists():
        try:
            payload = json.loads(skill_json.read_text(encoding="utf-8"))
            for item in payload.get("platforms", []):
                value = str(item).strip().lower()
                if value:
                    platforms.add(value)
        except Exception:
            pass
    platforms.update(infer_platforms_from_skill_md(skill_dir))
    if skill_type == "trae-skill":
        platforms.add("trae")
    elif skill_type == "claude-skill":
        platforms.update(COMMON_PLATFORM_SET)
    elif skill_type == "node-skill":
        platforms.add("universal")
    if "claude-code" in platforms and "cc" in platforms:
        platforms.remove("cc")
    if not platforms:
        platforms.add("universal")
    return sorted(platforms)


def read_skill_name(skill_dir: Path) -> str:
    """读取 Skill 名称（按优先级：SKILL.md frontmatter > skill.json > package.json > 目录名）"""
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_frontmatter_name(content)
        if parsed:
            return parsed
    skill_json = skill_dir / "skill.json"
    if skill_json.exists():
        try:
            return json.loads(skill_json.read_text(encoding="utf-8")).get("name", skill_dir.name)
        except Exception:
            return skill_dir.name
    package_json = skill_dir / "package.json"
    if package_json.exists():
        try:
            return json.loads(package_json.read_text(encoding="utf-8")).get("name", skill_dir.name)
        except Exception:
            return skill_dir.name
    return skill_dir.name


def detect_skills(skills_dir: Path) -> list:
    """枚举目录下所有 Skill，返回基本信息列表"""
    candidates = []
    for child in skills_dir.iterdir():
        if not child.is_dir() or child.name in IGNORE_DIRS:
            continue
        if (
            (child / "SKILL.md").exists()
            or (child / "skill.json").exists()
            or (child / "package.json").exists()
        ):
            candidates.append(child)
    if (
        (skills_dir / "SKILL.md").exists()
        or (skills_dir / "skill.json").exists()
        or (skills_dir / "package.json").exists()
    ):
        candidates.append(skills_dir)
    normalized = sorted({item.resolve() for item in candidates})
    skills = []
    for item in normalized:
        skill_type = classify_skill_type(item)
        platforms = infer_platforms(item, skill_type)
        skills.append({
            "name": read_skill_name(item),
            "path": str(item),
            "type": skill_type,
            "type_zh": TYPE_NAME_ZH.get(skill_type, skill_type),
            "platforms": platforms,
            "platforms_zh": [PLATFORM_NAME_ZH.get(p, p) for p in platforms],
        })
    return skills


def format_platforms_zh(platforms: list) -> str:
    if not platforms:
        return "通用（跨平台）"
    return "、".join(PLATFORM_NAME_ZH.get(p, p) for p in platforms)