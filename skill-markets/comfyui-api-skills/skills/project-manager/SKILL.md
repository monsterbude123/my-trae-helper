---
name: project-manager
description: 创建带有 YAML 清单和角色档案的项目结构。跟踪生成历史、记录有效配置、管理角色身份（外貌、声音、LoRA、参考图）、在成功运行后更新默认值。用于管理项目与角色档案。
user-invocable: true
metadata: {"openclaw":{"emoji":"📁","os":["darwin","linux","win32"]}}
---

# 项目管理技能

管理项目结构、角色档案、生成历史。

## 项目结构

每个项目位于 `projects/{项目名}/`：

```
projects/{项目名}/
├── 清单.yaml              项目元数据与目标
├── 角色/
│   ├── {角色名}.yaml       角色档案
│   └── 参考图/            角色参考图像
├── 工作流/                工作流 JSON 文件
│   └── {名称}.json
├── 生成记录/              输出结果
│   └── {时间戳}/
└── 笔记.md                自由形式笔记
```

## 项目清单

`清单.yaml` 记录项目元数据：

```yaml
项目名: 角色展示
描述: 用 FLUX 写实风格呈现多个角色
创建时间: 2026-02-01
状态: 进行中
当前角色: Sage
comfyui_url: "{{COMFYUI_URL}}"
默认设置:
  模型: flux1-dev-fp8.safetensors
  步数: 28
  CFG: 3.5
  采样器: euler
  调度: normal
  分辨率: 1024x1024
最近生成:
  - 时间: 2026-02-15T14:30:00Z
    类型: 肖像
    模型: flux1-dev-fp8.safetensors
    提示词摘要: "Sage 半身像，森林背景"
    评级: 良好
有效组合:
  - 模型: flux1-dev-fp8.safetensors
    LoRA: sage_v3.safetensors
    LoRA强度: 0.85
    用途: 写实肖像
```

## 角色档案

`角色/{名}.yaml` 记录角色身份：

```yaml
角色名: Sage
外貌:
  性别: 女
  年龄: 28
  发型: 波浪长发
  发色: 赤褐
  眼睛: 绿色
  肤色: 浅
  体型: 中等
  特征: 雀斑
服装默认:
  - 棕色皮夹克
  - 米色围巾
  - 牛仔靴
声音档案:
  参考音频: 参考图/voice_sample.wav
  性别: 女
  音调: 中
  语速: 中
  口音: 美式
LoRA:
  - 名称: sage_v3.safetensors
    基础模型: flux1-dev
    训练步数: 2500
    强度建议: 0.8-0.9
参考图:
  - 参考图/ref_01.png
  - 参考图/ref_02.png
正面提示词模板: "Sage, {场景}, 写实人像, 自然光, 50mm"
负面提示词: "卡通, 绘画, 变形, 多余手指, 模糊"
```

## 创建项目

收到"创建项目"请求时：

1. 询问项目名、目标、首选模型
2. 在 `projects/{项目名}/` 下创建目录结构
3. 写入 `清单.yaml`
4. 若有角色，创建 `角色/{名}.yaml`

## 添加角色

收到"添加角色"请求时：

1. 询问角色名、外貌、风格
2. 在 `角色/{名}.yaml` 写入档案
3. 在 `清单.yaml` 的 `当前角色` 字段引用

## 记录生成

每次成功生成后：

1. 在 `清单.yaml` 的 `最近生成` 数组追加
2. 若评级良好，把配置加入 `有效组合`
3. 必要时更新 `默认设置`

## 跟踪有效配置

`有效组合` 是关键字段——记录**经实战验证**的配置组合。下次类似任务时优先复用：

```yaml
有效组合:
  - 标签: 写实肖像
    模型: flux1-dev-fp8.safetensors
    LoRA: sage_v3.safetensors
    LoRA强度: 0.85
    步数: 28
    CFG: 3.5
    备注: "森林/自然背景效果最佳"
  - 标签: 室内场景
    模型: flux1-dev-fp8.safetensors
    灯光: 暖色
    备注: "室内增加 CFG 至 4.0 提升对比"
```

## 与其它 skill 的协同

- `comfyui-prompt-engineer` 读取角色档案补充上下文
- `comfyui-character-gen` 引用 `参考图/` 目录
- `comfyui-lora-training` 把训练好的 LoRA 写回角色档案
- `comfyui-voice-pipeline` 使用 `声音档案` 字段

## 注意事项

- 角色档案应**只含通用且经多次成功验证**的描述
- 临时实验设置放在 `笔记.md` 而非档案
- 每次改动角色档案前应做备份
