# script-parser 模块

**对应源码**: `scripts/vaslib/parser/script_parser.py`

## 职责

将 Markdown 格式的中文配音剧本解析为结构化的 `ParsedScript` 对象。

## 关键函数

### parse_script(markdown: str) -> ParsedScript

**主入口**。按以下顺序解析：

1. 提取标题（`### **标题**`）
2. 提取时长（`● 时长:约XmYs`）
3. 提取人物元信息（`● 人物以中国五大瑞兽为形象，...`）
4. 解析 Markdown 表格
5. 逐行调用 `parse_time_range` + `parse_dialogue` + `extract_emotion_hint`

### parse_time_range(time_str: str) -> TimeRange

解析 `MM:SS~MM:SS` 格式时间范围。

| 输入 | 输出 |
|---|---|
| `"00:00~00:05"` | TimeRange(0, 5) |
| `"01:37~01:40"` | TimeRange(97, 100) |
| `"00:00\~00:05"` | TimeRange(0, 5)（处理 Markdown 转义） |

### parse_dialogue(cell: str, scene_id: str) -> list[Line]

解析台词单元格。

支持：
- 中文双引号 `""`
- 英文双引号 `""`
- OS 旁白：`貔貅(OS):"..."`
- 单格多角色：`老龟:"A" 貔貅:"B"`

### extract_characters(meta_section: str) -> list[Character]

从人物元信息 section 提取角色列表。

依赖：
- `CHARACTER_ID_MAP` - 中文名 → 英文 ID
- `GENDER_MAP` - 中文名 → 性别

未注册的字符会被静默丢弃（业务铁律 #2）。

### extract_emotion_hint(note_text: str) -> str

从备注列提取情感关键词。

支持：愤怒、开心、悲伤、恐惧、深情、傲娇、痞气、惊慌、严肃、淡定、夸张、从容、反差萌、无厘头。

## 错误处理

- 时间范围格式错误 → 跳过该行
- 角色未注册 → 静默丢弃（带 console warning）
- 表格行不足 5 列 → 跳过
- 缺台词 → 跳过（视为纯动作行）

## 测试

`scripts/tests/test_core.py::TestParseTimeRange / TestExtractCharacters / TestParseDialogue / TestParseScript`

共 17 个测试用例覆盖。
