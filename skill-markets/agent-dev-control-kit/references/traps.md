# agent-dev-control-kit — 反例库 (traps)

> **本文件由 my-trae-helper 2026-08-14 会话蒸馏生成**。每个反例来自真实失败案例,可作为下次写 Gate 时的避坑参考。
>
> **更新**(2026-08-14 第二轮):本文件的反例已结构化为 [trap-instructions.yaml](trap-instructions.yaml) — 每条 AP-* 含 detect_signal / fix_template / next_skill / reclaim_steps。详细机器可读字段从 YAML 消费,人类阅读继续用本文件。

---

## §0 反例索引

| ID | 反例标题 | 严重度 | 关联铁律 |
|----|---------|-------:|---------|
| AP-1 | 过度流程化(单文件纯新增) | MEDIUM | §0.3 |
| AP-2 | Gate 静默跳过不存在脚本 | HIGH | §11.1.2 |
| AP-3 | Guard 缺 CLI 自执行入口 | HIGH | §11.1.1 |
| AP-4 | Lint 硬编码文件列表 | HIGH | §11.1.1 |
| AP-5 | 一次性 commit 巨大违反最小变更 | MEDIUM | §7.4 (change ↔ feature)|
| AP-6 | 跨项目 skill 引用未消除 | LOW | §7 (project boundary) |
| AP-7 | Guard 正则覆盖不足 | HIGH | §11.1.1 |

---

## §AP-1 过度流程化

```
触发场景: 单文件纯新增(5 个测试文件)
错配: 对单文件套用三层控制(Execution + Guard + Gate)
     执行 CP1~CP6(风险判定/备份/创建/验证/回滚/审计)
     跑 4 个守卫(security/structure/capability/dependency)
     走 4 级 Gate(L1~L4)

代价: 工程成本 >> 实际风险
     工程师不愿遵守,Gate 沦为演戏

正确做法: 识别为"开发阶段新功能",豁免三层控制
  - 仅跑 lint
  - 不备份(单文件风险低)
  - 不审计(开发阶段非生产)
  - 不跑结构守卫(单文件改动小)

agent-dev-control-kit §0.3 已声明此场景"不适用"
本会话坑: 没读 §0.3,硬套用了三层控制
```

## §AP-2 Gate 静默跳过不存在脚本

```
触发场景:
  pre-commit 写:
    if command -v npm &> /dev/null && grep -q '"lint"' package.json; then
      echo "1️⃣ Lint..."
      npm run lint
    fi

失败路径:
  package.json 没 lint 脚本
  → grep 返回 false
  → if 块整体不执行
  → 没有"❌ Gate 配置错误"消息
  → exit 0 → 假通过
  → 用户发现 L1 Gate 静默跳过

本会话发生:
  第一次 commit (172 文件) "L1 Gate 通过"
  → 用户: "Commit Gate 直接通过了??为啥,我看你测试skill的测试用例都没有写啊"

正确写法:
  if ! grep -q '"lint"' package.json; then
    echo "❌ Gate 配置错误: package.json 缺少 lint 脚本"
    exit 1
  fi
  echo "1️⃣ Lint..."
  npm run lint
```

## §AP-3 Guard 缺 CLI 自执行入口

```
触发场景:
  src/guards/skill-dependency-guard.mjs 文件
  只有 export async function runDependencyGuard(args)
  没有 main 块

失败路径:
  node src/guards/skill-dependency-guard.mjs never-existed-zzz
  → 仅加载模块
  → runDependencyGuard 从未被调用
  → exit 0
  → 没有"❌ 缺失硬依赖"消息
  → 完全不工作

本会话发生:
  测试 "dependency guard 不存在技能 → BLOCK" 第一次跑 → exit 0 假通过
  → 用户: "我没有看见你去测试skills 里的脚本啊"

正确写法(ESM 自执行入口):
  // CLI 自执行入口
  const isMain = import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`;
  if (isMain) {
    runDependencyGuard(process.argv.slice(2));
  }

注意: CJS 用 `require.main === module`
      ESM 必须用 import.meta.url 比较
```

## §AP-4 Lint 硬编码文件列表

```
触发场景:
  package.json scripts.lint:
    "node --check bin/cli.mjs && node --check src/add.mjs && ... (15 个文件)"

失败路径:
  新加 src/foo.mjs → 不在硬编码列表 → 不被 lint
  新加 src/_lint_break.mjs 含 TS 语法错误 → 不被发现
  → Gate "通过" 但实际 lint 未覆盖

本会话发生:
  加 src/_lint_break.mjs(TS 语法错)
  → commit "L1 Gate 通过"
  → 我才发现 lint 没扫这个文件

正确写法:
  改为 scripts/lint.mjs 用 glob 扫描:
    walk(root, exclude={node_modules, skill-markets, example, docs, logs, tests, .git, ...})
    for file in files: node --check file

  或用 eslint --ext .mjs src/ bin/
```

## §AP-5 一次性 commit 巨大违反最小变更

```
触发场景:
  本会话某次 commit (216f1af) 含:
    172 files changed, 25051 insertions(+), 339 deletions(-)

失败路径:
  - 一个 commit 跨多个关注点(CLI + 测试 + 守卫 + 配置 + 文档)
  - 难以 revert (要 revert 整 25051 行)
  - Gate 只校验最新 commit,前面 commit 没保护
  - Code review 范围爆炸(171 个文件要看)

本会话发生: 第一次 commit 172 文件
  → 应该是 5-6 个 commit,每个对应一个 stage(prep/design/impl/verify/bug)

正确做法:
  - 切分 commit(每个 < 50 文件 / < 1000 行)
  - 用 change-id 命名: {YYYY-MM-DD}-{kebab-name}
  - 每个 commit 加 stage 标签:
    prep/design/impl/verify/bug/health
  - 1 change = 1 feature branch = N commits
```

## §AP-6 跨项目 skill 引用未消除

```
触发场景:
  AGENTS.md 含 11 处 fullstack4TraeV11/references/* 链接

失败路径:
  - AGENTS.md 应该反映"本项目"现状
  - 链接到其他 skill 内部 references 让 AGENTS.md 变得"跨项目"
  - 当其他 skill 重构时,链接断裂
  - 用户感受:AGENTS.md "已经没啥意义"

本会话发生: 用户 3 轮纠正
  1. "先更新agents md 移除掉不再需要的内容"
  2. "相关的fullstack4TraeV11 其实不需要在这个项目的agents md提及了"
  3. "D:\workspace\my-trae-helper\AGENTS.md 这个完全重写,已经没啥意义"

正确做法:
  - AGENTS.md 只描述本项目状态
  - 不引用其他 skill 的内部路径(除非必要)
  - 引用其他 skill 时只说名字(如 "see skill-acceptance")
  - 项目结构图反映实际目录(用 LS 列出真实文件树)
```

## §AP-7 Guard 正则覆盖不足

```
触发场景:
  capability guard 用 r'scripts/([^`]+)' 提取 CAPABILITY-MAP.md 中已注册脚本

失败路径:
  - CAPABILITY-MAP.md 实际含 vision-audit/scripts/vision-audit.mjs
  - 正则只匹配 scripts/xxx.py 形式
  - 漏掉 vision-audit/scripts/vision-audit.mjs
  - 创建含同名 basename 的脚本时 guard 通过
  - 实际生产中重复脚本未被检测

本会话发生:
  测试 "vision-audit.mjs 重复" 第一次跑 → guard 通过(假)
  → 修复正则后才真阻断

正确做法:
  - 写正则前穷举所有可能的路径形式
  - 测试用例覆盖 3-5 种不同路径前缀
  - 返回 (完整路径列表, basename 列表) 二元组
  - 用通用扩展名正则:`r'([^`]*\.(?:py|mjs|sh|ps1))'`
```

---

## §1 反例使用方式

```
写 Gate 时:
  1. 列出本会话相关的反例(§AP-*)
  2. 每个反例生成对应的自验收用例
  3. 固化进 tests/unit/test_*.py
  4. 加进 npm run test:unit
  5. 每次改 Gate 重跑全部反例
```

---

## §2 反例新增流程

```
发现新反例时:
  1. 在本文件追加 §AP-N+1
  2. 在 SKILL.md §11.3 加反例引用
  3. 在 tests/unit/ 加自验收用例
  4. 在 docs/discuss/ 写蒸馏汇报文档
```