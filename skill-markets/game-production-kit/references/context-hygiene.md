# 上下文卫生规则

> 参照 godogen PLAN.md/STRUCTURE.md/MEMORY.md/ASSETS.md 文档协议 + fullstack4TraeV7 上下文隔离模式 + CC Studio File-backed state。

## 核心原则

1. **逐阶段加载**：每个阶段开始时加载对应子技能文件，阶段完成后卸载。不在主上下文中同时持有多个阶段的详细指令。
2. **状态落盘**：关键状态写入文件（story-design.md / asset-manifest.md / quality-report.md），不依赖对话记忆。
3. **断点恢复**：通过读取状态文件恢复进度，不需要重放对话历史。
4. **文件即状态**：参照 CC Studio File-backed state 策略。会话中断后通过状态文件恢复。

## Session State Recovery

> 参照 CC Studio session-start.sh + active.md 模式。

```
新会话启动 → 第一动作：读 .project-state-card.md
  │
  ├── 文件存在 → 输出驾驶舱快照:
  │     • 引擎: {已确认引擎}
  │     • 当前 Phase: {N}
  │     • 阶段状态: {各 Phase PASS/FAIL/⏳}
  │     • 上次操作: "Phase 2: 生成 elise_normal.png — CONCERNS (纯色背景问题)"
  │     • 素材版本: {过期数量}/{总数} 过时
  │     → 加载当前 Phase 子技能 → 恢复工作
  │
  └── 文件不存在 → Phase 0 启动协议
```

## 状态文件协议

> 参照 godogen PLAN.md / STRUCTURE.md / MEMORY.md / ASSETS.md 模式。

| 文件 | 生存周期 | 写入时机 | 读取时机 |
|------|---------|---------|---------|
| `.project-state-card.md` | 全流程 | Phase 0 完成时创建，每次阶段切换/素材生成/设计变更时更新 | 新会话自检时（第一动作） |
| `story-design.md` | 全流程 | Phase 1 完成时 | Phase 2/3 开始时 |
| `asset-manifest.md` | Phase 2-4 | Phase 2 每类素材生成后 | Phase 3/4 开始时 |
| `quality-report.md` | Phase 4 | Phase 4 每项检查后 | Phase 5 开始时 |
| `quirks-{engine}.md` | Phase 5→全流程 | 构建时发现新坑时追加 | 下次构建时 |

### quirks 反馈环

> 参照 godogen MEMORY.md → quirks.md 提升机制。

```
Phase 5 构建时:
  发现新坑 → 写入项目级 quirks-{engine}.md
    → 定期由 kit 维护者审查
    → 有价值 → 提升到 webgal-engine-build/SKILL.md「常见构建错误」节
```

## 子技能加载策略

> 参照 godogen 的逐阶段读取子文件模式。

```
Phase 0: 主上下文 → 引擎确认 → 写入 .project-state-card.md
Phase 1: 加载 game-story-design → 完成 → 产出 story-design.md → 卸载
Phase 2: 加载 game-asset-pipeline → 完成 → 产出 asset-manifest.md → 卸载
Phase 3: 按引擎加载脚本技能 → 完成 → 产出脚本文件 → 卸载
Phase 4: 加载 game-quality-gate → 完成 → 产出 quality-report.md → 卸载
Phase 5: 按引擎加载构建技能 → 完成 → 产出构建产物 + quirks-{engine}.md → 卸载
Phase 6: 按引擎加载部署技能 → 完成 → 交付
```

> 阶段 A 和阶段 B 的详细指令永远不会同时存在于主上下文。编排器 SKILL.md 只持有骨架流程和路由表。

## 显式卸载协议

> H6 修复：从"愿望"升级为"可验证的机制"。

### 卸载触发条件

阶段切换时，Agent 必须在加载下一阶段指令前执行卸载：

1. 确认当前阶段产物已落盘（文件存在 + 非空）
2. 更新 .project-state-card.md 状态为 ✅
3. 在回复中声明：`[unload phase{N}] {skill_name} 已卸载`
4. 加载下一阶段指令

### 卸载验证

Phase 4 门禁加载时，检查：
- .project-state-card.md 中上一阶段状态是否为 ✅
- 若不是 → 上一阶段未完成 → CONCERNS

### 多阶段累计检测

Phase N 加载时，自检：
- 当前上下文中是否有 Phase N-2 或更早的详细指令？
- 若有 → 输出告警 `[context-bloat] Phase {M} 指令未卸载`，先卸载再继续

### 引擎上下文子代理隔离

每个引擎阶段的详细文档（references/ 下的长文件）通过子代理隔离：
- Phase 3 scripting → 通过 subagent 加载引擎脚本技能，不在主上下文中展开
- 子代理返回结构化结果（scene-manifest.json + 变更摘要）
- 主上下文只持有编排器 SKILL.md + 当前阶段的产出摘要

## 禁止行为

| 禁止 | 原因 | 正确做法 |
|------|------|---------|
| Phase 1 中加载 webgal-scripting | engine-agnostic 阶段不应看引擎特定指令 | Phase 3 按需加载 |
| 一次加载所有子技能 | 上下文撑爆，指令互相干扰 | 逐阶段加载 |
| 不写状态文件直接跳到下一阶段 | 断点无法恢复 | 每阶段结束时落盘 |
| SKILL.md 中展开子技能详细逻辑 | 编排器变胖，维护困难 | 只放路由表 |
| 用对话记忆跨会话保持状态 | 上下文压缩后丢失 | 写入状态文件 |

---

## 变更广播协议

> 游戏开发中 97% 的场景涉及变更。不冻结设计，只做可追溯的版本追踪。

### 版本标记规则

每个产出物标注自己从哪个设计版本生成的：

```yaml
# asset-manifest.md 中每个素材条目
character_elise_01.png:
  source: story-design.md
  source_version: "v3"       # 生成时 story-design.md 的版本号
  generated_at: "2024-07-08"
```

### 变更广播流程

```
1. story-design.md 发生任何修改 → 版本号递增 (v2 → v3)
2. 在 .project-state-card.md「设计变更日志」中追加一行:
   | v3 | 07-08 15:30 | 发色红→深棕 | 立绘: elise_*.png |
3. 在「素材版本追踪」中标记受影响素材:
   | character_elise_01.png | 立绘 | v2 | v3 | ⚠️ 可能过时 |
4. Phase 4 门禁检测到 ⚠️ → CONCERNS → 询问用户是否重新生成
5. 重新生成后 → 更新 source_version 为 v3 → 状态 ✅
```

### 版本号策略

```
v1, v2, v3 ... 递增
每次修改 story-design.md 时递增
微小修改（错别字、格式）不递增
内容修改（角色属性、场景变更、剧情调整）必须递增
```

### 方向调整（Pivot）与版本追踪的关系

```
视觉微调（发色红→棕）:
  → story-design.md v2 → v3
  → 素材追踪: 标记该角色立绘为 ⚠️
  → 门禁时 CONCERNS → 用户决定是否重新生成

设计调整（新增结局分支）:
  → story-design.md v3 → v4
  → 素材追踪: 追加新场景素材（初始 ⚠️）
  → 门禁时检查新素材是否存在

引擎换型（WebGAL → Ren'Py）:
  → .project-state-card.md 引擎字段更新
  → Phase 3 脚本从头开始
  → Phase 1/2 产出物不变（引擎无关）
```
