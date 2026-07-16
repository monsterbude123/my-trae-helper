# 上下文经济（Context Economy）

> V9.8 — 根因：上下文浪费来自结构缺失（单文件肥大、缺父文件摘要），不是来自字数本身。
> 解决方案不是硬编码行数/字数，而是**体量自适应拆分**（见 [progressive-disclosure.md](progressive-disclosure.md)）。
> 本文件定义读取纪律和行为约束。数字是参考，结构是铁律。

---

## §1 读文件纪律（主上下文 + 子代理通用）

```
读前判断: 这个工件的父文件存在吗？
  ├── 存在（如 proposal.md + proposal/why.md）→ 先读父文件（永远小）
  │    读完父文件 2 分钟内理清全景
  │    需要细节 → 读对应子文件
  │    不需要 → 不读
  └── 不存在（单文件模式）→ 先 Grep 摘要段（## N. 段名）
     看完摘要再决定是否深入

读时纪律:
  ✅ 父文件优先: 先读 index/summary 文件，再按需读子文件
  ✅ 按需深入: 需要哪段读哪段（Grep 定位 + Read 限定范围）
  ❌ 禁止预加载: 开工前不要全量读所有子文件
  ❌ 禁止回读: 同一文件不读第二遍（除非 agent 更新了它 → 机械验证重读例外）

适用对象:
  主上下文 + 所有子 agent 均遵循此纪律。
  子 agent 额外遵循 [minimum-knowledge.md](minimum-knowledge.md) 的 MUST/ON-DEMAND/DON'T 对照表。
```

---

## §2 主上下文委派 prompt 纪律

```
委派任何子代理时:
  1. 任务描述: 只写增量（背景已在上游工件里），约 200 字符
  2. 注入模板: 引用路径 + agent 名，不内联全文
     正确: "注入 implementer 模板 → delegation-injection-template.md §implementer"
     错误: 把 MUST 列表铺在 prompt 里
  3. 上下文: 传文件路径列表，不传文件内容
  4. prompt 保持在可管理范围内（约 1KB）
```

---

## §3 主上下文汇报纪律

```
用户汇报原则 — 变化点驱动:
  ✅ 状态有变化 → 1句结论 + 1句证据
  ✅ 状态无变化 → "状态不变，{当前阶段}，无阻塞"
  ❌ 禁止每次回复列"已完成清单 + 当前状态 + 红旗表 + 闭环表"
  ❌ 禁止大表格（5红旗/6闭环/7维度 全展开）

阶段切换汇报模板:
  "{Phase N} → {Phase N+1} | 通过: {关键门禁} | 下一步: {委派谁做什么}"
  + 1 行 diff stat（如有代码变更）
```

---

## §4 TodoWrite 纪律

```
✅ 只在以下时机更新 TodoWrite:
  - 阶段切换（Phase N → Phase N+1）
  - 用户明确要求
  - 新增未规划的阻塞项

❌ 禁止每步操作都更新 TodoWrite
❌ 禁止在并行工具调用批次中单独插入 TodoWrite

批操作原则: 一组 3-5 个并行工具调用完成后，批量标记已完成。
```

---

## §5 子代理 Completion Report 纪律

> 详见 [completion-report-protocol.md](completion-report-protocol.md) §二·0

```
✅ Completion Report 保持紧凑（约 800 字符）
✅ 代码在产出文件里，Report 引用路径即可
❌ 禁止在 Report 中重复任务描述或注入模板内容
```
