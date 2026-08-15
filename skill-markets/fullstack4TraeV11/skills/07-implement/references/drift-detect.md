# 漂移检测（Drift Detect）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 3 Implement Step 3 DRIFT CHECK 必走。V10 implementer 铁律 3 + drift-detect.md 蒸馏。

---

## GitNexus 影响面三步（V10 NEW — 防 API 契约改动漏下游）

> 来源：V10 references/drift-detect.md §"改 API 契约前 GitNexus impact 三步"。
> **V11 缺失关键步骤**：原 V11 drift-detect.md 仅含字段级漂移检测，无 API 契约改动的下游影响追踪。

### 三步协议

```
Step 1 GitNexus impact() 找所有调用点
  impact({target, direction: "upstream"}) 找上游 / impact({target, direction: "downstream"}) 找下游 / context({name}) 查看 360 度视图
  禁止: 用 grep/glob 代替 impact() 找调用点

Step 2 评估影响范围
  ├─ 公共 API（≥10 个调用者）→ 必通知所有下游 + 评估 breaking change
  ├─ 私有 API（< 10 个调用者）→ 抽样评估 3 个 + 通知作者
  └─ 内部 API → 改完后跑全量回归

Step 3 写漂移测试
  ├─ 为每个 changed symbol 加测试
  ├─ 改 caller 测试（如果签名变化）
  └─ 必含: 旧行为兼容（如允许）/ 新行为（如有）
```

### 反例（V11 Article V 必走）

```
❌ 改 API 契约前不跑 GitNexus impact()
  现象: implementer 改了 API 签名 → 没跑 impact() → 下游 5 个调用者编译失败
  根因: 跳过 GitNexus 三步协议
  教训: 改 API 契约必须 GitNexus impact() 找所有调用点 + 写漂移测试
```

---

## DRIFT CHECK 流程

```
🔍 DRIFT CHECK 触发时机:
  ├─ 每完成 1 个 TDD 循环后
  ├─ 提交前
  └─ Stage 4 Review 前
  ↓
对照 contracts/ 验证:
  ├─ 接口签名一致？（method / path / params）
  ├─ 字段类型一致？（string / number / bool）
  ├─ 错误码一致？（V10 D-009 错误码规范）
  ├─ 必填字段一致？
  └─ 鉴权要求一致？
  ↓
任一不一致 → 立即报告回流（不静默修改）
```

---

## 漂移处置流程

```
检测到漂移:
  ├─ 是契约问题（契约与 spec 不一致）？
  │   └─ 是 → 报告用户 → 更新契约（走 BREAKING 流程）
  └─ 是实现问题（代码与契约不一致）？
      └─ 是 → 立即修代码（不改契约）
```

**V10 铁律 3**: 漂移必报告，禁止静默。

---

## DRIFT CHECK 工具

```bash
# 自动检测接口签名漂移
# 注意: drift-detect.py 是 hook 模板(V11 templates/hooks/),需先通过 init-from-zero.py 安装到项目 .trae/hooks/ 后才能直接调用
# V11 skill 内调用方式(开发期):
python ../../templates/hooks/drift-detect.py --contracts contracts/ --src src/
# 项目实际调用方式(已 init-from-zero 安装后):
python .trae/hooks/drift-detect.py --contracts contracts/ --src src/

# 输出
{
  "drift_count": 3,
  "drifts": [
    {
      "contract": "POST /api/v1/auth/login",
      "field": "password",
      "contract_type": "string",
      "code_type": "any",
      "severity": "high"
    }
  ]
}
```

---

## 反例

### 反例 A：静默修改契约

```
实现改了接口 → 不更新契约文档 → 测试通过 → 上线后客户端报错
正确: 实现与契约不一致 → 报告用户 → 走 ADDITIVE/BREAKING 流程
```

### 反例 B：契约与代码双向漂移

```
契约改了 → 实现未跟进 → 测试通过（mock）→ 上线后真实环境失败
正确: 契约修改必同步代码 + 测试（V10 配置治理 D-009 三方同步）
```

---

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — 漂移必报告
- [tdd-workflow.md](tdd-workflow.md)
- V10 drift-detect.md: `V10 来源` (已蒸馏到本文档)
