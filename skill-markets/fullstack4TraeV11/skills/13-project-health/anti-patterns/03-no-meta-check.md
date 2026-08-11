# 反例 3：self-diagnose 未跑

**违反**: 铁律 7 self-diagnose

**现象**: project-health-auditor 自身可能失真但未检测。

**正确替代**: 必跑 self-diagnose.py 检测 auditor 自身（meta 元检测）。