# {{PROJECT_NAME}}

> V11 全栈文档驱动开发项目

> **V11.7.0+ 项目级规则加载(必读)**:
> - **AC 核销门禁(Stage 4 Review)** → `scripts/ac-gate.py`
> - **贾维斯门禁守护** → `skills/00-boot/SKILL.md` + `agents/jarvis.md`
> - **Gate 修改必经 [JARVIS-DELEGATION] 委派** + `gate-integrity-guard.py --verify` PASS
> - **layer 分层字段**:本项目 gate 应在 `gates/gate-config.json` levels[*].layer 标注 module/app/system

---

## §0 项目定位

本项目使用 `fullstack4TraeV11` 技能包进行全栈文档驱动开发。

---

## §1 铁律（强约束）

### §1.1 会话启动加载协议（强制）

```
1. Skill(name="project-rule-skill")  → 输出 needed_rules
2. 按场景关键词自动加载相关 skill：
   ├─ 测试/验收 → acceptance-discipline + test-experience
   ├─ 安全扫描 → trae-security-review
   └─ 重构/升级 → fullstack-skill-architect
3. 只 Read needed_rules + 加载的 skill 列出的文件
```

### §1.2 V11 Stage 铁律

1. **必须从 Stage 1 Spec 开始**：任何代码编写前必须有完整 Spec
2. **状态卡必须存在**：`docs/specs/.state-card.md` 必须存在且同步
3. **Gate 必须通过**：L1 → Stage 1 / L2 → Stage 3.5
4. **禁止跨 Stage 跳跃**：必须按 1→2→3→3.5→4→5 顺序推进

---

## §2 目录结构

```
{{PROJECT_NAME}}/
├── docs/
│   └── specs/
│       ├── .state-card.md    (状态卡)
│       ├── overview.md        (项目概述)
│       ├── architecture.md    (架构设计)
│       └── api.md             (API 设计)
├── src/                       (源码)
├── tests/                     (测试)
├── .husky/
│   ├── pre-commit             (L1 -> Stage 1)
│   └── pre-push               (L2 -> Stage 3.5)
└── AGENTS.md                  (本文件)
```

---

## §3 Gate 映射

| Gate | 触发 | Stage | 验证内容 |
|------|------|-------|----------|
| L1 | pre-commit | 1-spec | Spec 完整性 + lint + typecheck |
| L2 | pre-push | 3.5-verify | Spec-Impl 一致性 + 测试 + 覆盖率 |
| L3 | merge | 4-review | 全量验证 + CHANGELOG |
| L4 | release | 5-release | 安全审计 + 发布清单 |

---

## §4 技术栈

- **语言**：JavaScript/TypeScript
- **运行时**：Node.js
- **包管理**：npm
- **测试框架**：Jest / Vitest
- **Lint**：ESLint + TypeScript
- **构建**：tsc / esbuild / webpack

---

## §5 开发流程

### 5.1 初始化

```bash
npm install
npm run setup
```

### 5.2 开发

```bash
npm run dev
```

### 5.3 测试

```bash
npm run lint
npm run typecheck
npm run test:unit
npm run test:integration
npm run test:coverage
```

### 5.4 构建

```bash
npm run build
```

---

## §6 状态卡使用

```bash
cat docs/specs/.state-card.md
```

**关键字段**：

- `current_stage`：当前 Stage（1-spec ~ 5-release）
- `gate_result`：最近 Gate 结果（PENDING / PASS / FAIL）
- `last_gate_time`：最近 Gate 时间戳

---

## §7 相关文档

- [fullstack4TraeV11 SKILL.md](~/.trae-cn/skills/fullstack4TraeV11/SKILL.md)
- [状态卡模板](docs/specs/.state-card.md)