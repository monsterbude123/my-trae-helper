# ComfyUI 中文版技能包 — 用户指南

> 这份文档是给**使用本技能包的人**看的。安装与架构在 `README.md`，
> 路由规则在 `SKILL.md`（编排器），本文只回答：**我能用它做什么？**

---

## 一句话总结

把 ComfyUI 的 HTTP 接口、模型知识、调试经验打包成 15 个专项 skill，AI 助手根据你说的话自动路由——你说"做个角色图"它就调图像生成，你说"出错了"它就调排错。

---

## 15 个 Skill 能做什么

### 基础 3 个（任何项目都用得上）

| Skill | 你说 | 它做什么 |
|-------|------|----------|
| `comfyui-api` | "连接我的 ComfyUI" / "提交工作流" / "查进度" | 跑通 REST 调用：提交→轮询→取结果 |
| `comfyui-inventory` | "看看我装了啥" / "显存够吗" | 探查已装模型/节点/显存，缓存到 `state/inventory.json` |
| `project-manager` | "新建项目" / "添加角色" | 管项目清单、角色档案、生成历史 |

### 研究 1 个

| Skill | 你说 | 它做什么 |
|-------|------|----------|
| `comfyui-research` | "最新模型" / "Wan 2.6 怎么用" | 监控 YouTube/GitHub/HF，标记陈旧信息 |

### 核心创作 4 个

| Skill | 你说 | 它做什么 |
|-------|------|----------|
| `comfyui-prompt-interview` | "我有个模糊想法" / "帮我梳理" | 引导对话，产出创意简报 |
| `comfyui-prompt-engineer` | "优化这个 prompt" / "给 FLUX 写 prompt" | 按模型特性优化提示词（含负面提示词模板） |
| `comfyui-workflow-builder` | "搭个工作流" / "生成 JSON" | 从自然语言生成 ComfyUI 工作流 JSON |
| `comfyui-character-gen` | "生成角色图，保持脸一致" | 身份保持（InstantID/PuLID/IP-Adapter/LoRA） |

### 生产 4 个

| Skill | 你说 | 它做什么 |
|-------|------|----------|
| `comfyui-video-pipeline` | "做个视频" / "图生视频" | 调度视频引擎（LTX-2.3/Wan 2.6/Wan 2.2/HunyuanVideo/FramePack/AnimateDiff） |
| `comfyui-video-production` | "做一个 30 秒多镜头视频" | 端到端：关键帧→I2V 动画→拼接转场 |
| `comfyui-voice-pipeline` | "克隆这个声音" / "生成语音" | TTS 引擎（Qwen3-TTS/Chatterbox/IndexTTS-2/F5-TTS/VibeVoice）+ 口型同步 |
| `comfyui-lora-training` | "训练 Sage 的 LoRA" | AI-Toolkit/Kohya_ss/FluxGym 训练流程 |

### 输出 2 个

| Skill | 你说 | 它做什么 |
|-------|------|----------|
| `video-assembly` | "把这些剪辑拼起来" | FFmpeg 拼接、Remotion 高级合成 |
| `video-publisher` | "上传到 YouTube" | 多平台发布（YouTube/Shorts/Reels/TikTok） |

### 支持 1 个

| Skill | 你说 | 它做什么 |
|-------|------|----------|
| `comfyui-troubleshooter` | "出错了" / "OOM" / "节点找不到" | 四类错误（服务/工作流/质量/性能）诊断 + 修复建议 |

---

## 五种典型使用流程

### 流程 1：第一次启动

```
你：扫描我的 ComfyUI 安装，{{COMFYUI_INSTALL_DIR}}
AI：（调用 inventory）→ 输出已装模型/节点清单
你：显存多少？适合跑 FLUX 吗？
AI：32GB 够用，会自动选 FP8 量化节省显存
```

### 流程 2：角色图像

```
你：新建项目"角色展示"
AI：（调用 project-manager）→ 创建 projects/角色展示/清单.yaml
你：加角色 Sage——赤褐色长发，绿眼睛，雀斑，24 岁
AI：（写入角色档案）
你：用 FLUX 给 Sage 写一张写实肖像，柔光
AI：（route 到 prompt-interview → prompt-engineer → workflow-builder → character-gen）
   → 提交工作流 → 轮询 → 返回图像
```

### 流程 3：多镜头视频

```
你：做一个 30 秒的 Sage 演讲视频，分 5 个镜头
AI：（route 到 video-production）
   1. 生成 5 张关键帧
   2. 逐张做 I2V 动画
   3. 0.5s 交叉淡化拼接
   4. 导出 final.mp4
你：第 3 个镜头人脸崩了
AI：（route 到 troubleshooter）→ 调高 IP-Adapter 权重 → 重渲
```

### 流程 4：LoRA 训练

```
你：训练 Sage 的写实 LoRA
AI：（route 到 lora-training）
   1. 准备 25 张参考图
   2. 用 JoyTag 打标签
   3. 启动 AI-Toolkit（FLUX）
   4. 训练 1500 步 → 输出 .safetensors
你：跑一下测试图
AI：（用新 LoRA 生成对比图）
```

### 流程 5：发布

```
你：把刚才的视频发到 YouTube
AI：（route 到 video-publisher）
   1. 准备元数据（标题/描述/标签）
   2. 调用 YouTube API
   3. 上传 → 返回视频链接
```

---

## 配置文件

| 文件 | 作用 | 修改时机 |
|------|------|----------|
| `.env` | 全局配置（服务地址、路径、超时） | 换机器/换网络时 |
| `projects/{名}/清单.yaml` | 单项目配置 | 加新项目时 |
| `state/inventory.json` | 库存缓存 | 安装新模型后 |

完整说明：[配置.md](file:///d:/workspace/my-trae-helper/skill-markets/comfyui-api-skills/foundation/配置.md)

---

## 三个核心约定

1. **先查库存** — 生成任何工作流前必须先 `comfyui-inventory`，否则不知道模型装没装
2. **失败先排错** — 任何报错先 `comfyui-troubleshooter`，别瞎试
3. **状态要持久** — 成功配置写回项目清单，下次不用重复摸索

---

## 不会做的事

为了避免误用，下列场景本技能包**不**处理：

- ❌ 静态图像生成之外的视频剪辑（在 DaVinci/Premiere 里做）
- ❌ ComfyUI 安装与硬件推荐（看官方文档）
- ❌ 模型训练数据采集（自己准备）
- ❌ 商业变现与版权合规（自己判断）

---

## 下一步

- [ ] 复制 `.env.example` → `.env`，填入你的 ComfyUI 地址
- [ ] 复制整个包到 `~/.trae-cn/skills/`
- [ ] 重启 Trae IDE
- [ ] 试着说"扫描我的 ComfyUI 安装"
