# V7 项目目录结构

```
项目根/
├── docs/
│   ├── modules/{module}.md      # 模块文档 — 唯一事实来源（DOC FIRST 的锚）
│   ├── CODEMAPS/                # 架构地图
│   ├── ARCHITECTURE.md          # 架构总览
│   ├── prototypes/              # V7 NEW 项目级原型 + 组件速查（Cockpit）
│   ├── contracts/               # V7 NEW 项目级公共协议
│   ├── test-plan/               # V7 NEW 项目级测试方案（架构期定调，迭代补全）
│   ├── archive/
│   │   ├── out/                 # V7 NEW 过时 Spec 归档（被淘汰/覆盖的变更）
│   │   └── done/                # V7 NEW 已完成并合并到模块文档的变更
│   └── specs/                   # 变更工作区
│       ├── config.yaml          # 项目上下文 + 圆桌会议开关
│       ├── .state-card.md       # V7 NEW 项目级 Cockpit 状态卡
│       └── changes/             # 活跃变更（按构建次序编号）
│           └── {NN}-{change-name}/
│               ├── .state-card.md   # per-change 状态卡（隐藏，SessionStart 注入）
│               ├── proposal.md
│               ├── specs/           # 每个能力一个子目录
│               │   └── {capability}/
│               │       └── spec.md  # BDD + E2E 场景 + 测试骨架
│               ├── prototypes/      # per-change 原型（施工图纸）
│               │   ├── README.md    # 原型索引
│               │   └── {module}.md  # 每个页面/模块一个原型文件
│               ├── contracts/       # per-change 协议先行
│               │   ├── domain-models.md
│               │   ├── api-contracts.md
│               │   ├── event-contracts.md
│               │   └── validation-rules.md
│               ├── meeting-notes/   # V7 NEW 圆桌会议纪要（可选，config 控制）
│               │   └── round-{N}.md
│               ├── design.md
│               ├── tasks.md
│               ├── check-list.md    # 验收清单
│               ├── report-{0X}.md   # V7 NEW 技能生长报告
│               └── acceptance-scorecard-{YYYYMMDD}.md  # 量化打分卡归档
└── src/                         # 源代码
```

## Cockpit 驾驶舱

> 解决"Agent 假性完成 + 用户看不出进度 + spec 爆炸性增长"三大痛点。

### 双层状态卡架构

```
docs/specs/.state-card.md          # 项目级 Cockpit：全局视图
docs/specs/changes/{change}/.state-card.md  # per-change：单变更视图
```

| 层级 | 内容 | 更新者 | 读取者 |
|------|------|--------|--------|
| **项目级 Cockpit** | 所有活跃 change 列表 + 各自阶段 + 阻塞项 + 最后活动时间 | 主 Agent（阶段切换时） | 所有 Agent 激活时 |
| **per-change** | 单 change 工件进度 + 健康度 + 下一步 | 该 change 的当前 Agent | 该 change 的下一个 Agent |

分层原则：两层无继承关系，各管各的粒度。新会话自检铁律：

```
Agent 在新会话激活时：
1. 先输出项目级 Cockpit（如有）
2. 对比 per-change state-card 声称的状态 vs 实际文件系统
3. state-card 与实际不符 → 标记为 ⚠️ 状态失真，回溯修复
4. state-card 更新时间 > 30 分钟且无新产出 → 🛑 疑似假性完成，询问用户
```

### 驾驶舱渲染

驾驶舱输出由脚本渲染，不由 LLM 生成：

```powershell
python render-cockpit.py [-Change <change-name>]
```

详见 [references/cockpit.md](cockpit.md) 和 [templates/cockpit-state-card.md](../templates/cockpit-state-card.md)。
