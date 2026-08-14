---
name: fullstack-skill-architect
version: 1.0.0
description: "全栈技能设计专家 — 起源于 fullstack4TraeV11 V11→V11.3 升级会话蒸馏,适用于任何多 stage + 多 sub-agent 协同的全栈开发技能包设计/改造/升级(V11/V12/V{n+1})。核心 5 把刀: 物理隔离、husky式门禁硬化、子代理严格边界、验收瘦身、革命性瘦身。触发词: 技能设计/技能升级/技能瘦身/V11→V12/V11.3/物理隔离/门禁硬化/子代理越界/验收精简/革命性清理/陈旧移除。"
origin: fullstack4TraeV11 V11.3 升级会话(2026-08-13)
applicability: 通用全栈技能设计方法论(不止 V11,适用于任何多 stage + 多 sub-agent 协同场景)
requires:
intent: 全栈技能设计专家 — 起源于 fullstack4TraeV11 V11→V11
category: gate
audience: [agent, designer]
---
# fullstack-skill-architect — 全栈技能设计专家

> **一句话定位**: 你设计/改造/升级全栈开发技能包时,这个 skill 让你用"物理隔离 + 门禁硬化 + 子代理边界 + 革命性瘦身"四把刀,把臃肿的技能包砍到清爽。

---

## §0 核心价值主张

```
用户痛点(本会话6 轮实战蒸馏):
  1. 技能包臃肿,简单功能跑一天(阶段门禁放水)
  2. 子代理过度处理上下文(无白名单边界)
  3. 验收 stage 评判代码细节(越界 + 漫长)
  4. stage 流程文档与事实文档未隔离("stage 7 打回 stage 3"不知删哪些)
  5. 文档管理债务爆炸(历史V10→V11 残留,去不掉)
  6. 升级不敢动(怕破坏现有项目)

本 skill 的 5 把刀:
  物理隔离(借鉴 Docker 镜像层)
  门禁硬化(借鉴 husky pre-commit)
  子代理边界(借鉴 K8s RBAC)
  验收瘦身(像产品经理验收,不像工程师审计)
  革命性瘦身(减法 > 加法, 删 V 过渡产物)
```

---

## §1 9 条核心铁律(MUST/NEVER)

```
1. MUST 物理隔离: 事实文档(fact/) 与流程文档(stage/) 用物理目录分离
   WHY: 重置 stage 时不会误删事实源
   验证: grep "stage/.*fact/" 0 命中 = 隔离生效

2. MUST husky 式门禁: 每个 stage 切换前必跑 gate 脚本,exit 0/1 硬阻断
   WHY: 主上下文不可手动放行,杜绝"先继续回头看"
   验证: stage-gate-pre-stage.sh --check exit 0 = 放行

3. MUST 子代理白名单: 每个 stage agent 只读自己的 stage/ + fact/,主上下文负责跨 stage 注入
   WHY: 子代理不再读白名单外文件,context 不再膨胀
   验证: sub-agent Completion Report 含 "未读白名单外" 字段

4. MUST 验收瘦身: 验收 stage 只读 spec AC + 截图 + prototype, 不读代码细节
   WHY: 代码细节由实施 stage 自身门禁覆盖,验收只看"通不通"
   验证: 验收报告不含 file:line 代码引用 = 验收边界守住

5. MUST 精华/糟粕二元判定: 技能升级前必列 2 张清单(保留什么/剔除什么)
   WHY: 避免"以升级为名膨胀",必须先减后加
   验证: 糟粕清单非空 + 剔除动作有 commit

6. NEVER 主版本号激进: 软升级默认走 patch 版本(V11.x),不改 V 除非破坏性必需
   WHY: 现有项目零迁移 = 用户零感知 = 真实可推广
   验证: CHANGELOG.md 当前版本是 V{N}.x.patch 而非 V{N+1}.0

7. NEVER 加 README 治标: 文档债务用"删/归档"治本,不用"加 README 索引"治标
   WHY: 加索引 = 心智负担加重,治标不治本
   验证: 革命性瘦身报告含 "已删 X 文件 / 减 Y 行 / -Z%"

8. NEVER 信任阶段跨级: 阶段 4 不可读 stage/3-implement/notes.md,主上下文负责跨级摘要
   WHY: 子代理读取越界 = 决策被污染
   验证: 黑名单文件 0 命中 = 边界守住

9. NEVER 无证据 PASS: 任何完成声明必含 evidence(file:line + 命令输出 + 产物存在)
   WHY: 杜绝"看起来对"虚假完成
   验证: state-card-validator.py PASS = 状态卡字段完整
```

---

## §2 5 步骨架流程

```
Step 1: 诊断期 — 列"精华/糟粕"二元判定表
  ├─ 读现有 skill 的 SKILL.md + 13 stage skill + scripts/ + references/
  ├─ 提炼精华(必保留):核心架构 / 17 Articles / scripts / 反虚假交付 / 灵活度铁律
  ├─ 提炼糟粕(必剔除):门禁放水 / 验收越界 / 单卡膨胀 / 子代理无界 / 历史残留
  └─ 输出:精华清单 + 糟粕清单 + 质疑性校验 4 维度

Step 2: 设计期 — 设计 5 把刀的具体实现
  ├─ 物理隔离: fact/ + stage/ 双目录布局(老路径不动 = opt-in)
  ├─ 门禁硬化: stage-gate-pre-stage.sh(exit 0/1)
  ├─ 子代理边界: doc_whitelist 强白名单(委派头注入)
  ├─ 验收瘦身: 拆分"页面功能验证" vs "代码质量验证"(后者由实施自身门禁覆盖)
  └─ 革命性瘦身: V 过渡产物 + research/ 草稿 → 删除清单

Step 3: 验尸期 — 跑 4 维度质疑性校验(每次方案必走)
  ├─ [1] 根因验证: 引用的章节/SKILL.md 条款真实存在(附 file:line)
  ├─ [2] 责任主体校验: 修复位置 vs 上游层效果一致
  ├─ [3] 重叠校验: 现有规则 grep 不重叠,差异化论证
  └─ [4] 修复成本 vs 价值: 修复行数 / 是否破坏 ≤ 10 铁律 ≤ 150 行

Step 4: 落地期 — 写最小改动方案(零迁移优先)
  ├─ 优先级 1: 新建独立文档(opt-in,不动老路径)
  ├─ 优先级 2: 修改已有文件(必走质疑性校验)
  ├─ 优先级 3: 删除陈旧文件(必查 0 引用)
  └─ 输出:3 阶段 × N commit 计划,体积影响预估

Step 5: 验证期 — 跑通 + 出瘦身报告
  ├─ grep 0 引用断裂
  ├─ scripts/state-card-validator.py / proactive-scan.py / self-diagnose.py 全 PASS
  └─ 写 docs/reports/v{N}.x-slim-{date}.md(体积统计 + 验证证据)
```

---

## §3 反向提示词(从本会话失败蒸馏的 NEVER 项)

```
NEVER: 加 README 治文档债务
  触发: 用户说"docs/ 太乱了"+ 你想"加 INDEX.md"
  错误代价: 文档越多 = 心智负担越重 = 治标不治本
  正确替代: 先评估哪些目录可删/可归档,治本后再写 INDEX
  会话证据: AIGCMediaDesktop 演练 — 用户说"去伪存真",本质是删不是加

NEVER: 阶段门禁放水(主上下文直接放行到下一 stage)
  触发: "Stage 3 implementer 已返回" → 主上下文默认放行
  错误代价: 实施未通过自身门禁就进入验证 → 腐化累积 → Stage 4 才暴露
  正确替代: stage-gate-pre-stage.sh --check 必须 exit 0 才放行
  会话证据: 2026-08-12 canvas-asset-folders "简单功能跑一天完成不了,华而不实"

NEVER: 验收 stage 读 src/*.ts 代码细节
  触发: 验收 agent 评判命名 / 函数抽象 / 性能 / 重构建议
  错误代价: review 时间膨胀 + 与 Stage 3 职责重叠 + 主上下文链冗长
  正确替代: 像产品经理验收,只看 AC vs 实际 + 视觉差异%
  会话证据: 用户原文"验收 stage 不需要关注代码细节,像提 bug 一样汇报"

NEVER: 子代理读白名单外文件
  触发: 委派头只有黑名单,无白名单 → agent 自由探索
  错误代价: context 膨胀 + 决策被旧报告污染 + 后续 stage 失去独立性
  正确替代: 委派头注入 [DOC_WHITELIST] + 主上下文跨 stage 摘要注入
  会话证据: 用户原文"子代理还是存在过度处理自己任务范围外的上下文"

NEVER: 物理重置时删 fact 层
  触发: "stage 7 打回 stage 3"时 agent 把 spec.md / plan.md / contracts/ 全删
  错误代价: 事实源丢失 + 重新做 Stage 0/1/2(耗时数小时)
  正确替代: scripts/stage-gate.py --reset-to 默认保留 fact/ 整个目录
  会话证据: 用户原文"如果事实文档没有任何问题,我只需要在stage 目录把stage3的流程中的文档重置"
```

---

## §4 适用场景 vs 不适用场景

```
✅ 适用:
  - 设计/改造/升级全栈开发技能包(类似 fullstack4TraeV11)
  - 多 stage 流水线需要门禁硬化
  - 多 sub-agent 协作需要边界控制
  - 文档管理债务爆炸需清理
  - 验收 stage 时间膨胀需瘦身

❌ 不适用:
  - 单文件 bug 修复(用 trae-security-review / gitnexus-debugging)
  - 项目级配置模板(用 fullstack-auto)
  - 纯搜索研究任务(用 deep-research)
  - 单 agent 单任务(本 skill 价值为多角色协同场景)
```

---

## §5 必读 references

- [methodology.md](references/methodology.md) — 5 把刀详细设计 + 借鉴来源
- [patterns.md](references/patterns.md) — V11→V11.3 实战模式提炼
- [traps.md](references/traps.md) — 7 大反例与避坑指南
- [templates/](templates/) — 产出物模板

---

## §6 完成报告协议(本 skill 调用时)

```
## Completion Report — fullstack-skill-architect
- target_skill: {被改造的 skill, e.g. fullstack4TraeV11}
- 5 把刀启用情况:
  - 物理隔离: [启用 / 跳过 / 不适用]
  - 门禁硬化: [启用 / 跳过 / 不适用]
  - 子代理边界: [启用 / 跳过 / 不适用]
  - 验收瘦身: [启用 / 跳过 / 不适用]
  - 革命性瘦身: [启用 / 跳过 / 不适用]
- artifacts:
  - {path-1}
  - {path-2}
- 体积影响: {+/- 行数, +/-%}
- 质疑性校验: 4/4 通过 / N 项未过
- evidence:
  - file: {file}:line
  - command: {cmd} + output: {output}
- next_step: [用户确认 / 继续优化 / 阻塞]
```

---

## §7 一句话铁律

```
全栈技能设计 = 物理隔离(分清事实与流程) + 门禁硬化(husky 式硬阻断)
            + 子代理边界(K8s RBAC) + 验收瘦身(产品经理视角)
            + 革命性瘦身(减法 > 加法,删 V 过渡产物)
            = 一个让用户简单功能不再跑一天的清爽技能包
```

## §8 起源与适用范围(简版,完整版见 references/applicability.md)

```
起源: fullstack4TraeV11 V11→V11.3 升级会话(2026-08-13)

✅ 适用: 多 stage(≥ 3)+ 多 sub-agent(≥ 2)+ 文档债务 / 门禁放水 / 子代理越界 / 验收越界
⚠️ 部分适用: 单一治理(用单把刀)
❌ 不适用: 单文件 bug 修复 → trae-security-review / 项目级模板 → fullstack-auto / 纯搜索 → deep-research

防误用铁律:
  NEVER: 看到"V11"就以为只能用于 V11(它适用任何全栈技能 V12/V13/...)
  NEVER: 把本 skill 用于项目级配置模板(那是 fullstack-auto)
```

---

*来源: 2026-08-13 my-trae-helper V11.3 升级会话蒸馏(用户 6 轮发言 + 4 份文档产出 + AIGCMediaDesktop 演练 + canvas-asset-folders 实战反馈)。*
*版本: 1.0.0 — 用户原始诉求"以后关于全栈技能设计,全找它"*