# 十二、资源目录结构

```
游戏目录/
├── config.txt                 # 游戏配置
├── scene/                     # 剧情脚本
│   ├── start.txt              # 入口脚本（必须存在）
│   └── *.txt                  # 场景脚本
├── background/                # 背景图片
├── figure/                    # 角色立绘（PNG/Live2D/Spine）
├── bgm/                       # 背景音乐 & 音效
├── vocal/                     # 配音
├── video/                     # 视频
├── game/
│   ├── template/              # UI 模板
│   │   ├── template.json
│   │   ├── Stage/
│   │   │   ├── Textbox/textbox.scss
│   │   │   └── Choose/choose.scss
│   │   └── UI/
│   │       └── Title/title.scss
│   └── animation/             # 自定义动画 JSON
│       ├── animationTable.json
│       └── *.json
└── docs/                      # 策划文档
    └── story-design.md
```

## 资源命名规范

| 目录 | 推荐格式 | 示例 |
|:---|:---|:---|
| `background/` | `{场景名}.webp` | `classroom.webp` |
| `figure/` | `{角色名}.png` 或 `{角色名}_{表情}.png` | `linxiaowan.png` |
| `bgm/` | `{用途}_{名称}.mp3` 或 `s_{标题}.mp3` | `s_Title.mp3` |
| `vocal/` | `{角色}{场景}_{序号}.wav` | `charA_hello.wav` |
| `video/` | `{场景}.mp4` | `opening.mp4` |

**要点**：纯英文命名，避免中文、空格和特殊符号。
