# Acceptance Baseline Extract — Stage 4 Review Step -2

> Stage 4 Review 必走(V11.6.0 NEW)。验收基准提取协议 — **先有基准,再验收;无基准 = BLOCK,禁止退回默认清单**。
>
> 定位:把 Step -2"拆解验收基准"从口号落地为 Guard 层输入。产出物直接供 [ac-gate.py](../../../scripts/ac-gate.py) 机械判定。

---

## 原则

```
验收基准 = spec.md 的 AC 全集 + ui-ux-logic.md 的交互流全集 + test-plan.md 的 TC 映射
验收 = 逐 AC 核销(PASS/FAIL),不是评分。
无基准 → BLOCK(exit ≠ 0),不是"默认按 4 维通用清单评"。
```

## 流程(4 步)

```
Step 1: 读 docs/specs/changes/{id}/spec.md → 提取 AC 全集
  ├─ 5 类 AC(功能/非功能/错误/兼容/集成)
  └─ UI 交互 AC(AC-UI-*,引用 ui-ux-logic 交互流,必含)

Step 2: 读 prototypes/ui-ux-logic.md → 提取交互流全集
  ├─ 每个"流 N"至少对应 1 条 AC(无 AC 的交互流 = 基准缺口 → 补 AC 或删流)
  └─ 错误与边界处理表声明的状态 → 决定附加 UI 检查范围(声明才查)

Step 3: 读 test-plan.md → 校验 TC ↔ AC 强映射
  ├─ 每个 AC 至少 1 个 TC(映射字段必须是 AC-ID,禁止自由文本)
  └─ 无 TC 的 AC → 基准缺口(退回 Stage 0.5 补,不是放宽验收)

Step 4: 产出验收基准清单 → 写入 review-report.md "## AC 核销矩阵"
  ├─ 列: AC-ID | 类型 | TC-ID | TC结果 | UI证据 | 状态
  ├─ 类型: API / UIUX / INV / EC(错误) / PERF(非功能)
  └─ 状态仅 ✅ / ❌(TC PASS + 证据齐全 = ✅;否则 ❌)
```

## UI 交互 AC 模板(第 6 类,V11.6.0 NEW)

```yaml
AC-UI-1: 新增按钮可见并触发新增
  given: "列表页加载完成"
  when: "用户点击 Header 右侧'新增'按钮"
  then:
    - "弹出新增表单(ui-ux-logic 流-1)"
    - "提交后 POST /items 返回 201(TC-001)"
    - "列表刷新且含新条目(TC-010, E2E)"
  ui_flow_ref: "ui-ux-logic.md#流-1"
```

## 判定(与 ac-gate.py 一致)

| 情形 | 判定 |
|------|------|
| 基准清单 4 步任一步缺失/为空 | 🛑 BLOCK(退回上游补基准) |
| 矩阵某 AC 行 TC=FAIL 或 状态=❌ | 🛑 BLOCK + 失败标签 |
| spec 中 AC 未出现在矩阵 | 🛑 BLOCK(漏核销) |
| 矩阵 TC 不存在于 test-plan | 🛑 BLOCK(编造测试) |
| 全部 AC ✅ | 🟢 GATE PASS |

## 门禁执行

```bash
python scripts/ac-gate.py \
  --review-report docs/specs/changes/{id}/review-report.md \
  --spec docs/specs/changes/{id}/spec.md \
  --test-plan docs/specs/changes/{id}/test-plan.md
```

## 反例

### 反例 A:无基准默认评

```
spec 缺 AC → 拿 4 维通用清单评 → 出分  # ❌ "没有标准"逼出"僵硬标准"
正确: 基准缺失 = BLOCK,退回 Stage 1 Spec 补 AC
```

### 反例 B:AC 核销映射用自由文本

```
acceptance_dimension: "正确凭据可登录"  # ❌ 无法机械追溯
正确: ac: AC-1(AC-ID 强映射,ac-gate.py G4/G5 可断言)
```

## 关联引用

- [SKILL.md](../SKILL.md) — Step -2 / Step 3
- [ac-gate.py](../../../scripts/ac-gate.py) — 机械判定(G1-G5)
- [review-report-template.md](../templates/review-report-template.md) — 核销矩阵模板
- [ui-ux-logic.md](../../05-prototype/templates/ui-ux-logic.md) — 交互流来源
