---
name: comfyui-research
description: 监控 YouTube 频道、GitHub 仓库、HuggingFace 趋势，提取 ComfyUI 相关新技术，标记陈旧信息。用于研究最新模型、节点、技术时调用。
user-invocable: true
metadata: {"openclaw":{"emoji":"🔬","os":["darwin","linux","win32"]}}
---

# ComfyUI 研究技能

通过监控外部信息源持续更新知识库，标记陈旧信息。

## 监控范围

### YouTube 频道（7 个）

| 频道 | 关注内容 |
|------|----------|
| Olivio Sarikas | ComfyUI 教程、新工作流 |
| Sebastian Kamph | 工作流技巧、节点解析 |
| ComfyUI 官方 | 官方更新、Node 公告 |
| Latent Vision | 视频生成管线 |
| Aitrepreneur | AI 艺术、模型评测 |
| Sebastian Lague | 通用 AI 探索 |
| Two Minute Papers | 前沿论文与成果 |

### GitHub 仓库（11 个）

| 仓库 | 关注内容 |
|------|----------|
| comfyanonymous/ComfyUI | 核心更新、新节点 |
| comfyanonymous/ComfyUI_examples | 示例工作流 |
| ltdrdata/ComfyUI-Impact-Pack | Impact Pack 节点 |
| cubiq/ComfyUI_InstantID | InstantID 节点 |
| cubiq/ComfyUI_IPAdapter_plus | IPAdapter 节点 |
| kosinkadink/ComfyUI-AnimateDiff-Evolved | AnimateDiff |
| Fannovel16/ComfyUI-Frame-Interpolation | RIFE 帧插值 |
| Kijai/ComfyUI-WanVideoWrapper | Wan 视频节点 |
| kijai/ComfyUI-FluxTrainer | FLUX 训练 |
| bflAML/FluxGym | 低显存 FLUX 训练 |
| lkwq007/stablediffusion-infinity | Stable Diffusion Infinity |

### HuggingFace 趋势

- 每日查看 `trending?category=text-to-image` 和 `text-to-video`
- 关注 FLUX、Wan、LTX、HunyuanVideo、Qwen-Image 家族
- 跟踪新发布与高频下载

## 研究流程

### 触发条件

- 用户说"研究最新模型" / "看看有什么新东西"
- `SessionStart` 钩子发现研究数据超过 2 周未更新
- 陈旧度报告标记某条目过期

### 步骤

1. **拉取 YouTube 频道**最近视频列表（用 youtube-chapter-clipper 抓转写稿）
2. **遍历 GitHub 仓库**提交记录与发布（提取 release note）
3. **抓取 HuggingFace 趋势页**（按类别过滤）
4. **提取技术要点**：模型名、显存、用途、节点、参考工作流
5. **更新 references/** 下的相应文件
6. **生成陈旧度报告**

## 信息组织

研究成果写入 `references/`：

| 文件 | 内容 |
|------|------|
| `模型清单.md` | 完整模型目录与下载链接 |
| `工作流.md` | 完整工作流节点配置 |
| `研究日志.md` | 持续积累的技术调研 |
| `陈旧度报告.md` | 条目新鲜度跟踪 |

## 提取教程技术

从 YouTube 教程中提取技术时：

1. 用 `youtube-chapter-clipper` 抓转写稿
2. 识别关键章节（"新模型"、"新工作流"、"技巧"）
3. 抽取：模型名、参数、节点、显存
4. 写入对应参考文件，附原始链接
5. 标注入库日期与作者

## 陈旧度判定

| 类别 | 过期阈值 |
|------|----------|
| 模型 | 90 天 |
| 自定义节点 | 60 天 |
| 工作流 | 60 天 |
| 技术趋势 | 30 天 |

过期条目标记为 `⚠️ 待复核`，在 `references/陈旧度报告.md` 列出。

## 与其它 skill 的协同

- `comfyui-prompt-engineer` 用最新提示词策略更新档案
- `comfyui-workflow-builder` 引用新发现的工作流模式
- `comfyui-troubleshooter` 用新发现的修复方案更新错误库

## 会话钩子

`staleness-check.ps1` 脚本在 `SessionStart` 钩子中运行：

```powershell
pwsh -File scripts/陈旧度检查.ps1
```

发现研究数据超过 2 周未更新时提醒用户：

```
⚠️ 研究数据已 X 天未更新。建议运行 comfyui-research 技能。
```

## 输出格式

研究更新后的报告：

```markdown
# 研究更新 - {日期}

## 新发布
- **FLUX.2 [dev]** - 2026-03-15 发布，32B 参数，24GB+ 显存
  来源：https://huggingface.co/...
  用途：写实人像、多参考图

## 重要更新
- **Wan 2.6** - 新增原生口型同步
  适用场景：说话人视频无需单独口型同步节点

## 监控列表更新
- 新增关注：Rodin3D Gen-2（合作伙伴节点）
- 移除关注：Stable Diffusion 1.5 相关（已停更）

## 待复核（陈旧）
- ⚠️ InstantID 详细文档 - 132 天未更新
```

## 注意事项

- 外部信息源有不可靠风险——交叉验证后再写库
- 商业/付费内容不收录
- 不抓取未经授权的私有内容
- 维护更新日志 `references/演进.md`
