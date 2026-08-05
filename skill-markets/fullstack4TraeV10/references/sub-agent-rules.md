# 子代理通用铁律（V10.6）

> 全 agent 通用，主上下文委派时引用本文件路径（不内联全文）。
> 详见 [artifact-lifecycle.md](artifact-lifecycle.md) 文档分层 + [bug-workflow.md](bug-workflow.md) 任务路由。

---

## 1. 文档分层（3 条）

- **只读 fact 层**：contracts/、spec.md、ARCHITECTURE.md、模块文档 — 任务执行时必读
- **禁读 process 层**：diagnose.md、fix_result.md、分析手记、v1v2v3 — 主上下文提取事实摘要注入，子代理不主动读
- **log 层不作依据**：changelog、commit log、review 报告 — 可看但不作验收依据

## 2. 证据规则（3 条）

- **raw_payload 优先**：字段语义以当前原始数据为准，不以历史诊断结论为准
- **历史结论不复用**：上一会话的判定 = 线索，不是事实；需重新取证验证
- **完成 = 多维可观测**：status=SUCCESS 必须含 ≥3 维证据（文件+测试+hash/DB/CSV）

## 3. 上下文经济（3 条）

- **只读白名单**：主上下文注入 [DOC_WHITELIST]，白名单外不读
- **不遍历目录**：禁止 `ls docs/bugs/` 或 `glob docs/reports/*` 考古
- **不复制全文**：引用路径，不把文档内容搬进 prompt 或产物

## 4. 汇报纪律（2 条）

- **≤300 字符**：Completion Report 只含 status / evidence(file:line) / pass_count / next_hook
- **详情走 json**：详细产物放 `.trae/logs/agent-detail/`，不进 markdown 报告

## 5. 失败处理（4 条）

- **连续 2 次失败 → 切 agent 类型**：不继续派同一 agent
- **5 次失败 → rescue hatch**：回退 Phase 0 重做需求分析
- **禁止应付性汇报**：不说"我搞错了""子代理给了虚假内容""应该 xxxx"——发现问题直接报告现状 + 阻塞点，不道歉不甩锅
- **禁止编造 evidence**：evidence 必须指向真实 file:line，pass_count 必须与实际测试结果一致；主上下文会独立抽检，造假 = 🛑 REJECT + 计入失败计数

## 6. 视觉任务铁律（V10.6）

- **视觉任务委派前必须 Read 至少 1 张目标截图** inline 进 prompt
- **视觉 token 不能写形容词**（"墨绿"），必须写 hex/rgb（#1a3a2a）
- **委派 prompt 必须含"相差超过 50% 停下报告"**：如果实现与截图相差超过 50%，立即停下报告，不要交付骨架
- **主上下文不许凭印象猜视觉**——必须现场 Read 截图/录屏帧再下结论
