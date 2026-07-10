# migration-guide.md — V5 → V7 迁移指南

> 适用场景：项目已按 fullstack V5 组织，需要迁移到 V7 工作流。

---

## 核心原则

```
存量不毁，增量走新规。
已完成的 change 不动，新 change 走 V7 结构。
```

---

## 目录映射

| V5 路径 | V7 处理 | 说明 |
|---------|---------|------|
| `docs/modules/{module}.md` | **不动** | 模块文档依然是一事实来源 |
| `docs/spec/changes/{change}/` | → `docs/specs/changes/{change}/` | 目录名统一加 s（V7 路径规范） |
| `docs/archive/{change}/` | → `docs/archive/done/{change}/` | 已完成变更的归档 |
| `docs/specs/`（旧历史） | → `docs/archive/out/` | 淘汰的旧 Spec |
| — | **新建** `docs/specs/.state-card.md` | Cockpit 驾驶舱 |
| — | **新建** `docs/prototypes/` | 项目级原型组件速查 |
| — | **新建** `docs/test-plan/` | 项目级测试方案 |
| — | **新建** `docs/archive/out/` | 淘汰归档目录 |

---

## 迁移步骤

### 第 1 步：目录重命名（5 分钟）

```powershell
# 如果有旧的 docs/spec/ 目录
Rename-Item "docs\spec" "docs\specs"

# 拆分 archive
New-Item -ItemType Directory -Path "docs\archive\done","docs\archive\out" -Force
# 把已有的 archive/* 移动到 archive/done/
Move-Item "docs\archive\*" "docs\archive\done\" -Exclude "done","out"
```

### 第 2 步：创建 Cockpit（1 分钟）

```powershell
# 复制模板
Copy-Item "~\.trae-cn\builtin_skills\fullstack4TraeV7\templates\cockpit-state-card.md" "docs\specs\.state-card.md"
```

编辑 `docs/specs/.state-card.md`：
- 列出所有活跃 change（从 `docs/specs/changes/` 读取）
- 填写阶段和最后活动时间

### 第 3 步：更新 config.yaml（2 分钟）

在 `docs/specs/config.yaml` 中追加：

```yaml
paths:
  changes: docs/specs/changes/{NN}-{change-name}/
  archive_out: docs/archive/out/{change-name}/
  archive_done: docs/archive/done/{change-name}/
  prototypes: docs/prototypes/
  test_plan: docs/test-plan/

roundtable:
  enabled: false        # 新项目建议开启，存量可先关闭
  max_rounds: 3
  auto_converge: true
```

### 第 4 步：更新 per-change 状态卡（每个活跃 change 1 分钟）

在每个活跃 change 的 `.state-card.md` 中：

1. 添加 `最后产出` 字段（`{YYYY-MM-DD HH:MM}`）
2. 工件进度表追加 `prototypes/` 和 `meeting-notes/` 行

### 第 5 步：安装 V7 技能（1 分钟）

```powershell
Copy-Item -Recurse 
"$env:USERPROFILE\.trae-cn\builtin_skills\fullstack4TraeV7"
Remove-Item -Recurse -Force "$env:USERPROFILE\.trae-cn\builtin_skills\fullstack4TraeV4"
```

---

## 新项目初始化（V7）

如果你是新项目：

```powershell
# 1. 创建目录结构
New-Item -ItemType Directory -Path "docs\modules","docs\CODEMAPS","docs\prototypes","docs\contracts","docs\test-plan","docs\archive\out","docs\archive\done","docs\specs\changes" -Force

# 2. 创建项目上下文
Copy-Item "$env:USERPROFILE\.trae-cn\builtin_skills\fullstack4TraeV7\templates\config.yaml" "docs\specs\config.yaml"
# 编辑 config.yaml：填写技术栈、域名、圆桌开关

# 3. 初始化 Cockpit
Copy-Item "$env:USERPROFILE\.trae-cn\builtin_skills\fullstack4TraeV7\templates\cockpit-state-card.md" "docs\specs\.state-card.md"
# 编辑：留空的活跃变更表即可

# 4. 写 ARCHITECTURE.md 模板
# 告诉 Agent: "初始化项目架构文档"
```

---

## V5 Agent 使用变化

| V5 习惯 | V7 变化 |
|--------|--------|
| 直接进 intake | **先加载 Cockpit**，Agent 激活时先输出全局快照 |
| intake 做四步 | intake 现在做**六步**（+Cockpit 读取 + 30% 去重） |
| spec 后直接 contract | 如果 roundtable.enabled=true，先走**圆桌会议** |
| 不看最后产出时间 | 新会话必须**自检**状态卡 vs 文件系统 |
| 有磕绊口头抱怨 | **写 report-{0X}.md**，交付时汇总 |
| 归档不分类型 | out/done 分类归档 |
