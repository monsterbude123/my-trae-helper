# 反例 4：自动循环 Round 3+ 继续绕

**违反**: V10.12 Step 2.6 rescue hatch

**现象**: Round 3 失败 → 继续 Round 4 → ... → 5 轮小修小补。

**正确替代**: Round 3+ 自动触发 rescue hatch → 回退 Phase 0 重新审视需求。
