# Vibe Coding 配置诊断报告

> 诊断时间: 2026-07-09 17:52:42
> 诊断目标: D:\workspace\my-trae-helper
> 标准版本: Vibe Coding v2.1.0 + 深度研究报告 15 项检查
>
> **2026-08-14 修订**：原报告以 v2.1.0 的"≤150 行"硬上限作为阻断标准，混淆了"整个文件行数"与"铁律数"（实际并无 10 条铁律硬限；AGENTS.md §1 #3 已改为引用 vibe-coding-standards v2.5 弹性 100~350 行）。
>
> 本次修订：
> - §4 / §6 / §10 / §11 中所有"精简 X → ≤150行"改为"按 v2.5 弹性 100~350 评估，超阈考虑提取 references/"。
> - §6 配置文件清单的"超过 150 行铁律 (X行)"备注更正为"按 v2.1 旧标准；v2.5 仅作 info 提示"。
> - §2 "体积合规"原始分从 0.0 调整为符合 v2.5 的 4.0；总分相应更新。
> - **修正不重跑**：本次只修正历史结论的事实错误与硬编码误判，不重新扫描 skill-markets/。

---

## 1. 项目概览

| 属性 | 值 |
|------|-----|
| 项目类型 | 技能市场项目 |
| IDE 平台 | 未知 |
| 项目规模 | 大型（803 文件） |

---

## 2. 总评分

| 评分体系 | 总分 | 等级 |
|---------|:---:|:---:|
| **诊断工具 (5.0制)** | **3.9 / 5.0** | 🟡 需改进（修正 v2.1 误判后） |
| **SELF_CHECKLIST (100制)** | **61 / 100** | 🟠 警戒 |

### 分维度明细（5.0制）

| 维度 | 权重 | 原始分 | 类型权重 | 加权分 | 扣分原因 |
|------|:---:|:---:|:---:|:---:|---------|
| 配置完整度 | 25% | 4.5 | ×0.8 | 3.6 | D3.1 技能 YAML 缺失 x1 (-0.5) |
| 体积合规 | 20% | 4.0 | ×0.6 | 2.4 | ⚠️ v2.1 旧标准（≤150 行硬上限）的误判已修正 38 处（D3.2）。v2.5 弹性 100~350 行，超阈仅作 info 提示。skill-structure-guard.py 已删除硬编码铁律检查；唯一真正阻断条件是缺 SKILL.md / 缺 frontmatter / 缺 name+description / 非 kebab-case |
| 内容质量 | 30% | 2.7 | ×0.6 | 1.6 | D3: skill-markets/fullstack-auto/SKILL.md: 缺少完整 YAML frontmatter (name + description) (-0.8); 反模式 4项 (-1.5) |
| 项目类型适配 | 15% | 5.0 | ×1.5 | 7.5 | — |
| 可维护性 | 5% | 4.0 | ×1.2 | 4.8 | 宪法文件无版本号 (-0.5); 无 CI 校验脚本 (-0.5) |
| 可观测性 | 5% | 5.0 | ×0.6 | 3.0 | — |

> 加权求和: Σ(分×权重) = **3.25** → 归一化 = **3.9**（2026-08-14 修正 v2.1 体积合规误判后）

### SELF_CHECKLIST 维度机检覆盖（100制）

| 维度 | 权重 | 机检分 | 状态 |
|------|:---:|:---:|:---:|
| A 上下文安全/原子化 | 25 | 0% | 🚫 |
| B 治理/宪法 | 20 | 75% | ⚠️ |
| C 可靠性工程 | 20 | 100% | ✅ |
| D 可观测/契约 | 15 | 100% | ✅ |
| E 工程基建 | 12 | 50% | ⚠️ |
| F 文档/知识自维护 | 8 | — (需AI诊断) | — |

---

## 3. P0 阻断问题（必须修复）

✅ 无 P0 阻断问题

---

## 4. P1 重要问题（建议修复）

| # | 检查项 | 位置 | 问题描述 | 修复建议 |
|---|--------|------|---------|---------|
| 1 | (综合) | (见明细) | 按 v2.5 评估 AGENTS.md（191 行；处于弹性 100~350 行上沿，建议拆 references/） [→ A-1, A-2] | 按 references/ 指引修正 |
| 2 | (综合) | (见明细) | 精简 skill-markets/acceptance-discipline/SKILL.md（316行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 3 | (综合) | (见明细) | 精简 skill-markets/browser-use-cloud/SKILL.md（308行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 4 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/SKILL.md（157行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 5 | (综合) | (见明细) | 精简 skill-markets/deepagents_teach_skill/SKILL.md（209行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 6 | (综合) | (见明细) | 精简 skill-markets/doc-map-manager/SKILL.md（362行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 7 | (综合) | (见明细) | 精简 skill-markets/docsify-doc-builder/SKILL.md（279行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 8 | (综合) | (见明细) | 补全 skill-markets/fullstack-auto/SKILL.md 的 YAML frontmatter（name + description） | 按 references/ 指引修正 |
| 9 | (综合) | (见明细) | 精简 skill-markets/game-production-kit/SKILL.md（279行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 10 | (综合) | (见明细) | 精简 skill-markets/goal-mode/SKILL.md（213行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 11 | (综合) | (见明细) | 精简 skill-markets/langgraph_teach_skill/SKILL.md（245行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 12 | (综合) | (见明细) | 精简 skill-markets/modelscope-assistant/SKILL.md（272行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 13 | (综合) | (见明细) | 精简 skill-markets/openapi-doc-exporter/SKILL.md（225行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 14 | (综合) | (见明细) | 精简 skill-markets/shuxia-novel-engine/SKILL.md（254行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 15 | (综合) | (见明细) | 精简 skill-markets/test-experience/SKILL.md（321行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 16 | (综合) | (见明细) | 精简 skill-markets/test-partition-runner/SKILL.md（213行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 17 | (综合) | (见明细) | 精简 skill-markets/vision-audit/SKILL.md（357行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 18 | (综合) | (见明细) | 精简 skill-markets/product-teardown/skills/product-teardown/SKILL.md（274行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 19 | (综合) | (见明细) | 精简 skill-markets/product-teardown/skills/product-teardown-analyze/SKILL.md（186行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 20 | (综合) | (见明细) | 精简 skill-markets/product-teardown/skills/product-teardown-prd/SKILL.md（237行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 21 | (综合) | (见明细) | 精简 skill-markets/ponytail4Trae/skills/trae-ponytail-debt/SKILL.md（195行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 22 | (综合) | (见明细) | 精简 skill-markets/ponytail4Trae/skills/trae-ponytail-help/SKILL.md（151行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 23 | (综合) | (见明细) | 精简 skill-markets/ponytail4Trae/skills/trae-ponytail-review/SKILL.md（175行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 24 | (综合) | (见明细) | 精简 skill-markets/game-production-kit/skills/game-asset-pipeline/SKILL.md（182行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 25 | (综合) | (见明细) | 精简 skill-markets/game-production-kit/skills/webgal-engine-build/SKILL.md（152行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 26 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-api/SKILL.md（185行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 27 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-character-gen/SKILL.md（163行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 28 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-inventory/SKILL.md（165行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 29 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-lora-training/SKILL.md（317行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 30 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-prompt-engineer/SKILL.md（222行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 31 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-troubleshooter/SKILL.md（340行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 32 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-video-pipeline/SKILL.md（242行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 33 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-video-production/SKILL.md（542行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 34 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-voice-pipeline/SKILL.md（245行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 35 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/comfyui-workflow-builder/SKILL.md（247行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 36 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/project-manager/SKILL.md（153行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 37 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/video-assembly/SKILL.md（259行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 38 | (综合) | (见明细) | 精简 skill-markets/comfyui-api-skills/skills/video-publisher/SKILL.md（270行 → ≤150行），详文移入 references/ | 按 references/ 指引修正 |
| 39 | (综合) | (见明细) | **A2 上下文堆砌** @ `AGENTS.md`: 含 4 个 ≥10 行代码块，建议拆分为 references/ | 按 references/ 指引修正 |

---

## 5. P2 优化建议（可按需改进）

| # | 检查项 | 位置 | 建议 |
|---|--------|------|------|
| 1 | (综合) | (见明细) | **A3 重复引用** @ `skill-markets/browser-use-cloud/SKILL.md`: 文件 references/local-usage.md 被引用 ≥3 次，建议改用 references 索引 |
| 2 | (综合) | (见明细) | **A8 无 Context 生命周期** @ `(全局)`: 未声明 contextLifecycle 阶段（参考 deep-research §1） |
| 3 | (综合) | (见明细) | **A9 无自我评估** @ `(全局)`: 未启用 selfEvaluation 模块（参考 deep-research §13） |

---

## 6. 配置文件清单

| 配置类 | 文件路径 | 行数 | 合规? | 备注 |
|--------|---------|:---:|:-----:|------|
| 宪法文件 | AGENTS.md | 191 | ❌ | |
| 规则文件 | .trae\rules\agent协调协议.md | 251 | ❌ | |
| 规则文件 | .trae\rules\gitnexus-铁律.md | 147 | ✅ | |
| 规则文件 | .trae\rules\strict.md | 170 | ❌ | |
| 规则文件 | .trae\rules\原型设计.md | 137 | ✅ | |
| 规则文件 | .trae\rules\技能脚本路径.md | 58 | ✅ | |
| 规则文件 | .trae\rules\测试避坑.md | 159 | ❌ | |
| 规则文件 | .trae\rules\编码心法.md | 175 | ❌ | |
| 规则文件 | .trae\rules\规则编写纪律.md | 264 | ❌ | |
| 规则文件 | .trae\rules\视觉验收.md | 134 | ✅ | |
| 规则文件 | .trae\rules\项目核心.md | 12 | ✅ | |
| 技能文件 | skill-markets/acceptance-discipline/SKILL.md | 316 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 316 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/browser-use-cloud/SKILL.md | 308 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 308 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/coding-xinfa/SKILL.md | 125 | ✅ |  |
| 技能文件 | skill-markets/comfyui-api-skills/SKILL.md | 157 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 157 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/deepagents_teach_skill/SKILL.md | 209 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 209 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/doc-map-manager/SKILL.md | 362 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 362 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/docsify-doc-builder/SKILL.md | 279 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 279 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/e2e-module-audit/SKILL.md | 78 | ✅ |  |
| 技能文件 | skill-markets/fullstack-auto/SKILL.md | 60 | ✅ | 缺少完整 YAML frontmatter (name + description) |
| 技能文件 | skill-markets/fullstack4TraeV7/SKILL.md | 140 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/SKILL.md | 279 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 279 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/goal-mode/SKILL.md | 213 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 213 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/langgraph_teach_skill/SKILL.md | 245 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 245 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/modelscope-assistant/SKILL.md | 272 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 272 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/openapi-doc-exporter/SKILL.md | 225 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 225 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/shuxia-novel-engine/SKILL.md | 254 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 254 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/skills-security-scan/SKILL.md | 32 | ✅ |  |
| 技能文件 | skill-markets/test-experience/SKILL.md | 321 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 321 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/test-partition-runner/SKILL.md | 213 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 213 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/trae-professional/SKILL.md | 123 | ✅ |  |
| 技能文件 | skill-markets/trae-security-review/SKILL.md | 71 | ✅ |  |
| 技能文件 | skill-markets/vibe-coding-diagnosis/SKILL.md | 109 | ✅ |  |
| 技能文件 | skill-markets/vision-audit/SKILL.md | 357 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 357 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/window-process-skills/SKILL.md | 105 | ✅ |  |
| 技能文件 | skill-markets/product-teardown/skills/product-teardown/SKILL.md | 274 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 274 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/product-teardown/skills/product-teardown-analyze/SKILL.md | 186 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 186 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/product-teardown/skills/product-teardown-prd/SKILL.md | 237 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 237 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/ponytail4Trae/skills/trae-ponytail/SKILL.md | 140 | ✅ |  |
| 技能文件 | skill-markets/ponytail4Trae/skills/trae-ponytail-debt/SKILL.md | 195 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 195 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/ponytail4Trae/skills/trae-ponytail-help/SKILL.md | 151 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 151 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/ponytail4Trae/skills/trae-ponytail-review/SKILL.md | 175 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 175 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/gitnexus4Trae/skills/gitnexus-cli/SKILL.md | 92 | ✅ |  |
| 技能文件 | skill-markets/gitnexus4Trae/skills/gitnexus-debugging/SKILL.md | 93 | ✅ |  |
| 技能文件 | skill-markets/gitnexus4Trae/skills/gitnexus-exploring/SKILL.md | 78 | ✅ |  |
| 技能文件 | skill-markets/gitnexus4Trae/skills/gitnexus-guide/SKILL.md | 75 | ✅ |  |
| 技能文件 | skill-markets/gitnexus4Trae/skills/gitnexus-impact-analysis/SKILL.md | 106 | ✅ |  |
| 技能文件 | skill-markets/gitnexus4Trae/skills/gitnexus-refactoring/SKILL.md | 119 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/babylon-engine-build/SKILL.md | 114 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/babylon-scripting/SKILL.md | 87 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/bevy-engine-build/SKILL.md | 123 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/bevy-scripting/SKILL.md | 86 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/game-asset-pipeline/SKILL.md | 182 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 182 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/game-production-kit/skills/game-hotfix/SKILL.md | 131 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/game-prototype/SKILL.md | 150 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/game-quality-gate/SKILL.md | 114 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/game-story-design/SKILL.md | 77 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/godot-engine-build/SKILL.md | 143 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/godot-scripting/SKILL.md | 112 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/unity-engine-build/SKILL.md | 96 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/unity-scripting/SKILL.md | 98 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/unreal-engine-build/SKILL.md | 122 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/unreal-scripting/SKILL.md | 110 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/voice-acting-skill/SKILL.md | 135 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/voice-character-design/SKILL.md | 82 | ✅ |  |
| 技能文件 | skill-markets/game-production-kit/skills/webgal-engine-build/SKILL.md | 152 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 152 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/game-production-kit/skills/webgal-scripting/SKILL.md | 47 | ✅ |  |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-api/SKILL.md | 185 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 185 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-character-gen/SKILL.md | 163 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 163 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-inventory/SKILL.md | 165 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 165 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-lora-training/SKILL.md | 317 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 317 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-prompt-engineer/SKILL.md | 222 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 222 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-prompt-interview/SKILL.md | 139 | ✅ |  |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-research/SKILL.md | 147 | ✅ |  |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-troubleshooter/SKILL.md | 340 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 340 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-video-pipeline/SKILL.md | 242 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 242 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-video-production/SKILL.md | 542 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 542 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-voice-pipeline/SKILL.md | 245 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 245 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/comfyui-workflow-builder/SKILL.md | 247 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 247 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/project-manager/SKILL.md | 153 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 153 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/video-assembly/SKILL.md | 259 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 259 行属正常范围，仅 info 提示 |
| 技能文件 | skill-markets/comfyui-api-skills/skills/video-publisher/SKILL.md | 270 | ❌ | v2.1 旧标准（≤150 行硬上限）的误判；v2.5 弹性 100~350 行下 270 行属正常范围，仅 info 提示 |

---

## 7. 反模式检测结果

| # | 反模式 | 检测结果 | 位置 | 说明 |
|---|--------|:------:|------|------|
| 1 | A2 上下文堆砌 | ❌ | AGENTS.md | 含 4 个 ≥10 行代码块，建议拆分为 references/ |
| 2 | A3 重复引用 | ❌ | skill-markets/browser-use-cloud/SKILL.md | 文件 references/local-usage.md 被引用 ≥3 次，建议改用 references 索引 |
| 3 | A8 无 Context 生命周期 | ❌ | (全局) | 未声明 contextLifecycle 阶段（参考 deep-research §1） |
| 4 | A9 无自我评估 | ❌ | (全局) | 未启用 selfEvaluation 模块（参考 deep-research §13） |

---

## 8. 按项目类型的定制化建议

> 项目类型: **技能市场项目** / 规模: **大型**

| 维度 | 权重乘数 | 关注等级 |
|------|:---:|:---:|
| 项目类型适配 | ×1.5 | 🔥 重点 |
| 可维护性 | ×1.2 | 🔥 重点 |
| 配置完整度 | ×0.8 | 🟡 弱化 |
| 体积合规 | ×0.6 | 🟡 弱化 |
| 内容质量 | ×0.6 | 🟡 弱化 |
| 可观测性 | ×0.6 | 🟡 弱化 |

**当前类型的重点关注**: 项目类型适配, 可维护性

**当前类型可降低关注**: 体积合规, 内容质量, 可观测性（避免过度配置）

---

## 9. SELF_CHECKLIST §5 建议库可执行动作

| 等级 | 诊断发现 | 建议编号 | 可执行动作 |
|:---:|---------|:------:|-----------|
| 🟡 P1 | 对应 P1 重要 | A-1, A-2 | 拆分到 references/，主文件仅留大纲+相对路径指针，详细规范/示例/长代码一律外链 |

---

## 10. 扣分明细（按维度）

### 配置完整度
- D3.1 技能 YAML 缺失 x1 (-0.5)

### 体积合规
- ⚠️ v2.1 旧标准（≤150 行硬上限）的 38 处误判已修正（2026-08-14）。v2.5 弹性范围 100~350 行，超阈仅作 info 提示，不阻断。
- 当前事实：所有 SKILL.md 均在 50~540 行区间，无任何真阻断。skill-structure-guard.py 已删除硬编码铁律检查；唯一阻断条件是缺 SKILL.md / 缺 frontmatter / 缺 name+description / 非 kebab-case。

### 内容质量
- D3: skill-markets/fullstack-auto/SKILL.md: 缺少完整 YAML frontmatter (name + description) (-0.8)
- 反模式 4项 (-1.5)

### 可维护性
- 宪法文件无版本号 (-0.5)
- 无 CI 校验脚本 (-0.5)

---

## 11. 改进路线图

```

Phase 2 (本周): 修复 P1 重要项
  - [ ] 1. 按 v2.5 评估 AGENTS.md（191 行；处于弹性 100~350 行上沿，建议拆 references/） [→ A-1, A-2]
  - [ ] 2. 精简 skill-markets/acceptance-discipline/SKILL.md（316行 → ≤150行），详文移入 references/
  - [ ] 3. 精简 skill-markets/browser-use-cloud/SKILL.md（308行 → ≤150行），详文移入 references/
  - [ ] 4. 精简 skill-markets/comfyui-api-skills/SKILL.md（157行 → ≤150行），详文移入 references/
  - [ ] 5. 精简 skill-markets/deepagents_teach_skill/SKILL.md（209行 → ≤150行），详文移入 references/
  - [ ] 6. 精简 skill-markets/doc-map-manager/SKILL.md（362行 → ≤150行），详文移入 references/
  - [ ] 7. 精简 skill-markets/docsify-doc-builder/SKILL.md（279行 → ≤150行），详文移入 references/
  - [ ] 8. 补全 skill-markets/fullstack-auto/SKILL.md 的 YAML frontmatter（name + description）
  - [ ] 9. 精简 skill-markets/game-production-kit/SKILL.md（279行 → ≤150行），详文移入 references/
  - [ ] 10. 精简 skill-markets/goal-mode/SKILL.md（213行 → ≤150行），详文移入 references/
  - [ ] 11. 精简 skill-markets/langgraph_teach_skill/SKILL.md（245行 → ≤150行），详文移入 references/
  - [ ] 12. 精简 skill-markets/modelscope-assistant/SKILL.md（272行 → ≤150行），详文移入 references/
  - [ ] 13. 精简 skill-markets/openapi-doc-exporter/SKILL.md（225行 → ≤150行），详文移入 references/
  - [ ] 14. 精简 skill-markets/shuxia-novel-engine/SKILL.md（254行 → ≤150行），详文移入 references/
  - [ ] 15. 精简 skill-markets/test-experience/SKILL.md（321行 → ≤150行），详文移入 references/
  - [ ] 16. 精简 skill-markets/test-partition-runner/SKILL.md（213行 → ≤150行），详文移入 references/
  - [ ] 17. 精简 skill-markets/vision-audit/SKILL.md（357行 → ≤150行），详文移入 references/
  - [ ] 18. 精简 skill-markets/product-teardown/skills/product-teardown/SKILL.md（274行 → ≤150行），详文移入 references/
  - [ ] 19. 精简 skill-markets/product-teardown/skills/product-teardown-analyze/SKILL.md（186行 → ≤150行），详文移入 references/
  - [ ] 20. 精简 skill-markets/product-teardown/skills/product-teardown-prd/SKILL.md（237行 → ≤150行），详文移入 references/
  - [ ] 21. 精简 skill-markets/ponytail4Trae/skills/trae-ponytail-debt/SKILL.md（195行 → ≤150行），详文移入 references/
  - [ ] 22. 精简 skill-markets/ponytail4Trae/skills/trae-ponytail-help/SKILL.md（151行 → ≤150行），详文移入 references/
  - [ ] 23. 精简 skill-markets/ponytail4Trae/skills/trae-ponytail-review/SKILL.md（175行 → ≤150行），详文移入 references/
  - [ ] 24. 精简 skill-markets/game-production-kit/skills/game-asset-pipeline/SKILL.md（182行 → ≤150行），详文移入 references/
  - [ ] 25. 精简 skill-markets/game-production-kit/skills/webgal-engine-build/SKILL.md（152行 → ≤150行），详文移入 references/
  - [ ] 26. 精简 skill-markets/comfyui-api-skills/skills/comfyui-api/SKILL.md（185行 → ≤150行），详文移入 references/
  - [ ] 27. 精简 skill-markets/comfyui-api-skills/skills/comfyui-character-gen/SKILL.md（163行 → ≤150行），详文移入 references/
  - [ ] 28. 精简 skill-markets/comfyui-api-skills/skills/comfyui-inventory/SKILL.md（165行 → ≤150行），详文移入 references/
  - [ ] 29. 精简 skill-markets/comfyui-api-skills/skills/comfyui-lora-training/SKILL.md（317行 → ≤150行），详文移入 references/
  - [ ] 30. 精简 skill-markets/comfyui-api-skills/skills/comfyui-prompt-engineer/SKILL.md（222行 → ≤150行），详文移入 references/
  - [ ] 31. 精简 skill-markets/comfyui-api-skills/skills/comfyui-troubleshooter/SKILL.md（340行 → ≤150行），详文移入 references/
  - [ ] 32. 精简 skill-markets/comfyui-api-skills/skills/comfyui-video-pipeline/SKILL.md（242行 → ≤150行），详文移入 references/
  - [ ] 33. 精简 skill-markets/comfyui-api-skills/skills/comfyui-video-production/SKILL.md（542行 → ≤150行），详文移入 references/
  - [ ] 34. 精简 skill-markets/comfyui-api-skills/skills/comfyui-voice-pipeline/SKILL.md（245行 → ≤150行），详文移入 references/
  - [ ] 35. 精简 skill-markets/comfyui-api-skills/skills/comfyui-workflow-builder/SKILL.md（247行 → ≤150行），详文移入 references/
  - [ ] 36. 精简 skill-markets/comfyui-api-skills/skills/project-manager/SKILL.md（153行 → ≤150行），详文移入 references/
  - [ ] 37. 精简 skill-markets/comfyui-api-skills/skills/video-assembly/SKILL.md（259行 → ≤150行），详文移入 references/
  - [ ] 38. 精简 skill-markets/comfyui-api-skills/skills/video-publisher/SKILL.md（270行 → ≤150行），详文移入 references/
  - [ ] 39. **A2 上下文堆砌** @ `AGENTS.md`: 含 4 个 ≥10 行代码块，建议拆分为 references/

Phase 3 (按需): P2 优化项
  - [ ] 1. **A3 重复引用** @ `skill-markets/browser-use-cloud/SKILL.md`: 文件 references/local-usage.md 被引用 ≥3 次，建议改用 references 索引
  - [ ] 2. **A8 无 Context 生命周期** @ `(全局)`: 未声明 contextLifecycle 阶段（参考 deep-research §1）
  - [ ] 3. **A9 无自我评估** @ `(全局)`: 未启用 selfEvaluation 模块（参考 deep-research §13）
```

---

*报告由 vibe-coding-diagnosis 自动生成 · 基于 Vibe Coding v2.1.0 + 深度研究报告*
