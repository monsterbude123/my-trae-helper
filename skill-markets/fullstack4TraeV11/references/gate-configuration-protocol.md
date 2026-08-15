# Gate Configuration Protocol — 贾维斯委派 7 步 SOP(调用方视角)

> **适用对象**:V11 会话内**任何**想调整 guard/gate 的 agent(主 agent / 13 stage sub-agent / reviewer / implementer)。
> **核心**:你自己**没有** gate 写权。所有 gate 变更走贾维斯([jarvis.md](../skills/00-boot/agents/jarvis.md))。
> **为什么**:防止 agent 为了通过门禁自己改标准 — 协议(软) + 白名单(中) + hash 锁(硬)三层防线。

---

## 三层防线总览

| 层 | 机制 | 挡住谁 |
|----|------|--------|
| 协议层 | 本 SOP + [JARVIS-DELEGATION] 委派头部 | 守规矩的 agent(流程引导) |
| 白名单层 | jarvis.md §3 — 非贾维斯 Edit 白名单路径 = 违规 | 越权直改的 agent(事后审计) |
| 机械层 | gate-integrity-guard.py hash 锁 — 跑 gate 前强校验 | **一切绕过行为(事前拦截)** — 即使 agent 偷改了 ac-gate.py,hash 不匹配照样 BLOCK |

---

## 7 步 SOP

```
┌────────────────────────────────────────────────────────────┐
│ Step 1. 识别需求                                             │
│   触发源:                                                   │
│     - 用户显式要求("给订单模块加 CRUD gate")                 │
│     - gate 报错 BLOCK(ac-gate G4 漏核销 / code-hygiene FAIL)│
│     - 新项目初始化(01-intake → project-init)                │
│     - 新增技术分层(monorepo 新 app / 新 module)              │
│   输出:一句话"要改什么 + 为什么 + 属于哪层(L-module/app/system)"│
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ Step 2. 自我判定 — 我能直接改吗?                              │
│   查 jarvis.md §3 白名单:                                    │
│     目标 ∈ 白名单(五表/gate 脚本/gate-config/lock/.husky)     │
│       → ❌ 不能直改 → Step 3 委派贾维斯                       │
│     目标 = 普通业务代码 / 普通文档                             │
│       → ✅ 自己改,与 gate 无关                               │
│     目标 = 阈值削减/检查项删除(降标准)                        │
│       → 🛑 需用户显式指令原话附在委派头部,否则贾维斯会拒绝     │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ Step 3. 准备 [JARVIS-DELEGATION] 头部                        │
│   按 jarvis.md §4 填全 5 字段(任务/上下文/影响范围/约束)      │
│   关键:影响范围不许省 — 贾维斯要判断重跑哪些 gate 三态         │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ Step 4. 委派贾维斯                                            │
│   Task(subagent_type="general-purpose",                     │
│        description="jarvis: <一句话任务>")                   │
│   选择 sub-agent 原因:上下文隔离(不被主任务污染)+ 审计独立    │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ Step 5. 验收贾维斯报告                                        │
│   必含:改动清单 / 影响层 / 新 lock hash 前缀 / 三态验证结果    │
│   阈值变更未单列"标准变更"段 → 打回重写                       │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ Step 6. 主 agent 兜底验证(不信 sub-agent 一面之词)            │
│   亲自跑:                                                   │
│     python gate-integrity-guard.py --verify   → PASS        │
│     重跑受影响 gate(真反例)→ BLOCK 如预期                    │
│   任一异常 → 回 Step 3 重派                                  │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│ Step 7. commit + 状态卡同步                                   │
│   - lock/gate-config 变更随代码一起 commit                   │
│   - 涉及 13 stage 流转的,同步状态卡 gate_result              │
└────────────────────────────────────────────────────────────┘
```

---

## 新项目初始化(时机①)快捷路径

```
01-intake 识别 project-init 意图
  → 主 agent 委派贾维斯(Step 3-4,头部注明"初始化")
  → 贾维斯:gate-installer.py --preset <nodejs|python> --layers module,app,system
  → 产出:gates/gate-config.json + .husky/{pre-commit,pre-push} + gate.lock.yaml
  → 主 agent 兜底:--verify PASS + lock 存在
```

---

## 反模式(调用方必避免)

| # | 反例 | 后果 |
|:--:|------|------|
| 1 | reviewer 嫌 ac-gate 严 → 直接 Edit ac-gate.py 删 G4 | 白名单违规 + hash 锁 BLOCK + 会话冻结 |
| 2 | implementer 测试不过 → 改 gate-config.json 删 checks | 同上 |
| 3 | 无头部直接命令贾维斯"把阈值调低" | 贾维斯按 §6-5 拒绝,浪费一轮 |
| 4 | 委派头部省略影响范围 | 贾维斯无法选层,gate 三态验证缺项 |
| 5 | 贾维斯改完不跑 --verify 就 commit | lock 过期,下次自检 BLOCK |
| 6 | "初始化时跳过 installer,手抄 scaffolds 的 .husky" | 无 lock = 机械防线不存在 |

---

## 关联引用

- [jarvis.md](../skills/00-boot/agents/jarvis.md) — 贾维斯 agent(白名单 + 5 步流程)
- [gate-installer.py](../scripts/gate-installer.py) — 时机①安装器
- [gate-integrity-guard.py](../scripts/gate-integrity-guard.py) — 时机②hash 锁
- [registry/gates.yaml](../registry/gates.yaml) — 13 gate + layer 分层字段
- [scaffolds/README.md](../scaffolds/README.md) — nodejs/python 脚手架
