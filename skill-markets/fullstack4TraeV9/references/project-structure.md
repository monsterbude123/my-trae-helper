# 项目目录结构

> V9.2 扁平化结构。Spec 是唯一真相源，prototypes/ 按 feature 存放，archive/ 只读。

---

## 完整目录树

```
project/
├── docs/
│   ├── specs/                          # ★ Spec 真相源
│   │   ├── .state-card.md              #   驾驶舱状态卡（单源）
│   │   ├── INDEX.md                    #   Spec 索引（agent 发现入口）
│   │   ├── {feature}/                  #   每个功能一个目录
│   │   │   ├── spec.md                 #     Spec（Delta 或完整）
│   │   │   ├── define.md               #     Define 定义文档
│   │   │   ├── design.md               #     架构设计（可选，复杂功能）
│   │   │   ├── tasks.md                #     任务清单（checkbox）
│   │   │   ├── .state-card.md          #     Feature 级状态卡
│   │   │   ├── contracts/              #     Feature 级契约
│   │   │   │   ├── api-contracts.md
│   │   │   │   ├── domain-models.md
│   │   │   │   ├── events.md
│   │   │   │   └── validation-rules.md
│   │   │   ├── prototypes/             #     UI 原型文档（涉及 UI 时）
│   │   │   │   ├── design-prompt.md    #       Trae Work 视觉原型提示词/规格
│   │   │   │   └── ui-ux-logic.md      #       交互逻辑 + 状态 + 组件行为
│   │   │   └── _invalidated/           #     回流隔离旧产物
│   │   └── archive/                    #   只读归档
│   │       └── done/
│   │           └── {archived-feature}/ #   已完成的 feature
│   ├── modules/                        # 模块文档（DOC SYNC 写入）
│   │   └── {module-name}.md
│   ├── reports/                        # 审查/验收报告历史
│   ├── api-endpoints/                   # ★ 项目级 API 注册表（归档时积累，一个 feature 一个文件）
│   │   └── {feature}.md
│   ├── domain-models/                   # ★ 项目级领域模型注册表（归档时积累，一个 feature 一个文件）
│   │   └── {feature}.md
│   ├── events/                          # ★ 项目级事件目录（归档时积累，一个 feature 一个文件）
│   │   └── {feature}.md
│   ├── ARCHITECTURE.md                 # 架构总览
│   ├── DECISIONS.md                    # 技术决策记录
│   ├── INDEX.md                        # 项目文档索引
│   ├── CONTRIBUTING.md                 # 贡献指南
│   └── README.md                       # 项目说明
├── contracts/                          # 项目级全局契约
│   ├── schema.sql
│   └── manifest-schema.json
├── .trae/
│   ├── hooks.json                      # V9.2 Hook 配置
│   ├── hooks/                          # Hook 脚本（.py）
│   └── logs/                           # Hook 执行日志
├── src/                                # 源代码
└── tests/                              # 测试
```

---

## Prototypes 位置说明

```
V8:  docs/prototypes/       ← 项目级，V9.2 不使用（迁移时进 bak_v8doc/）
V9:  docs/specs/{feature}/prototypes/
     ├── design-prompt.md   ← Trae Work 视觉原型输入 / 视觉规格
     └── ui-ux-logic.md     ← 开发者交互逻辑
```

纯后端 feature 不产生 `prototypes/` 目录。

---

## INDEX.md 规范（Agent 知识发现入口）

> `docs/INDEX.md` 是 agent 发现项目知识结构的第一入口。每次 Intake 和 Define 阶段必须读取。

### 格式

```markdown
# {Project Name} — 项目索引

## Active Specs
| Feature | Directory | Phase | Capabilities |
|---------|-----------|-------|-------------|
| User Auth | user-auth/ | Implement | user-auth, jwt-issuance |
| 2FA | user-auth-2fa/ | Spec | two-factor-auth |

## Archived Specs
| Feature | Directory | Archived |
|---------|-----------|----------|
| Base Setup | 00-base-prepare/ | 2026-01-15 |

## Module Map
| Module | File | Owner Spec |
|--------|------|------------|
| Authentication | modules/auth.md | user-auth |

## Architecture
- [ARCHITECTURE.md](ARCHITECTURE.md) — 系统架构总览
- [DECISIONS.md](DECISIONS.md) — 技术决策记录
```

### 更新规则

| 触发 | 动作 |
|------|------|
| 新 Spec 创建 | reviewer DOC SYNC 阶段追加 Active Specs 行 |
| Spec 归档 | reviewer 归档阶段移动行到 Archived Specs |
| 模块变更 | reviewer DOC SYNC 更新 Module Map |

---

## 知识发现协议

Agent 启动或开始新任务时，按以下顺序读取：

```
1. docs/specs/.state-card.md      → 当前状态（活跃 change / 阻塞 / 健康度）
2. docs/INDEX.md                  → Spec 全景 + 模块映射（知道"有什么"）
3. docs/ARCHITECTURE.md           → 架构约束（知道"在哪改"）
4. GitNexus impact()              → 影响面评估（知道"影响谁"）
5. docs/specs/{feature}/spec.md   → 具体 Spec（知道"要做什么"）
6. docs/specs/{feature}/define.md → 任务定义（实现阶段）
```

---

## 约束

- Spec 必须在 `docs/specs/{feature}/`，不能在其他位置
- `archive/done/` 只读，禁止修改
- 模块文档必须在 `docs/modules/`，由 DOC SYNC 写入
- `docs/specs/.state-card.md` ≤ 40 行
