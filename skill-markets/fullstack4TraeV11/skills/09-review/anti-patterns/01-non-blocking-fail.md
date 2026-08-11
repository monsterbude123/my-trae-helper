# 反例 1："非阻塞 FAIL" 放水

**违反**: reviewer 铁律 1 FAIL IS FAIL

**现象**: reviewer 发现问题但标"非阻塞"放行。

**正确替代**: 任一 FAIL = REJECT + 失败标签。
