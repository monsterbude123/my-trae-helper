# voice-acting-script-skill · 决策记录 (ADR)

## ADR-001: 使用 Python 而非 TypeScript

**日期**: 2026-05-05

**背景**: 原实现是 TypeScript + Next.js + npm 工具链。

**决策**: 迁移到 Python 3.11+ + click + pydantic + httpx。

**理由**:
- Next.js 是 Web 框架，本项目纯 CLI 管道工具，从未用 Web
- 40+ 个零散 JS/TS debug 脚本，工具链臃肿（node_modules 50MB+）
- Python 的 pydantic 比 TypeScript 的 interface+手动序列化更可靠
- click CLI 比 commander 更简洁
- Python 测试用 pytest 简单直接
- 项目 90% 是数据处理 + 字符串操作，Python 生态更合适

**后果**:
- ✅ 工具链减重到 2MB
- ✅ 35 个测试 0.2s 跑完
- ✅ CLI 启动时间 < 100ms
- ❌ 失去 TypeScript 编译期类型检查（由 pydantic 验证补足）

## ADR-002: 数据模型用 pydantic v2 而非 dataclass

**决策**: 全部数据模型用 pydantic BaseModel。

**理由**:
- 自动 JSON 序列化（`model_dump(mode="python")`）
- 自动验证（防止 actor_id 拼错等问题）
- IDE 类型提示友好
- 嵌套模型透明

**代价**: 多 1 个依赖。但相比收益可忽略。

## ADR-003: 多音字词典在 Python 常量而非 JSON

**决策**: 81 词 POLYPHONE_DICT 写在 `scripts/vaslib/config/voices.py`。

**理由**:
- 编译期检查（词条 key 类型）
- IDE 跳转支持
- 与 DIALECT_MAPPINGS 同文件，便于人类审查
- 81 个词条是稳定的，配置 vs 代码的区分不必要

**人工审查导出**: `assets/configs/polyphone-dictionary.md` 给人看。

## ADR-004: 批次切分上限 13 秒

**决策**: `MAX_BATCH_SECONDS = 13`（15s 目标 - 2s 安全 margin）

**理由**:
- CosyVoice / OmniVoice 单次请求超时通常 15s
- 长句语调合成时容易因内存/计算超限
- 2s margin 留给网络波动

**测试**: `test_batch_duration_within_limit` 验证所有 batch < 15s。

## ADR-005: 倾斜修正窗口 [0.8, 1.2]

**决策**: 估算时长与目标时长比值在 [0.8, 1.2] 时不修正。

**理由**:
- < 0.8：内容太少，需要减速（speed < 1）
- > 1.2：内容太多，需要加速（speed > 1）
- 0.8-1.2 区间内微调影响小，避免引入更多失真

## ADR-006: 三引擎并存的策略

**决策**: 保留 QwenTTS / CosyVoice / OmniVoice 三个引擎并列生成。

**理由**:
- QwenTTS：阿里云 API，情感标签丰富，适合对话场景
- CosyVoice：本地部署，instruct 控制细腻
- OmniVoice：支持副语言标签（叹息、笑声），适合表达强烈情绪

**生成时同时输出三个 JSON，让用户人工选择最佳引擎合成。**

## ADR-007: Markdown 报告 + JSON 数据双输出

**决策**: `annotated/{engine}.{json,md}` 同时输出。

**理由**:
- JSON 给程序消费（直接喂给 TTS API）
- Markdown 给人审核（情感标签 / 多音字是否正确）

**审核效率**: 直接在 Markdown 中编辑可读性最高。

## ADR-008: 项目结构按 Trae 技能包规范

**决策**: `SKILL.md` + `skills/{name}/SKILL.md` + `references/` + `scripts/` + `assets/` + `agents/` + `workflows/`

**理由**:
- 符合父项目 `AGENTS.md` 规则
- 顶层 SKILL.md 作为编排器，按用户需求路由到 5 个子技能
- 深度资料在 references/，避免污染 SKILL.md
- 编剧+素材在 assets/，可独立分发

## ADR-009: 不做 Web UI

**决策**: 纯 CLI 工具 + Markdown 报告，不开发 Web 界面。

**理由**:
- 本项目核心用户是 AI 代理 + 开发者，不是设计师
- CLI 启动快、可脚本化、可批处理
- Markdown 报告可直接在任何编辑器/IDE 中查看
- 避免 React/Vue 重量级前端依赖

## ADR-010: 不接 LLM 做自动决策

**决策**: 配置 / 多音字 / 情感标签全部由代码常量 + 人工审核决定，不接 LLM。

**理由**:
- 确定性可重入
- 无 API key 风险（不暴露 key）
- 测试简单
- ponytail 思维：能用代码解决的事不上 LLM
