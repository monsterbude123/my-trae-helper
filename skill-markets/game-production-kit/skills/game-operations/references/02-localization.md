# 本地化管线

> 来源：游戏本地化行业标准
> 关联：game-operations SKILL.md §骨架流程.2

引擎无关的本地化管线。核心原则：key-based 文本系统 + 翻译管线 + 自动化溢出检查。

## §1 Key-based 文本系统

```json
// strings.json — 所有本地化文本单一数据源
{
  "ui.main_menu.start": "开始游戏",
  "ui.main_menu.continue": "继续",
  "dialogue.ch1.npc_greeting": "欢迎来到冒险者公会！",
  "item.sword_fire.name": "火焰之剑",
  "item.sword_fire.desc": "燃烧着不灭之焰的传奇武器"
}
```

**Key 命名规范**：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `ui.*` | UI 文本（按钮/标签/提示） | `ui.settings.volume` |
| `dialogue.*` | 对话文本 | `dialogue.ch2.boss_taunt` |
| `item.*` | 物品名称/描述 | `item.potion_hp.name` |
| `tutorial.*` | 教程文本 | `tutorial.combat.step1` |
| `system.*` | 系统消息/错误提示 | `system.save.error` |

## §2 翻译管线

```
原文提取（strings.json 源语言）
  → PO/POT 文件生成（gettext 格式）
  → 翻译记忆库（TMX 格式）匹配已有翻译
  → 机器翻译预填充（DeepL/Google Translate API）
  → 人工审校（校对+文化适配）
  → 导出为 strings.{lang}.json
  → 导入游戏验证
```

**PO 文件示例**：

```po
msgid "ui.main_menu.start"
msgstr "Start Game"
```

**平台翻译工具链**：

| 平台 | 工具/服务 |
|------|----------|
| 通用 | Lokalise / Crowdin / POEditor |
| 开源 | Weblate / gettext |
| 本地脚本 | `gen_pot.py` → 发送给翻译团队 |

## §3 溢出检查

> 德语/俄语文本通常比英文长 30-50%。必须自动化检测。

| 检查项 | 工具方法 |
|--------|---------|
| UI 容器宽度 vs 翻译后文本渲染宽度 | 运行时检测 + 截图对比 |
| 德语/俄语/阿拉伯语 溢出专项 | 自动化 UI 遍历 |
| 梵文/泰文 行高溢出 | 字体行高计算 |
| 截断检测 | 文本末尾 "..." 出现率 |

```
目标语言溢出检查覆盖率要求：≥ 支持的语言数
至少覆盖：德语(de)、俄语(ru)、阿拉伯语(ar)
```

## §4 字体回退

```
字体链配置示例：
  Latin/Cyrillic → Noto Sans
  CJK → Noto Sans CJK
  Arabic → Noto Naskh Arabic
  Devanagari → Noto Sans Devanagari
  回退链: 目标字体 → Noto Sans → 系统默认
```

**字体验证清单**：
- [ ] CJK 字体覆盖（简中/繁中/日文/韩文）
- [ ] Arabic 从右到左（RTL）渲染
- [ ] 特殊字符（¿¡ñçß）可渲染
- [ ] 数字/货币格式适配

## §5 平台差异

| 平台 | 多语言配置方式 |
|------|--------------|
| **Steam** | 多语言 Depot + Steamworks 语言设置 |
| **App Store** | App Store Connect 语言元数据 + iOS 本地化 string |
| **Google Play** | Google Play Console 翻译服务 + Android 资源本地化 |
| **itch.io** | 多文件分发（每语言独立 build） |
