# V9 精密化改动验证协议

> **用途**：验证本技能包 V9/V9.1 改动是否真正杜绝了 AIGCMediaDesktop 报告中暴露的 8 类问题。
> **原则**：每条验证必须可被机械执行，不接受主观判断。
> **执行时机**：技能包更新后、新项目首次走 fullstack 流程前、跨版本比对时。

---

## 验证环境准备

```powershell
# 1. 确认技能包版本
ls "$env:USERPROFILE\.trae-cn\skills\fullstack4traev8\references\completion-report-protocol.md"
# 存在 → V9+，不存在 → V8-，必须先更新

# 2. 确认规则版本
grep "V9.1 NEW" "$env:USERPROFILE\.trae-cn\.trae\rules\agent协调协议.md"
# 有结果 → 规则已更新
```

---

## P0-1 验证：主上下文不再直编文档索引

| 项目 | 内容 |
|------|------|
| **原始问题** | 主上下文直接用 Read/Edit 改文档索引，跳过 agent 委派和 doc-map-manager 技能 |
| **修复位置** | `agent协调协议.md` §2.2 委派映射 + §4 禁止行为 + `doc-updater.md` 铁律8 |

### 验证步骤

```
Step A — 技能加载验证:
  在任意会话中，请求 "更新文档索引"
  观察主上下文行为:
    ✅ 正确: 主上下文说 "委派 doc-updater" → doc-updater 说 "调用 doc-map-manager 技能"
    ❌ 失败: 主上下文直接 Read 并 Edit 文档索引文件

Step B — 规则拦截验证:
  检查 agent协调协议 §4 禁止行为表:
    ✅ 正确: 表中存在 "主上下文直接编辑文档索引文件" 条目
    ❌ 失败: 无此条目

Step C — 铁律覆盖验证:
  检查 doc-updater.md 铁律:
    ✅ 正确: 铁律第 8 条 "SKILL CHAIN ONLY — 文档索引文件只能通过 doc-map-manager 技能更新"
    ❌ 失败: 无此铁律
```

**通过标准**: 三个步骤全部 ✅

---

## P0-2 验证：gitignore 误杀可被检测

| 项目 | 内容 |
|------|------|
| **原始问题** | build-index.py 静默修改 .gitignore，排除 docs/ 下的关键文件，产出落盘后被忽略 |
| **修复位置** | `agent协调协议.md` §5 Step4 + `completion-report-protocol.md` Step4 + `doc-updater.md` 铁律9 + 场景6 |

### 验证步骤

```
Step A — 机械验证链覆盖验证:
  检查 agent协调协议 §5 中 Step 4:
    ✅ 正确: 包含 "git check-ignore" 和 "git log -- .gitignore" 两条检查
    ❌ 失败: 只有一条或没有

Step B — 反模式表覆盖验证:
  检查 completion-report-protocol.md §五 反模式:
    ✅ 正确: 包含 "build-index.py 静默写 .gitignore" 和 "直接编辑文档索引" 两条
    ❌ 失败: 无这两条

Step C — 模拟测试（在目标项目执行）:
  # 1. 在 .gitignore 中添加文档索引文件
  echo "docs/索引文件" >> .gitignore
  
  # 2. 创建一个测试变更
  echo "test" >> docs/索引文件
  
  # 3. 模拟 agent 返回 Completion Report:
  #    artifacts_produced: [{path: "docs/索引文件", ...}]
  
  # 4. 执行机械验证 Step 4:
  git check-ignore docs/索引文件
  
  ✅ 正确: 返回 "docs/索引文件"（被忽略）→ 🛑 REJECT 触发
  ❌ 失败: 无输出（未被忽略，检查未生效）
  
  # 5. 清理
  git checkout .gitignore
  git checkout docs/索引文件
```

**通过标准**: Step A+B 均 ✅；Step C 可选，作为集成环境验证

---

## P0-3 验证：门禁不再接受"非阻塞"

| 项目 | 内容 |
|------|------|
| **原始问题** | Reviewer 发现 3 项文档缺失，标记 "P1 非阻塞" 直接通过 |
| **修复位置** | `quantitative-acceptance.md` V6.0 §六 + Step5 + `reviewer.md` V6.0 铁律3 + N/A 验证 |

### 验证步骤

```
Step A — "非阻塞"废除验证:
  检查 quantitative-acceptance.md:
    grep "非阻塞" → 
    ✅ 正确: 没有出现 "非阻塞 P1" 或 "待改进项" 等准许放行标记
    ❌ 失败: 存在上述标记

Step B — FAIL=FAIL 铁律验证:
  检查 reviewer.md 铁律:
    ✅ 正确: 铁律第 3 条 "FAIL IS FAIL — NO NON-BLOCKING"
    ❌ 失败: 无此铁律

Step C — 审查阶段 N/A 新增禁止验证:
  检查 reviewer.md 阶段 8.1:
    ✅ 正确: 包含 "禁止在审查阶段新增 N/A" 
    ❌ 失败: 无此约束

Step D — 一致性校验存在性验证:
  检查 quantitative-acceptance.md Step 3:
    ✅ 正确: 包含 "checklist 通过率 ↔ 计算评分 偏差 < ±0.5"
    ❌ 失败: 无一致性校验
```

**通过标准**: 全部 ✅

---

## P1-1 验证：agent 产出不再不可见

| 项目 | 内容 |
|------|------|
| **原始问题** | doc-updater 通过 acceptEdits 静默修改文件，用户看不到任何 diff |
| **修复位置** | `completion-report-protocol.md` + `agent协调协议.md` §5 + §5.1 |

### 验证步骤

```
Step A — Completion Report 协议存在性验证:
  检查 completion-report-protocol.md:
    ✅ 正确: 包含 §三 主上下文验证步骤(6步) + §五 反模式表
    ❌ 失败: 文件不存在或章节缺失

Step B — doc-sync diff 确认门禁验证:
  检查 agent协调协议 §5.1:
    ✅ 正确: 包含 "git diff --stat -- docs/" + "展示给用户确认" 流程
    ❌ 失败: 无此节或无 diff 回显

Step C — acceptEdits 反模式验证:
  检查 completion-report-protocol.md §五 反模式:
    ✅ 正确: 包含 "acceptEdits 静默操作无 diff 回显" 行
    ❌ 失败: 无此行

Step D — Completion Report 硬门禁验证:
  检查 agent协调协议 §5 Step 0:
    ✅ 正确: 存在 "无 Completion Report → 🛑 REJECT" 
    ❌ 失败: 无 Step 0 或无硬门禁描述
```

**通过标准**: 全部 ✅

---

## P1-2 + P2-2 验证：doc-updater 覆盖 8 类文档

| 项目 | 内容 |
|------|------|
| **原始问题** | doc-updater 只更新 4/8 类文档，遗漏 prototypes/文档索引/modules 深层 |
| **修复位置** | `doc-updater.md` DOC SYNC 完整性清单(8类) |

### 验证步骤

```
Step A — 完整性清单覆盖验证:
  检查 doc-updater.md "DOC SYNC 完整性清单" 表:
    ✅ 正确: 包含 8 行（ARCHITECTURE/README/state-card/scaffold/modules/文档索引/prototypes/reports）
    ❌ 失败: < 8 行

Step B — 质量阈值验证:
  检查每行是否有 "质量阈值" 列:
    ✅ 正确: 每行有具体阈值（≥5行 / 非空 / 已执行 / grep -c 计数）
    ❌ 失败: 任何一行无阈值或阈值为 "已更新"（模糊）

Step C — Completion Report 同步验证:
  检查 doc-updater.md Completion Report 中的 required_artifacts:
    ✅ 正确: 包含至少 6 项（ARCHITECTURE/README/state-card/文档索引/modules/prototypes）
    ❌ 失败: < 6 项
```

**通过标准**: 全部 ✅

---

## P2-1 验证：doc-sync 后有 diff 确认门禁

| 项目 | 内容 |
|------|------|
| **原始问题** | doc-sync 执行后直接进入 commit，中间无 diff 展示确认 |
| **修复位置** | `strict.md` 阶段 7.5 + `agent协调协议.md` §5.1 |

### 验证步骤

```
Step A — 门禁链阶段验证:
  检查 strict.md 阶段门禁链表:
    ✅ 正确: 第 7 和第 8 阶段之间存在 "7.5 Doc-Sync Confirm"
    ❌ 失败: 无 7.5

Step B — 门禁内容验证:
  检查 7.5 门禁列内容:
    ✅ 正确: 包含 "git diff --stat -- docs/" + "Completion Report 完整性验证"
    ❌ 失败: 内容不匹配

Step C — 特殊验证协议验证:
  检查 agent协调协议 §5.1:
    ✅ 正确: 包含 "展示给用户确认" 和 "用户确认后 → 进 commit"
    ❌ 失败: 无用户确认环节
```

**通过标准**: 全部 ✅

---

## P2-3 验证：报告不再放错路径

| 项目 | 内容 |
|------|------|
| **原始问题** | 验收计分卡放在 test-plan/，不是 docs/reports/ |
| **修复位置** | `strict.md` docs/目录规范 + `agent协调协议.md` §5 Step5 + `acceptance-scorecard.md` |

### 验证步骤

```
Step A — 目录规范权威源验证:
  检查 strict.md "docs/目录规范":
    ✅ 正确: 存在 reports/ 目录 + 路径铁律表
    ❌ 失败: 无此章节

Step B — 机械验证覆盖验证:
  检查 agent协调协议 §5 Step 5:
    ✅ 正确: 包含 "reports 类文件 → docs/reports/（不是 test-plan/）"
    ❌ 失败: 无此路径约束

Step C — 模板路径验证:
  检查 acceptance-scorecard.md 模板文件名和描述:
    ✅ 正确: 模板内标注归档路径为 "docs/reports/"
    ❌ 失败: 标注为 test-plan/ 或无标注
```

**通过标准**: 全部 ✅

---

## P2-4 验证：Hook 体系可被证明生效

| 项目 | 内容 |
|------|------|
| **原始问题** | Hook 脚本存在但未生效 — 路径只覆盖 src/ 忽略 docs/，关键 hook 默认关闭 |
| **修复位置** | `session-start.ps1` 日志产出 + `auto-test.ps1` 启用 + `doc-sync-gate.ps1` 扩展 docs/ + `fullstack-hooks.json` + `agent协调协议.md` §5.0.1 |

### 验证步骤

```
Step A — auto-test 启用验证:
  检查 fullstack-hooks.json:
    grep '"fullstack-auto-test"' | grep '"enabled".*true'
    ✅ 正确: enabled 为 true
    ❌ 失败: enabled 为 false

Step B — doc-sync-gate 覆盖范围验证:
  检查 doc-sync-gate.ps1:
    grep "docs/"
    ✅ 正确: 包含 docs/ 匹配逻辑
    ❌ 失败: 只匹配 src/

Step C — session-start 日志产出验证:
  检查 session-start.ps1:
    grep "hook-session-start"
    ✅ 正确: 包含日志文件写入逻辑
    ❌ 失败: 无日志产出

Step D — Hook 日志验证触发点验证:
  检查 agent协调协议 §5.0.1:
    ✅ 正确: 包含 "SessionStart Hook 后" 和 "每次阶段切换" 两个触发点
    ❌ 失败: 少于两个触发点

Step E — 环境集成验证（在目标项目执行）:
  # 1. 确认 .trae/logs/ 目录存在
  ls .trae/logs/
  
  # 2. 启动一次会话（触发 SessionStart hook）
  
  # 3. 检查日志是否产生:
  ls .trae/logs/hook-session-start-*.log
  
  ✅ 正确: 日志文件存在，内容含 "Status: EXECUTED"
  ❌ 失败: 无日志文件
  
  # 4. 检查 auto-test hook 状态:
  grep "fullstack-auto-test" .trae/hooks.json
  ✅ 正确: enabled: true
```

**通过标准**: Step A-D 至少全部 ✅；Step E 可选

---

## V9.2-1 验证：implementer 编码前强制 impact()

| 项目 | 内容 |
|------|------|
| **原始问题** | 主上下文委派 implementer 后，implementer 直接编码，未调用 GitNexus impact() |
| **修复位置** | `implementer.md` 铁律11 + 步骤 0.8 + `agent协调协议.md` §5 Step 0.5 |

### 验证步骤

```
Step A — 铁律存在性验证:
  grep "GITNEXUS IMPACT" implementer.md
  ✅ 正确: 铁律第 11 条存在
  ❌ 失败: 无此铁律

Step B — 步骤存在性验证:
  grep "步骤 0\.8" implementer.md
  ✅ 正确: 存在 "步骤 0.8: GitNexus 影响面分析"
  ❌ 失败: 无此步骤

Step C — 机械验证触发验证:
  grep "Step 0\.5" agent协调协议.md
  ✅ 正确: §5 中存在 Step 0.5 GitNexus 影响面验证
  ❌ 失败: 无 Step 0.5

Step D — Completion Report 必填字段验证:
  grep "GitNexus 验证" implementer.md
  ✅ 正确: 量化汇报模板中包含 "GitNexus 验证" 段
  ❌ 失败: 无此段
```

**通过标准**: 全部 ✅

---

## V9.2-2 验证：detect_changes() 纳入强制流程

| 项目 | 内容 |
|------|------|
| **原始问题** | 编码完成后，主上下文未要求 implementer 执行 detect_changes() 验证变更范围 |
| **修复位置** | `implementer.md` 量化汇报 GitNexus 段（detect_changes 行）+ `agent协调协议.md` §5 Step 0.5 |

### 验证步骤

```
Step A — detect_changes 在 Completion Report 中:
  grep "detect_changes" implementer.md
  ✅ 正确: 量化汇报模板包含 detect_changes 执行标记和变更范围行
  ❌ 失败: 无 detect_changes

Step B — 机械验证拦截:
  检查 agent协调协议 §5 Step 0.5:
  ✅ 正确: 包含 "implementer Completion Report 中是否包含「GitNexus 验证」段"
  ❌ 失败: 无此拦截逻辑
```

**通过标准**: 全部 ✅

---

## V9.2-3 验证：doc-map-manager 技能不可被绕过

| 项目 | 内容 |
|------|------|
| **原始问题** | 主上下文给 doc-updater 的指令中包含 `python build-index.py`，绕过了 doc-map-manager 技能 |
| **修复位置** | `doc-updater.md` 铁律10 + `agent协调协议.md` §4 禁止行为 |

### 验证步骤

```
Step A — doc-updater 自防:
  grep "REJECT DIRECT COMMAND" doc-updater.md
  ✅ 正确: 铁律第 10 条 "REJECT DIRECT COMMAND" 存在
  ❌ 失败: 无此铁律

Step B — 主上下文禁止:
  grep "python build-index\.py" agent协调协议.md
  ✅ 正确: §4 禁止行为表包含 "委派 doc-updater 时指令中包含 python build-index.py"
  ❌ 失败: 无此禁止项
```

**通过标准**: 全部 ✅

---

## 验证结果汇总

| # | 问题 | Step A | Step B | Step C | Step D | Step E | 状态 |
|---|------|:---:|:---:|:---:|:---:|:---:|:---:|
| P0-1 | 主上下文越界 | | | | — | — | |
| P0-2 | gitignore 误杀 | | | | — | — | |
| P0-3 | 门禁绕过 | | | | | — | |
| P1-1 | agent 不透明 | | | | | — | |
| P1-2/P2-2 | doc-updater 遗漏 | | | | — | — | |
| P2-1 | 缺 diff 确认 | | | | — | — | |
| P2-3 | 放错路径 | | | | — | — | |
| P2-4 | Hook 未生效 | | | | | | |
| V9.2-1 | impact() 未执行 | | | | — | — | |
| V9.2-2 | detect_changes() 未执行 | | | — | — | — | |
| V9.2-3 | 技能被绕过 | | | — | — | — | | |

**全局判定**：所有 Step 标记为 "可选" 的在目标项目中执行；其余必须在技能包层面全部通过。

---

## 快速自检命令（一键）

```powershell
# 在 my-trae-helper 项目根执行
python $env:USERPROFILE\.trae-cn\skills\fullstack4TraeV8\scripts\v9-self-check.py
```
