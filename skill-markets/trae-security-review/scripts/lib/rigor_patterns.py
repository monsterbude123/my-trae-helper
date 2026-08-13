"""
Rigor Pattern Registry — 严谨用词模式注册表

按类别组织中英文触发模式，供 rigor_scanner.py 加载。
新增模式：在 RIGOR_PATTERNS 追加条目，遵循
references/rigor-patterns.md 的 schema。
"""

from __future__ import annotations

import re
from typing import Callable, List, NamedTuple


class RigorRule(NamedTuple):
    code: str
    category: str
    severity: str
    description: str
    patterns: List[re.Pattern]
    suggestion: str


def _zh(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def _en(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


# --- EMOTIONAL_TONE 情绪化用词 ---------------------------------------------
EMOTIONAL_TONE = RigorRule(
    code="EMOTIONAL_TONE",
    category="情绪化用词",
    severity="low",
    description="非事实性形容词 / 感叹词，影响文档专业性",
    patterns=_zh([
        r"非常好用",
        r"非常强大",
        r"非常方便",
        r"非常高效",
        r"非常棒",
        r"极其",
        r"完美",
        r"极致",
        r"超棒",
        r"超好",
        r"满分",
        r"超快",
        r"绝佳",
    ]) + _en([
        r"\bawesome\b",
        r"\bamazing\b",
        r"\bperfect(?:ly)?\b",
        r"\bexcellent\b",
        r"\b(fantastic|brilliant|outstanding)\b",
        r"\bwow\b",
    ]),
    suggestion="删除或改为可验证的描述（如“通过 X 项验证”）",
)

# --- ABSOLUTE_CLAIM 绝对断言 -----------------------------------------------
ABSOLUTE_CLAIM = RigorRule(
    code="ABSOLUTE_CLAIM",
    category="绝对断言",
    severity="low",
    description="无可证伪条件的绝对论断，违反严谨表达",
    patterns=_zh([
        r"100\s*%",
        r"百分百",
        r"零风险",
        r"零缺陷",
        r"零漏洞",
        r"完全可靠",
        r"绝对安全",
        r"绝不会",
        r"不可能失败",
        r"永远不会",
    ]) + _en([
        r"\b100\s*%",
        r"\bzero[-\s]?risk\b",
        r"\babsolutely\s+safe\b",
        r"\bnever\s+fails?\b",
        r"\bguaranteed\b",
    ]),
    suggestion="改为带条件的陈述（如“在 X 条件下验证通过”）",
)

# --- VAGUE_QUANTIFIER 模糊量化 ---------------------------------------------
VAGUE_QUANTIFIER = RigorRule(
    code="VAGUE_QUANTIFIER",
    category="模糊量化",
    severity="low",
    description="不指向具体数字的量词，难以验证",
    patterns=_zh([
        r"大量",
        r"少量",
        r"不少",
        r"很多",
        r"一大堆",
        r"一点点",
        r"差不多",
        r"几乎都",
        r"基本上都",
        r"多数情况下",
        r"大部分都",
    ]) + _en([
        r"\b(lots|lot|a lot)\s+of\b",
        r"\b(many|several|some|few)\b",
        r"\b(fairly|pretty|kind\s+of)\b",
    ]),
    suggestion="改为具体数值（“N 项 / ≤ N / ≥ N”）",
)

# --- INCLUSIVE_HEDGE 兜底模糊 ----------------------------------------------
INCLUSIVE_HEDGE = RigorRule(
    code="INCLUSIVE_HEDGE",
    category="兜底模糊",
    severity="medium",
    description="以“等”收尾未穷尽列表，违背严谨枚举",
    patterns=_zh([
        r"等等",
        r"等[、，]",
        r"等等等",
        r"诸如此类",
        r"以此类推",
        r"以及诸?多",
        r"包括但不限于",
    ]),
    suggestion="若项数有限 → 全部列出；若项数较多 → 补充“省略其余 N 项”或加“等 50 类”",
)

# --- UNDEFINED_TERM 未定义术语 ---------------------------------------------
UNDEFINED_TERM = RigorRule(
    code="UNDEFINED_TERM",
    category="未定义术语",
    severity="medium",
    description="指代对象不明确，违反可追溯原则",
    patterns=_zh([
        r"特殊情况",
        r"特殊场景",
        r"极端情况",
        r"某些情况",
        r"某种情况",
        r"某些场景",
        r"相关[情况场景]",
        r"相应[的]?处理",
    ]) + _en([
        r"\b(edge|corner)\s+cases?\b",
        r"\bspecial\s+cases?\b",
        r"\bunder\s+certain\b",
        r"\bsome\s+cases?\b",
    ]),
    suggestion="明确枚举触发条件或引用具体章节",
)

# --- DEAD_ANGLE_MARKER 死角提示词 ------------------------------------------
DEAD_ANGLE_MARKER = RigorRule(
    code="DEAD_ANGLE_MARKER",
    category="死角提示词",
    severity="medium",
    description="含常规/通常意义的修饰词掩盖未覆盖场景",
    patterns=_zh([
        r"一般情况下",
        r"通常情况下",
        r"一般来说",
        r"原则上",
        r"理想情况下",
        r"默认情况下",
        r"大多数情况下",
        r"一般场景",
        r"常规场景",
    ]) + _en([
        r"\bgenerally\b",
        r"\btypically\b",
        r"\busually\b",
        r"\bin\s+most\s+cases?\b",
        r"\bby\s+default\b",
    ]),
    suggestion="提供统计或显式边界，若不能则改为“在配置 X 时”",
)

# --- PERSONAL_OPINION 主观判断 ---------------------------------------------
PERSONAL_OPINION = RigorRule(
    code="PERSONAL_OPINION",
    category="主观判断",
    severity="low",
    description="第一人称或主观判断词，缺乏依据",
    patterns=_zh([
        r"我觉得",
        r"我认为",
        r"个人觉得",
        r"我想",
        r"应该[会]?",
        r"想必",
        r"估计",
    ]) + _en([
        r"\bi\s+(?:think|believe|guess|feel)\b",
        r"\bin\s+my\s+opinion\b",
        r"\bshould\s+(?:be|probably)\b",
    ]),
    suggestion="改为引证（如“依据 X 规范 / 实测 N = ...”）",
)

# --- PROHIBITED_PHRASE 禁用短语 --------------------------------------------
PROHIBITED_PHRASE = RigorRule(
    code="PROHIBITED_PHRASE",
    category="禁用短语",
    severity="low",
    description="评价性短语，不提供证据",
    patterns=_zh([
        r"显而易见",
        r"毫无疑问",
        r"显然",
        r"不言而喻",
        r"理所当然",
        r"众所周知",
        r"显然易见",
        r"自不必说",
    ]) + _en([
        r"\bobviously\b",
        r"\bundoubtedly\b",
        r"\bwithout\s+doubt\b",
        r"\bclearly\b",
        r"\b众所周知\b",
    ]),
    suggestion="删除或提供证据 / 引用",
)

# --- OVER_PROMISE 过度承诺 -------------------------------------------------
OVER_PROMISE = RigorRule(
    code="OVER_PROMISE",
    category="过度承诺",
    severity="medium",
    description="夸大实现难度或省略前提条件",
    patterns=_zh([
        r"一键搞定",
        r"一键解决",
        r"轻松实现",
        r"轻松完成",
        r"分分钟",
        r"速成",
        r"无脑",
        r"傻瓜式",
        r"毫不费力",
    ]) + _en([
        r"\bone[-\s]?click\b",
        r"\beffortlessly\b",
        r"\bin\s+no\s+time\b",
    ]),
    suggestion="补充先决条件与代价",
)

# --- UNMEASURED_BENEFIT 不可量化收益 --------------------------------------
UNMEASURED_BENEFIT = RigorRule(
    code="UNMEASURED_BENEFIT",
    category="不可量化收益",
    severity="low",
    description="收益描述无可测量指标",
    patterns=_zh([
        r"提升效率",
        r"改善体验",
        r"优化性能",
        r"更快(?!.*\d)",
        r"更稳(?!.*\d)",
        r"更安全(?!.*\d)",
        r"更强(?!.*\d)",
    ]) + _en([
        r"\bimprove(?:s|d)?\s+performance\b",
        r"\benhance(?:s|d)?\s+experience\b",
        r"\bbetter\s+performance\b",
    ]),
    suggestion="改为带单位的量化指标（“延迟从 X 降到 Y ms”）",
)


RIGOR_RULES: List[RigorRule] = [
    EMOTIONAL_TONE,
    ABSOLUTE_CLAIM,
    VAGUE_QUANTIFIER,
    INCLUSIVE_HEDGE,
    UNDEFINED_TERM,
    DEAD_ANGLE_MARKER,
    PERSONAL_OPINION,
    PROHIBITED_PHRASE,
    OVER_PROMISE,
    UNMEASURED_BENEFIT,
]
