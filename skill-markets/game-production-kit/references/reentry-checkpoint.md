# 重入与 Checkpoint 机制

> 来源：fullstack4TraeV9 cockpit 新会话自检协议
> 解决游戏制作流水线的跨会话恢复（断连、IDE 重启、上下文丢失）

---

## Checkpoint 定义

每个 Phase 门禁通过后 = 一个 checkpoint。checkpoint 数据存储在 `.project-cockpit.md` 中。

```
Phase 0 → checkpoint 0: engine-confirmed.md 存在
Phase 1 → checkpoint 1: story-design.md + game-design-doc.md 存在
Phase 2 → checkpoint 2: asset-manifest.md + 素材文件齐全
Phase 3 → checkpoint 3: scene-manifest.json + .checkpoint-phase3.json（逐场景进度文件）
Phase 4 → checkpoint 4: quality-report.md 全部 PASS
Phase 5 → checkpoint 5: build.log 成功
Phase 6 → checkpoint 6: deploy.log 成功
Phase 7 → checkpoint 7: ops-checklist.md 全 PASS
```

---

## 子 Checkpoint — Phase 3（防止大场景数断连）

Phase 3 脚本编写过程中，Agent 每完成一个场景即写入临时进度文件：

.checkpoint-phase3.json:
{
  "done": ["scene_01", "scene_02", "scene_03"],
  "current": "scene_04",
  "pending": ["scene_05", "scene_06", "scene_07"],
  "last_update": "2026-07-09T22:15:00"
}

重入时读取此文件替代 .txt 计数。场景编号精确，避免 100+ 场景的误判。

---

## 回退规则

| 当前 Phase | 失败原因 | 回退到 | 保留策略 |
|-----------|---------|--------|---------|
| Phase 3 | 场景脚本不可解析 | Phase 2（重做素材管线） | 已有素材 .bak.old |
| Phase 4 | 质量门禁 FAIL | Phase 3（修复脚本） | 失败 report 保留 |
| Phase 5 | 引擎构建失败 | Phase 3（修复脚本）或 Phase 2（缺失素材） | 按根因选择 |
| Phase 6 | 部署失败 | Phase 5（修复构建） | build.log 保留 |

回退时：保留失败前的 checkpoint 文件，在新文件尾部加 `.bak.old`，重新生成。

---

## 新会话重入协议

```
Agent 在新会话激活时：

Step 0: 读 {game_key}/.project-cockpit.md
  → 不存在 → 询问用户 "新游戏还是恢复已有项目？"
  → 新游戏 → Phase 0 从头开始
  → 已有项目 → 用户提供 game_key → 继续 Step 1

Step 1: cockpit 存在
  → 输出 cockpit 快照（render-cockpit.ps1 渲染）
  → 对照文件系统验证每个 checkpoint 文件存在
  → 确认当前 phase 和下一步

Step 2: 假性完成检测
  → 最后产出 > 30 分钟 + 无新文件 → 🛑 询问用户
  → 否则 → 继续从当前 phase 开始

Step 3: 恢复上下文
  → 加载当前 phase 对应的 skill
  → 输出: "🎮 已恢复 — {game_key} Phase {N} {phase_name}"
```

---

## 重入最优实践

- **Phase 1 (story-design) 重入时**：先读 story-design.md 当前内容，再加载 game-story-design
- **Phase 2 (asset) 重入时**：先读 asset-manifest.md → 检查已有素材 vs 缺失素材
- **Phase 3 (scripting) 重入时**：先读 scene-manifest.json → 检查已实现 vs 未实现场景
- **每个 Phase 完成时**：立即更新 `.project-cockpit.md` 的 `最后产出时间` 字段

---

## 与 cockpit.md 的分工

| cockpit.md | reentry-checkpoint.md |
|-----------|----------------------|
| 状态卡架构、版本追踪、方向调整 | 技术回退机制、重入流程 |
| "状态是什么" | "断连后怎么恢复" |
| ".project-cockpit.md 的内容" | "checkpoint 的判定与回退" |

两个文档互补：cockpit 提供状态源，reentry-checkpoint 提供恢复路径。
