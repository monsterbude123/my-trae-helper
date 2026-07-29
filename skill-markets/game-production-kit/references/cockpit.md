# Cockpit 驾驶舱

> 来源：fullstack4TraeV9 cockpit 模式
> 解决游戏制作流水线中"Agent 假性完成 + 进度不可见 + 重入困难"三大痛点

## 设计动机

- **假性完成**：Agent 中途停止，state-card 显示 ✅ 但实际文件不存在。用户看不出问题。
- **进度不可见**：8 阶段流水线，用户不知道卡在哪、产出是什么。
- **重入困难**：用户断连后重新连接，Agent 不知道"上次做到 Phase 几"。

## 双层状态卡

### 项目级 cockpit（每个游戏项目一个）

文件：{game_key}/.project-cockpit.md

| 字段 | 含义 | 更新时机 |
|------|------|---------|
| 当前 phase | Phase 0-7 | 每次阶段切换 |
| phase 状态 | ✅/⏳/🔄/🚫 | 门禁通过后更新 |
| 最后产出 | YYYY-MM-DD HH:MM | 每次文件落盘 |
| 激活 skill | 当前加载的技能名 | 每次切换 |
| 下一步 | 一个句子的动作描述 | 阶段切换时 |
| 长耗时任务 | TTS批处理/图片批生成 等 | 耗时任务开始前 |
| 阻塞 | 阻塞原因/NULL | 门禁 FAIL 时 |

### 健康度指标

| 指标 | 阈值 | 信号 |
|------|------|------|
| 素材漂移 | story-design 版本 > asset-manifest source_version | ⚠️ |
| 场景覆盖 | 已实现分支 / story-design 总分支 | < 100% → ⚠️ |
| 构建状态 | 最后一次 build 是否成功 | FAIL → 🛑 |

## 新会话自检协议

```
Agent 在新会话激活时：
1. 读 .project-cockpit.md → 输出当前状态快照
2. 对照文件系统验证每个 phase 产物的实际存在性
3. cockpit 声称 ✅ 但文件不存在 → ⚠️ 状态失真，回溯
4. 最后产出 > 30 分钟且无新文件 → 🛑 疑似假性完成
   → 检查 .project-cockpit.md 中是否记录了 "长耗时任务" 标记（如 TTS 50条/图片批处理）
   → 若有长耗时标记 → 不触发假性完成警告，仅延长等待时间到 120 分钟
5. cockpit 不存在 → Phase 0 从头开始
```

## 状态卡生命周期

```
Phase 0 创建 → 每个 Phase 切换更新 → Phase 7 完成归档
```

## 脚本渲染

驾驶舱快照由 render-cockpit.ps1 渲染，不由 LLM 生成。保证格式一致、0 token 浪费。

渲染内容：
- 当前 phase / 状态 / 最后产出时间
- phase 门禁进度条 (0/8 → 7/8)
- 健康度（素材漂移/场景覆盖/构建状态）
- 活跃文件清单（story-design.md / asset-manifest.md / scene-manifest.json）
- 下一步 + 阻塞

## 引擎切换协议

触发: Phase 0.5 后用户要求换引擎

Phase 判定:
- 当前 ≤ Phase 1 → 直接切换，保留 story-design.md，重做 Phase 2-3
- 当前 = Phase 2 → 已有素材保留为备份，重新走 Phase 2
- 当前 ≥ Phase 3 → 🛑 先完成当前 Phase，再评估切换代价

资产处理:
- 通用格式素材(PNG/OGG/MP3) → 直接复用
- 引擎特定格式(.tscn/.unity/.uasset) → 废弃
- asset-manifest.md → 追加 engine 字段后重新生成

状态更新:
- .project-cockpit.md: engine 字段更新 + phase 回退标记
- 写入 report-{0X}.md: [L2] 引擎切换
