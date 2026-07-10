"""
Markdown剧本解析器
将特定格式的Markdown表格解析为结构化数据
"""

from __future__ import annotations
import re

from vaslib.types.script import ParsedScript, ScriptMeta, Character, Scene, TimeRange, Line, LineType

CHARACTER_ID_MAP: dict[str, str] = {
    "貔貅": "pixiu",
    "老龟": "laogui",
    "凤": "feng",
    "龙": "long",
    "麒麟": "qilin",
}

GENDER_MAP: dict[str, str] = {
    "貔貅": "male",
    "老龟": "male",
    "凤": "female",
    "龙": "male",
    "麒麟": "male",
}

_DIALECT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"渝普|川渝"), "渝普"),
    (re.compile(r"东北"), "东北口音"),
    (re.compile(r"沪普|上海"), "沪普"),
    (re.compile(r"北京"), "北京口音"),
    (re.compile(r"天津"), "天津口音"),
]

_EMOTION_KEYWORDS: dict[str, str] = {
    "反差萌": "反差萌",
    "无厘头": "无厘头",
    "愤怒": "愤怒",
    "开心": "开心",
    "悲伤": "悲伤",
    "恐惧": "恐惧",
    "深情": "深情",
    "傲娇": "傲娇",
    "痞气": "痞气",
    "惊慌": "惊慌",
    "严肃": "严肃",
    "淡定": "淡定",
    "夸张": "夸张",
    "从容": "从容",
}

_LOCATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(.+?家)"),
    re.compile(r"(.+?室)"),
    re.compile(r"(.+?厅)"),
    re.compile(r"(.+?医院)"),
]


def parse_time_range(time_str: str) -> TimeRange:
    """解析 "MM:SS~MM:SS" 格式的时间范围"""
    normalized = time_str.replace("\\~", "~").strip()
    match = re.match(r"(\d{2}):(\d{2})~(\d{2}):(\d{2})", normalized)
    if not match:
        raise ValueError(f"Invalid time range format: {time_str}")
    start_seconds = int(match.group(1)) * 60 + int(match.group(2))
    end_seconds = int(match.group(3)) * 60 + int(match.group(4))
    return TimeRange(start_seconds=start_seconds, end_seconds=end_seconds)


def extract_dialect_hint(detail: str) -> str:
    """从角色详情中提取方言提示"""
    for pattern, hint in _DIALECT_PATTERNS:
        if pattern.search(detail):
            return hint
    return ""


def extract_personality_from_detail(detail: str, dialect_hint: str) -> str:
    """从角色详情中提取性格描述，去掉方言关键词和括号内容"""
    result = detail
    if dialect_hint:
        escaped = re.escape(dialect_hint)
        result = re.sub(escaped, "", result)

    # 替换括号内容，保留内部文本
    result = re.sub(
        r"[（(][^）)]*[）)]",
        lambda m: m.group(0)[1:-1].strip(),
        result,
    )
    result = result.replace("性格外化", "")
    result = re.sub(r"\s+", " ", result).strip()
    return result


def infer_age(name: str, detail: str) -> str:
    """推断角色年龄段"""
    if re.search(r"大爷|老", detail) or name == "老龟":
        return "elderly"
    if re.search(r"童|小", detail):
        return "child"
    return "middle"


def extract_characters(meta_section: str) -> list[Character]:
    """解析人物元信息section"""
    characters: list[Character] = []
    segments = meta_section.split()
    segments = [s for s in segments if s]

    current_name = ""
    current_detail = ""
    in_parentheses = False

    for segment in segments:
        name_match = re.match(r"^([^：:]+)[：:](.*)$", segment)

        if name_match and not in_parentheses:
            if current_name and current_detail:
                _push_character(characters, current_name, current_detail)
            current_name = name_match.group(1)
            current_detail = name_match.group(2)
            in_parentheses = False
        else:
            current_detail += (" " if current_detail else "") + segment

        if "(" in current_detail and ")" not in current_detail:
            in_parentheses = True
        if ")" in current_detail:
            in_parentheses = False

    if current_name and current_detail:
        _push_character(characters, current_name, current_detail)

    return characters


def _push_character(
    characters: list[Character], name: str, detail: str
) -> None:
    """构建并添加角色对象"""
    if name not in CHARACTER_ID_MAP:
        return

    clean_detail = re.sub(r"配音为?\s*", "", detail).strip()
    dialect_hint = extract_dialect_hint(clean_detail)
    personality = extract_personality_from_detail(clean_detail, dialect_hint)

    characters.append(
        Character(
            id=CHARACTER_ID_MAP[name],
            name=name,
            gender=GENDER_MAP.get(name, "other"),
            age=infer_age(name, clean_detail),
            personality=personality,
            dialect_hint=dialect_hint,
        )
    )


def clean_text(text: str) -> str:
    """清理台词文本中的转义字符"""
    return re.sub(r'\\["]', '"', text).strip()


def parse_dialogue(cell_content: str, scene_id: str) -> list[Line]:
    """解析台词单元格"""
    lines: list[Line] = []
    line_counter = 0

    normalized = cell_content
    normalized = normalized.replace("\\!", "!")
    normalized = normalized.replace("\\~", "~")
    normalized = normalized.replace("\\*", "*")
    normalized = normalized.replace("\\\\", "\\")

    # 匹配模式：角色名(修饰符):"台词" 或 角色名:"台词"
    # 支持中文引号 " " 和英文引号 " "
    left_quote = "\u201c"
    right_quote = "\u201d"
    pattern = re.compile(
        rf'([^：:\s]+?)(?:\(([^)]*)\))?\s*[：:]\s*[{left_quote}"]([^{right_quote}"]*?)[{right_quote}"]'
    )

    for match in pattern.finditer(normalized):
        char_name = match.group(1).strip()
        modifier = (match.group(2) or "").strip()
        text = match.group(3).strip()

        character_id = CHARACTER_ID_MAP.get(char_name)
        if modifier.upper() == "OS":
            line_type: LineType = "narration"
        else:
            line_type = "dialogue"

        line_counter += 1
        lines.append(
            Line(
                id=f"{scene_id}-line-{line_counter}",
                type=line_type,
                character_id=character_id,
                text=clean_text(text),
                raw_text=text,
                emotion_hint="",
                pause_before=0.0,
                pause_after=0.0,
            )
        )

    return lines


def extract_emotion_hint(note_text: str) -> str:
    """从备注/笔记中提取情感提示"""
    hints: list[str] = []
    for keyword, hint in _EMOTION_KEYWORDS.items():
        if keyword in note_text:
            hints.append(hint)
    return ",".join(hints)


def parse_markdown_table(markdown: str) -> list[list[str]]:
    """解析Markdown表格"""
    rows: list[list[str]] = []
    for line in markdown.split("\n"):
        trimmed = line.strip()
        if not trimmed.startswith("|"):
            continue
        if re.match(r"^\|[\s:\-]+\|", trimmed):
            continue

        cells = [cell.strip() for cell in trimmed.split("|")[1:-1]]
        rows.append(cells)
    return rows


def extract_location(description: str) -> str:
    """从场景描述中提取位置信息"""
    for pattern in _LOCATION_PATTERNS:
        match = pattern.search(description)
        if match:
            return match.group(1)
    return ""


def clean_description(description: str) -> str:
    """清理场景描述，去掉**和中文括号内容"""
    result = description.replace("**", "")
    result = re.sub(r"\（[^）]*\）", "", result)
    return result.strip()


def parse_script(markdown_content: str) -> ParsedScript:
    """解析完整Markdown剧本"""
    title_match = re.search(r"###\s*\*\*(.+?)\*\*", markdown_content)
    title = title_match.group(1).strip() if title_match else "未命名剧本"

    duration_match = re.search(r"时长[:：]\s*约?(\d+)m(\d+)s", markdown_content)
    if duration_match:
        total_duration_seconds = int(duration_match.group(1)) * 60 + int(
            duration_match.group(2)
        )
    else:
        total_duration_seconds = 0

    meta_section_match = re.search(r"人物以中国五大瑞兽为形象[^|]*", markdown_content)
    meta_section = meta_section_match.group(0) if meta_section_match else ""
    characters = extract_characters(meta_section)

    table_rows = parse_markdown_table(markdown_content)

    scenes: list[Scene] = []
    scene_counter = 0

    for row in table_rows:
        if len(row) < 5:
            continue

        time_str = row[0]
        description = row[1]
        dialogue_cell = row[3]
        note = row[4] if len(row) > 4 else ""

        if not re.search(r"\d{2}:\d{2}", time_str):
            continue

        time_range = parse_time_range(time_str)
        scene_counter += 1

        scene_id = f"scene-{scene_counter}"
        dialogue_lines = parse_dialogue(dialogue_cell, scene_id)

        emotion_hint = extract_emotion_hint(note)
        for line in dialogue_lines:
            if emotion_hint and not line.emotion_hint:
                line.emotion_hint = emotion_hint

        has_action_only = len(dialogue_lines) == 0 and dialogue_cell.strip() == ""
        if has_action_only:
            continue

        scenes.append(
            Scene(
                id=scene_id,
                scene_number=scene_counter,
                time_range=time_range,
                location=extract_location(description),
                time_of_day="",
                description=clean_description(description),
                lines=dialogue_lines,
            )
        )

    return ParsedScript(
        meta=ScriptMeta(
            title=title,
            characters=characters,
            total_duration_seconds=total_duration_seconds,
        ),
        scenes=scenes,
    )
