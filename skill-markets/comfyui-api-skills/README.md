# ComfyUI 中文版技能包

> ComfyUI 视频制作编排器的全量中文本地化版本。

基于 [ComfyUI-Expert](https://github.com/MCKRUZ/ComfyUI-Expert) 全量翻译与本地化。**15** 个专项 skill，覆盖 ComfyUI 全流程：角色图像生成、视频生产、语音合成、LoRA 训练、发布。

## 这是什么

一个 **会话级** 的 AI 编排器系统——把 Claude / Trae 变成资深 ComfyUI 视频制作技术总监，通过自然语言路由到 **15** 个专项 skill 模块：

```
用户输入（中文）
  ↓
编排器（SKILL.md）路由
  ↓
按需读取对应 skill
  ↓
读取 references/ 中的深度资料（按指令）
  ↓
执行并返回结果
```

## 15 个 Skill 速览

| 类别 | Skill | 用途 |
|------|-------|------|
| **基础** | `comfyui-api` | 连接 ComfyUI、提交工作流、轮询结果 |
| **基础** | `comfyui-inventory` | 探查已装模型/节点/显存 |
| **基础** | `project-manager` | 项目清单、角色档案、生成历史 |
| **研究** | `comfyui-research` | 监控 YouTube/GitHub/HF，提取新技术 |
| **核心创作** | `comfyui-prompt-interview` | 模糊想法访谈，产出创意简报 |
| **核心创作** | `comfyui-prompt-engineer` | 模型特定提示词优化 |
| **核心创作** | `comfyui-workflow-builder` | 从自然语言生成工作流 JSON |
| **核心创作** | `comfyui-character-gen` | 身份保持（InstantID/PuLID/IP-Adapter/LoRA） |
| **生产** | `comfyui-video-pipeline` | 视频引擎调度（LTX/Wan/HunyuanVideo/FramePack） |
| **生产** | `comfyui-video-production` | 端到端多镜头生产（关键帧→动画→拼接） |
| **生产** | `comfyui-voice-pipeline` | 语音合成 + 口型同步 |
| **生产** | `comfyui-lora-training` | 角色/风格 LoRA 训练 |
| **输出** | `video-assembly` | FFmpeg / Remotion 视频合成 |
| **输出** | `video-publisher` | YouTube/Shorts/Reels/TikTok 发布 |
| **支持** | `comfyui-troubleshooter` | 四类错误诊断与修复 |

## 快速开始

### 前置条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或 Trae IDE
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)（本地或远程）
- [FFmpeg](https://ffmpeg.org/)（视频合成）
- [PowerShell 7+](https://github.com/PowerShell/PowerShell)（Windows 工具脚本）
- Windows（其它平台可类比改造）

### 安装到 Trae IDE

```powershell
# 复制整个包到 Trae 全局技能目录
Copy-Item -Recurse "{skill_root}" "$env:USERPROFILE\.trae-cn\skills\comfyui-api-skills"
```

安装后**重启 Trae IDE** 加载技能。

### 第一次使用

1. **启动 ComfyUI**（本地或远程）
2. **扫描库存**（首次或安装新模型后）：
   ```
   扫描我的 ComfyUI 安装，{{COMFYUI_INSTALL_DIR}}
   ```
3. **开始创作**：
   ```
   创建一个名为"角色展示"的项目
   添加一个角色，名叫 Sage——赤褐色长发，绿色眼睛，雀斑
   用 FLUX 给 Sage 写实肖像
   ```
4. **研究更新**（可选）：
   ```
   检查 ComfyUI 视频模型的最新动态
   ```

## 架构

### 三层上下文

| 层 | 文件 | 加载时机 | 大小 |
|----|------|----------|------|
| **第一层：基础** | `foundation/*.md` | 会话开始（首次交互） | ~2K tokens |
| **第二层：工作** | `projects/{名}/*` | 处理具体项目时 | 视项目 |
| **第三层：参考** | `references/*.md` | skill 明确需要时 | 较大 |

### Skill 依赖图

```
SKILL.md（编排器 - 始终加载）
  │
  ├─ 基础（无依赖）
  │  ├─ comfyui-api
  │  ├─ comfyui-inventory
  │  └─ project-manager
  │
  ├─ 研究（独立）
  │  └─ comfyui-research
  │
  ├─ 核心创作（依赖 inventory）
  │  ├─ comfyui-prompt-interview
  │  ├─ comfyui-prompt-engineer
  │  ├─ comfyui-workflow-builder
  │  └─ comfyui-character-gen
  │
  ├─ 生产（依赖创作）
  │  ├─ comfyui-video-pipeline
  │  ├─ comfyui-voice-pipeline
  │  └─ comfyui-lora-training
  │
  ├─ 输出（依赖生产）
  │  ├─ video-assembly
  │  └─ video-publisher
  │
  └─ 支持
     └─ comfyui-troubleshooter
```

### 请求路由示例

| 用户说 | 路由到 |
|--------|--------|
| "我想做一个有电影感的视频" | comfyui-prompt-interview |
| "给角色 Sage 生成肖像" | comfyui-character-gen |
| "用 Wan 2.6 做一个 5 秒视频" | comfyui-video-pipeline |
| "优化这个提示词" | comfyui-prompt-engineer |
| "出错了" | comfyui-troubleshooter |
| "查库存" | comfyui-inventory |
| "训练 Sage 的 LoRA" | comfyui-lora-training |

## 翻译策略

为兼顾**中文阅读体验**与**技术准确性**：

- **模型/库/工具名保留英文**（FLUX、Wan、LoRA、VAE、ComfyUI 等）
- **首次出现**用 `中文名（English Name）` 形式
- **API 端点、命令行参数、节点类名、文件名** 一律保留英文
- **其余说明性文字** 全部中文

这样：

- 读起来是流畅的中文
- 查技术细节时不需翻译
- 复制粘贴代码/命令不需转写

## 与英文版（comfyui-expert）的差异

| 方面 | 英文版 | 中文版（本包） |
|------|--------|----------------|
| 语言 | 英文 | 全中文（保留专有名词） |
| 编排器文件 | `CLAUDE.md` | `SKILL.md` |
| `foundation/` 文件名 | 英文 | 中文（智能体人设.md 等） |
| `references/` 文件名 | 英文 | 中文（模型清单.md 等） |
| 子 skill `SKILL.md` | 英文 | 全中文 |
| Skill 数量 | 15 | 15（1:1 对齐） |
| 模型信息 | 同步 | 同步 |
| 工作流模板 | 同步 | 同步 |

## 目录结构

```
comfyui-api-skills/
├── SKILL.md                        # 编排器 + 路由表
├── README.md                       # 本文件
├── foundation/                     # 第一层（始终可用速查）
│   ├── 智能体人设.md
│   ├── 接口速查.md
│   ├── 硬件档案.md
│   ├── 模型景观.md
│   └── 技能注册表.md
├── skills/                         # 15 个 skill 模块
│   ├── comfyui-api/SKILL.md
│   ├── comfyui-inventory/SKILL.md
│   ├── comfyui-prompt-interview/SKILL.md
│   ├── comfyui-prompt-engineer/SKILL.md
│   ├── comfyui-workflow-builder/SKILL.md
│   ├── comfyui-character-gen/SKILL.md
│   ├── comfyui-research/SKILL.md
│   ├── comfyui-video-pipeline/SKILL.md
│   ├── comfyui-video-production/SKILL.md
│   ├── comfyui-voice-pipeline/SKILL.md
│   ├── comfyui-lora-training/SKILL.md
│   ├── comfyui-troubleshooter/SKILL.md
│   ├── project-manager/SKILL.md
│   ├── video-assembly/SKILL.md
│   └── video-publisher/SKILL.md
└── references/                     # 第三层（按需）
    ├── 模型清单.md
    ├── 工作流.md
    ├── lora-训练.md
    ├── 语音合成.md
    ├── 提示词模板.md
    ├── 故障排查.md
    ├── 研究日志.md
    ├── 陈旧度报告.md
    └── 演进.md
```

## 典型工作流

### 角色肖像

```
1. "创建项目 角色展示"
2. "添加角色 Sage——赤褐色长发，绿色眼睛，雀斑"
3. "用 FLUX 给 Sage 生成写实肖像"
```

助手路径：读取项目 → 加载 inventory → 加载 character-gen → 加载 prompt-engineer → 优化提示词 → 构建工作流 → 提交 → 轮询 → 记录。

### 端到端多镜头视频

```
1. "做一个 30 秒的 5 镜头叙事视频，主角是 Sage"
```

助手路径：加载 video-production → 选管线（关键帧→动画→拼接）→ 生成关键帧（用 character-gen）→ I2V 动画（用 video-pipeline）→ 拼接（用 video-assembly）→ 输出。

### 说话人视频

```
1. "用 Sage 制作一个说话人视频，说'欢迎来到我的频道'"
```

助手路径：加载 voice-pipeline → 选引擎（Qwen3-TTS + Wan 2.6 内置口型）→ 生成语音 → 生成视频（带口型）→ 合成 → 视频文件。

### LoRA 训练

```
1. "用 20 张参考图训练 Sage 的 LoRA"
```

助手路径：加载 lora-training → 检查数据集 → 选工具（Kohya ss）→ 配置 → 训练 → 多检查点评估 → 部署到 ComfyUI。

## 定制

### 换 GPU

编辑 `foundation/硬件档案.md`：

```markdown
## 显卡
- **型号**：你的 GPU
- **显存**：你的显存
```

### 换 ComfyUI 路径

在项目清单中设置或启动时传入。

### 调整模型景观

编辑 `foundation/模型景观.md`（前 3 速查）和 `references/模型清单.md`（完整目录）。

## 故障排查

| 问题 | 解决 |
|------|------|
| 助手不作为 ComfyUI 中文助手 | 通过 `comfyui-api-skills` 技能包加载 |
| 工作流报"模型未找到" | 运行库存扫描，然后重新生成 |
| ComfyUI 连不上 | 检查服务是否运行、端口 8188 是否开放 |
| 研究数据陈旧 | 触发 `comfyui-research` 更新 |
| 显存不足 | 启用 `--lowvram`、降低分辨率、用 FP8 量化 |

更多错误见 `references/故障排查.md`。

## 更新日志

### v1.0.0（2026-03-18）

- 首次发布
- 基于 ComfyUI-Expert 全量中文本地化
- 15 个 skill、5 个基础层文件、9 个参考文件
- 完整中文界面 + 技术专名保留英文

## 维护

- 仓库：{skill_root}/
- 上游：ComfyUI-Expert（英文原版）
- 维护人：comfyui-api-skills 编排器

## 许可证

本中文版基于英文版 ComfyUI-Expert。沿用 MIT 许可证（参考英文原版 LICENSE 文件）。

---

**开始使用**：

```powershell
# 安装
Copy-Item -Recurse "d:\workspace\my-trae-helper\skill-markets\comfyui-api-skills" "$env:USERPROFILE\.trae-cn\skills\comfyui-api-skills"

# 重启 Trae IDE
# 然后在 IDE 中告诉助手："扫描我的 ComfyUI 安装，{{COMFYUI_INSTALL_DIR}}"
```
