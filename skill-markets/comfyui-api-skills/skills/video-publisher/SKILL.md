---
name: video-publisher
description: 薄编排器，委托全局 YouTube skill 完成研究、标题/缩略图优化、上传、数据分析。生成各平台元数据（YouTube、Shorts、Instagram Reels、TikTok）。用于视频发布。
user-invocable: true
metadata: {"openclaw":{"emoji":"📤","os":["darwin","linux","win32"]}}
---

# 视频发布技能

把成片发布到各平台。编排器层负责元数据生成与委托上传。

## 平台矩阵

| 平台 | 时长 | 比例 | 备注 |
|------|------|------|------|
| YouTube（标准） | 无限制 | 16:9 | 横屏长视频 |
| YouTube Shorts | ≤ 60 秒 | 9:16 | 竖屏短片 |
| Instagram Reels | ≤ 90 秒 | 9:16 | 竖屏短片 |
| TikTok | ≤ 10 分钟 | 9:16 | 竖屏短片 |
| X（推特） | ≤ 140 秒 | 16:9 / 1:1 / 9:16 | 灵活 |
| Facebook | 无限制 | 16:9 / 1:1 / 9:16 | 多比例 |

## 元数据生成

### YouTube 标题

**结构**：

```
{主关键词}：{价值主张} ({年份})
```

**公式**：

- **悬念 + 价值**：如"我用 AI 给角色做了完整的电影预告片"
- **教程型**：如"ComfyUI Wan 2.6 完整教程（2026）"
- **对比型**：如"FLUX.2 vs FLUX.1：画质与速度的真实差距"
- **故事型**：如"我用 30 天训练了一个 AI 角色，结果出乎意料"

**长度**：50-70 字符（避免截断）

**关键词**：前 30 字符包含主关键词

### YouTube 描述

**结构**：

```
{开头钩子}（1-2 句）

📌 本视频内容：
- 重点 1
- 重点 2
- 重点 3

⏱ 时间戳：
0:00 简介
1:23 第一步
...

🔗 资源链接：
- 工具：{URL}
- 模型：{URL}
- 项目仓库：{URL}

📱 关注我：
- YouTube：{URL}
- Twitter：{URL}
- Discord：{URL}

#AI #ComfyUI #视频生成
```

**长度**：200-500 字符（前 3 行最关键）

### 标签

**生成策略**：

1. **核心关键词**：ComfyUI、Wan 2.6、FLUX、LoRA、视频生成
2. **长尾关键词**：ComfyUI Wan 2.6 教程、FLUX 角色 LoRA 训练
3. **平台关键词**：AI 视频、AI 角色、AI 工具
4. **品牌关键词**：项目名、角色名

**数量**：15-30 个标签

### 缩略图设计

**核心原则**：
- **大字体**：3-5 个词
- **高对比**：明暗对比强
- **人脸特写**：增加点击率
- **颜色对比**：用对比色吸引注意
- **简单背景**：避免杂乱

**尺寸**：1280x720（YouTube）

**工具**：
- ComfyUI 图像生成
- 全局 youtube-thumbnail skill
- Remotion 动态缩略图

## 元数据生成模板

```yaml
标题: "{主钩子}: {价值} ({年份})"
描述: |
  {开头钩子}

  📌 本视频涵盖：
  - {重点 1}
  - {重点 2}
  - {重点 3}

  ⏱ 时间戳：
  0:00 简介
  {其他时间戳}

  🔗 资源：
  - 工具：{URL}
  - 模型：{URL}

  #ComfyUI #AI视频 #{主题关键词}
标签:
  - ComfyUI
  - Wan 2.6
  - FLUX
  - AI视频
  - 视频生成
  - LoRA训练
  - 角色生成
  - 教程
  - {年度关键词}
缩略图: 缩略图.png
分类: 科学与技术
隐私: 公开
```

## 各平台元数据变体

### YouTube Shorts

```yaml
标题: "{钩子} #Shorts"
描述: "{简要内容} #Shorts #ComfyUI"
标签:
  - Shorts
  - YouTubeShorts
  - {主题标签}
时长: ≤ 60 秒
比例: 9:16
```

### Instagram Reels

```yaml
标题: "{钩子} ✨"
描述: "{简要} . . . #Reels #AI #{主题}"
标签: 25-30 个相关标签
时长: ≤ 90 秒
比例: 9:16
封面: 第 1 帧或自定义
```

### TikTok

```yaml
标题: "{钩子} #AI"
描述: "{简要} #ComfyUI #{主题}"
标签: 3-5 个（TikTok 标签数少）
时长: ≤ 10 分钟（推荐 30-90 秒）
比例: 9:16
声音: 原创音频（避免版权问题）
```

## 上传流程

### 通过全局 YouTube skill

委托给 `youtube-uploader`（若已安装）：

```bash
# 调用 youtube-uploader
youtube_uploader \
  --video "成片/youtube.mp4" \
  --title "..." \
  --description "..." \
  --tags "comfyui,wan,flux,..." \
  --thumbnail "缩略图.png" \
  --category "28" \
  --privacy "public"
```

### 通过 yt-dlp（替代方案）

```bash
# 安装
pip install yt-dlp

# 上传（需要 cookies）
yt-dlp --username oauth2 --password "" \
       --title "..." \
       ...
```

### 通过 API（高级）

YouTube Data API v3：

```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

youtube = build("youtube", "v3", credentials=creds)

body = {
  "snippet": {
    "title": "...",
    "description": "...",
    "tags": [...],
    "categoryId": "28"
  },
  "status": {
    "privacyStatus": "public"
  }
}

media = MediaFileUpload("video.mp4", mimetype="video/mp4", resumable=True)
youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
```

## 发布前检查清单

- [ ] 视频分辨率与平台匹配
- [ ] 音频已归一化到 -16 LUFS
- [ ] 字幕已烧入或外挂
- [ ] 缩略图已生成
- [ ] 标题含主关键词
- [ ] 描述前 3 行有钩子
- [ ] 标签 15-30 个
- [ ] 分类与隐私设置正确
- [ ] 时长符合平台要求
- [ ] 文件大小符合平台上限

## 与其它 skill 的协同

- `video-assembly` 提供最终视频
- `comfyui-research` 提供关键词与趋势
- 全局 `youtube-strategy` 提供发布策略
- 全局 `youtube-uploader` 执行上传
- 全局 `youtube-video-analyst` 后续数据分析

## 输出

发布完成后向用户报告：

1. 平台列表与各平台链接
2. 上传时间
3. 元数据摘要（标题、标签数、缩略图）
4. 后续建议（数据分析时机、互动策略）

## 注意事项

- **平台政策**：遵守各平台社区准则
- **版权**：背景音乐、素材、声音克隆均需合法授权
- **AI 标识**：YouTube 要求 AI 生成内容明确标识
- **多语言**：上传多语言版本时分别优化元数据
- **发布节奏**：保持稳定的发布频率
- **数据分析**：发布 24-48 小时后查看初步数据
