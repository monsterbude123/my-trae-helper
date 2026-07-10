# LoRA 训练手册

> 训练参数与最佳实践完整指南。

## 训练工具对比

| 工具 | 适用 | FLUX.2 支持 | 显存 | 优势 |
|------|------|:---:|------|------|
| Kohya ss（sd-scripts） | 金标准、全功能 | 是 | 12-24GB | IP noise gamma、FLUX 的 CFG 采样 |
| Musubi Tuner | 视频 LoRA | 是 | 16-24GB | 激活值卸载省 20-30% 显存 |
| Ostris AI Toolkit | 简单 FLUX 训练 | 是 | 12-24GB | 易用 |
| FluxGym | 低显存 FLUX | 是 | 8-12GB | 简化界面 |
| SimpleTuner | 低显存 FLUX/SDXL | 是 | 8-16GB | 多种优化策略 |

## 数据集准备

### 数量建议

| 目标 | 最少 | 推荐 | 最多 |
|------|------|------|------|
| 角色 | 15 | 20-30 | 50 |
| 风格 | 30 | 50-100 | 200 |
| 概念 | 50 | 100-200 | 500 |

### 图像要求

- 主体清晰、不同角度
- 背景干净或多样
- 分辨率：
  - FLUX：1024x1024
  - SDXL：1024x1024
  - SD1.5：512x512
- 格式：PNG（无损）或 JPG（高质）
- 单张 1-5MB

### 角度覆盖

| 角度 | 数量 | 备注 |
|------|------|------|
| 正面 | 3-5 | 关键视角 |
| 45° | 3-5 | 自然对话 |
| 侧面 | 3-5 | 90° |
| 半身 | 5-8 | 展示服装 |
| 全身 | 3-5 | 整体造型 |
| 表情 | 3-5 | 笑、严肃、惊讶等 |
| 场景 | 5-8 | 室内、室外、不同光线 |

## 打标签（Captioning）

### 自动工具

| 工具 | 仓库 | 特色 |
|------|------|------|
| BLIP | https://github.com/salesforce/BLIP | 通用 |
| Florence-2 | https://huggingface.co/microsoft/Florence-2-large | 详细 |
| JoyTag | https://github.com/novitalabs/joytag | 标签式 |
| CogVLM | https://github.com/THUDM/CogVLM | 详细多模态 |
| LLaVA | https://github.com/haotian-liu/LLaVA | 详细 |

### 标签格式

#### FLUX（自然语言）

```text
Sage, character, woman, portrait, leather jacket, forest background, golden hour lighting, 50mm lens

Sage, character, woman, smile, indoor, cafe, natural light, professional photography
```

**注意**：首行触发词稳定，后续描述场景。

#### SDXL（混合）

```text
(masterpiece, best quality:1.3), photorealistic, 1girl, auburn hair, green eyes, freckles, leather jacket, forest, sunlight
```

**负面**：`(cartoon:1.3), (deformed:1.2), (extra fingers:1.4), blurry`

#### SD1.5（短标签）

```text
(masterpiece:1.3), (best quality:1.3), photorealistic, 1girl, auburn_hair, green_eyes, freckles, leather_jacket, forest, sunlight
```

## FLUX LoRA 训练配置

### Kohya ss 完整配置

```yaml
# 基础
pretrained_model: flux1-dev-fp8.safetensors
output_dir: ./output/sage_lora
output_name: sage_v3
save_precision: bf16

# 网络
network_module: networks.lora_flux
network_dim: 16              # 16-32，越大越细但易过拟合
network_alpha: 16            # 通常等于 dim
network_train_unet_only: false

# 优化器
optimizer: AdamW8bit
learning_rate: 1e-4
unet_lr: 1e-4
text_encoder_lr: 5e-5

# 训练
train_batch_size: 1
num_epochs: 25
save_every_n_epochs: 5
mixed_precision: bf16
gradient_checkpointing: true

# 数据
train_data_dir: ./datasets/sage_lora
resolution: 1024x1024
bucket_reso_steps: 64
caption_extension: .txt

# 高级
cache_latents: true
cache_latents_to_disk: true
ip_noise_gamma: 0.1
caption_dropout_rate: 0.1
caption_dropout_every_n_epochs: 0
caption_tag_dropout_rate: 0.0

# 采样
sample_every_n_epochs: 5
sample_prompts:
  - "Sage, woman, leather jacket, forest, golden hour, portrait"
  - "Sage, character, smile, indoor, cafe, natural light"
  - "Sage, character, full body, urban, daytime, professional"
```

### 显存优化

| 优化 | 显存节省 | 速度影响 |
|------|----------|----------|
| FP8 模型 | -30% | 略快 |
| gradient_checkpointing | -30% | 慢 20% |
| batch_size=1 | 基准 | — |
| 8bit Adam | -10% | 略慢 |
| NF4 量化 | -50% | 慢 30% |
| 启用 LyCORIS（LoKr） | 同 LoRA | 类似 |

### 参数调优指南

| 现象 | 调整 |
|------|------|
| 训练不收敛 | LR 1e-4 → 2e-4；增 epoch |
| 过拟合 | 减 epoch；增数据集；caption_dropout 0.1 → 0.2 |
| 显存不足 | 启用 gradient_checkpointing；用 FP8/NF4；降 batch |
| 推理不像 | 调 LoRA 强度；用更近检查点 |
| 风格污染 | 强化 ip_noise_gamma；增 caption_dropout |

## SDXL LoRA 训练配置

```yaml
pretrained_model: RealVisXL_V5.0.safetensors
network_dim: 32
network_alpha: 16
learning_rate: 1e-4
train_batch_size: 2
num_epochs: 12
mixed_precision: fp16
gradient_checkpointing: true
resolution: 1024x1024
min_bucket_reso: 512
max_bucket_reso: 2048
caption_extension: .txt
```

**显存**：
- batch=2, 1024x1024: 16-20GB
- batch=1, 1024x1024: 12-16GB

## 视频 LoRA（Wan / HunyuanVideo / FramePack）

### Musubi Tuner 配置

```yaml
model: Wan2.1
dataset:
  video_directory: ./datasets/video_lora
  num_frames: 81
  frame_stride: 3
  resolution: [480, 832]

network:
  dim: 32
  alpha: 32

training:
  learning_rate: 5e-5
  batch_size: 1
  num_epochs: 10
  mixed_precision: bf16
  gradient_checkpointing: true
  activation_offloading: true  # 省 20-30% 显存

optimizer:
  type: AdamW8bit
```

**显存**：16-24GB（含 activation_offloading）

## 训练流程

### 命令行（Kohya ss）

```bash
# 安装
git clone https://github.com/bmaltais/kohya_ss.git
cd kohya_ss
setup.sh  # 或 setup.bat（Windows）

# 准备数据集
mkdir -p datasets/sage_lora/{images,log,model}
cp /path/to/refs/*.png datasets/sage_lora/images/

# 生成 tags
python tools/blip_caption.py \
  --input datasets/sage_lora/images \
  --output datasets/sage_lora/images

# 训练（FLUX）
accelerate launch --num_cpu_threads_per_process 2 \
  sd-scripts/flux_train_network.py \
  --pretrained_model_name_or_path=./models/flux1-dev-fp8.safetensors \
  --train_data_dir=./datasets/sage_lora/images \
  --output_dir=./output/sage_lora \
  --output_name=sage_v3 \
  --network_module=networks.lora_flux \
  --network_dim=16 --network_alpha=16 \
  --optimizer=AdamW8bit \
  --learning_rate=1e-4 --unet_lr=1e-4 --text_encoder_lr=5e-5 \
  --train_batch_size=1 \
  --num_epochs=25 \
  --save_every_n_epochs=5 \
  --mixed_precision=bf16 \
  --gradient_checkpointing \
  --cache_latents --cache_latents_to_disk \
  --ip_noise_gamma=0.1 \
  --caption_dropout_rate=0.1 \
  --sample_every_n_epochs=5 \
  --sample_prompts="Sage, woman, leather jacket, forest" \
  --save_precision=bf16
```

### 监控

```bash
# TensorBoard
tensorboard --logdir=./output/sage_lora/log
```

观察：
- **loss** 平稳下降并稳定
- **样本图** 逐渐符合预期
- **过拟合信号**：loss < 0.05 + 训练图完美复刻

## 检查点评估

### 评估模板

对每个检查点（每 5 epoch 保存）测试：

| 强度 | 提示词 | 评估维度 |
|------|--------|----------|
| 0.5 | Sage 半身像 | 身份相似度、多样性 |
| 0.7 | Sage 户外 | 身份相似度、多样性 |
| 0.85 | Sage 室内 | 身份相似度、细节 |
| 1.0 | Sage 极端场景 | 过拟合信号 |

### 评估记录

```markdown
# Sage LoRA 评估 - 2026-03-18

## 检查点 0025（推荐）
- 强度 0.7：身份 9/10，多样性 8/10
- 强度 0.85：身份 9.5/10，多样性 7/10
- **最佳强度**：0.8
- **显存**：22GB

## 检查点 0020
- 训练不足，脸部细节欠

## 检查点 0030
- 略过拟合，建议保留但不优先
```

## 部署

```bash
# 复制到 ComfyUI
cp output/sage_lora/sage_v3-0025.safetensors \
   {ComfyUI}/models/loras/sage_v3.safetensors

# 重新扫描库存
pwsh -File scripts/扫描清单.ps1 -ComfyUI安装路径 "{{COMFYUI_INSTALL_DIR}}"
```

## 常见问题

### 训练后推理不像

**原因**：
- 训练集不够多样
- 触发词不匹配
- 强度过低

**修复**：
- 调整 LoRA 强度（0.7-0.9）
- 检查推理时触发词
- 用更近的检查点
- 补训几轮

### 显存不足

**修复**：
- 启用 `gradient_checkpointing`
- 用 FP8/NF4 量化
- 降低 batch_size
- 用 FluxGym / SimpleTuner（低显存优化）
- 减少 dataset 并发

### 训练很慢

**优化**：
- 启用 `cache_latents_to_disk`
- 用 8bit 优化器
- 减 `caption_dropout_rate`
- 关 `gradient_checkpointing`（若显存够）

### 风格污染

**修复**：
- 强化 `ip_noise_gamma`（0.1 → 0.3）
- 提高 `caption_dropout_rate`
- 减少训练集风格类图
- 用更窄的触发词

## 商用合规

训练前确认：

- [ ] 基础模型许可证允许商用（如 FLUX.1-dev 默认非商用）
- [ ] 训练图像有合法使用权
- [ ] 角色身份有授权（真人需本人同意）
- [ ] 训练输出不侵犯第三方权利

## 维护说明

- 更新日期：2026-03-18
- 维护人：comfyui-api-skills 编排器
- 关联：基础模型清单见 `references/模型清单.md`
