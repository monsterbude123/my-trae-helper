# voice-acting-skill · Examples

> 剧本样例文件目录。所有样例均来自 `raw/` 原始资料，复制于此便于快速参考。

## 包含文件

| 文件 | 说明 |
|---|---|
| `demo-script.md` | 主样例 - 貔貅系列剧本AIGC指导版本（Markdown 5列表格格式） |
| `raw-dialogue.txt` | 原始台词本（无格式） |
| `shots.txt` | 分镜文本 |
| `ffmpeg-cmd.md` | FFmpeg 音频格式转换参考（m4a→wav） |

## 快速试用

```bash
pip install -e .
vas analyze assets/examples/demo-script.md -o output
```

输出结构：

```
output/
├── parsed/script.json
├── analyzed/script-analysis.json
├── analyzed/batch-plan.json
├── annotated/
│   ├── qwen-tts.json + .md
│   ├── cosyvoice.json + .md
│   ├── omnivoice.json + .md
│   └── all-engines.md
```

## 剧本格式规范

剧本必须是 Markdown 文件，结构如下：

```markdown
### **剧本标题**

● 时长:约XmYs ● 人物以中国五大瑞兽为形象，**整体风格**：
角色1:配音为方言A (性格描述)
角色2:配音为方言B (性格描述)

| 大致时间线 | 描述 | 内容、动作设计 | 台词 | 备注 |
| :---- | :---- | :---- | :---- | :---- |
| 00:00~00:05 | 场景描述 | 动作 | 角色:"台词文本" | 情感/动作备注 |
| 00:05~00:15 | ... | ... | 角色:"台词" | ... |
```

### 关键格式

- **时间范围**：`MM:SS~MM:SS`（注意 `~` 在 Markdown 中常被转义为 `\~`）
- **台词**：使用中文/英文双引号包裹，支持单格多角色：`老龟:"台词A" 貔貅:"台词B"`
- **角色 ID**：必须在 `scripts/vaslib/parser/script_parser.py::CHARACTER_ID_MAP` 中注册

## 详细文档

- 解析规则：`skills/script-parser/SKILL.md`
- 音色分配：`skills/voice-assigner/SKILL.md`
- 批次切分：`skills/batch-manager/SKILL.md`
