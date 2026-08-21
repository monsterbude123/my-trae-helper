# V11 Fidelity 等级与反虚假交付协议（§3.7 + §8）

> **来源**:V12 SKILL.md §3.7（反虚假交付禁止）+ §8（灵活度铁律 / fidelity 等级）
> **蒸馏日期**:2026-08-19（vibe-coding-standards v2.5 瘦身 — 从 SKILL.md 抽出）
> **设计哲学**:prototype 是"参考起点 + 单一真相源",但承认合理灵活度。

---

## §3.7 反虚假交付禁止项

> **核心**:任何"PASS"必附真实证据(command + output + file:line),禁止"看到进程即通过"。

### 9 项禁止 + 1 项反向陷阱

1. **障碍隐瞒**: 容器未启 / 迁移失败 / 测试 FAIL 不汇报,声称"完成"
2. **跳过测试**: 跳过 `npm run test:all` / `pytest` / `vitest` 声称"完成"
3. **文档验收自我满足**: 文档验收 100% PASS 但未实际跑验证
4. **引用不可证伪理由作为失败归因**: 未定义术语、未指明位置的偏差、未量化裁剪、未测量的心理负担、未定义的概念迁移等。允许的失败归因形式见 [agent-error-diagnosis.md](agent-error-diagnosis.md) §3 5 模式诊断
5. **二次再犯不可证伪理由**: 二次被质问仍引用不可证伪理由 → REJECT
6. **AI 描述当成真实像素**: Read PNG 工具返回 AI 描述,编造"截图显示 XXX" → 主上下文必亲自 Read 对比(Article IX)
7. **盲信子代理"已完成"**: 不抽检 evidence / 不跑 pass_count 命令 / 不 Glob 产物(Article IX)
8. **Visual = API PASS**: 用 vitest PASS 充作 UI 任务"完成"(V10.12 教训)
9. **"启动 = 完成"软指标**: 启动进程即声称"完成",无可见产物(V10 §0.10 启动验证)
10. **范围盲目扩大(反向 #5 陷阱)**(V11.8.4 NEW): 为避免"假完成"反模式而把范围扩大到不可能完成(60 路由全量截图塞 commit 阻塞路径;5 个 spec 版本反复改仍不收敛)。这是反虚假交付 #5 的镜像陷阱。**commit 准入最小集 ≠ 全量验收**,详见 [common-anti-patterns.md §7.3](common-anti-patterns.md)

### V12.0.0 沿用 V11.2.1 — 蒸馏自 canvas-asset-folders Stage 4 Round 1/2 失败案例引用

> **失败场景**:2026-08-12 Stage 4 Round 1/2 评审员**明知只看了"5 预设可见"未对照 prototype**,仍给 PASS。用户一句话(30 字)"这个UI和 prototypes/index.html 你前面阶段设计的内容不是一个东西啊"暴露 Stage 4 评审重大疏漏。
>
> **教训**:反例 #8 不只在"明知缺陷还往下走"层面失效,在"明知评审疏漏还放 PASS"层面也失效。V11 改进:
> 1. Stage 4 review-report 必含 prototype ↔ implementation 对照表(见 skills/09-review/SKILL.md Step -1)
> 2. 评审员必亲读 prototype 截图(≥ 2 张)
> 3. 实施截图与 prototype 截图视觉差异 > 20% → REJECT

### §3.7.2 Article V V12 沿用 V11.2.1 强化 — 可验证声明硬约束

**4 项硬约束(任一违反 = 🛑 REJECT)**:

1. **Review 必读 prototype 截图**: Stage 4 review-report 必含 prototype ↔ implementation 对照表,评审员必亲读 ≥ 2 张 prototype 截图,未读 = 评审疏漏
2. **实施 vs prototype 视觉差异 > 20% → REJECT**: 实施截图与 prototype 截图逐像素对比,差异 > 20% 即拒收
3. **PASS 必附三层证据**: command + output + file:line 三件套缺一不可;review-report 任一字段缺失 = 自动 FAIL
4. **评审疏漏二次再犯 → 升级用户**: 同一 stage 连续 2 轮评审疏漏 → 立即停止自评,5 字段阻塞报告 + 升级用户决策

**关联铁律**:Article V(可验证声明) + Article IX(质疑式验收) + Article XVI(质疑式校验)。

---

## §8 灵活度铁律 — prototype fidelity 等级 + 工具-人类分层判定

### 8.1 prototype fidelity 等级(必在 design-prompt.md 顶部标注)

| 等级 | 内容 | 视觉差异阈值 | 适用场景 |
|------|------|:---:|------|
| **L1 wireframe(线框)** | 仅布局骨架 + 组件清单 + 5 状态,**不约束**颜色/间距/字号/动画 | ≤ 50% | 早期探索、需求验证、低保真原型 |
| **L2 mockup(中保真)** | L1 + 主色板 + 字号层级 + 间距规则 | ≤ 30% | 中后期实施、UI 细节对齐 |
| **L3 pixel-perfect(高保真)** | L2 + 动效曲线 + 阴影 + 圆角 + hover 状态 | ≤ 5% | 精确还原、营销页、关键 UX 节点 |

**默认值**:design-prompt.md 无 fidelity 标注 → 视为 **L2 mockup**(默认中保真)

### 8.2 prototype 演进(V12 沿用 V11.3)

- Stage 3 实施期间如发现 prototype 设计不合理,**允许**调整 prototype + design-prompt + ui-ux-logic
- 调整必走:
  1. 主上下文决策(不能 agent 单方面调整)
  2. 同步 3 份文档(保持单一真相源)
  3. 在 review-report.md §prototype ↔ implementation 对照表 "偏离理由" 列填"prototype 演进 V11.3 §8.2"
- **NEVER**: 暗改 prototype 而不更新文档

### 8.3 偏离理由(正当理由清单)

实施可偏离 prototype,但**必在** review-report.md §prototype ↔ implementation 对照表 "偏离理由" 列填**正当理由**之一:

- **性能优化** — 实施用更高效算法,功能等价
- **可访问性** — 实施用 ARIA 增强,功能等价
- **国际化** — 实施 i18n 拆分,文案按 locale 切换
- **用户偏好** — 用户已确认偏离(如本期 prototype 设计 8 项,但用户要求聚焦 6 项)
- **prototype 演进** — 见 §8.2,实施期间调整了 prototype
- **fidelity 等级允许的差异** — 见 §8.1,L1/L2 容许范围内差异
- **第三方库限制** — 实施用第三方库有特定约束(如 Tailwind 不支持某 CSS)

主上下文在 review-report 末段"§偏离裁定"列每条偏离的批准理由。

**NEVER 空洞偏离理由**(无证据的偏离裁定反例):
- ❌ "差不多"
- ❌ "看起来对"
- ❌ "感觉 OK"
- ❌ "应该没问题"
- ❌ "差不多就行"

**反例来源**:2026-08-12 canvas-asset-folders Stage 4 Round 1/2 评审员写"5 预设可见 + API PASS"给 PASS,缺 prototype 1:1 对照 + 缺偏离理由

### 8.4 工具-人类分层判定(人工判定覆盖)

> 2026-08-12 用户决策记录:工具反馈通过 → 主上下文直接标记通过;工具反馈未通过 → 由 agent 决定放行时必须附偏离理由(见 §8.3 正当理由清单)。无证据放行视为流程违规。

```
工具检测 PASS → 主上下文直接标记通过
工具检测 FAIL → 不阻塞,仅作"提示"交给 agent 决策
agent PASS  → 必写偏离理由(§8.3 正当理由清单之一)
agent FAIL  → 必写 FAIL 原因(spec 违反 / prototype GAP / 实施错误)
```

**反例**:agent 工具检测 FAIL 时,无理由声称"通过" → 按反例 §4 不可证伪理由处理

**关联铁律**:Article V(可验证声明) + Article IX(质疑式验收) + Article XVI(质疑式校验)。

**修正路径**: 必走 [sub-agent-rules.md §8 三层验证](sub-agent-rules.md) + [agent-error-diagnosis.md](agent-error-diagnosis.md) 5 模式诊断 + Stage 3.5 Real Verify 5 类项目启动验证。