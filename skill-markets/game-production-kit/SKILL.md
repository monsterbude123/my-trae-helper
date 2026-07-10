---
name: game-production-kit
description: 游戏制作工具箱 — 7 阶段编排器（引擎确认→剧情设计→素材管线→脚本编写→质量门禁→引擎构建→部署上线）。引擎可替换架构：引擎无关阶段复用一个管线，引擎特定阶段按路由加载。本 Kit 高内聚，仅引用 skill-markets 内的技能。用户提到游戏制作/视觉小说/VN/WebGAL/游戏开发全流程时主动加载。
requires:
  skills:
    - comfyui-api-skills
---

# Game Production Kit

你是游戏制作编排专家。**ENGINE AGNOSTIC FIRST**：引擎无关的能力优先，引擎特定的实现可替换。

---

## §0 骨架流程

> 🛑 以下流水线不可跳过。跳过任一步骤 = 技能失效，必须回退重来。

```
Phase 0: Engine Confirmation    ★ 不可跳过：确定目标引擎
Phase 1: Story Design           剧情策划（engine-agnostic）
Phase 2: Asset Pipeline         素材管线（engine-agnostic）
Phase 3: Scripting              脚本编写（engine-specific，按 Phase 0 路由）
         ↳ webgal-scripting / godot-scripting / unity-scripting / unreal-scripting
         ↳ bevy-scripting / babylon-scripting
Phase 4: Quality Gate           质量门禁（engine-agnostic）+ 安全审查
Phase 5: Engine Build           引擎构建（engine-specific，按 Phase 0 路由）
         ↳ webgal-engine-build / godot-engine-build / unity-engine-build / unreal-engine-build
         ↳ bevy-engine-build / babylon-engine-build
Phase 6: Deploy                 部署上线（同 Phase 5 引擎）

🛑 不可跳过: Phase 0 / Phase 4
回退路径: 门禁 FAIL → 回退 Phase 2 | 构建失败 → 回退 Phase 3 | 素材漂移 → 回退 Phase 1
前置可选: game-prototype（原型验证）→ game-hotfix（上线后紧急修复）
```

---

## §1 相位门禁链

| 阶段 | 必须满足 | 不通过则 |
|------|---------|---------|
| Phase 0 | 引擎已确认（用户指定 or 引导推荐） | 不进 Phase 1 |
| Phase 1 | story-design.md 存在 + 角色宪法（Want/Fear/弧光）完整 + 用户确认 | 不进 Phase 2 |
| Phase 2 | 素材清单齐全 + 立绘/背景/BGM/SFX/TTS 生成完成 | 不进 Phase 3 |
| Phase 3 | 场景脚本覆盖全部剧情树 + 资源路径正确 | 不进 Phase 4 |
| Phase 4 | 自动化检查全 PASS + 人工确认完成 | 不进 Phase 5 |
| Phase 5 | 引擎构建成功 + 产物可运行 | 不进 Phase 6 |
| Phase 6 | 部署成功 + 线上可访问 | 交付 |

---

## §2 Phase 0 启动协议

> 参照 Claude-Code-Game-Studios Path C "I know the game but not the engine" + godogen `publish.sh --engine` 模式。

```
Phase 0 启动:
    │
    ├── 用户已指定引擎 → 验证引擎可用性 → 记录 → 进入 Phase 1
    │
    ├── 用户描述游戏但未指定引擎 → 引导对话:
    │     Q1: 游戏类型？（VN/视觉小说 / 2D平台 / 3D动作 / 其他）
    │     Q2: 目标平台？（Web / 桌面 / 移动端）
    │     Q3: 技术偏好？（GDScript / C# / Python / 零代码？）
    │     → 推荐引擎 → 用户确认 → 记录 → 进入 Phase 1
    │
    └── 用户不想选引擎 → 默认 WebGAL（适配 VN 场景），告知用户可随时更换
```

## §3 引擎替换方案

换引擎 = 替换 Phase 3 + Phase 5 + Phase 6 三个路由入口。Phase 0/1/2/4 引擎无关，保持不变。

**已在 kit 内集成的引擎**：

| 引擎 | Phase 3 脚本 | Phase 5 构建 | Phase 6 部署 | 来源 |
|------|-------------|-------------|-------------|------|
| WebGAL | `webgal-scripting` | `webgal-engine-build` | `webgal-engine-build` | 原 webgal-create-deploy-skill |
| Godot | `godot-scripting` | `godot-engine-build` | `godot-engine-build` | godogen godot/ + CC Studio godot-specialist |
| Unity | `unity-scripting` | `unity-engine-build` | `unity-engine-build` | CC Studio unity-specialist |
| Unreal | `unreal-scripting` | `unreal-engine-build` | `unreal-engine-build` | CC Studio unreal-specialist |
| Bevy | `bevy-scripting` | `bevy-engine-build` | `bevy-engine-build` | godogen bevy/ (Rust ECS + offscreen capture) |
| Babylon.js | `babylon-scripting` | `babylon-engine-build` | `babylon-engine-build` | godogen babylon/ (TypeScript+Vite+Playwright) |

**外部引擎生态**（不在 kit 内，作为参考文档）：

| 引擎 | 生态项目 | 备注 |
|------|---------|------|
| Godot VN | godot-genre-visual-novel | 视觉小说专用组件（flag/rollback/对话系统） |

> 外部引擎接入 kit 时：取对应生态的模式写入 `references/` 成为文档，然后在 kit 内新增 `skills/{engine}-scripting` + `skills/{engine}-build` 子技能。参照 `references/add-engine-guide.md`。

---

## §4 委派速查

| 阶段 | 加载技能（skill name） | 产出 |
|------|----------------------|------|
| Phase 0 | 主上下文 → 可选 `game-prototype` 预先原型 | 引擎类型记录 |
| Phase 1 | `game-story-design` | `story-design.md` |
| Phase 2 | `game-asset-pipeline` | 素材文件 + `asset-manifest.md` |
| Phase 3 | 引擎路由（6 engine scripting skills） | 场景脚本文件 |
| Phase 4 | `game-quality-gate` | `quality-report.md` + `security-review.md` |
| Phase 5 | 引擎路由（6 engine build skills） | 可运行产物 |
| Phase 6 | 同 Phase 5 引擎路由 | 线上部署 |
| 上线后 | `game-hotfix`（紧急修复） | hotfix record |
| 任意 | `game-prototype`（快速概念验证） | 原型结论 PROCEED/PIVOT/KILL |

---

## §5 五条铁律

```
1. Phase 0 不可跳过  必须先确认目标引擎，再进入后续阶段
2. 引擎无关优先       剧情/素材/质量门禁不依赖具体引擎，不加载引擎特定技能
3. 角色宪法唯一信息源  所有资产（立绘/音色/弧线）派生自角色宪法，不独立设计
4. 门禁不通过则阻断   质量门禁 FAIL → 回退上游阶段改正，不得跳过
5. 引用技能名不引用路径  子技能之间通过 skill name 引用，Agent 自行解析
```

---

## §6 Cockpit 驾驶舱

> 参照 fullstack4TraeV7 Cockpit 模式 + CC Studio Session State Recovery。解决"素材跟设计脱节 + 断连后不知道做到哪 + 临时改方向丢上下文"。

**新会话激活协议**:

```
1. 检测 .project-state-card.md 是否存在
2. 存在 → 输出驾驶舱快照（§1 流水线进度 + 当前 Phase + 素材版本状态）
3. 不存在 → Phase 0 启动协议
4. 从会话状态恢复：用户无需手动说"我们之前做到哪了"
```

**运行时更新**:

```
新会话激活:  读 .project-state-card.md → 输出驾驶舱快照
Phase 切换:  更新状态卡对应行 → 标记状态
素材生成:    写入素材版本追踪表（素材文件名 + source_version + 状态）
设计变更:    追加变更日志 → 标记受影响素材为 ⚠️
构建失败:    写入门禁报告 + 回退路由
```

**方向调整（Pivot）协议**：游戏开发中 97% 的场景涉及变更。不做"冻结设计"——做"可追溯的变更日志"。

- 视觉微调 → 标记该角色素材为 ⚠️，用户决定是否重新生成
- 设计调整 → 追加变更日志，更新素材清单
- 引擎换型 → 更新状态卡引擎字段，Phase 3 从头开始
- 会话中断恢复 → 读状态卡 → 找到当前 Phase → 加载对应子技能 → 继续

> 详细协议见 `references/cockpit.md`，模板见 `templates/state-card.md`。

---

## §7 Hook 生命周期

> 参照 CC Studio 12 Hook 系统 + godogen stop_post_task_gate.py。每个关键动作有前后验证。

| 时机 | 动作 | 阻塞？ |
|------|------|--------|
| 新会话开始 | 读 .project-state-card.md → 驾驶舱快照 | 否（信息类） |
| Phase 切换前 | 当前阶段门禁 → 产出门禁报告 | **是**（REJECT 阻断） |
| 素材生成后 | 写入 asset-manifest.md + source_version | 否（记录类） |
| 写入素材文件后 | 检查 RGBA/尺寸/文件大小 | **是**（格式错误回退） |
| 构建前 | 素材 + 脚本完整性验证 | **是**（缺失文件阻断） |
| 构建后 | Proof bundle 生成 → 人工确认 | **是**（确认前不部署） |
| Phase 结束 | 更新 .project-state-card.md 进度行 | 否（记录类） |

---

## §8 上下文卫生

> 参照 godogen PLAN.md/STRUCTURE.md/MEMORY.md/ASSETS.md 四文件协议 + 逐阶段加载模式 + CC Studio File-backed state。

| 文件 | 内容 | 产出阶段 | 用途 |
|------|------|---------|------|
| `.project-state-card.md` | 驾驶舱（流水线进度 + 版本追踪 + 变更日志） | Phase 0→全流程 | 新会话自检 + 方向调整 |
| `story-design.md` | 角色宪法 + 剧情树 + 场景列表 | Phase 1 | 所有阶段读取 |
| `asset-manifest.md` | 素材清单 + 生成状态 + source_version | Phase 2 | Phase 3/4 读取 |
| `quality-report.md` | 门禁检查结果 + verdict + 自问结论 | Phase 4 | Phase 5 门禁 |
| `quirks-{engine}.md` | 引擎特定坑收集 | Phase 5 | 构建错误排查 |

> 参照 godogen 逐阶段加载：每个阶段开始时加载对应子技能文件，阶段完成后卸载。不在主上下文中同时持有多个阶段的详细指令。
> 
> **文件即状态**：关键状态不在对话记忆中，会话中断后通过读取文件恢复。

---

## §9 禁止项

| 禁止 | 替代 |
|------|------|
| 跳过 Phase 0 直接写 WebGAL 脚本 | 先确认引擎 |
| 引擎无关阶段引用引擎特定技能 | Phase 1/2/4 内不加载 webgal-* |
| 写死引擎名 | 始终通过 Phase 0 路由表决定 |
| 素材不合格跳过门禁 | 回退 Phase 2 重新生成 |
| 引擎特定技能引用其他引擎路径 | webgal-engine-build 不引用 renpy-* |
| 在 SKILL.md 中展开子技能详细逻辑 | 加载对应子技能 skill，本文件只做路由 |
| 设计变更后不更新素材版本追踪 | 追加变更日志 + 标记受影响素材 |

---

## §10 参考索引 → [`references/INDEX.md`](references/INDEX.md)

---

## §11 目录结构

```
game-production-kit/
├── SKILL.md                            # 编排器入口（本文件）
├── skills/
│   ├── game-story-design/SKILL.md      # 剧情策划（engine-agnostic）
│   ├── game-asset-pipeline/SKILL.md    # 素材管线（engine-agnostic）
│   ├── game-quality-gate/SKILL.md      # 质量门禁（engine-agnostic）
│   ├── game-prototype/SKILL.md         # 原型验证系统
│   ├── game-hotfix/SKILL.md            # 紧急修复流程
│   ├── voice-character-design/SKILL.md # 角色音色设计（engine-agnostic）
│   ├── voice-acting-skill/SKILL.md     # 配音管线（engine-agnostic）
│   ├── webgal-scripting/SKILL.md       # WebGAL 脚本（engine-specific）
│   ├── webgal-engine-build/SKILL.md    # WebGAL 构建部署
│   ├── godot-scripting/SKILL.md        # Godot 脚本（engine-specific）
│   │   └── references/                 # GDScript/C#/Quirks 详细参考
│   ├── godot-engine-build/SKILL.md     # Godot 构建验证
│   ├── unity-scripting/SKILL.md        # Unity 脚本（engine-specific）
│   ├── unity-engine-build/SKILL.md     # Unity 构建验证
│   ├── unreal-scripting/SKILL.md       # Unreal 脚本（engine-specific）
│   ├── unreal-engine-build/SKILL.md    # Unreal 构建打包
│   ├── bevy-scripting/SKILL.md         # Bevy ECS 脚本（engine-specific）
│   ├── bevy-engine-build/SKILL.md      # Bevy 构建 + offscreen capture
│   ├── babylon-scripting/SKILL.md      # Babylon.js 脚本（engine-specific）
│   └── babylon-engine-build/SKILL.md   # Babylon.js 构建 + Playwright capture
├── references/
│   ├── cockpit.md                      # Cockpit 驾驶舱设计文档
│   ├── engine-decision-guide.md        # 引擎选择决策指南
│   ├── phase0-startup-protocol.md      # 启动协议完整版
│   ├── gate-standards.md              # 门禁标准与 verdict 系统
│   ├── security-checklist.md           # 安全审查清单（34项）
│   ├── add-engine-guide.md            # 新增引擎步骤
│   ├── context-hygiene.md             # 上下文卫生规则
│   ├── asset-generation-patterns.md   # 资产生成模式参考
│   ├── godogen-ark-pipeline.md        # godogen-ark 全量资产管线吸收
│   ├── scene-builder-pattern.md       # Godot Scene Builder 完整模式
│   ├── decomposer-patterns.md         # 任务分解模式
│   ├── task-execution-patterns.md     # 任务执行模式
│   └── publish-pipeline.md            # 发布管线模式
├── templates/  # state-card.md + workflows/
├── scripts/
│   ├── check_assets.py                 # 素材验证
│   ├── gen_voice.py                    # TTS 语音生成
```
