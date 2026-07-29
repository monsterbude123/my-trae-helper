# 流程腐烂分析报告 — V10 更新

> V10 变更：移除 _invalidated/ 隔离机制，替换为 spec-purge.py 机械归档。消除腐烂点 1/2/6。

---

## 腐烂点 7（HIGH）：外部结构冲突 — 多技能并存时的双重真相

**场景**：项目同时使用 V10 和另一个技能包，产生冲突目录结构。

**修复**: planner 增加结构兼容检测 → 发现外部结构 → 标注 + 建议归一。不强行转换，不静默忽略。

---

## 腐烂点 1（✅ RESOLVED — V10）：_invalidated_ 盲区

> **V10 解决**：移除 _invalidated/ 机制。spec-purge.py 物理删除目录 + 将旧产物归档到 archive/out/spec-purge/（Agent 不可读取）。去重只扫描活跃目录，无盲区。

---

## 腐烂点 2（✅ RESOLVED — V10）：change-status.py 盲区

> **V10 解决**：无 _invalidated/ → 无此问题。

---

## 腐烂点 3（RESOLVED）：Implementer L1 重做 — 旧代码残留

> **维持 V9 结论**：不删源码。agent 知道自己在重构，按新 spec 改代码是正常实现流程。

---

## 腐烂点 4（MEDIUM）：契约残留

**腐烂路径**:
```
spec 问题 → rework → spec-enhancer 增强 spec
  ↓
contract-writer "续写非重写" → 看到已有 contracts/
  ↓
在旧的 approved 契约上追加新接口
  ↓
旧接口可能已被 spec 废弃，但 contract 还在
```

**V10 修复**: contract-writer 必须检测旧契约 → 标注 MODIFIED 或 DEPRECATED。重构时 Planner 调 spec-purge.py 彻底清除。

---

## 腐烂点 5（LOW）：孤儿测试文件

**V10 保留修复**: contract-writer 完成时检查 __tests__/contracts/ → 移入 _deprecated/。

---

## 腐烂点 6（✅ RESOLVED — V10）：_invalidated/ 嵌套膨胀

> **V10 解决**：移除 _invalidated/。重构 = spec-purge.py 移动目录至 archive/out/spec-purge/，< 24h 的保留在工作目录外，无膨胀问题。

---

## 新增腐烂点 8（V10 引入 — LOW）：spec-purge.py 未执行

**腐烂路径**:
```
用户说"重构 XX" → Planner 应该调 spec-purge.py
  ↓
Planner 遗漏了 spec-purge → 直接在旧 spec 上 Plan
  ↓
旧 tasks 残留 [x] → 新一轮实现跳过部分 task
```

**V10 修复**: planner agent 铁律第 5 条强制 PURGE ON REFACTOR。主上下文机械验证 planner Completion Report 中 `spec_purged: yes`。

---

## 修复优先级（V10 更新）

| # | 严重度 | 腐烂点 | 修复方向 |
|---|:---:|------|---------|
| 1 | ✅ RESOLVED | _invalidated_ 盲区 (V9 #1) | spec-purge.py 替换 |
| 2 | ✅ RESOLVED | change-status.py 盲区 (V9 #2) | 无 _invalidated_ |
| 3 | RESOLVED | implementer 旧代码残留 (V9 #3) | 不删源码 |
| 4 | MEDIUM | 契约残留 (V9 #4) | contract-writer 检测 + spec-purge |
| 5 | LOW | 孤儿测试文件 (V9 #5) | contract-writer 清理 |
| 6 | ✅ RESOLVED | _invalidated_ 膨胀 (V9 #6) | spec-purge.py |
| 7 | HIGH | 外部结构冲突 (V9 #7) | planner 结构检测 |
| 8 | LOW | spec-purge 未执行 (NEW) | planner 铁律 + 机械验证 |
