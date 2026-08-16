# 首次启动自检清单

> 沉淀自 AGENT.md §8。skill / agent 新会话首次被调用时执行 4 步自检,确保工作空间状态已知。
> 单文件 ≤ 200 行。

## 1. 触发条件

- 新会话首次被调用
- 用户说"开始吧" / "看看如何处理" / 不带上下文的指令
- 长时间未活动(> 24h)后被唤醒

## 2. 4 步自检(顺序强制)

### Step 1 — 读 manifest.json,确认存在且 schema 合法

```bash
# 检查文件存在
ls <project_root>/manifest.json

# 校验 schema(必填 11 字段,见 manifest-schema.md §2)
python -c "
import json, sys
m = json.load(open('<project_root>/manifest.json'))
required = ['version', 'updated_at', 'repos']
for r in m.get('repos', []):
    required += ['name','owner','full_name','url','path','default_branch',
                 'added_at','last_pull_at','current_commit',
                 'current_commit_short','current_commit_date']
missing = [k for k in required if k not in m and k != 'repos']
print('MISSING:', missing) if missing else print('OK')
"
```

### Step 2 — 抽查 1~2 个 repo 路径是否存在

```bash
# 抽前 2 个仓库验证
for repo in $(python -c "import json; m=json.load(open('<project_root>/manifest.json')); print('\n'.join(r['path'] for r in m['repos'][:2]))"); do
  [ -d "$repo/.git" ] && echo "✅ $repo" || echo "❌ $repo 缺失"
done
```

### Step 3 — 检查 doc-map-manager 索引状态

```bash
# 索引文件是否存在
[ -f "<project_root>/docs/.docmap/docmap.db" ] && echo "✅ 索引存在" || echo "⚠️ 索引缺失,提示用户是否构建"
```

如果缺失,提示用户:
> 「检测到 `docs/.docmap/docmap.db` 不存在。是否执行首次构建?」

### Step 4 — 报告当前状态

```
仓库追踪器自检报告
- 已收录:N 个仓库
- 最近一次更新:YYYY-MM-DD HH:MM
- 索引状态:✅ 已建 / ⚠️ 未建
- 路径抽查:N 个抽查,全部正常 / X 个缺失
```

## 3. 反例

- ❌ 跳过自检直接进入"看起来项目已经初始化"假设
- ❌ 自检只看 manifest 存在,不看 schema 合法性
- ❌ 路径抽查用 `ls`(漏隐藏 `.git` 目录,见 pitfalls §001)
- ❌ 索引缺失时直接跑全量构建(用户可能想要先看现有 docs/)

## 4. 与其他 references 关系

- `manifest-schema.md §3` → 校验 11 必填字段的具体清单
- `doc-map-manager-usage.md §2` → 索引构建命令
- `pitfalls §001` → 隐藏 `.git` 目录探测反例
- `task-start-probe.md` → 自检后若有"未知初始状态"任务,走探测协议