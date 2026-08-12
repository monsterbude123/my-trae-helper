# 反例 4：大小写不敏感比较违规（Stage 6 Bug Fix）

> 来源：V10 sub-agent-rules.md §11 类型系统陷阱。

## 现象

```python
# ❌ 大小写敏感比较导致 bug
expected_hash = "abc123"  # 小写
actual_hash = compute_hash(data).upper()  # 外部 API 返回大写
assert actual_hash == expected_hash  # ❌ 永远 FAIL
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 没注意大小写规范 | 50% |
| 字符串比较未用 .lower() | 50% |

## 教训

**V10 sub-agent-rules.md §11 类型系统陷阱**：

```
任何 hash / ID / token 字符串比较必须用大小写不敏感比较
（外部 API 大写 vs hasher 输出小写）

数据库 BLOB 写入用 hex 字面量（SQLite X'hex'）不用字符串
```

## 正确替代

```python
# ✅ 大小写不敏感
expected_hash = "abc123"
actual_hash = compute_hash(data).upper()
assert actual_hash.lower() == expected_hash.lower()  # ✅ 一致

# ✅ hex 字面量
cursor.execute("INSERT INTO t (data) VALUES (X'48454C4C4F')")  # ✅ "HELLO"

# ❌ 字符串写入（V10 §11 禁止）
cursor.execute("INSERT INTO t (data) VALUES ('\\x48\\x45\\x4C\\x4C\\x4F')")  # ❌ 字面字符串
```

## 关联引用

- [SKILL.md §铁律 11 类型系统陷阱](../SKILL.md)
- V10 来源: `../../../../fullstack4TraeV10/references/sub-agent-rules.md` §11