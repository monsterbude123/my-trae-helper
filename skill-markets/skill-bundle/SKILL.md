---
name: skill-bundle
version: 1.0.0
description: 子 skills 装载规范 — 规定 TRAE 父包(含 skills/<sub>/SKILL.md)的目录结构、命名空间、一键装/卸/更新闸门。触发词:子 skills、bundle、批量装载、bundle install、子包结构。
intent: 子 skills 装载规范(目录结构 / 命名空间 / 三道闸)
category: standard
audience: [developer]
---

# Skill Bundle 规范 v1.0

> 规定"一个父包 + N 个子 skills"如何在 TRAE Work 中**正确装载、命名、版本管理、避免冲突**。
> 适用于 fullstack4TraeV11 / game-production-kit / agent-dev-control-kit 这类"包内有 skills/<sub>/"结构。

## 何时使用

| 场景 | 是否需要 bundle 规范 |
|------|---------------------|
| 单个独立 skill,无 skills/ 子目录 | ❌ 用 trae-professional 规范 |
| 父包 + 多个子 skills,但只在编排器内部引用 | ✅ 必走 bundle 规范 |
| 父包 + 多个子 skills,需要在 TRAE Work 中独立触发 | ✅ 必走 bundle 规范 + CLI 一键装载 |

## 目录结构(单层 — TRAE 协议只识别单层)

```
<parent-pkg>/
├── SKILL.md              # 父包入口(可空,只起命名空间作用)
├── scripts/              # 可选
├── references/           # 可选
└── skills/               # 单层 — TRAE 协议只识别这一层
    ├── <sub-skill-1>/
    │   └── SKILL.md      # 独立 frontmatter
    ├── <sub-skill-2>/
    │   └── SKILL.md
    └── <sub-skill-N>/
        └── SKILL.md
```

**禁止**:
- `skills/<sub>/skills/<grandchild>/` 双层嵌套(TRAE 协议不识别)
- `skills/<parent-pkg>/skills/<sub>/` 自指嵌套(BND-002)

## 命名约束

| 约束 | 规则 | 守卫代码 |
|------|------|----------|
| 目录名 kebab-case | `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` | BND-001 |
| 目录名 ≠ 父包名 | 避免命名冲突 | BND-002 |
| frontmatter name 必填 | 必含 `name:` 字段 | BND-003 |
| deprecated + redirect_to | DEPRECATED 必带重定向 | BND-004 |
| 单层 skills/ | 不嵌套 | BND-005 |
| 跨包 frontmatter name 不重复 | 整个 marketplace 唯一 | BND-006 |
| 子 skill 数量 ≤ 30 | 过度拆分 → WARN | BND-007 |

**实例(合规)**:
```
fullstack4TraeV11/skills/01-intake/SKILL.md       # ⚠ 数字开头不合规,应当 01-intake → stage-01-intake
game-production-kit/skills/babylon-scripting/SKILL.md  # ✅ kebab-case
agent-dev-control-kit/skills/guard-control/SKILL.md    # ✅ kebab-case
```

## 命名空间装载

子 skill 装到 TRAE 目标目录时,使用 `<parent-pkg>-<sub-skill>` 命名空间,避免不同父包之间冲突:

```
~/.trae-cn/skills/
├── fullstack4TraeV11-01-intake/      # 父包.子 skill 二级命名
├── fullstack4TraeV11-02-plan/
├── fullstack4TraeV11-13-project-health/
├── game-production-kit-babylon-scripting/
└── agent-dev-control-kit-guard-control/
```

**目的**:
- 不同父包的同名子 skill 不冲突
- 用户 `trae-skills bundle list` 一眼看出归属
- 卸载父包时 `trae-skills bundle uninstall <pkg>` 只删带 `<pkg>-` 前缀的,不影响其他

## CLI 命令(项目自带)

| 命令 | 作用 |
|------|------|
| `trae-skills bundle install <pkg>` | 一键装父包全部子 skills(命名空间隔离 + 三道闸) |
| `trae-skills bundle update <pkg>` | 一键检查 + 更新已装子 skills(版本比对) |
| `trae-skills bundle uninstall <pkg>` | 一键卸载(只删带 `<pkg>-` 前缀的) |
| `trae-skills bundle list <pkg>` | 列出子 skills + 装载状态(已装/未装/最新版) |
| `trae-skills bundle flatten --plan <pkg>` | **新增** — 报告 BND-005 嵌套结构 + 打印可执行拆扁 plan(不写盘) |
| `trae-skills verify <pkg>` | 跑全部守卫,含 07_bundle_structure |

**Options**:
- `-g / --trae-cn` 全局装(默认项目级)
- `-a <agent>` 目标 agent(trae-cn / claude-code / codex / cursor / ...)
- `--select <n1,n2>` 只装指定 index
- `--exclude <n>` 排除指定 index
- `-y / --yes` 跳过确认
- `--dry-run` 只打印,不实际操作
- `--copy` copy 而非 symlink

### flatten 子命令(BND-005 自检辅助)

`trae-skills bundle flatten --plan <pkg>` 是 BND-005 BLOCK 后的**可执行下一步**:

```
$ trae-skills bundle flatten --plan game-production-kit

🔍 [BND-005] game-production-kit 嵌套扫描:
  ❌ skills/voice-acting-skill/skills/  ← 嵌套深度 1,违反 TRAE 单层协议

📋 拆扁 plan(只读,不写盘):
  1. mkdir game-production-kit/skills/voice-acting-annotation-generator
  2. git mv game-production-kit/skills/voice-acting-skill/skills/annotation-generator/SKILL.md \
        game-production-kit/skills/voice-acting-annotation-generator/SKILL.md
  3. (重复步骤 1-2 给 batch-manager / script-parser / tts-synthesizer / voice-assigner)
  4. 更新 voice-acting-skill/SKILL.md 路由表:子 skill 入口改写为
     skills/voice-acting-annotation-generator/ 等
  5. 删除空目录 game-production-kit/skills/voice-acting-skill/skills/

💡 命名约定: voice-acting-{原嵌套名},把父 skill 名作为前缀,保留语义关联
```

**设计**:
- `--plan` 只打印 plan,不实际操作(避免误改)
- 嵌套**自动遍历**深度递归(不只看一层,任意层数都报)
- plan 输出**完整 git mv 命令** — 用户复制即可执行
- 不维护白名单(避免硬编码,与 trap-instructions.yaml 反硬编码对齐)

## 三道闸(每次 install/update/uninstall 都跑)

| 闸 | 检查 | 守卫 |
|----|------|------|
| 1. deprecation | frontmatter `status: deprecated` + `redirect_to` → BLOCK | DEP-002 |
| 2. version | 已装版本 vs marketplace 版本比对 | VER-001/002/003/004 |
| 3. name-conflict | 跨包同名 (cross-package) → BLOCK / self-overwrite → WARN / similar-name → WARN | BND-006 |

**实现**:
- Node: [src/install-guards.mjs](../../../../src/install-guards.mjs) — `deprecationGuard` / `versionGuard` / `nameConflictGuard` / `readInstalledVersion`
- 复用: add / update / remove / bundle 四个命令都调这三道闸

## 守卫脚本(skill-acceptance 体系)

```
python skill-markets/skill-acceptance/checks/07_bundle_structure.py --target <parent-pkg>
```

退出码:
- 0 = PASS(无 issues,或非 bundle 跳过)
- 2 = WARN(BND-007 等非阻塞)
- 4 = BLOCK(BND-001/002/003/005/006 等)

## 端到端示例

```bash
# 1. 列出所有 bundle
trae-skills bundle list

# 2. 装载指定父包(全局)
trae-skills bundle install fullstack4TraeV11 -a trae-cn -g -y

# 3. 装载到多个 agent
trae-skills bundle install game-production-kit -a trae-cn -a claude-code -y

# 4. 只装前 5 个
trae-skills bundle install fullstack4TraeV11 --select 1,2,3,4,5 -y

# 5. 排除 prototype / bug-fix
trae-skills bundle install fullstack4TraeV11 --exclude 5,12 -y

# 6. 预演(不实际操作)
trae-skills bundle install fullstack4TraeV11 --dry-run

# 7. 一键更新
trae-skills bundle update fullstack4TraeV11 -y

# 8. 一键卸载(只删 fullstack4TraeV11-*,不影响其他)
trae-skills bundle uninstall fullstack4TraeV11 -y

# 9. 守卫检查
trae-skills verify fullstack4TraeV11
```

## 命名反例

| ❌ 不合规 | ✅ 应改 |
|-----------|--------|
| `skills/01-intake/` | `skills/stage-01-intake/` 或 `skills/intake/` |
| `skills/fullstack4TraeV11-01-intake/`(子 skill 名前缀) | `skills/01-intake/`(命名空间在装载时加,不在目录名) |
| `skills/voice-acting-skill/skills/annotation-generator/`(嵌套) | 拆成 `skills/voice-acting-annotation-generator/` 等扁平 |
| 父包 `my-pkg` + 子 skill `my-pkg` | 改子 skill 名,如 `my-pkg-core` |
| 跨包同名 `name: webgal-scripting`(两个父包都写) | 用 `name: game-production-kit-webgal-scripting` 等带前缀 |

---

## 守卫与门禁(Guard + Gate)

> **3 道闸** × **3 个生命周期 Gate** = 自动检查 + 拦截矩阵
> 详见 [checks/07_bundle_structure.py](../checks/07_bundle_structure.py) 实现

### 检查项清单(BND-001 ~ BND-007)

| 守卫码 | 级别 | 检查项 | 触发原因 |
|--------|------|--------|----------|
| **BND-001** | BLOCK | 子 skill 目录名 kebab-case | TRAE 协议硬要求 |
| **BND-002** | BLOCK | 子 skill 目录名 ≠ 父包名 | 避免自指循环 |
| **BND-003** | BLOCK | 子 skill frontmatter 含 `name` 字段 | TRAE 触发依赖 |
| **BND-004** | WARN | DEPRECATED 子 skill 缺 `redirect_to` | 重定向完整性 |
| **BND-005** | BLOCK | 单层 `skills/<sub>/`(无双层嵌套,**自动遍历深度**,不维护白名单) | TRAE 协议只识别一层 |
| **BND-006** | BLOCK | 跨包 frontmatter name 不重复 | 全局命名空间唯一性 |
| **BND-007** | WARN | 子 skills 数量 > 30 | 过度拆分提示 |

### 3 种运行模式(单一脚本,不同 lifecycle 用)

| 模式 | CLI | 触发时机 | 跑哪些检查 | 用途 |
|------|-----|----------|------------|------|
| **single** | `--target <pkg>` | verify / 单包调试 | 全部 BND-001~007 | 完整诊断 |
| **all** | `--mode all` | L2 push / L3 PR merge / L4 publish | 全部 BND-001~007 × 全部父包 | 全量扫描 |
| **diff** | `--mode diff --changed <pkg1,pkg2>` | L1 commit | **仅 BND-006 跨包冲突** | 增量快查 |

### Gate 触发矩阵(自动接入项目三层控制)

| Gate | 触发时机 | 模式 | 阻塞级别 | 接入位置 |
|------|----------|------|----------|----------|
| **L1 Commit** | `git commit` | **diff**(增量) | BLOCK → 阻止提交 | [.husky/pre-commit](../../../../.husky/pre-commit) Step 4.5 |
| **L2 Push** | `git push` | **all**(全量) | BLOCK → 阻止推送 | [.husky/pre-push](../../../../.husky/pre-push) Step 3.5 |
| **L3 Merge** | PR merge | **all**(全量) | BLOCK → 阻止合并 | [.github/workflows/skill-market-gate.yml](../../../../.github/workflows/skill-market-gate.yml) L3-merge-gate |
| **L4 Publish** | Release | **all**(全量) | BLOCK → 阻止灰度发布 | [.github/workflows/skill-market-gate.yml](../../../../.github/workflows/skill-market-gate.yml) L4-publish-gate |

### 自动调用入口

```bash
# 显式调用(主动诊断)
npm run test:bundle                 # L2 模式:全量
python skill-markets/skill-acceptance/checks/07_bundle_structure.py --mode all
python skill-markets/skill-acceptance/checks/07_bundle_structure.py --target skill-markets/fullstack4TraeV11
python skill-markets/skill-acceptance/checks/07_bundle_structure.py --mode diff --changed fullstack4TraeV11,game-production-kit
```

### 退出码契约(对接 CI / pre-commit / pre-push)

| 退出码 | 含义 | Gate 行为 |
|--------|------|----------|
| `0` | PASS(全无 issue / 非 bundle 跳过 / diff 无跨包冲突) | 继续 |
| `2` | WARN(BND-007 等非阻塞) | L1/L2 继续(不阻断 commit/push);L3/L4 视 CI 配置 |
| `4` | BLOCK(BND-001/002/003/005/006) | **L1/L2/L3/L4 全部阻断** |
| `5` | ARG_ERROR(参数缺失) | Gate 配置错误,直接失败 |
| `6` | INTERNAL_ERROR(异常) | 走 fall-back 流程 |

### 现状快照(2026-08-14)

执行 `python skill-markets/skill-acceptance/checks/07_bundle_structure.py --mode all` 当前结果:

| 父包 | 子 skills | 状态 | 阻塞项 |
|------|----------|------|--------|
| acceptance-discipline | 3 | ✅ PASS | — |
| agent-dev-control-kit | 5 | ✅ PASS | — |
| comfyui-api-skills | 15 | ✅ PASS | — |
| **fullstack4TraeV11** | 13 | ❌ **BLOCK** | BND-001 × 13(目录名数字开头) |
| **game-production-kit** | 21 | ❌ **BLOCK** | BND-005 × 1(voice-acting-skill 嵌套,运行 `trae-skills bundle flatten --plan game-production-kit` 拿 plan) |
| trae-professional | 0 | ✅ skip(非 bundle) | — |
| ponytail4Trae | 0 | ✅ skip(无 SKILL.md) | — |
| ... 其他 | 0 | ✅ skip | — |

> **修法**:见 §命名反例
> - fullstack4TraeV11: `skills/01-intake/` → `skills/stage-01-intake/`
> - game-production-kit: `skills/voice-acting-skill/skills/` 拆扁

### 实战:跨 PR 拦截 BND-006

场景:开发者新增 skill 包 `my-game`,包含子 skill `name: babylon-scripting`。

- L1 commit: `--mode diff --changed my-game` → 扫到与 `game-production-kit/skills/babylon-scripting` 同名 → **BLOCK**
- 修复:把子 skill name 改为 `name: my-game-babylon-scripting` → 再次 commit → PASS

无需任何人工检查,**完全自动**。

## 与现有体系的关系

- **AGENTS.md §1.2 CLI 拆分**: bundle 是一个职责,放 src/bundle.mjs,bin/cli.mjs 只路由
- **AGENTS.md §1.5 经验沉淀**: install-guards.mjs 是这套三道闸的代码事实,经验沉淀在 trap-instructions.yaml
- **AGENTS.md §2.4 Gate 自验收**: 07_bundle_structure.py 已用 fullstack4TraeV11 / game-production-kit / agent-dev-control-kit / trae-professional 4 态自验证
- **三层控制**: bundle install 走 Execution(skill-install-control.mjs)+ Guard(install-guards.mjs 三道闸)+ Gate(skill-acceptance 守卫)

## 关联

- [src/bundle.mjs](../../../../src/bundle.mjs) — bundle 命令实现
- [src/install-guards.mjs](../../../../src/install-guards.mjs) — 三道闸实现(运行时)
- [checks/07_bundle_structure.py](../checks/07_bundle_structure.py) — 结构守卫(构建时)
- [bin/cli.mjs](../../../../bin/cli.mjs) — 命令路由
- [.husky/pre-commit](../../../../.husky/pre-commit) — L1 commit gate
- [.husky/pre-push](../../../../.husky/pre-push) — L2 push gate
- [.github/workflows/skill-market-gate.yml](../../../../.github/workflows/skill-market-gate.yml) — L3/L4 CI gate
- 父项目 [AGENTS.md](../../../../AGENTS.md) — 三层控制 + 铁律
