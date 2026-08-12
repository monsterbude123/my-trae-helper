# 反例 4：契约漂移（Contract Drift）

> 代码改了契约字段（加 role / 改类型），契约文档 / 测试未同步 = spec 失真 + Stage 4 Review REJECT + 下游客户端崩溃。

**违反**：铁律 10（THREE-WAY SYNC）
**严重度**：P1（直接导致 Stage 4 Review REJECT + 下游契约失真）

---

## 现象

```python
# 代码（src/user/create.py）
def create_user(name: str, email: str, role: str):  # ← 新增 role 参数
    user = User(name=name, email=email, role=role)
    db.save(user)
    return user

# api-contracts.md（未同步）
POST /api/users
request: { name, email }              # ❌ 反例：契约无 role 字段
response: { id, name, email, created_at }

# tests/contracts/test_user.py（未同步）
def test_create_user():
    response = api.create_user(name="alice", email="a@b.com")
    # ❌ 反例：测试无 role 参数
    assert response.name == "alice"
```

**识别信号**:
- 代码改了契约（参数 / 字段 / 类型），契约文档未同步
- drift-detect.py 报告三方不一致
- 下游客户端按旧契约调用 → 缺字段 / 类型错误
- Stage 4 Review 三方同步检查失败 → REJECT

---

## 根因

- **认知维度**：改代码时未回头看契约文档
- **流程维度**：跳过 drift-detect.py 验证
- **责任维度**：implementer 改了 API 但未通知 contract-writer

| 根因 | 占比 |
|------|:---:|
| 改代码时不看契约文档（无回顾习惯）| 50% |
| 跳过 drift-detect.py 验证 | 30% |
| implementer 改 API 未通知 contract-writer | 20% |

---

## 教训

- **V11 实战**：implementer 在 `create_user` 加了 `role` 参数（"业务需要"），但契约文档 / 测试未改。下游客户端按旧契约调用 → 服务端缺 role → 报错 → 2 天排错才发现契约漂移
- **真实场景**：代码改 `age: int` 为 `age: string`（"为了支持 '18岁'"），契约文档未改 → 前端按 int 处理 → 永远拿不到正确值 → 用户年龄显示错乱
- **字段重命名反例**：代码改 `username` 为 `user_name`，契约文档未改 → 前端按 `username` 读 → undefined → 登录态丢失 → 用户大面积掉线

---

## 正确替代

```yaml
# ✅ 正确：修改契约必走 THREE-WAY SYNC

## Step 1: 改代码前必读契约

implementer 在改 API 前必读:
  - api-contracts.md（接口定义）
  - domain-models.md（领域模型）
  - tests/contracts/（契约测试）

发现问题（如契约缺失 / 漂移）→ 必先停下来同步
```

```yaml
## Step 2: 三方同步修改

# 1. 代码（src/user/create.py）
def create_user(name: str, email: str, role: str):
    user = User(name=name, email=email, role=role)
    db.save(user)
    return user

# 2. 契约文档（api-contracts.md）
POST /api/users
request: {
  name: string,
  email: string,
  role: enum['user','admin']  # ✅ 同步新增
}
response: { id, name, email, role, created_at }

# 3. 契约测试（tests/contracts/test_user.py）
def test_create_user_with_role():
    response = api.create_user(
        name="alice",
        email="a@b.com",
        role="admin"  # ✅ 同步新增
    )
    assert response.role == "admin"
```

```yaml
## Step 3: drift-detect.py 自动验证

python scripts/drift-detect.py
# 检查 code ↔ contract ↔ test 三方一致性
# 输出:
#   ✓ code::create_user(name, email, role)
#   ✓ contract::POST /api/users.request.role
#   ✓ test::test_create_user_with_role.role
#   Consistency: 100%  ← 必达

未达 100% → 🛑 禁止合并
```

```yaml
# ✅ drift-detect.py 检测逻辑

def detect_drift():
    """
    1. 扫描代码：提取函数签名（参数名 + 类型）
    2. 扫描契约：提取 API 定义（request / response 字段）
    3. 扫描测试：提取测试调用（传入的参数）
    4. 三方交叉对比 → 不一致 = drift
    """
    code_signatures = extract_code_signatures()        # 函数签名
    contract_fields = extract_contract_fields()        # 契约字段
    test_calls = extract_test_calls()                  # 测试调用

    drifts = []
    for sig in code_signatures:
        if sig not in contract_fields:
            drifts.append(f"code {sig} not in contract")
        if sig not in test_calls:
            drifts.append(f"code {sig} not in test")
    # 反向也检查（contract 有但 code 无等）

    return drifts
```

---

## THREE-WAY SYNC 强制流程

```yaml
# V11 Stage 3 实施者必走
修改契约字段前:
  - 读契约文档
  - 同步修改代码
  - 同步修改契约文档
  - 同步修改契约测试
  - 跑 drift-detect.py 验证（必达 100%）

修改契约字段后:
  - commit message 必含 "sync: code+contract+test for {field}"
  - drift-detect 输出必含在 commit body
```

```yaml
# ✅ 自动化方案（V11 推荐）

# pre-commit hook
pre_commit:
  - drift-detect.py
  - 失败 → 🛑 禁止 commit

# CI gate
ci_pipeline:
  - drift-detect.py
  - 失败 → 🛑 禁止 merge
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走
1. git log 检查 commit 含 "sync: code+contract+test"
2. drift-detect.py 输出必含在 PR description
3. 一致性 < 100% → 🛑 REJECT
4. implementer 单独改代码无契约/测试同步 → 🛑 REJECT（违反铁律 10）
5. contract-writer 改契约未通知 implementer → 🛑 REJECT（责任主体错位）
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| 代码加字段契约未改 | 下游客户端缺字段 → 服务端报错 |
| 代码改类型契约未改 | 前端处理错乱 → 数据失真 |
| 代码字段重命名契约未改 | 前端 undefined → 功能崩溃 |
| 改代码不跑 drift-detect | 三方漂移 → Stage 4 REJECT |
| implementer 改 API 不通知 contract-writer | 🛑 责任主体错位 |

---

## 关联引用

- [SKILL.md §铁律 10](../SKILL.md) — THREE-WAY SYNC
- V10 drift-detect.md: 已蒸馏到本文档（V11 实战案例）
- [drift-detect.py](../../scripts/drift-detect.py) — 三方一致性自动验证
- 公共铁律 Article VIII: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
