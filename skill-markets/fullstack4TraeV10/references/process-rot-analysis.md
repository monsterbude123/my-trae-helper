# 流程腐烂分析报告 — V10 更新

> V10 变更：移除 _invalidated/ 隔离机制，替换为 spec-purge.py 机械归档。消除腐烂点 1/2/6。

---

## §0 腐烂(Rot)定义与分类框架

### 0.1 腐烂(rot)的本义

**腐烂(rot)** 是软件/流程/AI 代理在长期运行中,**因被动的无序增长(熵增)而逐渐丧失可验证性、可维护性、可信度**的缓慢退化过程。它不是 bug,bug 是"已知不该这样",腐烂是"没人发现它已经这样了"。

**词源**:
- 英文 `rot` = 腐烂、腐朽(物理: 物质分解; 隐喻: 系统退化)
- 中文 `腐烂` = 物质腐烂 + 抽象系统腐化

### 0.2 腐烂的 5 大共性特征(诊断依据)

| 特征 | 含义 | 检测方法 |
|------|------|---------|
| **渐进性** | 不是突然出现,是缓慢积累 | 时间序列分析(mtime 趋势) |
| **累积性** | 多个小问题叠加成大问题 | 数量阈值(N 个 WARN → FAIL) |
| **自强化** | 破窗效应: 一个腐烂引发更多腐烂 | 同一区域多个腐烂点聚集 |
| **可检测但需工具** | 主观判断常常漏掉 | 机械脚本(rot-detector) |
| **可逆但需主动** | 重构/清理可治愈,放任会致命 | 修复成本随腐烂时长指数增长 |

> **《程序员修炼之道》(Hunt/Thomas)**: "一旦一扇窗被打破,接下来所有的窗都会被打破。" —— 破窗效应是腐烂自强化的核心机制。

### 0.3 腐烂 vs 技术债 vs Bug(易混概念)

| 概念 | 定义 | 主动/被动 | 谁造成 | 谁发现 |
|------|------|:---:|------|------|
| **Bug** | 已知不该这样但就是这样 | 主动失误 | 开发者 | 开发者/QA |
| **技术债 (technical debt)** | 短期收益换取长期成本(主动借债) | 主动权衡 | 开发者有意识 | 开发者有意识 |
| **腐烂 (rot)** | 没人发现它已经这样了 | 被动积累 | 环境/时间/忽略 | 需专门工具 |

**关键区别**: 技术债是**主动选择**,腐烂是**被动积累**;技术债可记账,腐烂常被遗忘。

### 0.4 V10 腐烂 7 大分类(与 proactive-scan + rot-detector 对齐)

| # | 腐烂类 | 定义 | 典型腐烂点 | 检测器 |
|---|------|------|----------|------|
| 1 | **代码腐烂** (Code Rot) | 代码本身的腐化(依赖过时、API 废弃、注释失效) | rot #3 | orphan-detector (--no-deprecated-scan) |
| 2 | **流程腐烂** (Process Rot) | 流程阶段的腐化(阶段跳过、铁律放弃、spec-purge 未执行) | rot #4, #7, #8, #11, #14 | rot-detector 主上下文门禁 |
| 3 | **文档腐烂** (Document Rot) | spec/contract/archive 过期或被改 | rot #1, #2, #4, #6, #10 | proactive-scan (archive-drift) |
| 4 | **测试腐烂** (Test Rot) | 测试套件过期/孤儿/持续失败 | rot #5, #12 | proactive-scan (orphan-tests) |
| 5 | **视觉腐烂** (Visual Rot) | 视觉证据假阳性(PNG 真但内容错) | rot #9 | proactive-scan (visual-freshness) |
| 6 | **构建腐烂** (Build Rot) | 构建产物不一致(dist vs binary) | rot #13 | proactive-scan (bundle-staleness) |
| 7 | **代理腐烂** (Agent Rot) | AI 代理自验自签、不主动诊断、跳过验证 | rot #11, #14 | rot-detector 注入协议 + Article X |

### 0.5 腐烂的修复原则(NO ROT, NO ACCEPT)

```
1. 早发现     — 主动扫描,不靠用户问 (Article XIV: rot-detector 必跑)
2. 早修复     — 单个腐烂点立即修,不等堆积 (破窗效应要求)
3. 机械验证   — 用脚本检测,不靠主观判断 (proactive-scan / self-diagnose)
4. 阻断流程   — NO ROT, NO ACCEPT (任一 FAIL = 🛑 REJECT)
5. 元检测     — 检测器自身也要被检测 (Phase 4.5.1 self-diagnose)
6. 知识沉淀   — 新腐烂点编号 15+ 写入 process-rot-analysis.md
```

### 0.6 腐烂点编号体系

```
[1-8]   V10 引入时的已知腐烂点(部分已 RESOLVED)
[9-14]  V10.4 实战暴露的腐烂点(全部 P0/P1)
[15+]   未来 rot-detector 自动发现并写入
```

每个腐烂点必须含 4 要素:
- **场景**: 具体失败现象
- **腐烂路径**: 根因链(从触发到失控的因果序列)
- **修复方案**: 机械检测 + 主动门禁
- **验证证据**: 故意造一个该腐烂,扫描应能发现

---

## 腐烂点 7（HIGH）：外部结构冲突 — 多技能并存时的双重真相

**场景**：项目同时使用 V10 和另一个技能包，产生冲突目录结构。

**修复**: planner 增加结构兼容检测 → 发现外部结构 → 标注 + 建议归一。不强行转换，不静默忽略。

---

## 腐烂点 1（✅ RESOLVED — V10）：_invalidated_ 盲区

> **V10 解决**：移除 _invalidated/ 机制。spec-purge.py 物理删除目录 + 将旧产物归档到 archive/out/spec-purge/（Agent 不可读取）。去重只扫描活跃目录，无盲区。

---

## 腐烂点 2（✅ RESOLVED — V10）：change-status.py 盲区

> **V10 解决**：无 _invalidated/ → 无此问题。

---

## 腐烂点 3（RESOLVED）：Implementer L1 重做 — 旧代码残留

> **维持 V9 结论**：不删源码。agent 知道自己在重构，按新 spec 改代码是正常实现流程。

---

## 腐烂点 4（MEDIUM）：契约残留

**腐烂路径**:
```
spec 问题 → rework → spec-enhancer 增强 spec
  ↓
contract-writer "续写非重写" → 看到已有 contracts/
  ↓
在旧的 approved 契约上追加新接口
  ↓
旧接口可能已被 spec 废弃，但 contract 还在
```

**V10 修复**: contract-writer 必须检测旧契约 → 标注 MODIFIED 或 DEPRECATED。重构时 Planner 调 spec-purge.py 彻底清除。

---

## 腐烂点 5（LOW）：孤儿测试文件

**V10 保留修复**: contract-writer 完成时检查 __tests__/contracts/ → 移入 _deprecated/。

---

## 腐烂点 6（✅ RESOLVED — V10）：_invalidated/ 嵌套膨胀

> **V10 解决**：移除 _invalidated/。重构 = spec-purge.py 移动目录至 archive/out/spec-purge/，< 24h 的保留在工作目录外，无膨胀问题。

---

## 新增腐烂点 8（V10 引入 — LOW）：spec-purge.py 未执行

**腐烂路径**:
```
用户说"重构 XX" → Planner 应该调 spec-purge.py
  ↓
Planner 遗漏了 spec-purge → 直接在旧 spec 上 Plan
  ↓
旧 tasks 残留 [x] → 新一轮实现跳过部分 task
```

**V10 修复**: planner agent 铁律第 5 条强制 PURGE ON REFACTOR。主上下文机械验证 planner Completion Report 中 `spec_purged: yes`。

---

## 修复优先级（V10 更新）

| # | 严重度 | 腐烂点 | 修复方向 |
|---|:---:|------|---------|
| 1 | ✅ RESOLVED | _invalidated_ 盲区 (V9 #1) | spec-purge.py 替换 |
| 2 | ✅ RESOLVED | change-status.py 盲区 (V9 #2) | 无 _invalidated_ |
| 3 | RESOLVED | implementer 旧代码残留 (V9 #3) | 不删源码 |
| 4 | MEDIUM | 契约残留 (V9 #4) | contract-writer 检测 + spec-purge |
| 5 | LOW | 孤儿测试文件 (V9 #5) | contract-writer 清理 |
| 6 | ✅ RESOLVED | _invalidated_ 膨胀 (V9 #6) | spec-purge.py |
| 7 | HIGH | 外部结构冲突 (V9 #7) | planner 结构检测 |
| 8 | LOW | spec-purge 未执行 (NEW) | planner 铁律 + 机械验证 |

---

## 腐烂点 9（V10.4 实战新增 — P0）：视觉验证假阳性

**场景**：
```
AIGCMediaDesktop 00-04-system-settings 实战:
- V10.3.9 三层校验全过（PNG magic + bytes + PIL 亮度）
- 但用户实际看到：双齿轮 + TabBar 出现系统设置 + 三层标题（布局错乱）
- 结论：PNG 真、内容真、亮度合法，但布局错位全部 PASS
```

**腐烂路径**:
```
PNG magic 校验 → 通过
文件大小 ≥ 5000 → 通过
PIL 亮度 [30, 240] → 通过
视觉"内容错乱" → 没有任何校验
```

**V10.4 修复**: 
- `scripts/visual-content-check.py` 加 3 层: PIL 完整解码 + 颜色直方图（unique ≥ 50）+ 4 象限亮度极差（≥ 5）
- `acceptance-audit.py` uiux 维度先调 visual-content-check
- 任一不通过 = 🛑 REJECT,不允许 `--no-visual` 绕过

**验证证据**:
- `proactive-scan.py --only visual-freshness` 能发现此类问题
- 实战: 故意放一个"单色 PNG"或"整页同色"截图,visual-content-check 应报 FAIL

---

## 腐烂点 10（V10.4 实战新增 — P0）：Archive 修改无回溯

**场景**:
```
archive/ 目录本应"只读",但缺乏机械检测,可能:
- Agent 误改 archive/done/{feature}/spec.md
- 主上下文修复问题时直接编辑 archive/out/spec-purge/
- 1 周后"历史快照"已被修改,无法回溯
```

**腐烂路径**:
```
archive/ 无机械只读保护
  ↓
任何 Editor (含 Agent) 可修改
  ↓
历史快照被污染
  ↓
未来 review/事故复盘失去基线
```

**V10.4 修复**: 
- `proactive-scan.py` 的 `archive-drift` check: 扫 archive/ 下 7 天内 mtime 变化
- 发现 7 天内修改 → FAIL
- 兜底:archive/ 配 .gitignore? 不,改为 chmod 555 (Linux) 或设置 Windows ACL

**验证证据**:
- `proactive-scan.py --only archive-drift` 能发现此类问题
- 实战: 故意在 archive/ 下 touch 一个新文件,扫描应报 FAIL

---

## 腐烂点 11（V10.4 实战新增 — P0）：自验自签

**场景**:
```
主上下文自己当 reviewer
  ↓
自己写 review-latest.md
  ↓
自己 PASS（"total_score: 5.0"）
  ↓
实际是自我背书,无任何独立验证
```

**腐烂路径**:
```
reviewer = implementer (同 session)
  ↓
reviewer 自评"通过"= reviewer 自验自签
  ↓
"全绿"= 心理安慰,无独立证据
```

**V10.4 修复**: 
- Reviewer Completion Report 强制含 `session_id` + `self_attested` + `independently_verified_by`
- 主上下文对 `self_attested: true` 必做二次抽检
- 抽检项目: 随机挑 1 个核心断言,独立命令验证（如 `git diff --stat` / `find . -name "X"` / `pytest tests/feature.test.ts`）

**验证证据**:
- 故意让 reviewer 自评 `self_attested: true` 但不填 `independently_verified_by`
- 主上下文应检测出来,要求补填或抽检

---

## 腐烂点 12（V10.4 实战新增 — P0）：过期测试/孤儿组件

**场景**:
```
AIGCMediaDesktop 实战:
- 00-04-system-settings 新建了 SystemSettingsPage
- 但旧的 SettingsPage.tsx + SettingsPage.test.tsx 都没即时清除
- 结果: 9 failed 测试持续 1 周没人管
- 实现层"代码可用"≠"测试层清洁"
```

**腐烂路径**:
```
新组件 SystemSettingsPage 替代 SettingsPage
  ↓
仅添加新文件
  ↓
旧 SettingsPage.tsx 仍在代码中（旧实现）
旧 SettingsPage.test.tsx 仍在测试中（继续跑）
  ↓
旧测试继续失败 = 噪音
```

**V10.4 修复**: 
- `scripts/orphan-detector.py`: 扫测试文件 import 目标是否仍存在
- `scripts/orphan-detector.py`: 扫 @deprecated / DEPRECATED 标记
- Article IX (TDD 即时): 改实现 / 删组件 → 同 PR 改测试 / 删测试
- 触发时机: Phase 2 (Contract 开始前) / Phase 3 (Implement 末尾) / Phase 4.5 (rot scan)

**验证证据**:
- `python scripts/orphan-detector.py` 能发现孤儿
- AIGCMediaDesktop 演练: 预期发现 SettingsPage.test.tsx 引用了不存在的 SettingsPage

---

## 腐烂点 13（V10.4 实战新增 — P1）：隐式 build 假设

**场景**:
```
改 TS 文件 src/components/Settings.tsx
  ↓
跑 cargo build（Rust 改动编译）
  ↓
但 cargo build 不重触 pnpm build
  ↓
dist/assets/Settings-XXX.js 仍是旧 hash
  ↓
binary 内嵌的 chunk 引用旧的 Settings-YYY.js
  ↓
运行时 JS chunk 404 或加载旧版本
```

**腐烂路径**:
```
改 frontend (TS/TSX)
  ↓
cargo build（仅编译 Rust 端）
  ↓
pnpm build 没自动跑（cargo 不会触发）
  ↓
dist/ 过期但 binary 引用了 dist
  ↓
binary 嵌入了过期 chunk 引用
```

**V10.4 修复**: 
- `scripts/dist-hash-check.py`: 提取 binary 内嵌的 chunk 名称 vs dist/ 实际 chunk 列表
- 不一致 = 🛑 FAIL
- 仅 Tauri 项目启用（Web 项目无 binary）
- 触发时机: Phase 3 (Implement 末尾, 改 TS 后必跑) / Phase 4.5 (rot scan)

**验证证据**:
- `python scripts/dist-hash-check.py` 能发现 stale binary
- 故意在 dist/ 加新 chunk 但不重 build binary,扫描应报 FAIL

---

## 腐烂点 14（V10.4 实战新增 — P1）：Agent 不主动发现问题

**场景**:
```
V10.3.9 流程：
- Agent 完成 implementer
- 主上下文只读 Completion Report
- 不主动扫腐化
- 实战: 孤儿测试 / 过期 build / 视觉问题都没人发现，直到用户截图
```

**腐烂路径**:
```
implementer 完成 → 报"全绿"
  ↓
主上下文不主动诊断
  ↓
腐化点 9/10/11/12/13 全部潜伏
  ↓
用户问"流程有没有问题"才查
```

**V10.4 修复**: 
- 新 Agent: `agents/rot-detector.md`
- 新脚本: `scripts/proactive-scan.py`（5 项腐化扫描包）
- 新阶段: **Phase 4.5 (Proactive Rot Scan)** — Review 末尾 + Accept 之前强制
- 任一 FAIL = 阻断 Accept,implementer 必修复

**验证证据**:
- 演练 AIGCMediaDesktop: 5 项扫描应至少发现 1 项 WARN 或 FAIL
- proactive-scan.py 应能输出 Markdown 报告 + JSON

---

## V10.4 修复优先级（实战暴露，全部 P0/P1）

| # | 严重度 | 腐烂点 | 修复方向 | 引入版本 |
|---|:---:|------|---------|:---:|
| 9 | P0 | 视觉验证假阳性 | visual-content-check.py | V10.4 |
| 10 | P0 | Archive 修改无回溯 | archive-drift check | V10.4 |
| 11 | P0 | 自验自签 | Session-ID + 二次抽检 | V10.4 |
| 12 | P0 | 过期测试/孤儿组件 | orphan-detector.py + Article IX | V10.4 |
| 13 | P1 | 隐式 build 假设 | dist-hash-check.py | V10.4 |
| 14 | P1 | Agent 不主动发现问题 | rot-detector + Phase 4.5 | V10.4 |
| 15 | P0 | 自我吹嘘腐烂 | self-aggrandizing-doc check | V10.5 |
| 16 | P1 | 状态卡陈旧腐烂 | state-card-staleness check | V10.5 |
| 17 | P1 | 骨架堆积腐烂 | stub-pileup check | V10.5 |

---

## 腐烂点 15（V10.5 实战新增 — P0）：自我吹嘘腐烂 (Self-Aggrandizing Document Rot)

**场景**:
```
AIGCMediaDesktop .state-card.md 末段:
"跨模块不变量 | 9 个 (INV-STORE-02 / INV-API-IDEMPOTENT / INV-EV-04 / INV-ERR-CASCADE /
 INV-SSE-RESUME / INV-DEBOUNCE-SEARCH / INV-CONFIG-DEFAULTS / INV-OPTIMISTIC-ROLLBACK /
 INV-CAP-MAX)"

实际扫描 19 个 spec.md:
- INV-STORE-02  → 4 changes ✓
- INV-EV-04     → 1 change  ✓
- 其余 7 个      → 0 changes ✗
```

**腐烂路径**:
```
批次报告写"9 个跨模块不变量" → 复制到 state-card.md
  ↓
但实际只有 2 个 invariant 真正跨模块提及
  ↓
后续模块以为 9 个 invariant 都有约束 → 实际无任何约束
  ↓
跨模块修改时无人对齐 (因为 invariant 不存在)
```

**V10.5 修复**:
- `scripts/proactive-scan.py` 新增 `self-aggrandizing-doc` check
- 算法: 抽取 state-card.md (或 INDEX.md) 中所有 `INV-[A-Z0-9-]+` → 抽取所有 spec.md 的 INV → 比对 `doc_claims - code_actual`
- self_aggrandizing_rate = |doc_claims - code_actual| / |doc_claims|
- > 0.3 → 🛑 FAIL
- 文章层面: 新增 Article XII — **Document Honesty** (文档必含证据锚定,不可自评"完成"无 spec 落地)

**验证证据**:
- `proactive-scan.py --only self-aggrandizing-doc` 在 AIGCMediaDesktop 上能发现 7/9 (78%) 失效
- 故意在 fixture 写 "5 个 INV" 但 spec.md 只 1 个 → 应报 FAIL

---

## 腐烂点 16（V10.5 实战新增 — P1）：状态卡陈旧腐烂 (State Card Staleness)

**场景**:
```
AIGCMediaDesktop/docs/specs/.state-card.md:
- mtime: 2026-07-29 21:11:40 (46h ago)
- 列出 15 个 change
- 实际 19 个 change (新加 01-04 / 02-01 / 03-04 / 03-06 等)
```

**腐烂路径**:
```
主上下文 7/29 完成批次后写 state-card.md
  ↓
7/30 之后多个 stub 加入但未更新状态卡
  ↓
7/31 rot-reinforcer 启动看到的还是 7/29 的"全绿"状态
  ↓
实战决策基于过期数据 → 误判项目进度
```

**V10.5 修复**:
- `proactive-scan.py` 新增 `state-card-staleness` check
- 算法: mtime vs 当前时间 (>24h WARN, >72h FAIL) + change 数量比对
- 长期: spec/define/tasks 文件变更时 PostToolUse hook 触发 state-card 自动更新

**验证证据**:
- `proactive-scan.py --only state-card-staleness` 应报 AIGCMediaDesktop 46h stale + 4 个 change 缺失
- fixture: state-card 故意 96h 前 mtime,应报 FAIL

---

## 腐烂点 17（V10.5 实战新增 — P1）：骨架堆积腐烂 (Stub Pile-up Rot)

**场景**:
```
AIGCMediaDesktop 19 个 change:
- Archived: 4 个
- Plan 完成: 1 个
- Stub (只 define.md): 12 个
- 控制器: 1 个
- 其他: 1 个

Stub 比例: 12/19 = 63%
```

**腐烂路径**:
```
里程碑 (00-01~00-04) 完成后进入扩张期
  ↓
11+ 个新模块同时起 define.md (急于铺开)
  ↓
但无 1 个模块完成 define→spec→tasks 全流程
  ↓
状态卡 "🟡 骨架" 给人"项目在前进"印象
  ↓
实际 0% 推进,破窗效应: 新模块也开始只起 define
```

**V10.5 修复**:
- `proactive-scan.py` 新增 `stub-pileup` check
- 算法: 扫 `docs/specs/changes/*/` 各文件存在性 → 分类 (archived/full-plan/stub/controller) → stub_rate = stub/total
- stub_rate > 0.4 → ⚠️ WARN; > 0.6 → 🛑 FAIL (破窗临界)
- 文章层面: 新增 Article XIII — **Stub is Debt** (🟡 骨架 = 隐性技术债,2 周未推进必冻结或归档)

**验证证据**:
- `proactive-scan.py --only stub-pileup` 在 AIGCMediaDesktop 上应报 63% → 🛑 FAIL
- fixture: 10 个 changes,8 个 stub → 应报 FAIL

