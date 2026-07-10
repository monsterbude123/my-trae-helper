---
name: video-assembly
description: 两种模式：FFmpeg（拼接、混音、字幕、转场）与 Remotion（动画字幕、动态图形、基于 React 的模板）。音频归一化到 -16 LUFS（YouTube 标准）。质量预设 CRF 15-28。用于视频合成、剪辑、字幕添加。
user-invocable: true
metadata: {"openclaw":{"emoji":"🎞️","os":["darwin","linux","win32"],"requires":{"anyBins":["ffmpeg"]}}}
---

# 视频合成技能

把生成的视频片段、音频、字幕合成为最终成片。

## 两种模式

### 模式 A：FFmpeg（轻量、命令行）

**适用**：简单拼接、混音、加字幕、转场

**优势**：
- 速度快
- 资源占用低
- 可脚本化

**前置**：FFmpeg 在 PATH

```bash
# 验证
ffmpeg -version
```

### 模式 B：Remotion（基于 React 的复杂合成）

**适用**：动画字幕、动态图形、模板化渲染

**优势**：
- 复杂动画
- 模板复用
- 矢量元素

**前置**：Node.js + Remotion 项目

## 模式 A：FFmpeg 工作流

### 拼接视频片段

```bash
# 创建文件列表
cat > filelist.txt <<EOF
file 'clip1.mp4'
file 'clip2.mp4'
file 'clip3.mp4'
EOF

# 拼接（流拷贝，无重编码）
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# 重编码（确保兼容性）
ffmpeg -f concat -safe 0 -i filelist.txt -c:v libx264 -crf 18 output.mp4
```

### 添加音频轨

```bash
# 替换原音频
ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4

# 混合（保留原音频 + 叠加新音频）
ffmpeg -i video.mp4 -i audio.wav -filter_complex "[0:a][1:a]amix=inputs=2:duration=longest" \
       -c:v copy output.mp4
```

### 音频归一化（YouTube 标准 -16 LUFS）

```bash
# 单遍
ffmpeg -i input.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.wav

# 双遍（更精准）
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | grep -v "frame="
ffmpeg -i input.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=...:measured_TP=...:measured_LRA=...:measured_thresh=...:offset=...:linear=true" output.wav
```

### 添加字幕

```bash
# 烧入硬字幕
ffmpeg -i video.mp4 -vf "subtitles=subs.srt" -c:v libx264 -crf 18 output.mp4

# 软字幕（可切换）
ffmpeg -i video.mp4 -i subs.srt -c:v copy -c:s mov_text output.mp4
```

### 转场效果

```bash
# 简单交叉淡入
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=fade:duration=1:offset=5" \
  -c:v libx264 -crf 18 output.mp4

# 可用转场：fade, wipeleft, wiperight, slideup, slidedown, circlecrop, etc.
```

### 质量预设

| 预设 | CRF | 用途 |
|------|-----|------|
| 高质量 | 15-18 | 母版归档 |
| YouTube | 18-20 | 视频上传 |
| 社交媒体 | 20-23 | 平台压缩 |
| 预览 | 23-28 | 快速分享 |

## 模式 B：Remotion 工作流

### 初始化项目

```bash
npm init video
# 选模板
```

### 项目结构

```
my-video/
├── src/
│   ├── Root.tsx           # 根组合
│   ├── Composition.tsx    # 单个合成
│   ├── components/        # 组件
│   │   ├── Caption.tsx
│   │   ├── Logo.tsx
│   │   └── Overlay.tsx
│   └── data/              # 数据
│       ├── captions.json
│       └── scenes.json
├── public/                # 静态资源
├── out/                   # 渲染输出
└── package.json
```

### 字幕组件示例

```tsx
import { useCurrentFrame, useVideoConfig, AbsoluteFill } from "remotion";

export const Caption: React.FC<{ text: string; start: number; duration: number }> = ({
  text, start, duration,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  
  if (t < start || t > start + duration) return null;
  
  const localT = (t - start) / duration;
  const opacity = Math.min(localT * 5, 1) * Math.min((1 - localT) * 5, 1);
  
  return (
    <AbsoluteFill style={{
      justifyContent: "flex-end",
      alignItems: "center",
      padding: 60,
    }}>
      <div style={{
        color: "white",
        fontSize: 60,
        fontWeight: "bold",
        textShadow: "0 2px 8px rgba(0,0,0,0.8)",
        opacity,
        backgroundColor: "rgba(0,0,0,0.5)",
        padding: "20px 40px",
        borderRadius: 10,
      }}>
        {text}
      </div>
    </AbsoluteFill>
  );
};
```

### 渲染

```bash
# 预览
npm start

# 渲染单条
npx remotion render src/index.tsx MyComp out/video.mp4

# 批量渲染
npx remotion render src/index.tsx MyComp out/video.mp4 --concurrency=4
```

## 决策表

| 需求 | 推荐模式 |
|------|----------|
| 简单拼接 + 混音 | FFmpeg |
| 字幕 + 转场 | FFmpeg |
| 动画字幕 | Remotion |
| 复杂动态图形 | Remotion |
| 模板复用（系列视频） | Remotion |
| 快速一次合成 | FFmpeg |
| 母版归档 | FFmpeg（CRF 15） |

## 标准成片模板

### YouTube 标准（横屏 16:9）

```bash
ffmpeg -i video.mp4 -i audio.wav \
  -vf "scale=1920:1080,fps=30,subtitles=subs.srt" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  youtube.mp4
```

### YouTube Shorts（竖屏 9:16）

```bash
ffmpeg -i video.mp4 -i audio.wav \
  -vf "scale=1080:1920,fps=30,subtitles=subs.srt" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  youtube_short.mp4
```

### Instagram Reels / TikTok（竖屏 9:16）

```bash
ffmpeg -i video.mp4 -i audio.wav \
  -vf "scale=1080:1920,fps=30" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v libx264 -preset slow -crf 20 \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  reels.mp4
```

## 输出

合成完成后：

1. 最终视频存到 `projects/{项目}/成片/`
2. 各平台版本另存（YouTube / Shorts / Reels）
3. 在 `清单.yaml` 记录合成参数与效果

## 注意事项

- **音频先行归一化**——避免平台二次压缩爆音
- **CRF 越低质量越高体积越大**——18-23 为甜点
- **`-movflags +faststart`**——流式播放友好
- **Remotion 渲染慢**——预览用 480p，最终 1080p
- **多语言字幕**用 ASS/SSA 格式
- 多分辨率输出用 `-vf scale=` 配合
