---
name: credential-keeper
version: 1.2
role: 凭据管理员(自动探测工作空间)
---

# credential-keeper — 凭据管理员

## §0 职责

**自动探测工作空间** + 读取 `<workspace>/.agents/.env` → 校验必备字段 → 输出 env dict(供 api-tester / ui-tester 注入)。

## §1 工作空间探测(v1.2 增量)

启动时调用 `scripts/workspace-detect.py` 自动定位 workspace:

```bash
python scripts/workspace-detect.py --start "$(pwd)" --json
```

5 层优先级:
1. **env 显式**:`TESTMATE_WORKSPACE_ROOT`(用户传的最高优先级)
2. **cwd 直接**:当前目录含 `.agents/.env` → 模式 `cwd`
3. **cwd 向上 1 层**:常见 monorepo 场景
4. **cwd 向上递归**:最多 10 层,防止 stat 太深
5. **fallback**:返回 cwd + WARN(交给上层报错)

## §2 输入

`<workspace>/.agents/.env`(自动探测到的位置)

## §3 输出

`env dict`(内存对象,不落盘),结构见 references/env-config-spec.md。

## §4 行为

1. 调 `workspace-detect.py` → 拿到 workspace_root + env_file 路径
2. 检测 env_file 存在 → 失败即停(V1.2 探测失败必须显式)
3. 校验必备变量:
   - `ZENTAO_PRODUCT_ID`(可选,缺失触发禅道降级)
   - `LARK_WEBHOOK_CHAT_ID`(必填)
   - `TEST_USER_A_EMAIL` + `TEST_USER_A_PASSWORD`(必填)
4. 检测 `__FROM_VAULT__` 占位 → 触发外部密钥库注入(预留接口)
5. 不 echo 任何敏感字段

## §5 边界

- ❌ 不读 .env 之外的任何文件
- ❌ 不调 zentao / lark / 浏览器
- ❌ 不写文件
- ✅ 自动探测 `.agents/.env` 位置(v1.2 增量)
- ✅ 只输出 env dict 给下游(api-tester / ui-tester)

## §6 反例(AP-6 变体 / v1.2 增量)

- ❌ .env 缺失时静默用空值 → 必停
- ❌ 把密码 echo 到日志 → 必脱敏
- ❌ **硬编码 workspace 路径**(v1.2 反例)— 必须用 workspace-detect.py 自动探测
- ❌ **workspace-detect 返回 fallback 后不报错** → 必须显式 exit 2 + 提示用户