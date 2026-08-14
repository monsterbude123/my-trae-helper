# Changelog - V11

> V11 独立 skill 版本 changelog。V10 -> V11 蒸馏 + 架构升级。

---

## [V11.3.0] - 2026-08-13

### ✨ 新增（V11.3 opt-in 三件套）

- **stage-gate-pre-stage.sh**: husky 式硬阻断门禁（exit 0/1），stage 切换前必跑 stage-gate.py + state-card-validator.py
- **references/stage-physical-isolation.md**: 物理隔离规范（fact/ + stage/ 双目录布局，借鉴 Docker 镜像层）
- **docs/给验收角色的一封信.md**: 验收瘦身操作手册（像产品经理验收，不读代码细节）

### 🗑️ 精简过渡产物（删除 53 个 V10 过渡文件，体积降低约 50%）

- 删除 `references/V10-distillation-source-map.md`（V10 蒸馏溯源，过渡产物）
- 删除 13 份 `skills/*/anti-patterns/V10-battle-tested.md`（V10 过渡引用）
- 删除 `research/` 整个目录（39 文件，V10->V11 升级期工作笔记）
- 精简 CHANGELOG V11.0 段（移除 scripts 实装清单 + stage 文件清单）

### 🎯 V11.3 vs V11.0 差异

- 新增 opt-in 门禁硬化（stage-gate-pre-stage.sh），不破坏现有 pre-stage.sh
- 新增物理隔离 + 验收瘦身设计文档（opt-in，不改现有 stage 流程）
- 删除 53 个 V10 过渡产物，体积 -50%
- 不改任何 13 stage SKILL.md / 24 scripts / frontmatter version

---

## [V11.0.0] - 2026-08-11

### ✨新增（V11 架构升级）

- **架构升级**: 从 V10 agents/ + references/ 分散架构升级为 **高内聚专家 skill** 架构
- **13 stage skill**: 每个 stage 自包含 SKILL/README/workflows/references/templates/anti-patterns
- **公共 references/**: 9 个文档（constitution / common-iron-rules / common-anti-patterns / stage-card-protocol / stage-interaction-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns）
- **公共 scripts/**: 24 个公共 Python 脚本（全部实装，非占位）
- **公共 templates/**: 8 个模板（含 spec / plan / test-plan / domain-models / api-contracts / events / validation-rules / bug）

### 📦继承（V10.10-10.12 蒸馏）

- **17 Articles 宪法**（Article I-XVII，含 V10.10 新增 XV 障碍诚实 + XVI 质疑性校验 + V11.1 新增 XVII Secret Redaction）
- **13 stage 流水线**（-1 Intake -> 0 Plan -> 0.5 Test Plan -> 1 Spec -> 1.5 Prototype -> 2 Contract -> 3 Implement -> 3.5 Real Verify -> 4 Review -> 4.5 Rot Scan -> 5 Accept + 6 Bug Fix + 7 Project Health）
- **10 项腐化扫描**（V10.10 NEW）
- **4 维评分**（代码 25% / API 30% / UIUX 25% / 边际 20%）
- **3 类通过依据**（后端编译 / UI 渲染 / 用户视角）
- **5 类项目启动验证**（Web / Tauri / CLI / Library / Backend）
- **Article XV 5 字段阻塞报告**
- **Article XVI 4 维度质疑性校验**

### 🎯 V11 改进（vs V10）

- **SUITE 减肥**: 每个 skill 文件遵循 vibe-coding-standards v2.5 弹性 100~350 行（V10.12 减肥 → 2026-08-14 解除硬上限）
- **3 层依赖配置**: 全局（user-level）/ V11 / 项目级
- **独立部署**: V11 不依赖 V10 目录
- **runtime 引用归零**: 全部 66 处 V10 运行时路径已替换为 V11 内部 reference

### 🎯 部署清单

```bash
# V11 是独立版本，部署到 ~/.trae-cn/skills/fullstack4TraeV11/
cp -r skill-markets/fullstack4TraeV11/* ~/.trae-cn/skills/fullstack4TraeV11/
```

### 关联引用

- [SKILL.md](SKILL.md) - V11 总编排器
- [README.md](README.md) - V11 README
