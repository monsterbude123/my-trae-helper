#!/usr/bin/env python3
"""V11 spec-validate-hook.py — PostToolUse Hook（蒸馏自 V10）

写 spec.md 后自动检查格式（Delta Spec + Scenario + SHALL）+ prototypes/ 完整性。
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
    print(f"[V11 Spec Validate] File not found: {file_path}")
    sys.exit(1)

try:
    content = spec_file.read_text(encoding="utf-8")
except Exception:
    print(f"[V11 Spec Validate] Cannot read: {file_path}")
    sys.exit(1)

issues = []

# ── Delta Spec 格式检测 ──
is_delta = any(h in content for h in ("## ADDED", "## MODIFIED", "## REMOVED"))

if is_delta:
    if "## ADDED" not in content and "## MODIFIED" not in content:
        issues.append("Delta Spec 缺少 ADDED 或 MODIFIED 段")
    if "#### Scenario:" not in content:
        issues.append("缺少 Scenario（格式: #### Scenario:）")
else:
    if "#### Scenario:" not in content:
        issues.append("缺少 Scenario（格式: #### Scenario:）")
    if "### Requirement:" not in content:
        issues.append("缺少 Requirement 定义")
    if not re.search(r'\bSHALL\b', content):
        issues.append("未使用 SHALL 表达契约")

# ── 异常词汇检测 ──
fuzzy_words = re.findall(r'\b(should|maybe|大概|可能|尽量)\b', content, re.IGNORECASE)
if fuzzy_words:
    issues.append(f"含模糊词汇: {', '.join(set(fuzzy_words))} → 用 SHALL/SHALL NOT 替代")

# ── prototypes/ 存在性校验（UI 类 spec 必含）──
ui_tokens = [
    '页面', '界面', 'UI', '前端', '按钮', '表单', '组件', '画布',
    'component', 'page', 'screen', '视图', '对话框', '弹窗', '面板',
    'Panel', 'Modal', 'Table', 'Form', 'Dashboard', 'Canvas', 'Toolbar',
]

has_ui = any(tok in content for tok in ui_tokens)

if has_ui:
    m = re.search(r'docs[\\/]specs[\\/]changes[\\/]([^\\/]+)[\\/]', file_path)
    if m:
        feature_name = m.group(1)
        proto_dir = Path(f"docs/specs/changes/{feature_name}/prototypes")
        if not proto_dir.exists():
            issues.append(f"UI 类 spec 缺 prototypes/ 目录（feature: {feature_name}）")
        else:
            has_design = (proto_dir / "design-prompt.md").exists()
            has_ux = (proto_dir / "ui-ux-logic.md").exists()
            if not has_design or not has_ux:
                missing = []
                if not has_design:
                    missing.append("design-prompt.md")
                if not has_ux:
                    missing.append("ui-ux-logic.md")
                issues.append(f"prototypes/ 缺 {' 和 '.join(missing)}")

if issues:
    print(f"[V11 Spec Validate] ⚠️ spec.md 格式问题 ({len(issues)} 项):")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)

print(f"[V11 Spec Validate] ✅ spec.md 格式 OK")
sys.exit(0)