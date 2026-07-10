---
name: comfyui-character-gen
description: 通过身份保持方法（InstantID、PuLID、IP-Adapter、LoRA）生成角色一致图像。本 skill 与全局 comfyui-character-gen 协同；本编排器负责补充库存上下文与工作流生成。用于带身份一致性的角色图像生成。
user-invocable: true
metadata: {"openclaw":{"emoji":"👤","os":["darwin","linux","win32"]}}
---

# 角色生成技能（编排器层包装）

包装全局 `comfyui-character-gen` skill，补充库存与项目上下文。

## 角色

全局 `comfyui-character-gen` 负责核心身份保持方法；本编排器层负责：

1. 读取库存并校验模型/节点
2. 读取角色档案提供上下文
3. 提交工作流到 ComfyUI
4. 跟踪生成结果

## 决策矩阵：身份保持方法

根据用户需求选择身份保持方法：

| 需求 | 推荐方法 | 显存 |
|------|----------|------|
| SDXL 单角色，最高保真度 | InstantID + IP-Adapter | 12-16GB |
| FLUX 单角色 | PuLID Flux II | 24-40GB |
| FLUX 2 单角色 | PuLID Flux 2 | 24-40GB |
| FLUX 多轮编辑 | FLUX Kontext | 12-32GB |
| 训练好的角色复用 | LoRA（强度 0.7-0.9） | 视基础模型 |
| 双角色 FLUX | PuLID Flux II（双实例） | 24-40GB |
| 风格/构图参考 | IP-Adapter Plus | +2-4GB |

## 调用流程

### 步骤 1：收集上下文

读取：

- `state/inventory.json`（确认模型/节点）
- `projects/{项目}/角色/{名}.yaml`（角色档案）
- `projects/{项目}/清单.yaml`（项目状态、默认设置）

### 步骤 2：选择身份保持方法

根据：

- 角色档案中的 LoRA（如有）
- 决策矩阵
- 用户明确要求

### 步骤 3：调用全局 comfyui-character-gen

委托给全局 skill 处理身份保持方法的核心逻辑：

- InstantID 工作流构造
- PuLID 参数配置
- LoRA 加载与强度
- IP-Adapter 应用

### 步骤 4：构造工作流并提交

通过 `comfyui-workflow-builder` 包装工作流 JSON，通过 `comfyui-api` 提交。

### 步骤 5：记录结果

成功生成后：

- 在 `清单.yaml` 追加到 `最近生成`
- 把有效配置加入 `有效组合`
- 必要时更新角色档案

## 角色档案必填项

执行前确认角色档案包含：

- [ ] 外貌特征（性别、年龄、发型、发色、眼睛等）
- [ ] 服装默认
- [ ] 参考图路径
- [ ] LoRA 信息（若有）
- [ ] 正面/负面提示词模板

缺失时通过 `project-manager` 提示用户补全。

## 典型提示词结构

### InstantID / PuLID（身份主导）

```
{角色名}，{稳定面部特征}，{场景}，{光线}，{风格}
```

不写：表情、姿态、动作（交给参考图）

### LoRA（已训练角色）

```
{LoRA 触发词}, {服装/场景}, {动态描述}
```

强度：写实 0.7-0.9，风格化 0.5-0.7

### IP-Adapter（参考风格）

```
{内容描述}, {风格关键词}
```

IP-Adapter 强度 0.5-0.8

## 组合策略

复杂场景可组合多种方法：

**LoRA + IP-Adapter**：
- LoRA：角色身份
- IP-Adapter：场景/风格
- 提示词：内容

**PuLID + LoRA**：
- PuLID：面部
- LoRA：身体/服装
- 注意不要让两者冲突

**InstantID + ControlNet**：
- InstantID：身份
- ControlNet：姿态/构图

## 故障排查

若角色一致性差：

1. 提升身份保持方法强度（如 PuLID 权重 0.8-1.0）
2. 使用更高质量参考图（正脸、清晰）
3. 添加负面提示词排除变形
4. 调整 CFG（FLUX 3.0-4.0，SDXL 6-8）
5. 增加步数（提升细节）
6. 考虑训练专属 LoRA

若生成失败：

- 转交 `comfyui-troubleshooter`
- 检查参考图路径
- 检查模型/节点是否安装

## 输出

生成完成后向用户报告：

1. 输出文件路径
2. 使用的身份保持方法与强度
3. 实际显存占用
4. 是否入库到 `有效组合`
5. 一致性观察（若用户反馈）

## 注意事项

- **不要**让所有方法互相冲突（如 LoRA + 强 IP-Adapter 可能过度风格化）
- 身份保持方法**不能叠加超过 3 个**——会互相干扰
- 参考图应**正脸、清晰、无遮挡**
- 多次实验后在角色档案记下**有效组合**
