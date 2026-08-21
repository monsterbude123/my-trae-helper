# zentao-integration — 禅道集成详细协议

## §1 调用时机表(必须遵守)

| # | 时机 | 角色 | 命令 | 类型 |
|:-:|------|------|------|------|
| 1 | planner 启动 | planner | `zentao product story list --product <id>` | 只读 |
| 2 | planner 启动 | planner | `zentao testcase list --product <id>` | 只读 |
| 3 | planner 启动(可选) | planner | `zentao product view --product <id>` | 只读 |
| 4 | reporter 收尾 | reporter | `zentao testtask create --product <id> --name <n> --cases <ids>` | **写** |
| 5 | reporter 收尾 | reporter | `zentao bug create --product <id> --title <t> --steps <s> --severity <sv>` | **写** |
| 6 | reporter 收尾(可选) | reporter | `zentao testcase run --case <id> --result <r>` | **写**(慎用) |

> ⚠️ **写权铁律**:只有 reporter 角色可调 4/5/6;其他角色调 = 越界,reporter 拒收。

## §2 字段映射

### §2.1 需求 → 测试用例

| 禅道字段(story) | test-cases.yaml 字段 |
|----------------|----------------------|
| `story.id` | `story_ref` |
| `story.title` | `name`(如已有 existing_ref,不覆盖) |
| `story.pri` | `priority`(P0/P1/P2 映射 1/2/3) |
| `story.spec` | `steps` + `expected` |

### §2.2 用例 → 禅道回写

| test-cases.yaml 字段 | 禅道字段(bug) |
|---------------------|---------------|
| `id` | `title` 前缀(`[TC-xxx] <name>`) |
| `steps` | `steps`(复现步骤) |
| `screenshots/<case_id>-failure.png` | `files`(附件) |
| `priority` | `severity`(P0→1, P1→2, P2→3) |

## §3 调用范式

```bash
# planner 只读
zentao product story list --product 1 --json | jq '.[] | {id,title,pri,spec}'

# reporter 写
zentao testtask create \
  --product 1 \
  --name "ai-testmate 20260820_174500" \
  --cases TC-001,TC-002,TC-003 \
  --owner <auto>

zentao bug create \
  --product 1 \
  --title "[TC-001] 用户登录失败" \
  --steps "1. /login 2. 输入错误密码 3. 点击登录" \
  --severity 2 \
  --pri 1 \
  --files screenshots/TC-001-failure.png
```

## §4 失败处理

| 错误码 | 含义 | 处理 |
|-------|------|------|
| 401 | zentao 鉴权失败 | 检查 zentao-cli 配置,标 BLOCK |
| 404 | product/cases 不存在 | 检查 ZENTAO_PRODUCT_ID,标 BLOCK |
| 500 | 禅道服务端错误 | 重试 1 次,仍失败则降级 + 标 PARTIAL |
| 网络超时 | - | 重试 3 次(L2 retry 上限) |

## §5 反例(AP-3)

- ❌ planner 调 `zentao bug create` → 越界 → reporter 拒收并告警
- ❌ reporter 把 product_id 写死成 `1` → 必从 env 取
- ❌ 重复创建同一个 testtask → reporter 必查重(同 timestamp 跳过)