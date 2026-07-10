# 模型注册表生成器

扫描本地模型仓库目录，自动生成 `model-registry.yaml` 的骨架。

## 用法

```powershell
.\scripts\scan-models.ps1 -RepoPath "D:\ai-models" -OutputPath "D:\ai-models\model-registry.yaml"
```

## 扫描逻辑

1. 遍历仓库每个子目录
2. 对每个 `.safetensors` / `.ckpt` / `.gguf` / 目录型模型生成一条记录
3. 根据所在目录自动推断 `type`
4. 计算 SHA256 和文件大小
5. `capabilities`、`recommended_for`、`quality` 等字段标记为 `# TODO: 请手动填写`

## 目录到类型的自动映射

| 目录 | 推断类型 |
|------|---------|
| `checkpoints/` | checkpoint |
| `loras/` | lora |
| `diffusion_models/` | diffusion_model |
| `text_encoders/` | text_encoder |
| `vae/` | vae |
| `controlnet/` | controlnet |
| `upscale_models/` | upscaler |
| `clip_vision/` | clip_vision |
| `llm/` | llm |
| `tts/` | tts |
