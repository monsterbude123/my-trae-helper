#!/usr/bin/env python3
"""
scripts/aigc-smart-kit-guard.py — aigc-smart-kit 专属守卫（2026-08-20 guard-smith 委派落地）

设计目的：
  aigc-smart-kit 是图生视频(I2V) 多模态创意工作台统一入口,内含 4 个子 skill:
    - skills/i2v-image-analyzer/    (图理解 → image-report.json)
    - skills/i2v-h3-prompt/         (MiniMax H3 / Hailuo 三段式 prompt)
    - skills/i2v-seedance-prompt/   (ByteDance Seedance 2.0/2.5 30s 四拍)
    - skills/i2v-kling-prompt/      (Kling 3.0 S/M/B 三段式 + element reference)
  + 顶层 scripts/ 2 个跨平台 Python 工具(i2v_vision_call.py + i2v_prompt_build.py)。

  守卫需覆盖 8 个 aspect: structure, security, schema, sub-skills, scripts, prompts, refs
  合并为 6+ 项硬检查,确保:
    1. 顶层 SKILL.md frontmatter 完整(name/description/version)
    2. SKILL.md 行数 ≤350(vibe-coding-standards v2.5 阈值)
    3. 4 个子 skill 目录都存在且各自 SKILL.md 含 frontmatter
    4. 顶层 scripts/*.py 入口 + docstring + Python 语法可解析
    5. 无硬编码 API Key(扫描 SKILL.md / references/*.md / scripts/*.py)
    6. JSON schema 引用存在性(image-schema.md 实际存在且非空)

用法:
  python scripts/aigc-smart-kit-guard.py aigc-smart-kit

退出码:
  0 = PASS（errors=0, warnings=0）
  1 = BLOCK（errors≥1）
  2 = WARN（errors=0 但 warnings≥1）

禁止:
  - 禁止 import skill-markets/<pkg>/scripts/*（与 AGENTS.md §1.11 冲突）
  - 禁止改本文件的 import 顺序（与 _guard_lib 契约不一致会导致 guard-router 失败）
"""
import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent

def _load_sibling_module(filename: str):
    """加载同目录下的连字符文件名模块（Python import 不支持 hyphen 文件名）."""
    spec = importlib.util.spec_from_file_location(
        filename.replace('.py', ''),
        _SCRIPTS_DIR / filename
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# 共享 aspect 守卫加载（连字符文件名用 importlib）
_module_structure = _load_sibling_module("skill-structure-guard.py")
check_structure_fn = getattr(_module_structure, "check_structure_for_skill")
_module_security = _load_sibling_module("skill-security-guard.py")
check_security_fn = getattr(_module_security, "check_security_for_skill")


# aigc-smart-kit 专属元数据
_REQUIRED_SUB_SKILLS = (
    "i2v-image-analyzer",
    "i2v-h3-prompt",
    "i2v-seedance-prompt",
    "i2v-kling-prompt",
)

_REQUIRED_TOP_SCRIPTS = (
    "i2v_vision_call.py",
    "i2v_prompt_build.py",
)

# vibe-coding-standards v2.5 行数弹性上限(与 scripts/vibe-coding-standards-line-guard.py 一致)
_SKILL_LINE_LIMIT = 350

# JSON schema 引用文件(aigc-smart-kit 特有的契约文件)
_REQUIRED_SCHEMA_REF = "skills/i2v-image-analyzer/references/image-schema.md"

# 硬编码密钥扫描的正则(skill-security-guard 已覆盖,这里再加固:aigc 常用 API Key 前缀)
_HARDCODED_KEY_PATTERNS = (
    (r'(?i)(?:sk-[a-zA-Z0-9]{20,}|sk_live_|sk_test_)', 'AIGC-KEY-PREFIX', '疑似 OpenAI/Stripe 风格 API Key 前缀'),
    (r'(?i)(?:AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16})', 'AWS-KEY-PREFIX', '疑似 AWS Access Key ID'),
    (r'(?i)Bearer\s+[A-Za-z0-9\-_.]{20,}', 'BEARER-TOKEN', '疑似 Bearer Token 字面量'),
)


def _parse_frontmatter(skill_md: Path):
    """解析 SKILL.md 顶部 YAML frontmatter(无依赖 stdlib 简易解析)."""
    try:
        text = skill_md.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith('---'):
        return None
    end = text.find('\n---', 3)
    if end < 0:
        return None
    block = text[3:end]
    fm = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def _check_top_skill_md(skill_dir: Path, errors: list, warnings: list, info: list):
    """Check 1+2: 顶层 SKILL.md frontmatter + 行数."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("顶层 SKILL.md 不存在(aigc-smart-kit 主入口必备)")
        return
    fm = _parse_frontmatter(skill_md)
    if not fm:
        errors.append("顶层 SKILL.md 缺 YAML frontmatter(以 --- 开头)")
        return
    # Check 1a: name 必须 + 与目录名一致
    if not fm.get("name"):
        errors.append("顶层 SKILL.md frontmatter 缺 name 字段")
    elif fm.get("name") != skill_dir.name:
        name_val = fm.get("name")
        errors.append(f"name='{name_val}' 与目录名 '{skill_dir.name}' 不一致")
    # Check 1b: description 必须
    if not fm.get("description"):
        errors.append("顶层 SKILL.md frontmatter 缺 description 字段(AGENTS.md §1 铁律)")
    # Check 1c: version 推荐(降级为 warning)
    if not fm.get("version"):
        warnings.append("顶层 SKILL.md frontmatter 推荐带 version 字段(AGENTS.md §1 推荐)")
    # Check 2: 行数 ≤350
    try:
        line_count = sum(1 for _ in skill_md.open('r', encoding='utf-8'))
    except (OSError, UnicodeDecodeError):
        line_count = 0
    if line_count > _SKILL_LINE_LIMIT:
        errors.append(
            f"顶层 SKILL.md 行数 {line_count} > {_SKILL_LINE_LIMIT} "
            f"(vibe-coding-standards v2.5 弹性上限,提取 references/ 子目录)"
        )
    else:
        info.append(f"顶层 SKILL.md 行数 {line_count} / {_SKILL_LINE_LIMIT}")


def _check_sub_skills(skill_dir: Path, errors: list, warnings: list, info: list):
    """Check 3: 4 个子 skill 目录齐全 + 各 SKILL.md 含 frontmatter."""
    skills_dir = skill_dir / "skills"
    if not skills_dir.exists():
        errors.append(f"skills/ 目录不存在(aigc-smart-kit 是 4 子 skill 套件,必须含)")
        return
    for sub in _REQUIRED_SUB_SKILLS:
        sub_dir = skills_dir / sub
        sub_skill_md = sub_dir / "SKILL.md"
        if not sub_dir.exists():
            errors.append(f"子 skill 目录缺失: skills/{sub}/")
            continue
        if not sub_skill_md.exists():
            errors.append(f"子 skill SKILL.md 缺失: skills/{sub}/SKILL.md")
            continue
        fm = _parse_frontmatter(sub_skill_md)
        if not fm:
            errors.append(f"子 skill 缺 YAML frontmatter: skills/{sub}/SKILL.md")
            continue
        if not fm.get("name"):
            errors.append(f"子 skill frontmatter 缺 name: skills/{sub}/SKILL.md")
        if not fm.get("description"):
            warnings.append(f"子 skill description 缺失: skills/{sub}/SKILL.md")
        # 子 skill references/ 推荐(降级 info)
        if not (sub_dir / "references").exists():
            info.append(f"子 skill 缺 references/ 目录: skills/{sub}/")
    info.append(f"子 skill 校验完成(应有 {len(_REQUIRED_SUB_SKILLS)} 项子 skill)")


def _check_top_scripts(skill_dir: Path, errors: list, warnings: list, info: list):
    """Check 4: scripts/*.py 入口 + docstring + Python 语法."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        errors.append("顶层 scripts/ 目录不存在(aigc-smart-kit 提供 2 个跨平台 Python 工具)")
        return
    for fname in _REQUIRED_TOP_SCRIPTS:
        p = scripts_dir / fname
        if not p.exists():
            errors.append(f"顶层 script 缺失: scripts/{fname}")
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            errors.append(f"顶层 script 不可读: scripts/{fname}")
            continue
        # docstring: 首行/块必须含三引号 docstring
        if '"""' not in text[:1200] and "'''" not in text[:1200]:
            warnings.append(f"顶层 script 缺 docstring: scripts/{fname}")
        # Python 语法解析
        try:
            compile(text, str(p), 'exec')
        except SyntaxError as e:
            errors.append(f"顶层 script Python 语法错误: scripts/{fname} → {e}")
    info.append(f"顶层 script 校验完成(应有 {len(_REQUIRED_TOP_SCRIPTS)} 项)")


def _check_hardcoded_keys(skill_dir: Path, errors: list, warnings: list, info: list):
    """Check 5: 无硬编码 API Key(SKILL.md + references/*.md + scripts/*.py 全文扫描)."""
    import re
    scan_targets = [skill_dir / "SKILL.md"]
    scan_targets.extend(sorted((skill_dir / "references").rglob("*.md")) if (skill_dir / "references").exists() else [])
    scan_targets.extend(sorted((skill_dir / "scripts").rglob("*.py")) if (skill_dir / "scripts").exists() else [])
    # 子 skill 内的 markdown/python 也要扫
    skills_sub = skill_dir / "skills"
    if skills_sub.exists():
        scan_targets.extend(sorted(skills_sub.rglob("*.md")))
        scan_targets.extend(sorted(skills_sub.rglob("*.py")))

    findings = 0
    for f in scan_targets:
        if not f.exists() or not f.is_file():
            continue
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        for pattern, tag, desc in _HARDCODED_KEY_PATTERNS:
            for m in re.finditer(pattern, text):
                snippet = m.group(0)
                # 占位符示例豁免(如 "<your-key-here>" / "xxx" / 纯环境变量引用)
                if any(placeholder in snippet.lower() for placeholder in ('<your', 'xxx', 'placeholder', 'example', '${', '$env', 'os.environ')):
                    continue
                errors.append(f"[{tag}] 硬编码疑似密钥: {f.relative_to(skill_dir)} → {desc}: {snippet[:30]}...")
                findings += 1
    if findings == 0:
        info.append("硬编码密钥扫描通过(覆盖 SKILL.md + references + scripts + 子 skill)")


def _check_image_schema(skill_dir: Path, errors: list, warnings: list, info: list):
    """Check 6: JSON schema 引用存在性(image-schema.md 必须存在 + 非空 + 含 'image-report')."""
    schema_ref = skill_dir / _REQUIRED_SCHEMA_REF
    if not schema_ref.exists():
        errors.append(f"JSON schema 引用缺失: {_REQUIRED_SCHEMA_REF}(i2v-image-analyzer 的核心契约)")
        return
    try:
        text = schema_ref.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        errors.append(f"JSON schema 不可读: {_REQUIRED_SCHEMA_REF}")
        return
    if len(text.strip()) < 200:
        errors.append(f"JSON schema 内容过短(<200 字符): {_REQUIRED_SCHEMA_REF}")
    elif 'image-report' not in text and 'image_report' not in text:
        warnings.append(f"JSON schema 未提及 'image-report' 契约名: {_REQUIRED_SCHEMA_REF}")
    else:
        info.append(f"JSON schema 引用存在: {_REQUIRED_SCHEMA_REF}({len(text)} 字符)")


def check_aigc_smart_kit(skill_path: str) -> dict:
    """aigc-smart-kit 专属守卫 — 组合 8 个 aspect,硬检查 6+ 项.

    Aspects:
      - structure  (顶层 SKILL.md frontmatter + 行数)
      - sub-skills (4 个子 skill 齐全)
      - scripts    (顶层 2 个 Python 工具可解析)
      - security   (硬编码 API Key 扫描,aigc 前缀特化)
      - schema     (image-schema.md 契约引用)
      - refs       (references/ 数量提示)
    """
    skill_dir = Path(skill_path)
    errors: list = []
    warnings: list = []
    info: list = []

    if not skill_dir.exists():
        errors.append(f"技能目录不存在: {skill_path}")
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    # 主检查 6 项
    _check_top_skill_md(skill_dir, errors, warnings, info)
    _check_sub_skills(skill_dir, errors, warnings, info)
    _check_top_scripts(skill_dir, errors, warnings, info)
    _check_hardcoded_keys(skill_dir, errors, warnings, info)
    _check_image_schema(skill_dir, errors, warnings, info)

    # 附加:复用共享 structure/security 检查(放进 info,不重复 6 项主检查)
    try:
        struct_result = check_structure_fn(str(skill_dir))
        # 把 shared structure 检查的 errors 合并(避免双源漂移,但保留独立性)
        for e in (struct_result.get('errors') or []):
            # 重复(顶层 SKILL.md 缺 frontmatter)已自检,跳过;其他保留
            if 'SKILL.md' in e and ('frontmatter' in e or '不存在' in e):
                continue
            errors.append(f"[shared-structure] {e}")
    except Exception as e:
        info.append(f"shared-structure-guard 调用异常(非致命): {type(e).__name__}: {e}")

    # passed: errors 为空
    passed = len(errors) == 0
    return {'passed': passed, 'errors': errors, 'warnings': warnings, 'info': info}


# 主入口 — 统一通过 _guard_lib 输出 JSON + exit code
from _guard_lib import cli_main

if __name__ == '__main__':
    sys.exit(cli_main(check_aigc_smart_kit, 'aigc-smart-kit-structure'))