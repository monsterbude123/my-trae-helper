# 图像素材生成

> 引擎无关。角色立绘、场景背景、标题画面。

## 提示词工程流程

```
1. 查模板  → 读取 templates/prompts/{类型}.md
2. 查模型  → 运行时通过 ComfyUI `/object_info` 接口查询可用模型
3. 问用户  → 风格选择
4. 填参数  → 从 story-design.md 提取具体特征
```

**必须询问用户的选择：**

| 素材类型 | 选择项 |
|----------|--------|
| 角色立绘 | 模型：运行时查询 ComfyUI 可用 checkpoint（不接受硬编码） |
| 场景背景 | 风格：A 写实恐怖 / B 赛博朋克 / C 日式阴郁 |
| 音频 | 需要哪些 SFX？时长偏好？ |

## 批量生成策略

1. **先单张验证**：批量跑之前，先跑 1 张确认 workflow 正确（模型、CLIP、尺寸、seed）
2. **小批量测流水线**：先跑 2-3 张验证整条链路（提交 → 轮询 → 下载 → 校验）
3. **再全量**：流水线验证通过后批量跑
4. **校验自动化**：每张图生成后自动检查尺寸、透明度、饱和度、主体占比

## 通用生成脚本

通过 `comfyui-api-skills` 技能提供的 ComfyClient 进行生成：

```python
c = ComfyClient()
assert c.check_connection(), "ComfyUI 未运行"
models = c.available_checkpoints()
pid = c.submit(workflow)
result = c.poll(pid, timeout=600)
files = c.download(result, output_dir, prefix="")
```

## Workflow JSON 注意事项

| 问题 | 现象 | 修复 |
|------|------|------|
| JSON 含 `meta` 字段 | ComfyUI 400 错误：缺少 `class_type` 的节点 | 从 JSON 中删除所有 `meta` 字段 |
| submit 提交了整个 wf | 提交结构错误 | 如果模板结构是 `{"meta":{...},"workflow":{...}}`，提交 `wf["workflow"]` |
| 蓝图 subgraph 嵌套 | `apply_overrides` 无法处理 | 展平为平面 workflow 后再提交 |

## 角色立绘

> **铁律：素材生成前必须先加载 `comfyui-api-skills`**。不要凭印象拼 workflow——不同模型族的 clip/vae/采样器参数完全不同。

### 每张图生成前必查

```
[ ] 1. comfyui-api-skills 已加载
[ ] 2. 读取 knowledge/models/{识别出的族}.yaml
[ ] 3. 确认 c.available_checkpoints() 中模型名与 yaml 一致
[ ] 4. 加载 cache/workflows/{对应 workflow}.json 作为模板
[ ] 5. 模板里所有 {{PLACEHOLDER}} 都填好才提交
[ ] 6. 提交后 read poll 输出，不只是看 return value
```

### 模型族识别

执行 `c.available_checkpoints()` 拿到模型列表后，**按文件名匹配模型族**：

| 模型族 | 识别特征 | 必用 workflow 模板 |
|--------|----------|---------------------|
| **ANIMA** (Cosmos-Predict2 微调) | `*ANIMA*.safetensors`、`*JANIMA*.safetensors`、`miaomiaoHarem_anima*.safetensors`、`waiANIMA_*.safetensors` | `anima_txt2img.json` |
| SDXL | `*xl*`、`*XL_*`、`sdxl_*.safetensors`、`Juggernaut*.safetensors` | `sdxl_txt2img.json`（cfg=7.5, euler_ancestral, steps=28） |
| FLUX.1-dev | `flux*.safetensors`、`FLUX*.safetensors` | `flux_txt2img.json`（警告：FLUX 极易漂白角色） |
| SD 1.5 | 其余无明显特征的小 ckpt | 通用配置 + 警告"SD1.5 角色质量差" |

### ANIMA 模型族必读

ANIMA 系列的 ckpt 文件**不带 clip/vae**（CheckpointLoaderSimple 的 clip/vae 输出是 None）。必须三件套：

```
1. CheckpointLoaderSimple(ckpt_name=miaomiaoHarem_anima13.safetensors)  ← 拿 model
2. CLIPLoader(clip_name=qwen_3_06b_base.safetensors, type=stable_diffusion)  ← 独立 clip
3. VAELoader(vae_name=qwen_image_vae.safetensors)  ← 独立 vae
```

KSampler 参数：
- `sampler_name: er_sde`（不是 euler）
- `cfg: 4.0`（不是 7.0）
- `steps: 24`
- `scheduler: normal`
- 错误症状：`mat1 and mat2 shapes cannot be multiplied` = CLIP 维度错；`clip input is invalid: None` = 没用独立 CLIPLoader

### 立绘生成流程

1. `c.available_checkpoints()` → 匹配模型族
2. 选对应 workflow 模板
3. 从 `story-design.md` 提取每个角色外观特征
4. 替换模板的 `{{POSITIVE}}` `{{NEGATIVE}}` `{{WIDTH}}` `{{HEIGHT}}` `{{SEED}}` `{{PREFIX}}`
5. 提交并下载
6. 抠图（白底图用 numpy `white_to_alpha()`，人物图用 rembg）
7. 保存到 `{game_key}/figure/{角色拼音}.png`

### 提示词结构

- 开头：`masterpiece, highres, absurdres, newest, best quality, score_7`
- 中段：`1girl, solo, simple background, white background, [年龄+外观特征]`
- negative：`ugly, blurry, low quality, distorted, deformed, watermark, text, multiple people, extra limbs, bad anatomy`

## 场景背景

1. 让用户选择风格（A/B/C）
2. 每个场景按模板组装提示词
3. ComfyUI 生成（1216x832 横版）→ 转 `.webp`（quality=90）
4. 保存到 `{game_key}/background/{场景名}.webp`

## 标题画面

生成 1920x1080，保存为 `{game_key}/background/bg.webp`。
