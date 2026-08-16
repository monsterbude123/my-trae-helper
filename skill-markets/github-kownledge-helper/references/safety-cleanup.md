# 安全与清理规则(4 条铁律)

> 沉淀自 project-rules.md §7。仓库追踪场景下"安全 + 文件卫生"的硬约束。
> 单文件 ≤ 200 行。

## 1. 4 条铁律

| # | 规则 | 反例 |
|---|------|------|
| 1 | **不泄露**:manifest 或仓库中如有 token / 密钥,输出时必须脱敏 | agent 回复时打印完整 token |
| 2 | **临时清理**:操作产生的临时文件(`manifest.json.bak` / 临时 diff)完成后立即清理 | manifest.json.bak 永久残留 |
| 3 | **不留报错脚本**:`scripts/` 下仅保留可跑通的脚本,报错脚本删除或修复 | 半成品 .ts / .ps1 留在 scripts/ |
| 4 | **`repos/` 不入 git**:第三方仓库不纳入本项目版本管理(必入 `.gitignore`) | `git add repos/` 把 facebook/react 全部提交到本项目 |

## 2. token / 密钥脱敏

```typescript
// 推荐脱敏模式(TS)
function maskKey(key: string): string {
  if (!key || key.length < 4) return '****';
  return '*'.repeat(key.length - 4) + key.slice(-4);
}
// 输出示例: "sk-****abcd" 而非 "sk-1234567890abcdefabcd"
```

**应用场景**:
- manifest 含 `auth_token` 字段 → 输出时 `maskKey()`
- 私有仓 clone URL 含 token → 输出时只显示 `https://<owner>/<repo>@github.com/...`(去 token)
- log / debug 输出任何敏感信息 → 自动走脱敏函数

## 3. 临时文件清理清单

| 临时文件 | 何时清理 | 如何清理 |
|---------|---------|---------|
| `manifest.json.bak` | 写成功后立即 | `fs.unlinkSync` |
| `<tmp_dir>/diff-*.patch` | merge / reset 后立即 | `fs.rmSync` |
| `*.tmp` | 写完成后 rename 取代 | 自动 rename |
| `logs/agent-hints.jsonl` | 每日 / 每次会话结束 | conftest 可清空 |

## 4. scripts/ 准入

```
MUST:
  - 任何 .ts / .ps1 / .sh 脚本必须有对应测试(vitest / pytest)
  - 本地实跑通过才提交
  - 单文件 ≤ 200 行,超出按职责拆分

MUST NOT:
  - 留报错脚本(commit 前删除)
  - 留半成品(.ts 只有 TODO,函数未实现)
  - 留调试脚本(debug-*.ts / test-*.ps1)
```

## 5. .gitignore 必须包含

```gitignore
# 第三方仓库(必入)
repos/

# 索引产物(部分 gitignore,看项目策略)
docs/.docmap/docmap.db
docs/.docmap/index/

# 临时文件
manifest.json.bak
*.tmp
*.bak
.tmp_*

# node / pnpm
node_modules/
.pnpm-store/

# 测试 / 调试
coverage/
.nyc_output/
```

## 6. 反模式

- ❌ manifest 输出时打印完整 token(违反脱敏)
- ❌ manifest.json.bak 永久残留(违反临时清理)
- ❌ scripts/ 留 debug-xxx.ps1 半年(违反不留报错脚本)
- ❌ `git add repos/` 把 facebook/react 全部提交(违反不入 git)
- ❌ .env 文件 commit 到 git(违反安全)
- ❌ 临时文件落 logs/ 之外的位置(违反路径约束,见 [project-paths.md](./project-paths.md))

## 7. 与其他 references 关系

- `project-paths.md` → 路径约束(哪里允许写文件)
- `manifest-schema.md §3` → manifest 原子写 + 备份机制
- `env-loadenv.md` → env 收口(避免硬编码 token / 路径)
- `skill-evolution.md §3` → 升级红线包含"不留报错脚本"