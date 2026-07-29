# 流程腐烂分析报告

> 系统推演全部流程，识别"历史残留污染新决策"的腐烂点。与 activeBar 案例同根。

---

## 腐烂点 7（NEW）：外部结构冲突 — 多技能并存时的双重真相

**场景**：项目同时使用 V9.2 和另一个技能包，产生冲突目录结构：

```
V9.2 期望:                    外部结构:
docs/specs/{feature}/         specs/{feats}/
├── define.md                 ├── plan.md          ← 同义冲突
├── contracts/                ├── contracts/
│   ├── api-contracts.md      │   └── api-spec.json  ← 格式冲突
│   ├── domain-models.md      └── data-model.md       ← 同义+路径冲突
│   └── events.md
└── tasks.md                  └── tasks.md            ← 同名但格式不同
```

**腐烂路径**:
```
项目初始化时同时安装了多个技能包
  ↓
技能 A 按 specs/{feats}/ 创建 plan.md + data-model.md
技能 B（V9.2）按 docs/specs/{feature}/ 创建 define.md + contracts/
  ↓
同一事实存在两个位置:
  - plan.md 和 define.md 描述同一个实现方案
  - data-model.md 和 domain-models.md 描述同一个数据模型
  ↓
agent 在不同阶段读取不同文件:
  - definer 读 define.md → 版本 A
  - 外部 agent 读 plan.md → 版本 B
  ↓
双重真相 → 实现分裂 → 验收混乱
```

**判定矩阵**:

| 外部文件 | V9.2 对应 | 冲突类型 | 腐烂风险 |
|---------|----------|---------|:---:|
| `plan.md` | `define.md` | 同义不同名 | HIGH — agent 找不到 define.md 就仿造 |
| `data-model.md` | `contracts/domain-models.md` | 同义+路径错 | HIGH — 两个位置描述同一模型 |
| `api-spec.json` | `contracts/api-contracts.md` | 同义+格式错 | MEDIUM — JSON vs MD 不可互操作 |
| `quickstart.md` | 无 | 无冲突 | LOW — 纯文档，无害 |

**修复**: intake 增加结构兼容检测 → 发现外部结构 → 标注 + 建议归一。不强行转换，不静默忽略。

## 腐烂点 1（HIGH）：Intake 去重 _invalidated_ 盲区

**当前代码**（[intake.md](file:///d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV9/agents/intake.md#L52)）:
```
查 docs/specs/ 下是否有重叠的已有 Spec
查 archive/done/ 是否有已完成的同名功能
```

**腐烂路径**:
```
feature-A 被重置 → 全量进 _invalidated/
  ↓
用户提出新需求（恰好跟 feature-A 有 60% 重叠）
  ↓
intake 扫描 docs/specs/ → 发现 feature-A/spec.md 仍在 _invalidated/ 中
  ↓
判定 "60% 重叠 → 合并" → 错误地把新需求合并到已废弃的 feature
```

**修复**: intake dedup 必须 **排除 `_invalidated/` 和 `archive/`**，只扫描活跃 spec。

---

## 腐烂点 2（HIGH）：change-status.py _invalidated_ 盲区

**当前代码**（[change-status.py](file:///d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV9/scripts/change-status.py#L71)）:
直接读文件系统，不知道 `_invalidated/` 存在。

**腐烂路径**:
```
feature-A/_invalidated/ 中有旧的 define.md（标记 tasks 全 [x]）
  ↓
change-status.py 主目录有新 define.md（全 [ ]）
  ↓
输出: 状态正确 ← 这没问题
  
但:
feature-A/_invalidated/ 中有旧 spec.md（已 merge）
  ↓
feature-A/spec.md 在重新编写中（不完整）
  ↓
change-status.py 仍然报告 spec done = true（读到了主目录的老 spec）
  ↓
实际上 spec 还是旧的，应该报告 "⚠️ spec 待重写（_invalidated/ 中可能有旧版干扰）"
```

**修复**: change-status.py 检测 `_invalidated/` 存在 → 标注 `reset_mode: true`，提醒调用方。

---

## 腐烂点 3（RESOLVED）：Implementer L1 重做 — 旧代码残留

> **用户判定：不删除。agent 知道自己在重构，按新 spec 改代码是正常实现流程，删除旧代码是结果而非前置步骤。** implementer 唯一需要的是不读取 `_invalidated/` 中的旧状态。

**修复**: 回流隔离只控制文档（_invalidated/），不主动操作源码。重构=按新 spec 改代码。

---

## 腐烂点 4（MEDIUM）：L3 规格重写 → 旧契约残留

**腐烂路径**:
```
spec 问题 → L3 rework → spec-writer 重写 spec
  ↓
contract-writer "续写非重写" → 看到已有 contracts/api-contracts.md
  ↓
在旧的 approved 契约上追加新接口
  ↓
旧接口可能已经被 spec REMOVED 标记，但 contract 还在
  ↓
implementer 根据 contract 实现了已废弃的接口
```

**修复**: contract-writer 必须检测 spec 中是否有 MODIFIED/REMOVED，对应更新或删除契约条目。

---

## 腐烂点 5（LOW）：变更后旧 test 文件残留

**腐烂路径**:
```
feature-A 的 contracts/ 变更 → implementer 写了新契约测试
  ↓
旧契约测试没被删除（测试文件在 __tests__/contracts/ 中）
  ↓
CI 运行 → 旧测试 FAIL（因为 API 已变）
  ↓
implementer 花时间调查 → 发现是旧测试 → 浪费时间
```

**修复**: implementer 在完成时检查 __tests__/ 中是否有 orphan 测试文件。

---

## 腐烂点 6（LOW）：_invalidated/ 嵌套

**腐烂路径**:
```
第一次重置: _invalidated/20260721-1000/
  ↓
第二次重置: _invalidated/20260721-1400/
  ↓
_invalidated/ 深层嵌套，文件数激增
  ↓
agent 扫描 docs/specs/ 时意外读到 _invalidated/ 内容
```

**修复**: _invalidated/ 只保留最近 3 次重置，超过的移到 archive/out/。

---

## 修复优先级

| # | 严重度 | 腐烂点 | 修复方向 |
|---|:---:|------|---------|
| 1 | HIGH | intake dedup 盲区 | 去重排除 _invalidated/ + archive/ |
| 2 | HIGH | change-status.py 盲区 | 检测 _invalidated/ → reset_mode |
| 3 | RESOLVED | implementer 旧代码残留 | 不删源码；agent 按新 spec 改代码是正常流程 |
| 4 | MEDIUM | contract-writer 旧契约残留 | 检测 MODIFIED/REMOVED → 更新契约 |
| 5 | LOW | 孤儿测试文件 | contract-writer 完成时清理 |
| 6 | LOW | _invalidated/ 膨胀 | 只保留 3 次，多余归档 |
| 7 | HIGH | 外部结构冲突 | intake 结构检测 + 归一建议 |
