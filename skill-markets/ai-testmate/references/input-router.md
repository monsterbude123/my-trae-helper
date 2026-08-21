# input-router — 4 模式输入自适应决策矩阵

> v1.1 增量。planner 启动时按此矩阵探测,产出 `planner_mode` 标签。

---

## §1 4 模式决策矩阵

| 模式 | 触发条件(planner 启动时探测) | planner_mode 标签 | 输出策略 |
|:---:|------------------------------|------------------|----------|
| **A** | 仅 `<ws>/docs/prds/<app>-prd.md` 单文件存在 | `prd-only` | 仅 PRD 功能点 → UI 用例 |
| **B** | `<ws>/docs/prds/<app>/` 是目录(≥1 个 `.md`) | `prd-tree` | 聚合目录下所有 `.md` → 合并功能点 |
| **C** | PRD(A 或 B) + openapi 文档同时存在 | `prd+openapi` | PRD → UI 用例 + openapi → API 用例,合并去重 |
| **D** | 无 PRD + 有 openapi 文档 | `openapi-only` | 仅 API 用例,不读 PRD,跳过 PRD 相关步骤 |

---

## §2 探测顺序

planner 启动**严格按此顺序**探测(先匹配先赢):

```
1. 检测 <ws>/docs/prds/<app>-prd.md(单文件)
   └─ 存在 + 无 openapi → 模式 A
   └─ 存在 + 有 openapi → 模式 C

2. 检测 <ws>/docs/prds/<app>/(目录)
   └─ 是目录 + 有 .md + 无 openapi → 模式 B
   └─ 是目录 + 有 .md + 有 openapi → 模式 C

3. 仅检测 openapi(无 PRD)
   └─ 找到 → 模式 D
   └─ 都没找到 → exit 2 + 告诉用户:缺 PRD 或 openapi 二选一

4. 检测 openapi 路径(优先级):
   a. <ws>/docs/openapi/<app>-openapi.json
   b. <ws>/docs/openapi/<app>-openapi.yaml
   c. <ws>/docs/openapi/<app>-swagger.json
   d. <ws>/openapi.json
   e. <ws>/openapi.yaml
   第一个找到的胜出
```

---

## §3 各模式行为

### §3.1 模式 A(prd-only)

```
planner:
  读 <ws>/docs/prds/<app>-prd.md
  调 zentao product story list --product <id>(可选)
  调 zentao testcase list --product <id>(可选)
  提取功能点 → 生成 UI 用例(占大多数)+ 少量 API 用例(从 PRD 中提到的接口)
  → output test-cases.yaml(每条用例 source=prd)
```

### §3.2 模式 B(prd-tree)

```
planner:
  glob <ws>/docs/prds/<app>/*.md(递归 2 层,防爆)
  合并所有 .md 内容 → 虚拟单 PRD(按文件名字典序拼接)
  → 后续同模式 A
  → output test-cases.yaml(每条用例 source=prd-tree,带 origin_file=<name>)
```

### §3.3 模式 C(prd+openapi)

```
planner:
  按模式 A 或 B 处理 PRD
  调 scripts/openapi-extractor.py → 生成 openapi-derived 用例
  合并两路 → 去重(同 path + method + expected_status 视为重复,保留 openapi 来的,标注 source=openapi)
  → output test-cases.yaml(混合 source)
```

### §3.4 模式 D(openapi-only)

```
planner:
  跳过所有 PRD 操作
  仅调 scripts/openapi-extractor.py → 全量 API 用例
  source=openapi
  跳过 zentao story 拉取(因为没 PRD 不知道哪些 story 关联)
  → output test-cases.yaml(纯 API)
```

---

## §4 探测脚本调用范式

planner 主代理用以下 shell 探测(避免 Python 引入):

```bash
# 检测 PRD 单文件
[ -f "<ws>/docs/prds/<app>-prd.md" ] && PRD_SINGLE=true || PRD_SINGLE=false

# 检测 PRD 目录
[ -d "<ws>/docs/prds/<app>" ] && [ -n "$(ls -A <ws>/docs/prds/<app>/*.md 2>/dev/null)" ] && PRD_TREE=true || PRD_TREE=false

# 检测 openapi(按优先级)
OPENAPI=""
for p in \
  "<ws>/docs/openapi/<app>-openapi.json" \
  "<ws>/docs/openapi/<app>-openapi.yaml" \
  "<ws>/docs/openapi/<app>-swagger.json" \
  "<ws>/openapi.json" \
  "<ws>/openapi.yaml"; do
  [ -f "$p" ] && OPENAPI="$p" && break
done
```

---

## §5 反例(V2-AP-4 / V2-AP-5)

- ❌ PRD 目录树与单文件并存时,只读目录树(覆盖检测)
  → 修复:单文件优先,目录树降级
- ❌ openapi 路径有 5 个候选,全部扫一遍浪费时间
  → 修复:按 §2 优先级,first match wins
- ❌ 模式 D 还去尝试读 PRD(产生 NoneType 错误)
  → 修复:planner §1 决策树里显式"PRD=None → 跳过"
- ❌ 用例 source 字段缺失(无法追溯来源)
  → 修复:每条用例必带 source(prd / prd-tree / openapi / mixed)