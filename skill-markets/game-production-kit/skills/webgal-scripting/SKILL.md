---
name: "webgal-scripting-skill"
description: "WebGAL 脚本编写完整参考。当需要编写、修改、检查或调试 WebGAL 视觉小说引擎的 .txt 场景脚本时自动加载此 skill。覆盖全部命令语法、变量系统、条件判断、分支选择、场景管理、立绘/音频/动画系统、UI 定制、config.txt 配置、常见错误与调试技巧。触发词：WebGAL 脚本、WebGAL 命令、.txt 场景、changeBg、changeFigure、choose、setVar、bgm、playEffect、changeScene、callScene、jumpLabel、label、intro、say、setTextbox、setAnimation、setTransform、end、unlockCg、unlockBgm、filmMode、miniAvatar、playVideo、pixiInit、pixiPerform、setTransition、setTempAnimation、setComplexAnimation、showVars、getUserInput、applyStyle、config.txt、Game_key、分支选择、条件判断、立绘、背景音乐、音效"
---

# WebGAL 脚本编写完整参考

面向 WebGAL 视觉小说引擎的脚本编写技能包。按需查阅对应的子文档。

> 完整官方文档见 [WebGAL_Doc](../../docs/reference/WebGAL_Doc/src/)。官方仓库：<https://github.com/OpenWebGAL/WebGAL>

---

## 前置条件

- WebGAL 引擎项目已初始化（`game/` 目录结构存在，含 `config.txt`、`scene/`、`background/`、`figure/` 等标准目录）
- 已确认游戏标题与资源目录布局

## 骨架流程

1. 读 `reference/01-base-syntax.md`（基础语法）
2. 读 `reference/02-commands.md`（按需查 34 个命令）
3. 按需查 03-09（变量/条件/场景/立绘/音频/UI/config）

## 约束

- 场景脚本 UTF-8 编码（中文/标点必须 UTF-8，否则 WebGAL 解析报错）
- 路径大小写敏感（`scene/start.txt` ≠ `scene/Start.txt`）
- 标点使用全角中文标点（，。！？：；）

## 质量清单

- [ ] 提交前过 `reference/11-checklist.md`（16 项自检条目）
- [ ] 旁白与角色对话格式正确
- [ ] 跨文件 flag 变量名一致
- [ ] TTS 标记可发音

---

## 子文档索引

| 序号 | 文档 | 内容 |
|:---:|:---|:---|
| 1 | [reference/01-base-syntax.md](reference/01-base-syntax.md) | 基础语法规范（语句结构、注释、转义、通用参数） |
| 2 | [reference/02-commands.md](reference/02-commands.md) | 34 个命令完全参考（语法、参数表、示例） |
| 3 | [reference/03-variables.md](reference/03-variables.md) | 变量系统详解（类型、运算、局部/全局、随机数、内置变量） |
| 4 | [reference/04-conditions.md](reference/04-conditions.md) | 条件判断详解（运算符、-when 参数、条件跳转、choose 条件语法） |
| 5 | [reference/05-scenes.md](reference/05-scenes.md) | 场景管理详解（changeScene/callScene、标签系统、入口） |
| 6 | [reference/06-figures.md](reference/06-figures.md) | 立绘系统详解（位置、id、类型、嘴型同步、变换属性、缓动、预置动画） |
| 7 | [reference/07-audio.md](reference/07-audio.md) | 音频系统详解（BGM、语音、效果音、音频鉴赏） |
| 8 | [reference/08-ui.md](reference/08-ui.md) | UI 定制（文本框/选择支/标题页样式、applyStyle、模板配置） |
| 9 | [reference/09-config.md](reference/09-config.md) | config.txt 配置项参考（Game_name、语言切换、Steam 等） |
| 10 | [reference/10-faq-debug.md](reference/10-faq-debug.md) | 常见错误与 FAQ + 调试技巧 |
| 11 | [reference/11-checklist.md](reference/11-checklist.md) | 脚本规范检查清单（16 项自检条目，含旁白/TTS/跨文件 flag） |
| 12 | [reference/12-directory.md](reference/12-directory.md) | 资源目录结构 |

---

## 快速定位

| 想做什么 | 查阅 |
|:---|:---|
| 写对话 | [02-commands § 2.1 say](reference/02-commands.md) |
| 做分支选择 | [02-commands § 2.15 choose](reference/02-commands.md) + [04-conditions § 4.4](reference/04-conditions.md) |
| 管理场景切换 | [05-scenes](reference/05-scenes.md) |
| 控制立绘进出场/动画 | [06-figures](reference/06-figures.md) |
| 播放音乐音效 | [07-audio](reference/07-audio.md) |
| 使用变量/计数/条件 | [03-variables](reference/03-variables.md) + [04-conditions](reference/04-conditions.md) |
| 自定义 UI 样式 | [08-ui](reference/08-ui.md) |
| 配置游戏标题/语言 | [09-config](reference/09-config.md) |
| 排查脚本错误（含已踩坑汇总） | [10-faq-debug §10.5](reference/10-faq-debug.md) |
| 提交前自检 | [11-checklist](reference/11-checklist.md) |
