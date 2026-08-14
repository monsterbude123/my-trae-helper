# 维度 4：边际维度（20%） + 主动证伪 + 失败标签 + 自动循环 — four-dim-acceptance.md 详情

> 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
> 来源：原 four-dim-acceptance.md 第 54-167 行（保留信息密度）

---

## 边际维度（4 项 GitNexus 检查 — V10 完整版）

> 蒸馏自 V10 reviewer-templates.md §边际检查。原 V11 仅 1 字段 `gitnexus_impact`，**严重失真**。

### 4 项检查清单

```
[ ] 1. GitNexus detect_changes() → 附 detect_changes 输出
[ ] 2. 检查公共模块变更的影响面 → 附 impact() 输出
[ ] 3. 确认无意外副作用（其他模块测试仍全绿）→ 附全量回归日志
[ ] 4. 模块接入文档完整 → 附文档路径 + 关键段
```

### 详细协议

#### 检查 1: GitNexus detect_changes()

```python
mcp__gitnexus__detect_changes(scope="compare", base_ref="main")
# 必含: 与 main 的 diff 列表 + 冲突风险
```

输出：
- `changed_symbols`: 变更的符号清单
- `conflict_risk`: 与其他 PR 的冲突

#### 检查 2: GitNexus impact() 公共模块影响面

```python
# 对每个 changed_symbol 跑 impact
for symbol in detect_changes.changed_symbols:
    mcp__gitnexus__impact(target=symbol, direction="downstream")
```

判断：
- **公共模块（≥10 个下游调用者）**: 必逐个评估副作用
- **私有模块**: 抽样 3 个调用者

#### 检查 3: 全量回归日志

```bash
# 必跑全量回归（不仅是新加测试）
npm run test:all  # 或 pytest / cargo test
# 附: exit code + 测试结果 + 失败详情
```

禁止：用"测了新代码 + 几个老测试"充当"全量回归"。

#### 检查 4: 模块接入文档

```bash
ls docs/modules/{changed-module}.md  # 必存在
cat docs/modules/{changed-module}.md | head -30  # 附关键段
```

文档必含：
- 模块功能简述
- 公共 API 签名
- 依赖与上游
- 扩展点（Extension Points）

---

## 评分公式

```
总分 = (通过维度 / 适用维度) × 5.0
- 任一维度 0 分 = 🛑 REJECT
- 总分 ≥ 4.0 才 PASS
- N/A 不计入分母（不可验证才标 N/A + 理由）
```

---

## 主动证伪（高风险清单核查）

```yaml
falsification_checklist:
  - check: "边界遗漏"
    how: "测 0/1/max/null/空字符串/极大值"
  - check: "依赖污染"
    how: "检查 import 是否全在 pyproject.toml/package.json"
  - check: "未提交文件"
    how: "git status | grep untracked"
  - check: "隐藏 TODO"
    how: "grep -E 'TODO|FIXME|XXX' src/"
  - check: "测试篡改"
    how: "比对测试 commit + 验证断言非空"
  - check: "桩代码标记"
    how: "grep -E 'STUB|NotImplementedError' src/  # 必明确标识"
  - check: "公共模块副作用"
    how: "跑 GitNexus impact() 看下游调用者是否仍 PASS"
```

---

## 失败标签（Stage 2.6 自动循环）

| 标签 | 含义 |
|------|------|
| `MISMATCH` | 货不对版（功能与 spec 不符）|
| `UNDERPERFORM` | 功能不达标 |
| `USER_VIEW_FAIL` | 用户视角 FAIL |
| `TEST_GAP` | 测试覆盖缺口 |
| `DRIFT` | 代码与契约漂移 |

---

## 自动循环协议

```
Round 1: 退回 implementer 重做 + 失败标签必填
Round 2: 升级上报用户（5 字段阻塞报告）
Round 3+: rescue hatch — 回退 Phase 0（Intake）
```

---

## 关联引用

- 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
- four-dimension-scoring.md：[../../references/four-dimension-scoring.md](../../references/four-dimension-scoring.md)
- skeptical-acceptance.md：[../../references/skeptical-acceptance.md](../../references/skeptical-acceptance.md)
- multi-round-revision.md：[../../references/multi-round-revision.md](../../references/multi-round-revision.md)
- GitNexus 失败处理协议：[../../../references/gitnexus-retry-protocol.md](../../../../references/gitnexus-retry-protocol.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
