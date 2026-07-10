# 通用约定与集成

> 两种 Workflow 共用的命名规范、vision-audit 集成、设计原则、接入步骤和 FAQ。

---

## 1. 命名规范

```
✅ route-01-LoginView.png              # 打开文件夹就懂
✅ interact-auth-01-login-start.png
✅ interact-auth-01-login-after.png
❌ route-01.png                         # 必须打开图片才知道
❌ screenshot1.png

命名模式: {phase}-{序号}-{描述}.png
```

## 2. vision-audit 集成

```bash
# Workflow A: 模块目录批量分析
vision-audit --dir screenshots/auth/

# Workflow B: 单张截图即时分析
vision-audit --file tmp/diag-1719123456789.png

# CI 增量
git diff --name-only HEAD~1 | extract-modules | xargs -I{} vision-audit --dir screenshots/{}
```

## 3. 设计原则

| 原则 | 说明 |
|------|------|
| **截图是线索，日志是证据** | 截图告诉"哪里不对"，日志告诉"为什么不对" |
| **时间戳是纽带** | 截图+日志+网络通过时间戳关联形成证据链 |
| **两种模式，一种引擎** | Workflow A/B 共享诊断推理引擎，仅输出形式不同 |
| **A 模式重归档，B 模式重速度** | A 产出持久化报告，B 产出即时修复 |
| **一次一个模块/问题** | A 一次一个模块，B 一次一个问题，不堆砌 |
| **Name 比 ID 重要** | 文件名带描述，不打开就知道内容 |
| **框架无关** | Playwright / Cypress / Selenium 通用 |

## 4. 接入步骤

### 新项目从零接入

```
1. 实现 screenshot helper（两种 Workflow 共用）
2. 实现后端日志端点 GET /api/debug/logs?tail=200&grep={}
   或降级方案 tail -f backend/logs/app.log
3. 实现 injectPageMonitors（console + network 拦截，两种 Workflow 共用）
4. 实现 Workflow A 专用: startLogCapture / captureLogSnapshot / stopLogCapture
   / DiagnosisContext / generateDiagnosisReport
5. 创建第一个模块 spec（按 Workflow A 模板），验证截图 + 日志 + 报告正确生成
6. 测试 Workflow B: 手动触发一个异常 → AI 按 B 协议即时诊断 → 修复 → 验证
7. 两种 Workflow 都跑通后推广全模块
```

### 已有项目迁移（仅 Workflow A）

```
1. 按文件名前缀将旧扁平截图归入子目录，对不上的放 _legacy/
2. 补充后端日志捕获端点
3. 补充 injectPageMonitors + 诊断 helper
4. 改造现有 spec 嵌入 Phase 0 + 日志快照 + 异常检测
5. 首次全量跑 → 检查 _diagnosis.md → 迭代诊断规则
6. 同步补充 Workflow B 能力
```

## 5. 常见问题

**Q: 后端没有日志端点怎么办？**
A: 即时降级方案 → `tail -f backend/logs/app.log`。长期推荐加 `GET /api/debug/logs?tail=200&grep={keyword}` 端点（可按模块/关键词过滤，Workflow B 用起来极快）。

**Q: 每步都捕获日志会不会太慢？**
A: 日志捕获异步追加写文件，< 10ms。瓶颈在截图本身（100-500ms）。

**Q: Workflow B 需要清旧数据吗？**
A: 不需要。即时诊断用 `tmp/diag-*.png` 临时文件，不污染模块截图目录。

**Q: 跨模块的交互怎么归属？**
A: 截图 + 诊断归入"主力模块"。例如 Dashboard → Settings 归入 Settings。后端日志按 request path 过滤。

**Q: Workflow A 诊断报告太长？**
A: 无异常的模块只输出 "✅ {模块} — 无异常"。有异常的模块才输出详细报告。

**Q: 日志文件会膨胀吗？**
A: Workflow A 的 beforeAll 会清 `_logs/`。Workflow B 不写日志文件。CI 建议上传 `_logs/` 和 `_diagnosis.md` 作为 artifact 后清理。

**Q: AI 怎么知道该用哪个 Workflow？**
A: 见项目 [AGENTS.md § 测试](../../../AGENTS.md) 中的模式选择决策树。关键词匹配 → 自动选择。不明确时问用户。
