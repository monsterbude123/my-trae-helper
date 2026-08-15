---
name: fullstack-00-boot
description: "V11 启动装载器(pre-stage 层)— 会话第一步装载贾维斯(Jarvis)门禁守护角色 + 初始化 hash 锁。不占 13 stage 编号。触发词:项目初始化 / init / 贾维斯 / jarvis / gate 配置。"
layer: pre-stage          # V11.8.0 P2 修复(2026-08-15):不在 13 stage 状态机里,用 layer 标识取代 stage
parent: fullstack4traev11
depends_on:
  skills: []
  stages: []
  references:
    - agents/jarvis.md
---

# Stage 0 Boot — 启动装载器(贾维斯注入点)

> **定位**:pre-stage 角色装载层。**不是第 14 个 stage**,不进 13 stage 状态机,不产生状态卡流转。
> 唯一职责:会话启动时把"贾维斯门禁守护协议"注入主上下文,并做 hash 锁存在性检查。

---

## 启动流程(会话第一步)

```
Step 1: 读 agents/jarvis.md → 注入贾维斯角色协议(白名单 + 3 时机)
Step 2: hash 锁检查
  ├─ 目标项目存在 gates/gate.lock.yaml?
  │   ├─ 存在 → python gate-integrity-guard.py --verify → PASS 才继续
  │   └─ 不存在(新项目)→ 时机①初始化:委派贾维斯跑 gate-installer
  └─ 任一 FAIL → 🛑 停止所有 stage 工作,先走 [JARVIS-DELEGATION] 审计
```

---

## 铁律(2 条)

```
1. JARVIS FIRST       — 任何 gate 配置/修改必先委派贾维斯,主 agent 和 13 stage 的所有 sub-agent 无权直改
2. LOCK BEFORE GATE   — 跑任何 gate 前必过 hash 锁校验;锁缺失/不匹配 = BLOCK(机械兜底,不信任任何 agent 自述)
```

---

## 关联引用

- [agents/jarvis.md](agents/jarvis.md) — 贾维斯 agent 定义(3 时机 + 分层模型 + 白名单)
- [gate-configuration-protocol.md](../../references/gate-configuration-protocol.md) — 调用方 7 步 SOP
- [scripts/gate-installer.py](../../scripts/gate-installer.py) — 时机①安装器
- [scripts/gate-integrity-guard.py](../../scripts/gate-integrity-guard.py) — 时机②hash 锁
