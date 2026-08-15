#!/usr/bin/env python3
"""V11 complexity-guard.py — UserPromptSubmit Hook（蒸馏自 V10）

评估需求复杂度，建议流程。

V11 简化:
  - 增加 gitnexus / GitNexus First 检测
  - 增加 Article XVII secret 误用警告

V11.2 硬化（2026-08-14）:
  - score >= 8: 强制用户确认（写阻塞标记 + exit 1）
  - score >= 5: 仅提示，不阻断
  - 阻塞标记文件: .trae/complexity-blocked
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path.cwd()
BLOCK_MARKER = PROJECT_ROOT / ".trae" / "complexity-blocked"


user_prompt = os.environ.get("TRAE_USER_PROMPT", "")
if not user_prompt:
    sys.exit(0)

try:
    user_prompt = Path(user_prompt).read_text(encoding="utf-8")
except Exception:
    pass

score = 0
signals = []

# ── V10 延续信号 ──
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

# ── V10 方向变/重置信号 ──
if re.search(r'重置|reset|重来|重新.*设计|重新.*方案|清理.*历史|从零|全部.*重写|推翻|推倒|废弃', user_prompt, re.IGNORECASE):
    score += 4
    signals.append("方向变/重置（V11: spec-purge.py archive/out/）")
if re.search(r'UI.*改|UI.*重新|原型.*重|重新.*设计|UX.*重|visual.*change|design.*overhaul', user_prompt, re.IGNORECASE):
    score += 3
    signals.append("UI/UX 重设计（需重新生成 prototypes/）")

# ── V11 NEW: GitNexus First 检测（提醒跑 gitnexus）──
if re.search(r'改.*实现|改.*函数|改.*模块|改.*接口|修改.*实现', user_prompt, re.IGNORECASE):
    score += 1
    signals.append("V11 Article V.5: 改 symbol 前必跑 gitnexus impact()")

# ── V11 NEW: Article XVII secret 检测 ──
if re.search(r'密码|password|token|api.*key|secret|凭据', user_prompt, re.IGNORECASE):
    score += 2
    signals.append("V11 Article XVII: 涉及 secret — 必走环境变量")

# ── V11 NEW: code-hygiene.py 调用结果检测 ──
code_hygiene_results = Path("code-hygiene-results.json")
if code_hygiene_results.exists():
    try:
        import json
        data = json.loads(code_hygiene_results.read_text(encoding="utf-8"))
        if data.get("hygiene_score", 5.0) < 3.0:
            score += 3
            signals.append("code-hygiene 检测不达标（< 3.0）")
        elif data.get("hygiene_score", 5.0) < 4.0:
            score += 1
            signals.append("code-hygiene 检测告警（< 4.0）")
    except Exception:
        pass

# V11.2 硬化阈值
if score >= 8:
    # BLOCK: 写阻塞标记 + exit 1
    print(f"[V11.2 Complexity Guard] 🛑 BLOCKED ({score})")
    print(f"  信号: {', '.join(signals)}")
    print("  建议: 需要用户显式确认")
    print("  阻塞标记: .trae/complexity-blocked")
    
    # 写阻塞标记文件
    BLOCK_MARKER.parent.mkdir(parents=True, exist_ok=True)
    block_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "signals": signals,
        "user_prompt": user_prompt[:500],  # 截断避免文件过大
    }
    BLOCK_MARKER.write_text(
        json.dumps(block_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    # 阻塞退出
    sys.exit(1)

elif score >= 5:
    # WARNING: 仅提示，不阻断
    print(f"[V11.2 Complexity Guard] ⚠️ WARNING ({score})")
    print(f"  信号: {', '.join(signals)}")
    print("  建议: 高复杂度任务，建议走 fullstack 流程 + 仔细规划")
    sys.exit(0)

elif score >= 3:
    print(f"[V11 Complexity Guard] 严重度: HIGH ({score})")
    print(f"  信号: {', '.join(signals)}")
    print("  建议: 走 fullstack 流程")
    sys.exit(0)

elif score >= 1:
    print(f"[V11 Complexity Guard] 严重度: LOW ({score})")
    print(f"  信号: {', '.join(signals)}")
    sys.exit(0)

else:
    print(f"[V11 Complexity Guard] 严重度: MINIMAL ({score})")
    sys.exit(0)