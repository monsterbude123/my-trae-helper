# 任务启动探测协议(强制)

> 沉淀自 AGENT.md §10。任何"未知初始状态"的任务,**探测先行**,不直接动手。
> 单文件 ≤ 200 行。

## 1. 触发条件

- 用户说「你看看 X」「处理一下」「这些仓库你看看」
- 任何**未知初始状态**的任务(资源已存在但结构未知)
- 涉及**多个决策点**的任务
- 长会话首次启动 / 长时间未活动后被唤醒

## 2. 4 步协议(顺序强制)

### Step 1 — 探测(仅读,不写)

**目的**:把当前状态摸清,生成"现状报告"表。

允许的命令:
```bash
# 目录结构
Get-ChildItem -Path <root> -Directory -Recurse -Force   # 注意 -Force(见 pitfalls §001)

# git 状态
git -C <path> rev-parse HEAD
git -C <path> rev-parse --abbrev-ref HEAD
git -C <path> log -1 --format=%cI HEAD
git -C <path> config --get remote.origin.url

# manifest 读取
python -c "import json; print(json.dumps(json.load(open('<root>/manifest.json')), indent=2))"

# 索引状态
[ -f "<root>/docs/.docmap/docmap.db" ] && echo "✅" || echo "⚠️"
```

**禁止**的命令(探测阶段不写):
```bash
# ❌ git clone
# ❌ git pull
# ❌ rm / mv
# ❌ write to manifest.json
# ❌ 编辑任何文件
```

### Step 2 — 列决策点(用 AskUserQuestion,一次 ≤ 4 个)

把"现状报告"中需要用户决策的项整理成 ≤ 4 个明确问题:

```yaml
问题1: "聚合目录 ai-skills-sets 下 18 个子项目,全部纳入 manifest 还是只挑核心 5 个?"
选项:
  - 全部纳入(18 个)
  - 只挑核心 5 个(列清单)
  - 先探测再决定(下一步决定)

问题2: "本地 HEAD 领先 origin/main,如何处理?"
选项:
  - reset --hard origin/main(丢本地)
  - 手动 rebase(保留本地)
  - 重新 clone(干净)
```

### Step 3 — 等用户决策

**禁止**:
- ❌ 收到部分决策就开始执行
- ❌ 用"既然你没反对那我就..."替代用户决策
- ❌ 决策点 > 4 个时分多次问(必须合并或先独立子步骤)

**允许**:
- ✅ 在等用户时,**展示完整探测报告**让用户看到上下文
- ✅ 用户回复"你来定"才走默认选项(并在结果报告里说明"用户授权默认")

### Step 4 — 执行计划公示

收到决策后,**先列完整阶段计划**,让用户看到完整路径再开始执行:

```
执行计划:
  阶段 1: 备份 manifest.json → manifest.json.bak(5 秒)
  阶段 2: 18 个子项目逐个 ls .git + 测 clone(2 分钟)
  阶段 3: 写入 manifest.json(N 条记录,30 秒)
  阶段 4: 触发增量索引(30 秒)
  阶段 5: 报告 N 个新收录 + 索引状态
总耗时预估: ~3-5 分钟
```

公示后才进入执行。

## 3. 反例(必避免)

- ❌ 收到「看看如何处理」就立即 clone / rename / write(违反探测先行)
- ❌ 用 LS 默认行为探测目录(漏隐藏 .git,见 pitfalls §001)— 必须 `-Recurse -Force`
- ❌ 决策点超 4 个分多次问(必须合并或先独立子步骤)
- ❌ 等用户决策时无脑展示所有数据(只展示决策相关项 + 1-2 个关键事实)
- ❌ 执行阶段突然改变计划(违反"先列计划,用户看到完整路径"原则)

## 4. 与其他 references 关系

- `first-run-checklist.md` → 首次启动自检(本协议的前置步骤)
- `workflows-baseline.md` → 探测完后,选哪条基线工作流
- `pitfalls §001` → LS 默认行为漏隐藏 `.git` 反例
- `pitfalls §006` → 用户视角测试盲点反例
- `reply-conventions.md §3` → 用户表态信号处理(不耐烦时终止探测,选保守方案)