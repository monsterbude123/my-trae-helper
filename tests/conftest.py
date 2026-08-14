"""主仓 conftest.py — 隔离子包 test 收集

背景:
  - 主仓 `tests/unit/test_*.py` 跑 pytest
  - 仓库内 `skill-markets/agent-dev-control-kit/tests/` 也是 pytest 套件
  - 若主仓 pytest 跨过 rootdir 边界,会吸入子包 conftest + autouse fixture
  - 反过来子包 wrapper 也不应跑主仓测试

本 conftest 用 `collect_ignore_glob` 排除跨包路径,确保主仓 pytest 严格在
`tests/` 范围内收集。

不动子包的 pytest.ini / conftest.py — 子包是子包,主仓是主仓。
"""
from __future__ import annotations

# collect_ignore_glob 是 pytest 顶层 hook,接受 glob 列表
# 任何匹配的文件/目录在收集阶段被忽略
#
# 注意:glob 是相对于 rootdir 的;主仓根 = D:\workspace\my-trae-helper
# "skill-markets" 任何子包 tests/ 都不在主仓收集范围。
collect_ignore_glob = [
    "skill-markets/**/tests/**",
    "skill-markets/**/tests",
]
