# 模型微调指南

## 推荐框架：ms-swift

魔搭自研训练框架，支持预训练、SFT、RLHF、GRPO 等。

```bash
pip install ms-swift
```

## 快速开始（LoRA 微调）

```bash
swift sft \
    --model_type qwen2-7b-instruct \
    --model_id_or_path Qwen/Qwen2-7B-Instruct \
    --dataset your-dataset \
    --output_dir ./output \
    --sft_type lora \
    --num_train_epochs 3 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --learning_rate 1e-4
```

## 微调完整流程

1. **准备数据集**：上传到魔搭 Dataset 或本地 JSONL
   ```json
   {"query": "你是谁？", "response": "我是魔搭助手"}
   ```

2. **选择基座模型**：从魔搭模型库选，常见：
   - NLP: Qwen2/Qwen3、DeepSeek、GLM
   - CV: ResNet、ViT、YOLO 系列
   - 语音: Paraformer、CosyVoice

3. **在 Notebook 上训练**（免本地 GPU）：
   - 打开 https://modelscope.cn/my/mynotebook
   - 选 GPU 实例
   - 粘贴训练命令

4. **上传训练结果**：
   ```bash
   # 使用 CLI 上传
   modelscope upload --model your-username/your-model --local_dir ./output
   ```

## 关键参数速查

| 参数 | 说明 | 常用值 |
|------|------|--------|
| `--sft_type` | 微调方式 | `lora` / `full` |
| `--lora_rank` | LoRA 秩 | 8 / 16 / 32 |
| `--lora_alpha` | LoRA alpha | 32 |
| `--learning_rate` | 学习率 | 1e-4 ~ 5e-5 |
| `--num_train_epochs` | 训练轮数 | 1~5 |
| `--batch_size` | 批大小 | 1（显存紧）/ 4 |
| `--gradient_accumulation_steps` | 梯度累积 | 8 / 16 |
