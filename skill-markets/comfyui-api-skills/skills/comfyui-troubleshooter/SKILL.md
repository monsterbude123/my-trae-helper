---
name: comfyui-troubleshooter
description: 诊断四类错误（服务、工作流、质量、性能），覆盖十大常见错误（OOM、节点缺失、精度不匹配、人脸崩坏等）并给出快速修复方案。含质量决策树与缺失依赖解决。用于排查 ComfyUI 故障或错误。
user-invocable: true
metadata: {"openclaw":{"emoji":"🛠️","os":["darwin","linux","win32"]}}
---

# ComfyUI 故障排查技能

诊断并修复 ComfyUI 错误。

## 错误分类

| 类别 | 典型症状 |
|------|----------|
| **服务类** | 连接失败、500 错误、无响应 |
| **工作流类** | 节点缺失、连线错误、参数非法 |
| **质量类** | 人脸崩坏、变形、过饱和、模糊 |
| **性能类** | OOM（显存不足）、运行缓慢、卡顿 |

## 错误排查流程

### 第 1 步：抓取错误信号

从以下来源获取信息：

- ComfyUI 控制台日志
- 接口响应（`/history/{prompt_id}`）
- 浏览器控制台（前端界面）
- 生成的图片（质量问题）

### 第 2 步：归类

按上述四类归类。

### 第 3 步：匹配模式

按下面"十大常见错误"库匹配。

### 第 4 步：给出修复方案

- 命令行操作
- 配置文件修改
- 工作流参数调整
- 模型/节点安装指引

### 第 5 步：验证

修复后重新运行验证。

## 十大常见错误

### 错误 1：显存不足（OOM / CUDA Out of Memory）

**症状**：

```
torch.cuda.OutOfMemoryError: CUDA out of memory.
Tried to allocate 2.00 GiB...
```

**原因**：
- 模型太大
- 批量过大
- 分辨率过高
- 同时加载多个模型

**修复**：

| 显存 | 建议 |
|------|------|
| < 12GB | 用 SD1.5 / FLUX FP8 / FramePack |
| 12-16GB | SDXL / FLUX FP8 / HunyuanVideo 1.5（小批量） |
| 16-24GB | FLUX FP16 / Wan 2.2 14B（小批量） |
| 24GB+ | 全模型原生 |
| 32GB+ | 无限制 |

**操作**：
- 减小 `batch_size`
- 降低分辨率
- 用 FP8/NVFP4 量化
- 启用 `--lowvram` / `--novram` 启动参数
- 关闭并行模型（卸载 LoRA、ControlNet 等）

### 错误 2：节点缺失

**症状**：

```
<class_type> not found: ApplyInstantID
```

**原因**：
- 自定义节点未安装
- 节点包路径错误
- 节点包版本过旧

**修复**：

```bash
# 通过 ComfyUI-Manager 安装
# 1. 重启 ComfyUI
# 2. 打开 Manager
# 3. Install Missing Custom Nodes

# 或手动安装
cd {ComfyUI}/custom_nodes
git clone https://github.com/cubiq/ComfyUI_InstantID.git
cd ComfyUI_InstantID
pip install -r requirements.txt
```

**节点-包映射**：见 `comfyui-inventory` 的"常见节点-包映射"。

### 错误 3：模型缺失

**症状**：

```
FileNotFoundError: flux1-dev.safetensors not found in checkpoints
```

**修复**：
- 从 `references/模型清单.md` 查下载链接
- 放到正确目录：
  - checkpoint → `models/checkpoints/`
  - lora → `models/loras/`
  - vae → `models/vae/`
  - controlnet → `models/controlnet/`
  - clip → `models/clip/`
- 重启 ComfyUI 或刷新节点

### 错误 4：精度不匹配

**症状**：
- 黑色输出
- 全噪点
- 模型加载警告

**修复**：
- 确认 checkpoint 是 FP16 / FP32 / FP8 中的哪种
- 启动参数 `--fp8_e4m3fn-unet` 切换
- VAE 用对应精度版本

### 错误 5：人脸崩坏

**症状**：
- 脸部变形
- 眼睛错位
- 皮肤糊状

**修复**：

| 方法 | 强度 |
|------|------|
| 加负面提示词 | `(deformed face:1.3), (cross-eyed:1.2), (poor facial details:1.2)` |
| 提升 CFG | FLUX 3.0 → 4.0；SDXL 7 → 8 |
| 增加步数 | FLUX 28 → 35；SDXL 30 → 40 |
| 换身份保持 | 提升 InstantID/PuLID 强度 |
| 用人脸修复 | `FaceDetailer` + `codeformer.pth` |
| 调整提示词 | 移除"abstract, surreal"等冲突词 |

### 错误 6：手部畸形

**症状**：
- 多余手指
- 手指粘连
- 手部消失

**修复**：
- 负面提示词：`(extra fingers, mutated hands:1.4), (extra limbs:1.3)`
- 用手部修复 LoRA（如 `hands-fix`）
- 提升分辨率（手部需要细节）
- 用 ControlNet（深度图控制手部姿态）

### 错误 7：过饱和 / 偏色

**症状**：
- 颜色不自然
- 整体偏橙/偏蓝

**修复**：
- 降低 CFG
- 换采样器（dpmpp_2m + karras 通常稳定）
- 调整提示词（移除"vivid, saturated"等）
- 用 `ImageColorCorrect` 节点后处理

### 错误 8：过拟合 / 模式崩坏

**症状**：
- 所有图风格雷同
- 训练图被完美复刻（LoRA）

**修复**：
- LoRA 训练：降低 epoch、增加数据集多样性、提高 caption_dropout
- 推理：降低 LoRA 强度（0.9 → 0.6）
- 换不同种子

### 错误 9：连接被拒 / 服务未运行

**症状**：

```
curl: (7) Failed to connect to {{COMFYUI_URL}} port 8188
```

**修复**：

```bash
# 检查 ComfyUI 状态
ps aux | grep -i comfyui

# 启动 ComfyUI
cd {{COMFYUI_INSTALL_DIR}}
python main.py {{COMFYUI_LAUNCH_FLAGS}}

# 或用 launcher
# 启动后等待 5-10 秒，再调用
```

### 错误 10：视频生成失败

**症状**：
- 视频帧缺失
- 时间不一致
- 黑屏/绿屏

**修复**：
- 检查 VAE（Wan / HunyuanVideo / LTX 各有专用 VAE）
- 用 `VHS_VideoCombine` 而非 `SaveImage`
- 检查 fps 与总帧数匹配
- 长视频拆分为多段
- 用 FramePack 处理长视频

## 质量决策树

图像生成后质量不佳时的决策路径：

```
生成图
  ↓
主体是否清晰？
  ├─ 否 → 提升步数 / 提升分辨率 / 用 img2img
  └─ 是
      ↓
      身份是否一致？
        ├─ 否 → 用身份保持方法 / 训练 LoRA
        └─ 是
            ↓
            构图是否合适？
              ├─ 否 → 用 ControlNet 控制
              └─ 是
                  ↓
                  风格是否符合预期？
                    ├─ 否 → 调整提示词 / 换 IP-Adapter 参考
                    └─ 是 → 完成
```

## 缺失依赖解决

### 缺失 Python 包

```bash
# 看错误堆栈
# 通常是 ModuleNotFoundError

# 安装
{ComfyUI}/venv/bin/pip install {package_name}
# 或全局
pip install {package_name}
```

### 缺失系统库

```bash
# Ubuntu/Debian
sudo apt install {lib_name}

# macOS
brew install {lib_name}
```

### 缺失 cuDNN

```bash
# 检查
python -c "import torch; print(torch.backends.cudnn.version())"

# 升级
pip install --upgrade torch torchvision
```

## 性能优化

| 问题 | 方案 |
|------|------|
| 生成慢 | 启用 TeaCache / WaveSpeed / Nunchaku |
| 启动慢 | 关闭未用节点包 |
| 显存占用高 | 用 FP8 / NVFP4 量化 |
| 视频生成慢 | 启用 SageAttn、WaveSpeed |

## 何时升级

遇到以下情况时建议升级：

- ComfyUI 版本超过 3 个月未更新
- 关键 bug 已修复但本地未应用
- 新模型/节点需要新版本支持
- 安全公告

## 报告模板

排查完成时输出：

```markdown
# 故障排查报告

## 错误
{用户报告的错误}

## 原因
{根本原因}

## 修复
{具体步骤}

## 验证
{修复后结果}

## 预防
{如何避免再次发生}
```

## 注意事项

- 错误信息**完整记录**——不要只截最后一两行
- **复现路径**——确认问题可复现
- **修改前备份**——工作流、配置、模型版本
- 排查完成后**记录到项目笔记**——便于团队复用
