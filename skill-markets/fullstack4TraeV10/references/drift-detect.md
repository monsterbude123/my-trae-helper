# 漂移检测 + 回流

> 发现规格/契约/代码不一致时，立即报告回流。
> ADDITIVE/BREAKING 契约变更流程。

---

## 漂移类型

| 类型 | 描述 | 触发者 |
|------|------|--------|
| Spec 漂移 | Spec 描述与实际需求不一致 | implementer |
| 契约漂移 | 代码实现与 Contract 四件套不一致 | reviewer |
| 文档漂移 | 模块文档与代码实现不一致 | DOC SYNC 自检 |
| 目标漂移 | 用户需求在开发中发生变化 | 用户中途修改 |

---

## 严重度判定

| 等级 | 条件 | 行动 |
|------|------|------|
| LOW | 注释/命名不一致 | 直接修复 |
| MEDIUM | 接口参数变更 | 通知用户确认后更新 |
| HIGH | 核心逻辑变更 | 🛑 停止开发，回流上游 |

---

## 回流判定树

```
发现漂移
  │
  ├── Spec 漂移 → 回流 spec-writer
  │    重走: Spec → Contract → Implement → Review
  │
  ├── 契约漂移 → 回流 contract-writer
  │    重走: Contract → Implement → Review
  │
  ├── 文档漂移 → DOC SYNC 修复
  │    不回流，reviewer 直接同步文档
  │
  └── 目标漂移 → 回流 Intake
       全链重走: Intake → Define → Spec → Contract → Implement → Review

同一 change Review FAIL 3 次 → 🛑 标记 🔴 高风险，汇报用户
```

---

## 契约变更流程（ADDITIVE / BREAKING）

```
需要改 approved 契约
    │
    ├── ADDITIVE（兼容 — 新增可选字段/接口/枚举值）
    │     直接添加 → 更新契约版本（minor）
    │
    └── BREAKING（不兼容 — 删字段/改类型/改路径/删枚举值）
         🛑 必须用户显式确认
         确认后 → 更新契约版本（major）→ 回流下游全链
```

---

## 禁止行为

- ❌ 发现漂移后静默迁就
- ❌ 绕过回流直接编码
- ❌ 修改测试掩盖漂移
- ❌ 单方面修改 approved 契约（必须走 ADDITIVE/BREAKING 流程）
- ❌ 改 API 契约前不跑 GitNexus impact()（V10.8 NEW，详见下方三步）

---

## 契约漂移检测三步（V10.8 NEW）

> Implementer 改 API 契约时强制执行。来源: agent-delegation-discipline/references/contract-drift-detection.md。
> **触发条件**: 改后端 API 响应结构 / 改前端 API 调用参数 / 改 DB schema / 改事件 payload。

```
Step 1 GitNexus impact() 找所有调用点
  impact({target, direction: "upstream"}) 找上游 / impact({target, direction: "downstream"}) 找下游 / context({name}) 查看 360 度视图
  禁止: 用 grep/glob 代替 impact() 找调用点

Step 2 逐个检查调用点是否同步修改
  后端改字段名/类型/新增/删除 → 前端是否同步改/适配/移除引用？
  任一答 N → 契约漂移风险

Step 3 写漂移测试（mock 后端新契约）
  mock 后端新响应 → 验证前端解析正确（字段映射 / 空数组 / undefined 防御）→ 测试 PASS 才可提交
```

### 反例: 字段对齐漏改一处
```
现象: 后端多端点统一 data.items，前端仍期望 data.models，页面白屏
根因: 字段对齐时漏改一处调用，未跑 impact() 找所有调用点
教训: 改 API 契约必须 GitNexus impact() 找所有调用点 + 写漂移测试
```
