# Fullstack4TraeV10

> **全栈文档驱动开发技能包 v10** — 派生自 spec-kit 五阶段文档驱动 (spec/define/plan/contracts/tasks)，聚焦 Agent 行为质量，用 OS 级强制取代 LLM 自律。
>
> 面向人类阅读的展示文档。可视化优先，代码逻辑看 [`SKILL.md`](./SKILL.md)。

---

## 1. 一句话定位

> **把"AI 自律"换成"OS/Hook 级强制"** — 5 阶段流水线 + 4 层铁律 + 四维满分硬门禁 + 机械归档，每一刀砍在"AI 自评 100 分但实际为空"的痛点上。

---

## 2. 设计哲学（Mermaid mindmap）

```mermaid
mindmap
  root((Fullstack v10<br/>设计哲学))
    复用而非自研
      spec-kit plan.md 格式
      spec-kit spec.md 格式
      acceptance-discipline 外部技能
    质量而非流程
      Agent 行为质量
      探索深度
      业务理解
      验收粒度
    验证而非信任
      四维满分硬门禁
      产物证据链
      主上下文机械校验
    干净而非兼容
      spec-purge.py
      物理删除旧产物
      不纠结 reset
    OS 级强制
      code-hygiene.py
      phase-gate.py
      Hook 拦截
      脚本门禁
```

---

## 3. 五阶段流水线（Mermaid flowchart）

```mermaid
flowchart LR
    subgraph Plan[Phase 0: Plan · 用户确认: 必]
        P0[Planner 前置探索] --> P1[3 个子代理并行]
        P1 --> P2[文档探索<br/>代码探索<br/>依赖探索]
        P2 --> P3[产出 plan.md]
    end

    subgraph Spec[Phase 1: Spec · 用户确认: 必]
        S0[Spec-Enhancer<br/>代写 spec.md<br/>(spec-kit 格式)] --> S1[质量增强段<br/>E2E + Invariants + 原型触发]
        S1 --> S2[E2E + Invariants<br/>+ 原型触发]
    end

    subgraph Contract[Phase 2: Contract · 用户确认: 自动]
        C0[Contract-Writer] --> C1[契约四件套<br/>+ 测试骨架]
    end

    subgraph Implement[Phase 3: Implement · 用户确认: 必]
        I0[业务深度理解<br/>+ 模块接入文档] --> I1[TDD 红绿循环]
        I1 --> I2[code-hygiene.py<br/>实时拦截]
        I2 --> I3[tasks.md 驱动]
    end

    subgraph Review[Phase 4: Review · 用户确认: 自动]
        R0[四维满分验收] --> R1{全部满分?}
        R1 -->|是 ✅| R2[完成 + DOC SYNC]
        R1 -->|否 🛑| R3[REJECT 退回]
    end

    Plan --> Spec
    Spec --> Contract
    Contract --> Implement
    Implement --> Review

    style Plan fill:#e1f5ff
    style Spec fill:#fff4e1
    style Contract fill:#e8f5e9
    style Implement fill:#fce4ec
    style Review fill:#f3e5f5
```

**用户确认分级**（V10 新增）：3 次必确认（Plan/Spec/Implement）+ 2 次自动（Contract/Review）

---

## 4. 五个 Agent 角色全景（Mermaid graph）

```mermaid
graph TD
    User[用户需求] --> Planner

    subgraph 规划层
        Planner[Planner<br/>general_purpose_task<br/>: 探索 + Plan 前置]
    end

    subgraph 规范层
        SpecEnhancer[Spec-Enhancer<br/>general_purpose_task<br/>: 质量增强段]
    end

    subgraph 契约层
        ContractWriter[Contract-Writer<br/>general_purpose_task<br/>: 四件套 + 测试骨架]
    end

    subgraph 实现层
        Implementer[Implementer<br/>general_purpose_task<br/>: TDD + 业务理解 + 接入文档]
    end

    subgraph 验收层
        Reviewer[Reviewer<br/>general_purpose_task<br/>: 四维满分 + 功能效果]
        Debugger[Debugger<br/>general_purpose_task<br/>: Bug 根因 + 修复]
    end

    Planner -->|plan.md| SpecEnhancer
    SpecEnhancer -->|spec.md 增强| ContractWriter
    ContractWriter -->|contracts/| Implementer
    Implementer -->|代码 + 测试| Reviewer
    Reviewer -->|REJECT 退回| Implementer
    Reviewer -.->|Bug 发现| Debugger
    Debugger -.->|修复| Implementer

    style Planner fill:#e1f5ff
    style SpecEnhancer fill:#fff4e1
    style ContractWriter fill:#e8f5e9
    style Implementer fill:#fce4ec
    style Reviewer fill:#f3e5f5
    style Debugger fill:#ffebee
```

---

## 5. 四维满分硬门禁（Mermaid mindmap）

```mermaid
mindmap
  root((四维验收<br/>满分硬门禁))
    代码层<br/>必检 7 项
      单元测试全绿
      合约测试全绿
      Lint 0 error
      覆盖率 ≥ 90%
      无 TODO
      code-hygiene 通过
      理解确认抽查 2 项
    API 层<br/>适用 5 项
      真实端点
      签名一致
      模型一致
      错误码一致
      事件一致
    UI-UX 层<br/>适用 6 项
      视觉 5 状态
      像素比对
      交互流路径
      状态变化
      错误边界
    边际层<br/>适用 4 项
      impact 列出下游
      无意外副作用
      模块文档同步
      扩展点标注
```

**核心规则**：

```text
✅ 4 维全部满分 = PASS
🛑 任一非满分 = REJECT 整个 change
🚫 禁 N/A 计入分母（须 Plan 阶段锁定）
🚫 禁"非阻塞 P1 / 降级验收 / 部分扣分"
```

---

## 6. 机械验证 6 步硬门禁（Mermaid sequence）

```mermaid
sequenceDiagram
    participant A as Coding Agent
    participant V as 主上下文验证器
    participant FS as 文件系统
    participant G as GitNexus

    A->>V: 返回 Completion Report
    V->>V: Step 0 字段值校验<br/>(存在 + 行数 + 交叉验算)

    alt 任一校验失败
        V-->>A: 🛑 REJECT
    else 通过
        V->>A: Step 0.5 GitNexus 段强制
        A->>G: impact() + context()
        G-->>A: 影响面分析
        A->>V: 含 GitNexus 验证段

        alt 缺该段
            V-->>A: 🛑 REJECT
        else 通过
            V->>FS: Step 1 git ls-files
            V->>FS: Step 2 git diff --stat
            V->>V: Step 3 artifacts 对账
            V->>FS: Step 4 .gitignore 检查
            V->>V: Step 5 路径规范
            V->>G: Step 6 LLM 二审抽查

            alt 全部通过
                V-->>A: 🟢 可进入下一阶段
            else 任一失败
                V-->>A: 🛑 REJECT
            end
        end
    end
```

详见 [`/trae/rules/agent-机械验证.md`](../../trae/rules/agent-机械验证.md)。

---

## 7. 三个硬门禁脚本（Mermaid graph）

```mermaid
graph LR
    subgraph 编写期
        CH[code-hygiene.py<br/>: 单文件 800 行<br/>单函数 50 行<br/>圈复杂度 15]
    end

    subgraph 阶段转换期
        PG[phase-gate.py<br/>: plan→spec<br/>spec→contract<br/>contract→implement<br/>implement→review<br/>review→accept]
    end

    subgraph 重构期
        SP[spec-purge.py<br/>: --keyword-detect<br/>--gitignore-auto<br/>幂等性保证]
    end

    CH -->|拦截脏代码| PG
    PG -->|门禁通过| SP
    SP -->|物理归档| Arch[archive/done/<br/>或<br/>archive/out/spec-purge/]

    style CH fill:#fff3cd
    style PG fill:#d1ecf1
    style SP fill:#f8d7da
    style Arch fill:#d4edda
```

**使用示例**：

```powershell
# 编写后立即检查
python scripts\code-hygiene.py --changed-files

# 阶段转换硬门禁
python scripts\phase-gate.py implement-to-review

# 重构时机械归档
python scripts\spec-purge.py --feature 00-05 --keyword-detect --gitignore-auto
```

---

## 8. 铁律 4 层分类（Mermaid mindmap）

```mermaid
mindmap
  root((铁律<br/>4 层分类))
    开发时<br/>Implementer
      TDD RED GREEN
      DRIFT DETECT
      MODULE DOC
      CODE HYGIENE
    规划时<br/>Planner
      EXPLORE FIRST
      IMPACT BY TOOL
      DEDUP BY ATOM
    验收时<br/>Reviewer
      FAIL IS FAIL
      SCORING DERIVED
      FOUR DIMENSIONS
    文档时<br/>全局
      DOC FIRST
      DELTA ONLY
      ARCHIVE IMMUTABLE
```

**冲突消解表**：

| 潜在冲突 | 优先级 | 判定 |
|---------|-------|------|
| TDD vs DRIFT | DRIFT > TDD | 实现中途发现契约错 → 立即停止 TDD，回流 spec |
| MODULE DOC vs CODE HYGIENE | MODULE DOC | 接入文档可放 references/ 子目录 |
| FAIL IS FAIL vs N/A | N/A > FAIL | 不适用维度不假装通过，也不算 FAIL |
| ARCHIVE IMMUTABLE vs 重构 | 重构 > ARCHIVE | 重构时 archive/out/ 目录可清理 |

---

## 9. 评分制度 V10 vs V9.2（Mermaid flowchart 对比）

```mermaid
flowchart LR
    subgraph V9.2[V9.2 旧制]
        V92_1[5 维度加权] --> V92_2[100 分制]
        V92_2 --> V92_3{≥ 80?}
        V92_3 -->|是| V92_Pass[PASS 含降级]
        V92_3 -->|否| V92_Fail[FAIL]
    end

    subgraph V10[V10 新制]
        V10_1[4 维二元] --> V10_2{全部满分?}
        V10_2 -->|是| V10_Pass[✅ PASS]
        V10_2 -->|否| V10_Reject[🛑 REJECT]
    end

    V9.2 -.废除.-> V10

    style V92_Pass fill:#fff3cd
    style V92_Fail fill:#f8d7da
    style V10_Pass fill:#d4edda
    style V10_Reject fill:#f8d7da
```

**核心差异**：

| 维度 | V9.2（旧） | V10（新） |
|------|----------|----------|
| 评分 | 5 维度加权 100 分制 | 4 维二元（PASS/REJECT） |
| 通过线 | ≥ 80 分通过 | 任何非满分 = REJECT |
| N/A 维度 | 不计入分母 | 必须 Plan 阶段锁定 |
| 降级验收 | "非阻塞 P1"允许 | 禁止 |
| 产物证据链 | agent 自报 | 必须附真实命令输出 |

---

## 10. AIGCMediaDesktop 实战状态（Mermaid pie + 仪表盘）

**当前 13 个 change 满分状态分布**：

```mermaid
pie title 13 个 Change 满分状态分布
    "🔴 非满分（需 REJECT）" : 12
    "🟢 满分（PASS）" : 1
    "🟡 控制器（边际未满分）" : 1
```

| 状态 | 数量 | 说明 |
|------|:---:|------|
| 🟢 满分 | 1 | 00-02 app-shell（纯前端，API/UI-UX/边际都达标） |
| 🔴 非满分 | 12 | 92/100 等旧评分，V10 下全部 REJECT |
| 🟡 控制器 | 1 | ui-ux-refactor（边际待补） |

**下一步（V10 路线）**：

```mermaid
flowchart TD
    A[11 个 🔴 Stub 跑 spec-purge] --> B[用户确认]
    B --> C[批量物理归档]
    C --> D[Planner 重新探索]
    D --> E[Spec-Enhancer 重做]
    E --> F[Spec-Enhancer 增强]
    F --> G[Contract-Writer 四件套]
    G --> H[Implementer TDD + 接入文档]
    H --> I[Reviewer 四维满分]
    I --> J{全部满分?}
    J -->|是| K[✅ PASS + DOC SYNC + 归档]
    J -->|否| H

    style A fill:#f8d7da
    style K fill:#d4edda
    style H fill:#fff3cd
```

---

## 11. 仓库结构（Mermaid graph）

```mermaid
graph TD
    Root[fullstack4TraeV10/]

    Root --> Agents[agents/<br/>6 个 agent 文件]
    Root --> Refs[references/<br/>17 个细化文档]
    Root --> Scripts[scripts/<br/>7 个 Python 脚本]
    Root --> Templates[templates/<br/>契约 + Hooks + 模板]

    Agents --> A1[planner.md]
    Agents --> A2[spec-enhancer.md]
    Agents --> A3[contract-writer.md]
    Agents --> A4[implementer.md]
    Agents --> A5[reviewer.md]
    Agents --> A6[debugger.md]

    Scripts --> S1[code-hygiene.py 🆕]
    Scripts --> S2[phase-gate.py 🆕]
    Scripts --> S3[spec-purge.py 🆕 keyword-detect + gitignore-auto]
    Scripts --> S4[migrate-v9-to-v10.py]
    Scripts --> S5[change-status.py]
    Scripts --> S6[spec-knowledge-extract.py]
    Scripts --> S7[install-hooks.py]

    Refs --> R1[acceptance-gates-v10.md 🆕]
    Refs --> R2[acceptance-gates.md 旧版标记废止]

    Templates --> T1[contracts/<br/>api/domain/event/validation 4 件套]
    Templates --> T2[hooks/<br/>8 个 .py + hooks.json]
    Templates --> T3[spec-template.md]
    Templates --> T4[state-card.md]

    style S1 fill:#d4edda
    style S2 fill:#d4edda
    style S3 fill:#d4edda
    style R1 fill:#d4edda
```

---

## 12. 版本演进（时间线）

```mermaid
timeline
    title Fullstack 版本演进
    V8 : 5 阶段流水线
        : 完整自研 spec 系统
        : 大量文档 + 自研 Hooks
    V9 : 7 阶段流水线
        : Delta Spec 格式
        : _invalidated/ 隔离
        : 5 维度 100 分制
    V10 2026-07-25 : 5 阶段精简
                : 派生自 spec-kit 五阶段
                : Planner/Spec-Enhancer 子代理代写
                : spec-purge 物理归档
                : 四维验收
    V10.1 2026-07-27 : 满分硬门禁
                  : 6 步机械验证
                  : 3 个硬门禁脚本
                  : AIGCMediaDesktop 配套治理
                  : 状态卡 v4 满分仪表盘
```

---

## 13. 核心成果数字

| 指标 | V9.2 | V10.1 | 改进 |
|------|:---:|:---:|:---:|
| 阶段数 | 7 | 5 | -29% |
| 用户确认次数 | 7 | 3 | -57% |
| 总文件数 | ~40+ | ~25 | -37% |
| 评分公式 | 100 分制 | 二元满分 | 杜绝灰色 |
| 验收降级 | 允许 | 禁止 | 100% 严化 |
| 跨项目治理 | 双仓副本 | 软链单一源 | 杜绝漂移 |
| 强制机制 | 0 | 6 步 + 3 脚本 | +∞ |

---

## 14. 常见问题（FAQ）

**Q: 满分硬门禁是不是太严？**
A: 是的。这是为了根治"AI 自评 100 分但实际为空"。不适用维度必须 Plan 阶段显式锁定。

**Q: V9.2 项目怎么升级？**
A: 跑 `python scripts/migrate-v9-to-v10.py` 一键迁移（含 dry-run）。

**Q: AIGCMediaDesktop 的 .trae/rules 副本怎么办？**
A: 已在 AIGCMediaDesktop 侧执行 `pwsh .trae/rules-link.ps1` 建立软链到 my-trae-helper 权威源。

**Q: 怎么强制 code-hygiene？**
A: 在 Implementer 完成任何 task 后立即跑 `python scripts/code-hygiene.py --changed-files`，exit 非 0 即 REJECT。

**Q: spec-purge 怎么用？**
A: `python scripts/spec-purge.py --feature XX --keyword-detect --gitignore-auto`，命中关键词白名单（重构/重写/推翻/从头来/重新设计）自动触发物理归档。

---

## 15. 相关链接

- 主 SKILL.md：[`./SKILL.md`](./SKILL.md)
- 验收清单 v10：[`./references/acceptance-gates-v10.md`](./references/acceptance-gates-v10.md)
- 阶段切换机械验证：[`/trae/rules/agent-机械验证.md`](../../trae/rules/agent-机械验证.md)
- AIGCMediaDesktop 状态卡 v4：[`/trae/specs/upgrade-fullstack-v10-harden/state-card-mirror-v4.md`](../../trae/specs/upgrade-fullstack-v10-harden/state-card-mirror-v4.md)
- 升级总策略：[`/trae/documents/fullstack-v10-升级总策略.md`](../../trae/documents/fullstack-v10-升级总策略.md)

---

**最后更新**：2026-07-27 · V10.1.0
**作者**：my-trae-helper 项目组