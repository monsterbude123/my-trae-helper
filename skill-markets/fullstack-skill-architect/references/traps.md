# 避坑指南 — 7 大反例与陷阱

> 本会话蒸馏的 7 个真实失败案例 + 避坑方案。

---

## 陷阱 1:加 README 治文档债务

### 现象

```
用户: "docs/ 太乱了"
Agent: "我加个 INDEX.md 索引"
结果: docs/ 多了 1 个 INDEX,但子目录还是乱
     6 个月后 docs/ 有 10 个 INDEX,30 个 README,100 个 md
     心智负担:从 N → 10N
```

### 根因

- 把"治标"当成"治本"
- 不评估哪些目录可删/可归档
- 用户说"太乱" = 用户想要"少",不是"索引"

### 避坑方案

```
MUST 先问 3 个问题:
  1. 哪些目录是历史残留(V10→V11 过渡)?
  2. 哪些目录可安全归档(0 引用)?
  3. 哪些目录可彻底删除?

正确顺序:
  Step 1: 删/归档(治本)
  Step 2: 加必要的 INDEX(瘦身后再加)
  Step 3: 写 WHY README(每个目录留 1 段说明)

反例验证: AIGCMediaDesktop 演练 — 用户说"去伪存真",本质是删不是加
```

---

## 陷阱 2:阶段门禁放水

### 现象

```
Stage 3 implementer 返回 → 主上下文 → 默认放行到 Stage 3.5
gate 脚本 = 摆设(主上下文从不调用)
结果: 实施未通过 TDD / drift-check 就进入验证 → 腐化累积 → Stage 4 才暴露
     简单功能跑一天完成不了(用户实战反馈)
```

### 根因

- 门禁脚本是独立可执行,主上下文可手动放行
- 无硬阻断机制
- "先继续回头看"成为习惯

### 避坑方案

```
MUST: stage-gate-pre-stage.sh 借鉴 husky pre-commit 硬阻断
  - exit 0 = 放行
  - exit 1 = 🛑 阻断(主上下文不可手动覆盖)

MUST NOT:
  - 看到"实施已返回" → 默认放行
  - 看到"测试通过" → 默认跳过 gate
  - 看到"主上下文认为够了" → 手动写 completed

正确: 任何 stage 切换前必跑 stage-gate-pre-stage.sh
     exit 0 才放行,exit 1 必跑修复 → 重跑 → 再 exit 0
```

---

## 陷阱 3:验收 stage 评判代码细节

### 现象

```
Stage 4 reviewer 读 src/*.ts 评判:
  - 命名风格
  - 函数抽象
  - 性能
  - 测试覆盖
  - 重构建议
结果:
  - review 时间膨胀(简单功能跑一天)
  - 与 Stage 3 职责重叠
  - 主上下文 review 链冗长
```

### 根因

- 4 维评分(代码 25%/API 30%/UIUX 25%/边际 20%)过度强调代码维度
- 必读 5 件套过重(prototype HTML + design-prompt + ui-ux-logic + design.md + HANDOFF-DESIGNER.md)
- 无明确边界"验收只看页面+功能"

### 避坑方案

```
MUST: 拆分验收为 2 个独立验证
  - 页面功能验证(Stage 4 主责): spec AC + 截图 + prototype ↔ implementation 对照
  - 代码质量验证(Stage 3.5 + Stage 4.5 副责): 代码细节 + 覆盖 + rot

MUST: 验收报告不含 file:line 代码引用(边界守住)

正确: 像产品经理验收,只看 AC vs 实际 + 视觉差异%
     验收产出 review-report.md ≤ 300 字
```

---

## 陷阱 4:子代理读白名单外文件

### 现象

```
委派头:[MUST-READ] + [PIPELINE] + [FORBIDDEN]  ← 只有黑名单
子代理自由探索 → 读了:
  - stage/4-review/ 旧 review-report(避免之前提的问题)
  - stage/3-implement/notes.md(主上下文专用)
  - docs/bugs/ 历史(归档)
结果:
  - context 膨胀(读 50+ 文件)
  - 决策被旧报告污染
  - 后续 stage 失去独立性
```

### 根因

- 委派头只有黑名单,无白名单
- 子代理默认"读越多越好"
- 主上下文不验证子代理读了哪些文件

### 避坑方案

```
MUST: 委派头注入 [DOC_WHITELIST] 强白名单(本会话蒸馏)

白名单矩阵(13 stage 各 2-3 条路径):
  Stage 3 Implement: fact/contracts/ + stage/2-contract/handoff-out.md
  Stage 4 Review: fact/spec.md AC + 截图 + 视频  ⚙ 不读 stage/3-implement/

MUST: 子代理 Completion Report 含 "未读白名单外" 字段(自证清白)

MUST: 主上下文负责跨 stage 摘要注入(从 handoff-out 提纯)
```

---

## 陷阱 5:物理重置时删 fact 层

### 现象

```
"stage 7 spec 打回 stage 3" 时:
  Agent 把 fact/spec.md / fact/plan.md / fact/contracts/ 全删
结果:
  - 事实源丢失
  - 需重新做 Stage 0/1/2(耗时数小时)
  - 用户工作白费
```

### 根因

- 重置规则不全,无明确"保留什么"清单
- Agent 不区分"事实层" vs "流程层"
- 主上下文未确认保留产物

### 避坑方案

```
MUST: scripts/stage-gate.py --reset-to {stage-id} 默认行为
  - 保留 fact/ 整个目录(除非用户明确说"重做 fact")
  - 保留 stage/{N-1} 之前的 stage/
  - 删除 stage/{N} 之后的所有 stage/

借鉴: git reset --hard(保留 HEAD ~ 删 commit)

反例验证: 用户原文"如果事实文档没有任何问题,我只需要在stage 目录把stage3的流程中的文档重置"
```

---

## 陷阱 6:加法式升级膨胀技能包

### 现象

```
"以升级为名"加 5 个 README + 3 个 references + 2 个 templates
结果:
  - 体积 +320 行(净增)
  - 文档越来越多,越来越慢
  - 心智负担:从 1 套 → 2 套(新旧并存)
```

### 根因

- 默认"加"为升级,不敢"减"
- 不评估旧内容是否仍有价值
- 没做"精华/糟粕"二元判定

### 避坑方案

```
MUST: 升级前必列"精华/糟粕"二元判定表
  - 精华 = 必保留(破坏 = 用户感知)
  - 糟粕 = 必剔除(删除 = 用户受益)

正确顺序:
  Step 1: 删 V 过渡产物(精华糟粕判定后)
  Step 2: 加必要的 INDEX
  Step 3: 写 WHY README(每个新增文件 1 段说明)

反例验证: 用户原文"直接移除掉陈旧项目的没有必要的内容,保持清爽,直接革命性的升级"
```

---

## 陷阱 7:重复蒸馏新建技能(已有相似技能)

### 现象

```
每次会话蒸馏 → 新建一个 skill
结果:
  - skill-markets/ 有 100+ 相似技能
  - Agent 不知道用哪个
  - 内容重复,占 context
```

### 根因

- 不先去重检查
- 不扫描已有技能
- 默认"新建"为蒸馏结果

### 避坑方案

```
MUST: 蒸馏前必走 §0 去重检查协议(session-distiller V2.1)
  Step 1: 分析会话内容 → 生成"会话主题指纹"
  Step 2: 扫描已有技能(带主题扫描)
  Step 3: 针对性匹配(主题指纹 vs 已有技能)
  Step 4: 决策路径
    - 无匹配 → 继续蒸馏 → 生成新技能
    - 有匹配 + 新会话有增量价值 → 更新已有技能
    - 有匹配 + 无增量价值 → 跳过,告知用户

正确做法: 本会话已扫描 skill-markets/ 100+ 技能 → 无完全重叠 → 新建 fullstack-skill-architect
```

---

## 7 大陷阱速查表

| # | 陷阱 | 一句话 | 避坑工具 |
|:-:|---|---|---|
| 1 | 加 README 治标 | "去伪存真" = 删不是加 | 二元判定表 |
| 2 | 门禁放水 | 实施已返回 ≠ 放行 | husky 式硬阻断 |
| 3 | 验收越界 | 验收 = 产品经理,不是工程师 | 白名单 + 一封信 |
| 4 | 子代理无界 | 读越多 ≠ 越好 | K8s RBAC 白名单 |
| 5 | 误删 fact | "打回 stage 3"≠删全部 | git reset --hard 借鉴 |
| 6 | 加法膨胀 | 升级 ≠ 必加 | 革命性瘦身 |
| 7 | 重复蒸馏 | 已有技能要先看 | 去重检查 V2.1 |

---

*来源: 本会话 6 轮实战蒸馏 + canvas-asset-folders 实战反馈 + AGENTS.md §3.1 R-3 表态信号。*