# 对外协作接口

> 触发: 用户需要给外部合作者（作曲/美术外包/配音演员/翻译）提供需求摘要

## 导出类型

| 导出目标 | 触发词 | 产出文件 | 格式 |
|---------|------|------|------|
| 作曲/音效师 | "导出 BGM 需求" / "给作曲家" | BGM-{game_key}-brief.md | 曲名 + 时长 + 情绪 + 使用场景 + 参考 |
| 美术外包 | "导出发包" / "给画师" | art-{game_key}-brief.md | 角色名 + 数量 + 风格 + 参考 + 格式 |
| 配音演员 | "导出配音需求" / "给声优" | voice-{game_key}-brief.md | 角色 + 台词量 + 性格描述 + 试音片段 |
| 翻译 | "导出翻译清单" | i18n-{game_key}-brief.md | 原文 + 行数 + 上下文 |

## 使用

```powershell
# 一键导出所有合作者需求摘要
python scripts/export-collaborator-brief.py {game_key} --all

# 只导出 BGM 需求
python scripts/export-collaborator-brief.py {game_key} --composer

# 只导出美术需求
python scripts/export-collaborator-brief.py {game_key} --artist
```

## 产出示例: BGM-星海咖啡馆-brief.md

```markdown
# BGM 需求 —《星海咖啡馆》

| # | 曲名 (暂定) | 时长 | 情绪 | 使用场景 | 参考 |
|---|----------|------|------|---------|------|
| 1 | Main Theme | 2:00 循环 | 温暖、期待 | 主菜单 | 《咖啡心语》主题曲 |
| 2 | Cafe Ambient | 3:00 循环 | 放松、日常 | 咖啡馆日常场景 | Lo-fi hip hop |
| 3 | Tense Moment | 1:00 | 不安、悬疑 | 剧情转折 | 《Undertale》— "Heartache" |

**交付格式**: 48kHz WAV + 320kbps MP3
**调性**: C major / A minor
**截止日期**: 2026-08-01
```

**注意**: 这份 BGM brief 的所有内容（曲名、时长、情绪、场景）来自 asset-manifest.md 和 story-design.md，脚本自动提取然后渲染成人可读格式。不是手工写的。
