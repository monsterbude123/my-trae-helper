# env-config-spec — `.agents/.env` 变量规范

## §1 必填变量(credential-keeper 缺失即停)

```bash
# === 禅道 ===
ZENTAO_PRODUCT_ID=<number>             # 关联禅道产品 ID

# === 飞书通知 ===
LARK_WEBHOOK_CHAT_ID=oc_xxxxxxxxx      # 报告推送群 chat_id

# === 测试账号池(至少 A) ===
TEST_USER_A_EMAIL=<email>              # 主测试账号
TEST_USER_A_PASSWORD=<password_or_vault_placeholder>

# === 报告目录(可选,默认 <workspace>/reports/) ===
TESTMATE_REPORT_DIR=<absolute_path>    # 报告输出根目录
```

## §2 推荐变量

```bash
# === 禅道自动登记 ===
ZENTAO_TESTTASK_AUTO_CREATE=true       # 默认 true,false 则不登记 testtask
ZENTAO_BUG_AUTO_CREATE=true            # 默认 true,false 则失败用例不创建 Bug

# === 飞书 @ 人 ===
REPORT_PUSH_USERS=ou_aaa,ou_bbb        # 报告推送时 @ 谁(open_id 列表)

# === 账号池扩展 ===
TEST_USER_B_EMAIL=<email>             # 第二测试账号
TEST_USER_B_PASSWORD=<password>

# === 工作空间根 ===
TESTMATE_WORKSPACE_ROOT=<path>         # 默认从 cwd 推导
```

## §3 vault 占位协议

```
密码字段值 = "__FROM_VAULT__"  →  credential-keeper 触发外部密钥库注入
                                →  当前预留接口,不实现(留给 Vault/Secret Manager 集成)
                                →  占位未替换 → credential-keeper 失败并报错
```

## §4 缺失降级(必停铁律)

```
任一 §1 变量缺失:
  → credential-keeper 输出: [BLOCK] missing required env: <var_name>
  → exit code = 2
  → 整单停,不静默用空值
  → 测试不跑
```

## §5 .gitignore 强约束

```
# 用户项目根 .gitignore 必须包含
.agents/.env
```

credential-keeper 启动时检测:不存在 .env → 报错并提示用户创建。

## §6 反例(AP-2 / AP-6)

- ❌ 把账号池从 .env 复制到 skill 内部 .env.example
  → .env.example 只允许写变量名,不允许写真实密码
- ❌ credential-keeper 把密码 echo 到日志
  → echo 时必 mask(`***`)
- ❌ 脚本读 .env 用 `cat` + `grep` → 改用 `python-dotenv` 或 `.env` 解析库