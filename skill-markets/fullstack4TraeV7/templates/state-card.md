# 📍 当前状态卡

> 任何 Agent 被激活时先输出此卡，再干活。
> 用户说"状态"/"定位"时立即输出此卡。

## 基本信息
- **变更**: {change-name}
- **当前阶段**: {stage} / 8
- **阶段名**: {intake/proposal/specs/contract/design/dev/review/accept}
- **最后产出**: {YYYY-MM-DD HH:MM}  # V7 NEW：防止假性完成
- **激活 Agent**: {agent-name}  # V7 NEW：当前正在工作的 Agent
- **提示词路径**: {path}  # V7 NEW：Agent 加载的 prompt 路径（如 agents/spec-writer.md），重入参考

## 工件进度
| 工件 | 状态 | 路径 |
|------|------|------|
| proposal.md | ✅/⏳/❌/— | docs/specs/changes/{change}/proposal.md |
| spec.md | ✅/⏳/❌/— | docs/specs/changes/{change}/specs/{cap}/spec.md |
| contracts/ | ✅/⏳/❌/— | docs/specs/changes/{change}/contracts/ |
| prototypes/ | ✅/⏳/❌/— | docs/specs/changes/{change}/prototypes/ |
| meeting-notes/ | ✅/⏳/❌/— | docs/specs/changes/{change}/meeting-notes/ |
| design.md | ✅/⏳/❌/— | docs/specs/changes/{change}/design.md |
| tasks.md | ✅/⏳/❌/— | docs/specs/changes/{change}/tasks.md |
| 代码 | ✅/⏳/❌/— | src/... |

## 健康度
- **Spec 漂移**: ✅ 无 / ⚠️ {N} 项 / 🛑 {N} 项严重
- **契约漂移**: ✅ 无 / ⚠️ {N} 项 / 🛑 {N} 项严重
- **目标对齐度**: {X}% 🟢/🟡/🔴
- **TDD 进度**: 🔴{X} 🟢{Y} / 共 {N} 个测试骨架

## 下一步
- {下一个动作，如：完成 design.md → 移交 implementer}

## 阻塞
- {阻塞项，如：等待用户确认 BREAKING 契约变更}
