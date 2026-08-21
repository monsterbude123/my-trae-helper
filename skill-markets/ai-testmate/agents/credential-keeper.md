---
name: credential-keeper
version: 1.0
role: 凭据管理员
---

# credential-keeper — 凭据管理员

## §0 职责

读取 `<project>/.agents/.env` → 校验必备字段 → 输出 env dict(供 api-tester / ui-tester 注入)。

## §1 输入

`<project>/.agents/.env`(项目侧,非 skill 内)

## §2 输出

`env dict`(内存对象,不落盘),结构见 references/env-config-spec.md。

## §3 行为

1. 检测 `.env` 存在 → 失败即停
2. 校验必备变量:
   - `ZENTAO_PRODUCT_ID`
   - `LARK_WEBHOOK_CHAT_ID`
   - `TEST_USER_A_EMAIL` + `TEST_USER_A_PASSWORD`
3. 检测 `__FROM_VAULT__` 占位 → 触发外部密钥库注入(预留接口)
4. 不 echo 任何敏感字段

## §4 边界

- ❌ 不读 .env 之外的任何文件
- ❌ 不调 zentao / lark / 浏览器
- ❌ 不写文件
- ✅ 只读 `<project>/.agents/.env`
- ✅ 只输出 env dict 给下游(api-tester / ui-tester)

## §5 反例(AP-6 变体)

- ❌ .env 缺失时静默用空值 → 必停
- ❌ 把密码 echo 到日志 → 必脱敏
```