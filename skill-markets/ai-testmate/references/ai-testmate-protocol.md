# ai-testmate Skill Protocol V1.0

> **依据**:V11 `references/skill-creation-workflow.md` §1 协议先行
> **生效日**:2026-08-20
> **独立性**:独立专精测试工程师 Skill,不替代任何现有 skill

---

## §1 scope(适用范围)

- **package**: `skill-markets/ai-testmate/`
- **定位**:AI 端到端测试助理 — 读产品文档 + 测试计划 → 在指定工作空间新建测试项目 → 并行执行 UI(playwright)+ API(requests)测试 → 输出 4 份报告 + 禅道回写 + 飞书推送
- **v1.1 增量定位**:输入自适应 4 模式(PRD / PRD 目录树 / PRD+openapi / 仅 openapi)+ 禅道可选(降级到本地 `<app-test>/docs/bugs/` 管理 bug 生命周期)
- **借用清单**(仅借鉴,不替代):
  - `fullstack4TraeV11`:三层架构骨架(Gate/Guard/Execution)+ 协议程序化解析思路 + 反例库格式 + **bug 状态机简化版**(OPEN/FIXED/CLOSED + source 字段,见 v11-bug-flow-borrowed.md)
  - `zentao-cli`:命令集(本 skill 仅声明调用时机)**+ 可选,缺失降级到本地 bug storage**
  - `lark MCP`:通知能力(本 skill 仅声明卡片格式)
- **不借用清单**(明确边界):
  - ❌ 不调 V11 的 13 stage / spec-kit / qa-loop / guard-smith 委派 / 6 层排查 / 角色矩阵
  - ❌ 不重写 zentao-cli 的命令实现
  - ❌ 不重写 lark MCP 的通知能力
  - ❌ 不写 registry/skills.yaml 注册(独立 skill,不入 V11 注册表 — 如需注册,由 guard-smith 委派)
  - ❌ V11 bug 单的 IN-FIX / VERIFIED / REOPENED / OBSOLETE 状态(开发流程相关,测试 agent 自动建单不需要)
  - ❌ V11 CLOSED 三方协议(代码提测 / 测试专家会签 / 用户确认)— 测试 agent 只能标 CLOSED 候选,真正 CLOSED 由开发流人工确认
  - ❌ 不挂 .husky/ai-testmate-gate(同上)

---

## §2 必填元数据(SKILL.md frontmatter)

| 字段 | 是否必填 | 示例 |
|------|:---:|------|
| `name` | 必填 | `ai-testmate` |
| `description` | 必填 | 含触发词 + 触发场景(见 §2.1) |
| `version` | 必填 | `1.0.0` |
| `requires.mcp` | 必填 | `[zentao, lark]` |
| `changelog` | 推荐 | V{major.minor} + date + note |

### §2.1 description 触发词清单(必须包含至少 3 个)

- `ai testmate` / `跑 e2e` / `出测试报告` / `同步 Bug 到禅道`
- `新建测试项目` / `UI API 测试` / `禅道登记测试单`

---

## §3 结构规则

### §3.1 行数弹性(参考 vibe-coding-standards v2.5)

| 文件 | 弹性上限 | 超阈处理 |
|------|:-----:|----------|
| `SKILL.md` | ≤350 行 | 瘦身到 references/ |
| `agents/*.md` | ≤200 行 | 同上 |
| `references/*.md` | ≤250 行 | 拆分多个文件 |

### §3.2 目录硬约束

```
skill-markets/ai-testmate/
├── SKILL.md                      # 1 份
├── agents/                       # 5 份(planner/credential-keeper/api-tester/ui-tester/reporter)
├── references/                   # 8 份(含本协议)
├── scripts/                      # 4 份
├── tests/unit/                   # ≥ 3 用例
├── todos/                        # task.md + checklist.md
└── .env.example                  # 1 份
```

### §3.3 多文件拆分(AGENTS.md §0 架构约束)

- ❌ 禁止单文件架构(全部堆 SKILL.md)
- ✅ 每个 agent 独立 md,带 `## §N 边界` 声明
- ✅ 每个 reference 独立 md,带 `## §1 必填` + `## §2 字段映射` + `## §3 反例`

---

## §4 反例库(本协议级)

| AP# | 反例 | 检测方法 | 修复 |
|-----|------|----------|------|
| **AP-1** | 工作空间路径硬编码 | `grep '/workspace/' scripts/*.sh` | env 注入 |
| **AP-2** | 账号池泄露到 skill 内 | `grep -r 'TEST_USER_' skill-markets/ai-testmate/ \| grep -v .env.example` | 仅 .env.example 含变量名 |
| **AP-3** | 禅道写权越界(planner 调 bug create) | `grep 'zentao bug create' agents/*.md` | 写权收敛 reporter |
| **AP-4** | 飞书直连 webhook URL | `grep 'hooks.lark\|webhook.*http' scripts/` | 走 lark MCP |
| **AP-5** | 截图脱敏漏做 | `grep 'mask\|redact' agents/ui-tester.md` | ui-tester 必带 mask CSS |
| **AP-6** | 跨平台 Python 路径硬编码 | `grep '/mnt/c/\|/usr/bin/python' scripts/` | 复用 detect-python.sh |
| **AP-7** | 报告覆盖历史(无时间戳) | `grep 'YYYYMMDD\|%Y%m%d' scripts/run-test.sh` | 时间戳强制 |
| **AP-8** | SKILL.md 超 350 行 | `wc -l SKILL.md` | 瘦身到 references/ |

---

## §5 测试要求

### §5.1 pytest ≥ 3 用例(必填/推荐/反例各 1)

| 用例 | 覆盖反例 |
|------|---------|
| `test_required_env_missing_blocks_run` | AP-6 变体 |
| `test_zentao_write_authority_converged` | AP-3 |
| `test_lark_must_use_mcp_not_direct_url` | AP-4 |

### §5.2 三态自检(AGENTS.md §2.4)

```
PASS  :正常样本 → exit 0
BLOCK :真反例 → exit ≠ 0 + 定位信息
边界 :模糊样本 → exit ≠ 0 + 不误报
```

---

## §6 协议版本

- **V1.2**(2026-08-20 增量):自动工作空间探测(`scripts/workspace-detect.py`,cwd 向上找 `.agents/.env`)
- **V1.1**(2026-08-20 增量):输入自适应 4 模式 + 禅道可选降级 + bug-storage 本地生命周期
- **V1.0**(2026-08-20 蒸馏首版)

---

## §7 v1.1 增量反例

| AP# | 反例 | 检测 |
|-----|------|------|
| **V2-AP-1** | openapi 解析忽略 `security` 字段(鉴权失败) | openapi-extractor.py 单元测试 |
| **V2-AP-2** | 禅道不可用时硬 exit(应降级) | reporter pytest mock zentao 不可达 |
| **V2-AP-3** | bug 单 frontmatter 字段不齐 | bug-storage.md 模板校验 |
| **V2-AP-4** | planner 4 模式漏 source 标签 | input-router.md 测试矩阵 |
| **V2-AP-5** | openapi-only 模式仍试图读 PRD | planner §1 决策树 |

---

## §8 v1.1 新增引用

- [references/input-router.md](input-router.md)— 4 模式决策矩阵
- [references/openapi-to-testcases.md](openapi-to-testcases.md)— openapi.json → test-cases.yaml 映射
- [references/v11-bug-flow-borrowed.md](v11-bug-flow-borrowed.md)— V11 bug 流程借鉴白名单
- [references/bug-storage.md](bug-storage.md)— 本地 bug 生命周期(降级路径)
- [scripts/openapi-extractor.py](../scripts/openapi-extractor.py)— openapi 解析器

---

## §7 与 V11 的引用关系

```
本协议仅"借鉴 V11 三层骨架思路"
  → 不读 V11 SKILL.md 内容
  → 不调 V11 命令
  → 不挂 V11 gate
  → 不入 V11 registry

如需任何 V11 集成,由用户授权后另行委派 guard-smith。
```
```