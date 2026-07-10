---
name: comfyui-lora-training
description: 训练 LoRA 让角色或风格可复用。覆盖 AI-Toolkit（FLUX）、Kohya_ss（SDXL）、FluxGym/SimpleTuner（低显存）。含数据集准备（15-30 张图）、打标签策略、超参指导、检查点评估、LoRA 与零样本方法组合。用于训练 LoRA。
user-invocable: true
metadata: {"openclaw":{"emoji":"🎨","os":["darwin","linux","win32"],"requires":{"anyBins":["python"]}}}
---

# ComfyUI LoRA 训练技能

训练专属 LoRA 让角色或风格可复用。

## 训练工具选择

| 工具 | 适用 | FLUX.2 支持 | 显存需求 | 备注 |
|------|------|:---:|----------|------|
| Kohya ss（sd-scripts） | 金标准、最可配 | 是 | 12-24GB | IP noise gamma、FLUX 的 CFG 采样 |
| Musubi Tuner | 视频 LoRA（Wan/HunyuanVideo/FramePack） | 是（dev+klein） | 16-24GB | 激活值卸载省 20-30% |
| Ostris AI Toolkit | 简单 FLUX 训练 | 是（dev+klein） | 12-24GB | 即将支持 Apple MPS |
| FluxGym | 低显存 FLUX 训练 | 是 | 8-12GB | 简化界面 |
| SimpleTuner | 低显存 FLUX/SDXL | 是 | 8-16GB | 多种优化策略 |
| AI-Toolkit | FLUX 全功能 | 是 | 12-24GB | Ostris 旗下 |

## 决策表

| 需求 | 推荐工具 |
|------|----------|
| FLUX 角色 LoRA + 全功能 | Kohya ss |
| FLUX 角色 LoRA + 简单易用 | Ostris AI Toolkit / FluxGym |
| SDXL 角色 LoRA | Kohya ss |
| 8GB 显存 FLUX | FluxGym / SimpleTuner |
| Wan / HunyuanVideo 视频 LoRA | Musubi Tuner |
| 高级实验 + IP noise gamma | Kohya ss |

## 数据集准备

### 图像数量

- **最少**：15 张
- **推荐**：20-30 张
- **最多**：50 张（再增加边际收益下降）

### 图像要求

- 主体清晰、不同角度、不同场景
- 背景干净或多样（避免固定背景）
- 分辨率：1024x1024（FLUX）、512x512（SD1.5）、1024x1024（SDXL）
- 文件格式：PNG / JPG
- 体积：单张 1-5MB

### 角度覆盖建议

| 类型 | 数量 | 备注 |
|------|------|------|
| 正面 | 3-5 张 | 关键视角 |
| 侧面 | 3-5 张 | 45° 角、90° 角 |
| 3/4 角度 | 3-5 张 | 自然对话视角 |
| 半身 | 5-8 张 | 展示服装 |
| 全身 | 3-5 张 | 整体造型 |
| 不同表情 | 3-5 张 | 笑、严肃、惊讶等 |
| 不同场景 | 5-8 张 | 室内、室外、不同光线 |

## 打标签（Captioning）

### 自动打标签

使用 BLIP / JoyTag / Florence-2：

- 通用描述：自动生成
- 触发词：标记角色名
- 排除项：标记要排除的相似概念

### 手动调整

每张图的标签应该：

- **第一行**：触发词 `Sage, character, woman`（与训练同）
- **后续行**：场景、服装、动作、风格等
- **避免**：与角色相关的通用描述（避免污染）

**示例**：

```text
Sage, character, woman, portrait, leather jacket, forest background, golden hour lighting

Sage, character, woman, smile, indoor, cafe, natural light
```

### 标签策略

| 策略 | 适用 |
|------|------|
| 自然语言描述 | FLUX（语义理解强） |
| 短标签 | SD1.5（77 token 限制） |
| 混合 | SDXL |

## 训练参数

### FLUX LoRA

**推荐参数**（Kohya ss）：

```yaml
# 基础设置
pretrained_model: flux1-dev-fp8.safetensors
output_dir: ./output/sage_lora

# 网络
network_module: networks.lora_flux
network_dim: 16              # 16-32，值大更细但易过拟合
network_alpha: 16            # 通常等于 dim

# 优化器
optimizer: AdamW8bit
learning_rate: 1e-4
unet_lr: 1e-4
text_encoder_lr: 5e-5

# 训练
train_batch_size: 1
num_epochs: 20-30
save_every_n_epochs: 5
mixed_precision: bf16

# 高级
cache_latents: true
cache_latents_to_disk: true
ip_noise_gamma: 0.1          # 提升鲁棒性
caption_dropout_rate: 0.1    # 部分丢弃 caption

# 采样
sample_every_n_epochs: 5
sample_prompts:
  - "Sage, woman, leather jacket, forest"
```

**显存估算**：
- batch=1, 1024x1024: 18-24GB
- batch=1, 768x768: 12-16GB
- FP8 模型: 显存省 30%

### SDXL LoRA

**推荐参数**：

```yaml
pretrained_model: RealVisXL_V5.0.safetensors
network_dim: 32
network_alpha: 16
learning_rate: 1e-4
train_batch_size: 2
num_epochs: 10-15
mixed_precision: fp16
```

**显存估算**：
- batch=2, 1024x1024: 16-20GB
- batch=1, 1024x1024: 12-16GB

## 训练流程

### 步骤 1：数据准备

```bash
# 创建项目目录
mkdir -p datasets/sage_lora/{images,log,model}

# 复制训练图
cp /path/to/refs/*.png datasets/sage_lora/images/

# 生成 tags（用 BLIP / Florence-2 / JoyTag）
python scripts/blip_caption.py --input datasets/sage_lora/images \
                               --output datasets/sage_lora/images
```

### 步骤 2：配置训练

Kohya ss：

```bash
# 启动 GUI
python -m kohya_gui
# 或使用 sd-scripts 命令行
accelerate launch --num_cpu_threads_per_process 2 \
  sd-scripts/flux_train_network.py \
  --pretrained_model_name_or_path=./models/flux1-dev-fp8.safetensors \
  --train_data_dir=./datasets/sage_lora/images \
  --output_dir=./output/sage_lora \
  --network_module=networks.lora_flux \
  --network_dim=16 --network_alpha=16 \
  --optimizer=AdamW8bit \
  --learning_rate=1e-4 --unet_lr=1e-4 \
  --train_batch_size=1 \
  --num_epochs=25 \
  --mixed_precision=bf16 \
  --save_every_n_epochs=5
```

### 步骤 3：监控训练

- TensorBoard：观察 loss 下降
- 采样图：每 5 epoch 评估
- 关键指标：loss 平稳但不过拟合

**过拟合信号**：
- 训练图完美复刻
- 验证图风格接近但内容死板
- loss < 0.05

### 步骤 4：评估检查点

每个检查点都要测试：

- 强度 0.5 / 0.7 / 0.9
- 不同提示词
- 不同场景
- 记录最佳检查点与强度

### 步骤 5：部署到 ComfyUI

```bash
# 复制到 ComfyUI 模型目录
cp output/sage_lora/sage_lora-0025.safetensors \
   {ComfyUI}/models/loras/sage_v3.safetensors
```

更新 `state/inventory.json`（通过 `comfyui-inventory` 重新扫描）。

## 检查点评估

训练过程中定期评估：

### 评估脚本

```bash
python -m kohya_gui  # GUI 评估
# 或用 ComfyUI 工作流批量测试
```

### 评估维度

- 身份相似度（与原图对比）
- 多样性（不同提示词表现）
- 强度敏感度（0.5/0.7/0.9）
- 与基础模型兼容性
- 显存占用

### 评估样本

保存评估结果到 `projects/{项目}/角色/{名}_lora_eval.md`：

```markdown
# Sage LoRA 评估

## 检查点 0025（推荐）
- 强度 0.7：身份相似度 9/10，多样性 8/10
- 强度 0.85：身份相似度 9.5/10，多样性 7/10
- **推荐强度**：0.8

## 检查点 0020
- 训练不足，细节欠缺

## 检查点 0030
- 略过拟合
```

## LoRA 与零样本方法组合

训练好的 LoRA 可与零样本身份保持方法组合：

| 组合 | 适用 |
|------|------|
| LoRA + IP-Adapter | 角色 + 风格/构图 |
| LoRA + InstantID | SDXL 极致身份 |
| LoRA + ControlNet | 角色 + 姿态 |
| LoRA + 提示词 | 标准用法 |

**强度调整**：
- 单用 LoRA：0.7-0.9
- LoRA + 零样本：LoRA 0.5-0.7，零样本 0.5-0.8

## 常见问题

### 训练不收敛

- 提升 learning_rate（1e-4 → 2e-4）
- 增加 epoch
- 检查数据集质量

### 过拟合

- 降低 epoch
- 降低 learning_rate
- 增加数据集多样性
- 提高 caption_dropout_rate

### 显存不足

- 用 FP8 / NF4 量化
- 启用 gradient checkpointing
- 降低 batch_size
- 用 FluxGym / SimpleTuner

### 推理时不像

- 调整 LoRA 强度
- 换更近的训练检查点
- 检查提示词是否包含触发词
- 评估参考图质量

## 注意事项

- **数据集质量 > 数量**——20 张高质量胜过 100 张低质量
- **触发词稳定**——训练和推理用同一触发词
- **多检查点评估**——不同 epoch 效果差异大
- **记录评估结果**——便于后续迭代
- 商用前**确认许可证**（基础模型 + 工具）
