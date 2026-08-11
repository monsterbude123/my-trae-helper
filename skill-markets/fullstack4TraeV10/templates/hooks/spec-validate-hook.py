#!/usr/bin/env python3
"""spec-validate-hook.py — V10.1 Spec 格式校验
PostToolUse Hook: 写 spec.md 后自动检查 Delta Spec 格式 + prototypes/ 完整性 + v10_simplified frontmatter。

SECURITY 标注（V10.12.2 NEW）: print() 输出风险已标注 — 实际仅校验信息。无外网、无破坏性命令。

V10.1 变更:
  - 支持 Delta Spec（ADDED/MODIFIED/REMOVED 段）
  - prototypes/ 检查改为两份文档（design-prompt.md + ui-ux-logic.md）
  - 移除 L0-L4 编号检查（V10 不再使用）
  - 移除 change_name 旧命名
  - V10.1 新增: 检测 v10_simplified frontmatter 而非 HTML 注释
"""

import sys
import os
import re
from pathlib import Path

file_path = os.environ.get("TRAE_FILE_PATH", "")

# 只处理 spec.md 文件
if not re.search(r'specs/.*/spec\.md$', file_path):
    sys.exit(0)

spec_file = Path(file_path)
if not spec_file.exists():
    print(f"[Fullstack Spec Validate] File not found: {file_path}")
    sys.exit(1)

try:
    content = spec_file.read_text(encoding="utf-8")
except Exception:
    print(f"[Fullstack Spec Validate] Cannot read: {file_path}")
    sys.exit(1)

issues = []

# ── 0. V10.1 v10_simplified frontmatter 检测 ──
if file_path.endswith("spec.md"):
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        if "v10_simplified" not in fm_text:
            issues.append("spec.md frontmatter 缺 v10_simplified 标记（V10 硬门禁要求）")

# ── 1. Delta Spec 格式检测 ──
is_delta = any(h in content for h in ("## ADDED", "## MODIFIED", "## REMOVED"))

if is_delta:
    # Delta 格式必须检查
    if "## ADDED" not in content and "## MODIFIED" not in content:
        issues.append("Delta Spec 缺少 ADDED 或 MODIFIED 段")
    if "#### Scenario:" not in content:
        issues.append("缺少 Scenario（格式: #### Scenario:）")
else:
    # 完整 Spec
    if "#### Scenario:" not in content:
        issues.append("缺少 Scenario（格式: #### Scenario:）")
    if "### Requirement:" not in content:
        issues.append("缺少 Requirement 定义")
    if not re.search(r'\bSHALL\b', content):
        issues.append("未使用 SHALL 表达契约")

# ── 2. 异常词汇检测 ──
fuzzy_words = re.findall(r'\b(should|maybe|大概|可能|尽量)\b', content, re.IGNORECASE)
if fuzzy_words:
    issues.append(f"含模糊词汇: {', '.join(fuzzy_words)} → 用 SHALL/SHALL NOT 替代")

# ── 3. prototypes/ 存在性校验（V9.2 两份文档）──
ui_tokens = [
    '页面', '界面', 'UI', '前端', '按钮', '表单', '组件', '画布',
    'component', 'page', 'screen', '视图', '对话框', '弹窗', '面板',
    'Panel', 'Modal', 'Table', 'Form', 'Dashboard', 'Canvas', 'Toolbar',
]

has_ui = any(tok in content for tok in ui_tokens)

if has_ui:
    m = re.search(r'docs[\\/]specs[\\/]([^\\/]+)[\\/]', file_path)
    if m:
        feature_name = m.group(1)
        proto_dir = Path(f"docs/specs/{feature_name}/prototypes")

        has_design = (proto_dir / "design-prompt.md").exists()
        has_ux = (proto_dir / "ui-ux-logic.md").exists()

        if not proto_dir.exists() or (not has_design and not has_ux):
            issues.append(
                f"涉及 UI 但 prototypes/ 缺少 V10 文档: "
                f"{'design-prompt.md ' if not has_design else ''}"
                f"{'ui-ux-logic.md' if not has_ux else ''}"
            )
            print(f"    💡 Run: spec-writer backfill mode → {feature_name}")

if issues:
    print(f"[Fullstack Spec Validate] FAILED for {file_path}:")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)

print(f"[Fullstack Spec Validate] PASSED for {file_path}")
sys.exit(0)
