# 反例 3：重构不 purge

> 重构场景必走 spec-purge.py 清除旧产物。跳过 = 旧产物污染 + 后续 spec.md 漂移。

## 现象

```
用户: "重构 auth 模块"
主上下文: 立即进入 Stage 1 Spec → 直接覆盖旧 auth spec  # ❌
```

**识别信号**:
- plan.md 含 "重构" 但未调用 spec-purge.py
- 旧 auth 模块产物仍在 docs/specs/changes/{old-id}/（未隔离）
- 后续 Stage 1 Spec 直接覆盖旧 spec

## 根因

| 根因 | 占比 |
|------|:---:|
| 不知道重构场景需 purge | 60% |
| 觉得 purge 是"额外工作" | 30% |
| 误以为"重构 = 改代码" | 10% |

## 教训

**重构不 purge = 旧产物污染 + spec.md 漂移 + 归档不可追溯。**

真实案例:
- 重构 auth 模块未 purge → 旧 auth-spec 仍存在
- 新 spec.md 与旧 spec.md 内容冲突
- Stage 5 Accept 时无法判断"归档哪个" → 返工

## 正确替代

```
Step 4 (重构场景):
  ├─ python ../../scripts/spec-purge.py --feature {name} [--dry-run]
  ├─ 确认清除成功（dry-run 验证）
  ├─ 旧产物隔离到 _invalidated/
  └─ 当成全新需求，重新走 Step 3 探索
```

**MUST**: 重构场景 Step 4 必走 spec-purge.py。

**NEVER**: 重构直接覆盖旧产物。

## 检测方法

```yaml
checklist:
  - [ ] 意图类型 = 重构？
  - [ ] 调用了 spec-purge.py？
  - [ ] 旧产物已隔离（_invalidated/ 或 archive/done/）？
  - [ ] Plan.md 标注 "spec_purged: yes"？
```

任一未勾选（如适用）→ 触发本反例 → 回到 Step 4 重新 purge。

## spec-purge.py 用法

```bash
# Dry-run 验证
python ../../scripts/spec-purge.py --feature auth --dry-run

# 实际执行
python ../../scripts/spec-purge.py --feature auth

# 指定目标目录
python ../../scripts/spec-purge.py --feature auth --target docs/specs/changes/old-auth-id
```

**输出**: 旧 spec.md / contracts/ / plan.md 隔离到 `_invalidated/{timestamp}-auth/`。

## 关联引用

- [SKILL.md §铁律 5](../SKILL.md) — PURGE ON REFACTOR
- [README.md §完整骨架 Step 4](../README.md) — 重构场景 spec-purge
- spec-purge 脚本: ../../scripts/spec-purge.py（Task 17 编写）
