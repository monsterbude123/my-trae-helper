# 场景 5: 断连重入：Cockpit 恢复

> 模拟目标: 验证 cockpit 新会话自检协议 + reentry-checkpoint 重入流程在 Phase 中途断连场景下的自愈能力。

---

## 用户视角

```
[Day 1 — 下午]
用户: "继续做《咖啡馆的猫》的脚本编写"

Agent: 🎮 Phase 3 Scripting — cafe_cat | webgal-scripting
       场景 1-3 完成，正在写 scene_04_clue.txt ...
       .project-cockpit.md: phase=3, status=⏳, 最后产出=2026-07-09 22:15

[用户关闭 IDE — 中途断连]

[Day 2 — 新会话]
用户: "Hi，继续昨天的游戏制作"

Agent: 🛩️ Cockpit 启动 — 检测 .project-cockpit.md → 存在

       驾驶舱快照:
       | Phase 0 | Engine | ✅ | engine-confirmed.md  |
       | Phase 1 | Story  | ✅ | story-design.md v3    |
       | Phase 2 | Asset  | ✅ | asset-manifest.md     |
       | Phase 3 | Script | ⏳ | scenes 01-04 done     |
       | Phase 4 | Gate   | — | —                     |
       最后产出: 13.5h 前 | 场景覆盖: 4/10

       文件系统交叉验证:
       story-design.md ✅ | asset-manifest.md ✅
       scene_01-04.txt ✅ | scene_05.txt ❌ | scene-manifest.json ⏳(未到)
       → 状态一致，无失真

       假性完成检测: 13.5h > 30min ⚠️
       → 判定: 正常中断（cockpit ⏳ + 断点明确），非假性完成

Agent: 🎮 已恢复 — cafe_cat Phase 3 Scripting。从 scene_05 开始编写...
```

---

## 系统内部流程

```
新会话 → game-production-kit 激活
  │
  ├── Step 0: 检测 .project-cockpit.md
  │     ├── 存在 → Step 1
  │     └── 不存在 → 询问用户 "新游戏/恢复已有" → Phase 0
  │
  ├── Step 1: 读取 cockpit + 渲染快照 → 定位当前 Phase 3 ⏳
  │
  ├── Step 2: 文件系统交叉验证
  │     ├── Phase 0-2 checkpoints ✅ (文件存在)
  │     ├── Phase 3 ⏳ → 不检查 scene-manifest.json（未到产出时机）
  │     │            → 遍历 scene/ 目录: scene_01~04 → max=4 → next=5
  │     └── cockpit 预期 vs 实际 → 一致
  │
  ├── Step 3: 假性完成检测
  │     ├── > 30min → ⚠️ 超时
  │     ├── cockpit 显示 ⏳（非 ✅） + 断点明确 → 正常中断
  │     └── 区分: ✅+文件缺失=假性完成 | ⏳+断点明确=正常中断
  │
  └── Step 4: 恢复执行 → 加载 webgal-scripting → 从 scene_05 继续
```

---

## 关键决策点

### 1. "scene_05 是下一个"的判断逻辑
```
遍历 scene/ 下已有 .txt → max(N)+1:
  scene_01, scene_02, scene_03, scene_04 → next=5

备选（编号不连续时）:
  - 读 story-design.md 场景列表 → 逐项比对哪些 .txt 存在
  - 读 scene-manifest.json → 但 Phase 3 未完成时可能不存在
```

### 2. 假性完成 vs 正常中断的区分
- 假性完成: cockpit ✅ 但文件缺失 → 🛑 回溯修复
- 正常中断: cockpit ⏳ + 文件与进度一致 → 继续执行
- 耗时任务中: 需 `running` 标记（见 ISSUE-05-03）

### 3. cockpit 不存在时的恢复
```
1. 询问用户: "新游戏/恢复已有？"
2. 已有项目 → 反向工程文件系统:
   story-design.md → P1✅, asset-manifest.md → P2✅, *.txt → P3 进度
3. 重建 .project-cockpit.md（状态=从文件系统推导）
```

---

## 发现的问题

### [ISSUE-05-01] cockpit 状态卡命名不一致
- **位置**: SKILL.md §6/§8 用 `.project-state-card.md`，cockpit.md + reentry-checkpoint.md + 模板用 `.project-cockpit.md`
- **建议**: 统一为 `.project-cockpit.md`，更新 SKILL.md 引用。

### [ISSUE-05-02] Phase 3 中途断连缺少部分进度 checkpoint
- **位置**: reentry-checkpoint.md §Checkpoint 定义 — 只在门禁通过后记录
- **描述**: Phase 3 写到一半断连，重入只能靠 .txt 文件计数，大场景数（100+）易误判
- **建议**: 增加 `.scene-progress.json` 轻量进度文件

### [ISSUE-05-03] 假性完成判定缺少运行状态标记
- **位置**: cockpit.md §假性完成检测
- **描述**: 仅依赖时间+文件系统，Agent 在跑耗时任务（TTS 50 条）时 cockpit 可能 5min 未更新，重连误判假性完成
- **建议**: 增加 `running: true/false` 字段
