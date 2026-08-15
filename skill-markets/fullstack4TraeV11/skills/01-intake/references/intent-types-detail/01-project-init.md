# 意图 1：project-init — intent-types.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../intent-types.md](../intent-types.md)
> 来源：原 intent-types.md 第 19-54 行（保留信息密度）

---

## 意图 1：project-init（项目 0→1 初始化）

**定义**: 从零开始一个新项目，包含目录结构 + 基础配置文件 + spec 骨架。

**触发词**:
- "初始化" / "新项目" / "项目 0→1"
- "create new project" / "scaffold project"

**典型流程**:
```
Stage -1 Intake → Stage 0 Plan（项目级 plan.md）
  → Stage 1 Spec（项目级 spec.md + 子 spec 骨架）
  → Stage 2 Contract（项目级 contract 骨架）
  → Stage 3 Implement（基础设施代码）
  → Stage 3.5 Real Verify（启动验证）
  → Stage 4 Review
  → Stage 4.5 Rot Scan
  → Stage 5 Accept
```

**状态卡**: project 级（位置 `{project}/docs/specs/.state-card.md`）

**子意图**（可选分类）:
- `cli-tool` — 命令行工具
- `web-app` — Web 应用（含前端 + 后端）
- `tauri-app` — Tauri 桌面应用
- `backend-only` — 纯后端 API 服务
- `library` — 库/包开发

**关键产出**:
- `AGENTS.md` — 项目入口
- `docs/constitution.md` — 项目宪法（可继承 V11 17 Articles,含 Article XVII Secret Redaction）
- `.trae/rules/*.md` — 项目级规则
- `.trae/fullstack4traev11.config.yaml` — stage_config 覆盖

---

## 关联引用

- 父文件：[../intent-types.md](../intent-types.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
