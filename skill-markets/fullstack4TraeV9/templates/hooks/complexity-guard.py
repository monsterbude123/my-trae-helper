#!/usr/bin/env python3
"""complexity-guard.py — V9.2 复杂度评估
UserPromptSubmit Hook: 评估需求复杂度，建议流程。

V9.2 变更: 新增"重置/方向变"信号检测
"""

import re
import sys
from pathlib import Path

user_prompt = os.environ.get("TRAE_USER_PROMPT", "") if "os" in dir() else ""
if not user_prompt:
    sys.exit(0)

try:
    user_prompt = Path(user_prompt).read_text(encoding="utf-8")
except Exception:
    pass

score = 0
signals = []

# ── V8 延续信号 ──
if re.search(r'refactor|重构|重写|rewrite', user_prompt, re.IGNORECASE):
    score += 3
    signals.append("重构")
if re.search(r'architecture|架构|database.*schema|数据.*迁移', user_prompt, re.IGNORECASE):
    score += 3
    signals.append("架构级变更")
if re.search(r'new.*feature|新功能|add.*support|integrate|集成', user_prompt, re.IGNORECASE):
    score += 2
    signals.append("新功能")
if re.search(r'multiple.*module|跨.*模块|several.*file|多.*文件', user_prompt, re.IGNORECASE):
    score += 2
    signals.append("多模块涉及")
if re.search(r'security|auth|permission|安全|权限|认证', user_prompt, re.IGNORECASE):
    score += 2
    signals.append("安全相关")
if re.search(r'api.*change|breaking|接口.*变更|contract|契约', user_prompt, re.IGNORECASE):
    score += 2
    signals.append("接口变更")

# ── V9.2 新增: 方向变/重置信号 ──
if re.search(r'重置|reset|重来|重新.*设计|重新.*方案|清理.*历史|从零|全部.*重写|推翻|推倒|废弃', user_prompt, re.IGNORECASE):
    score += 4
    signals.append("方向变/重置（铁律 11: 全量 _invalidated_）")
if re.search(r'UI.*改|UI.*重新|原型.*重|重新.*设计|UX.*重|visual.*change|design.*overhaul', user_prompt, re.IGNORECASE):
    score += 3
    signals.append("UI/UX 重设计（需重新生成 prototypes/）")

if score >= 4:
    print(f"[Complexity Guard] 严重度: CRITICAL ({score})")
    print(f"  信号: {', '.join(signals)}")
    print("  建议: 走完整 fullstack 流程 + 干净重置（铁律 11）")
elif score >= 3:
    print(f"[Complexity Guard] 严重度: HIGH ({score})")
    print(f"  信号: {', '.join(signals)}")
    print("  建议: 走 fullstack 完整流程")
elif score >= 1:
    print(f"[Complexity Guard] 严重度: MEDIUM ({score})")
    print(f"  信号: {', '.join(signals)}")
    print("  建议: 至少写 define + spec")
else:
    print(f"[Complexity Guard] 严重度: LOW")
    print("  建议: ponytail 模式")

sys.exit(0)
