# 编码规范 — {项目名}

> 本文档记录**项目特定**的编码铁律。
> 通用规范（≤800 行/函数 ≤50 行/无魔法数字/hash 大小写/GitNexus impact/datetime 兼容/子代理产物验证）已由 V11 skill 内部吸收（`references/common-iron-rules.md` Article I-VII），此处不重复。
>
> **本文件只放项目独有的编码规则**——agent 按项目实际情况配置,无项目独有规则则不创建本文件。

---

## §1 桩代码标记规范（示例 — 有未实现功能时必用）

### 铁律

```
MUST: 桩代码必须返回明确错误: "STUB: 功能未实现"
  ├─ 不要返回模糊错误: "not supported in phase 2"
  └─ 不要返回看起来像真实错误的错误

MUST: 桩代码必须在文档中明确标注
  ├─ 代码注释: "// STUB: 功能未实现，预计 Phase X 完成"
  └─ API 文档: "⚠️ 此端点为桩实现，不可用于生产"
```

### 反例

```
// 错误: 模糊错误 — 用户以为是真实错误，反复重试
async fn handle_hash(...) -> Result<TaskResult, TaskError> {
    Err(TaskError::Handler("hash lookup not supported in phase 2".into()))
}

// 正确: 明确标记 — 用户知道是桩,不会重试
async fn handle_hash(...) -> Result<TaskResult, TaskError> {
    // STUB: hash 反查未实现，预计 Phase X 完成
    Err(TaskError::Handler(
        "STUB: hash lookup not implemented yet. Use URL mode for now.".into()
    ))
}
```

### 适用场景

- 任何未实现的功能
- 任何占位符代码
- 任何分阶段交付标记的代码

### 合规豁免（@deprecated 保留 — 不视为违规）

```
ALLOWED: 已标注 @deprecated 但保留原因明确的代码 = 合规桩代码模式
  ├─ 必须含 "保留原因" / "fallback" / "compatible" 任一关键字
  ├─ orphan-detector / lint 应豁免此类警告（不是死代码，是版本兼容层）
  └─ 触发删除条件: 上游组件迁移完成才允许删

正例:
  - Model interface @deprecated → 注释含 "保留原因" + "升级计划"
  - AssetsPage @deprecated → 注释含 "保留为路由 fallback"

反例:
  - 仅 @deprecated 无保留原因说明 → 视为死代码，必须删除或补全说明
```

---

## §2 项目独有规则（示例 — 按项目实际填充）

> 此处放项目独有的、V11 通用规范未覆盖的编码规则。
> 无项目独有规则则删除本节。

### 示例 A: 数据模型重复判定（如有去重需求）

```
- blake3 和 sha256 都非空且都匹配才算同一记录
- 只有 blake3 重复时才激活 sha256 比较
- 所有路径操作的代码必须进行路径合法性检查
```

### 示例 B: API 响应格式（如有统一格式）

```
MUST: 所有 API 响应统一格式
  ├─ 成功: { code: 0, data: {...}, message: "ok" }
  ├─ 失败: { code: {非0}, data: null, message: "{具体错误}" }
  └─ 分页: { code: 0, data: { list: [...], total: N, page: P }, message: "ok" }
```

### 示例 C: 前端组件命名（如有命名约定）

```
- 组件文件名: PascalCase (如 UserProfile.tsx)
- 组件导出: named export (不用 default export)
- Props 类型: 独立 type 文件 (如 UserProfile.types.ts)
- 样式: CSS Modules (如 UserProfile.module.css)
```

---

## §3 禁止项（项目特定 — 按项目实际填充）

```
❌ {项目特有的禁止编码行为 1}
❌ {项目特有的禁止编码行为 2}
```

---

## 关联引用

- [V11 common-iron-rules.md Article I-VII](../../references/common-iron-rules.md) — 通用编码规范（不重复）
- [V11 dependency-config.md](../../references/dependency-config.md) — L0-L4 硬编码治理
- [stack.md](stack.md) — 构建/测试/lint 命令
