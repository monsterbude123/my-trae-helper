# AIGC-smart-kit 任务跟踪

> 包级任务状态卡。每个子 skill 完成后在本文件标记。

## 当前活跃任务

### 2026-08-20 batch-03: Kling 3.0 第三个平台子 skill 接入

| # | 任务 | 状态 | 落地物 |
|---|------|------|--------|
| 1 | i2v-kling-prompt 子 skill(目录 + SKILL.md + 3 references) | ✅ | `skills/i2v-kling-prompt/` |
| 2 | 主入口 SKILL.md 升级(路由表 + §5.1 改造钩子 + platform-coverage) | ✅ | `skill-markets/aigc-smart-kit/SKILL.md` |

### 2026-08-20 batch-02: analyzer 子 skill 接入 + 默认 H3 + 改造钩子

| # | 任务 | 状态 | 落地物 |
|---|------|------|--------|
| 1 | i2v-image-analyzer 子 skill(目录 + SKILL.md + 3 references) | ✅ | `skills/i2v-image-analyzer/` |
| 2 | 主入口 SKILL.md 升级(加入 analyzer + 3 类加载协议 + 改造钩子) | ✅ | `skill-markets/aigc-smart-kit/SKILL.md` |
| 3 | JSON schema(image-report.json v1.0) | ✅ | `skills/i2v-image-analyzer/references/image-schema.md` |
| 4 | 场景词表 + 失败模式 | ✅ | references/scene-vocabulary.md + failure-modes.md |
| 5 | 自检(vibe 行数 + 跨引用 + 路由闭环) | ✅ | batch-03 落地 |

## 完成定义(MUST 全勾才能划 ✅)

- [x] analyzer SKILL.md frontmatter 合规(name + description + role)
- [x] analyzer references 三件套齐:schema + vocabulary + failure-modes
- [x] 主入口路由表覆盖 4 子 skill(analyzer + h3 + seedance + kling)
- [x] 主入口 §2 加载协议明确 4 类触发(A/B/C/D)
- [x] 主入口 §5.1 改造钩子模板固化(含 Kling 3.0 跳转)
- [x] analyzer 默认路由到 H3,可切 Seedance / Kling
- [x] vision 调协议明确(vision 模型由主 Agent 选)
- [x] image-report.json schema 完整(9 个字段 + 必填 / 选填)
- [x] 所有 SKILL.md 行数 ≤200(Kling 主入口 ≤200,h3/seedance ≤350)
- [x] references 行数 ≤150
- [x] 跨子 skill 引用一致(主入口 → analyzer → h3/seedance/kling 链条不断)
- [x] 无硬编码 API Key / 私钥
- [x] Kling frontmatter 触发词覆盖(Kling / 可灵 / I2V / 图生视频)
- [x] Kling SKILL.md 不反向引用 H3 / Seedance 公式(职责分离)

## 后续任务(留待下一轮)

- i2v-vidu-prompt / i2v-wan-prompt 子 skill
- scripts/i2v_prompt_build.py 跨平台 CLI 构造器
- scripts/i2v_prompt_lint.py 反例库自动检测
- 接管 h3-prompt-architect(若用户后续迁入仓库)
- vision 调用具体落地(主 Agent 内置 / MiniMax-VL / GPT-4V 的选型策略)
- §3 analyzer 与 h3/seedance/kling 之间的端到端测试脚本