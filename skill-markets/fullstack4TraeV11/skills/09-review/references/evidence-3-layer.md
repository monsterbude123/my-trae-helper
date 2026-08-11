# 通过依据 3 类分层（Evidence 3-Layer）

> Stage 4 Review Step 0.5/1 必走。V10 acceptance-gates-v10.md §通过依据。

---

## 3 类证据

### [1] 后端/编译类

- ✅ vitest run: 50/50 PASS, exit 0
- ✅ cargo test: 30/30 PASS, exit 0
- ✅ tsc --noEmit: 0 error
- ✅ mypy: 0 error
- ✅ npm run build: success

### [2] UI 渲染类

- ✅ Playwright 截图 ≥1 张（≥5KB）→ docs/verifications/{change}/*.png
- ✅ 主上下文亲自 Read 像素验证
- ✅ PIL 解码 + 直方图校验通过
- ⚠️ 未跑 X（必须明说）

### [3] 用户视角类

- ⏳ 用户尚未启动 dev server 验收
- ⏳ 闭环未获用户签字
- 📋 必含：用户验收待办

---

## 通过依据完整性

```
[1] 后端/编译类: ✓ 通过
[2] UI 渲染类: ✓ 通过
[3] 用户视角类: ⏳ 待用户验收

结论: [1] 通过, [2] 通过, [3] 待办 → 不能声称"完成"
下一步: 邀请用户启动 dev server 验收
```

**反模式**: [3] 类未签字就声称"完成"。

---

## 反例

### 反例 A：只用 [1] 充数

```
[1] 后端: ✓ vitest 50/50
[2] UI: ⚠️ 未跑（"截图不在本次范围"）
[3] 用户: ⏳ 待办

→ 声称"完成"  # ❌ V10 视觉证据铁律
正确: UI 任务必含 [2] + [3]
```

### 反例 B：编造 [2] 证据

```
[2] UI: ✓ Playwright 截图已生成  # ❌ 子代理声称但主上下文未 Read
正确: 主上下文亲自 Read 截图 → 像素验证
```

---

## 关联引用

- [SKILL.md §铁律 8](../SKILL.md) — CROSS-SESSION VERIFY
- [four-dimension-scoring.md](four-dimension-scoring.md)
- V10 acceptance-gates-v10.md: `V10 来源` (已蒸馏到本文档)
