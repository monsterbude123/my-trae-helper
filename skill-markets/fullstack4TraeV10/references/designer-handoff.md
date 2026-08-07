# Designer ↔ 主上下文 ↔ spec-writer 交接协议

> 触发条件：项目有外部 Designer（人用 Trae Work 或其他工具）交付 HTML 原型页面。
> 本协议定义交接流程、职责矩阵、关键规则。**此为参考文档，非可委派 Agent。**

---

## §1 职责矩阵

| 角色 | 何时进入 | 输入 | 输出 | 退出标准 |
|------|---------|------|------|---------|
| **Designer**（外部） | Phase 1 Define 通过后 | define.md + 视觉源指引 | `design/*.html` 页面文件 | HTML 交付 + 主页面选定 |
| **主上下文** | Designer 交付 HTML 后 | HTML 文件 + define.md | HANDOFF 索引更新 + 缺失清单 + 触发 spec-writer | HANDOFF 完备 + 每个 spec 的 HTML 都已判定 |
| **spec-writer** | spec.md 编写前 | define.md + HTML + prototypes/（占位或完整） | `prototypes/design-prompt.md` + `ui-ux-logic.md`（含 §1 章节） | [prototype-linkage.md](prototype-linkage.md) §1.3 校验 5 条通过 |

---

## §2 关键规则

### 2.1 Designer 交付要求

```
MUST: HTML <title> 标签包含「模块名 — 产品名」格式（机械识别依赖此格式）
MUST: 每个业务页面对应一个 .html 文件，子组件可独立或内嵌
推荐: 交付时附带页面清单（文件名 + <title> + 一句话用途）
```

### 2.2 主上下文职责

```
MUST: 维护 HANDOFF 索引（HTML 文件 ↔ spec 的双向映射）
MUST: 检测缺失并生成清单（spec 有但无 HTML / HTML 有但无 spec）
MUST: 触发 spec-writer 前注入 §5.0 检查（外部 HTML 交接确认）
NEVER: 主上下文不写 prototypes/ 内容（只创建占位目录 + Stub 文件）
NEVER: 主上下文不替代 spec-writer 写 design-prompt.md / ui-ux-logic.md 正文
```

### 2.3 spec-writer 强制协议

```
MUST: 涉及 UI + 项目有外部 Designer HTML → 先查 HANDOFF 索引
MUST: 每份 prototypes/ 文件写入「## 引用的 HTML 文件」章节（prototype-linkage.md §1）
MUST: HTML 未交付 → 标记 P0 Stub，不强制产出完整原型
NEVER: 假设 HTML 对应关系（必须从 HANDOFF 索引查询，不可猜测）
```

---

## §3 交接流程

```
Phase 1: Define ✅（define.md 含 UI 声明）
  ↓
Designer 交付 HTML（外部，异步）
  ├─ Designer 交付 HTML 页面 + 清单
  ├─ 主上下文解析 <title> → 判定每个 HTML 的归属 spec
  ├─ 更新 HANDOFF 索引
  └─ 生成缺失清单（spec 缺 HTML → P2 / HTML 缺 spec → 需评估）
  ↓
主上下文触发 spec-writer
  ├─ 注入 §5.0 检查
  ├─ spec-writer 查 HANDOFF 索引 → 确认每个 spec 的 HTML 状态
  ├─ 完整 → 正常产出 prototypes/ + §1 章节
  └─ Stub → 产出占位文件 + P0 阻塞标记
  ↓
Phase 2: Spec 正常继续
```

---

## §4 HANDOFF 索引格式

```
项目级约定（V10）: 项目在 docs/specs/ 或项目根目录维护 HANDOFF-DESIGNER.md

> V8 残留路径: docs/prototypes/HANDOFF-DESIGNER.md（已废弃，不应使用）
> V10 项目应在 docs/specs/HANDOFF-DESIGNER.md 或自定义项目级位置维护索引

内容:
  §1 索引表（HTML 文件名 → spec 映射）
  §2 完整列表（prototypes/ 全部就位的 spec）
  §3 缺失清单
    §3.1 P0 Stub（spec 有 + HTML 有 + prototypes/ 缺）
    §3.2 P2 反向缺失（spec 有 + HTML 无）
  §4 更新日志（每次 Designer 交付或主上下文重排后 +1 条）
```

---

## §5 禁止项

- 禁止主上下文绕过 HANDOFF 索引直接触发 spec-writer（外部 Designer 场景）
- 禁止 spec-writer 在 §5.0 检查未通过时开始写原型内容
- 禁止将 HANDOFF 索引与项目级 INDEX.md 混淆（前者管 HTML↔spec 映射，后者管 Spec 全景）
