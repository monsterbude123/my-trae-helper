# 反例 3：编造测试覆盖

**违反**: V10.12 关键门禁套件 + Article X

**现象**: reviewer 接受"测试覆盖 90%"但未实际跑 coverage 命令。

**正确替代**: reviewer 亲自跑 `pytest --cov` / `vitest run --coverage` 验证。
