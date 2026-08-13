# V11 公共脚本说明

> 22 个公共脚本 + 各 stage 内部脚本。脚本失败 = 🛑 REJECT，不接受 AI 自评字符串。
> 主上下文亲自调用脚本（不委派给子代理，Article IV）。

---

## 公共脚本清单（scripts/）

| 脚本 | 用途 | 使用 stage |
|------|------|-----------|
| `stage-gate.py` | V11 阶段门禁（13 stage 统一） | 所有 stage 切换前 |
| `state-card-validator.py` | 状态卡字段 + 文件系统交叉验证 | 所有 stage 状态卡更新后 |
| `setup-feature.py` / `change-status.py` | 创建 change 骨架 / 读取 change 真实状态 | Stage -1 / 0 |
| `code-hygiene.py` / `orphan-detector.py` | 代码卫生 / 孤儿测试 | Stage 3 / 4 / 4.5 |
| `dist-hash-check.py` / `visual-content-check.py` | Bundle 一致性 / 视觉内容校验 | Stage 3.5 / 4 |
| `acceptance-audit.py` | 4 维验收审计 | Stage 4 |
| `proactive-scan.py` / `self-diagnose.py` | 5 项腐化扫描包 / Meta 自我诊断 | Stage 4.5 |
| `spec-purge.py` / `spec-knowledge-extract.py` | Spec 清除归档 / 知识沉淀 | Stage 5 |
| `reason-classifier.py` | 抽象理由分类器（6 类） | 所有 stage（被质疑时） |
| `init-from-zero.py` | 项目完整初始化（4 步:config+hooks+rules+AGENTS.md+docs 骨架） | 项目首次接入 V11 |
| `sync-after-upgrade.py` | 技能升级后覆盖性更新项目文件（hooks/config/rules/AGENTS.md 差异检查） | V11 技能升级后 |
| `install-hooks.py` | Hook 安装到项目 .trae/ | 项目首次接入 V11 |
| `hooks-fidelity.py` | Hook 完整性验证 | 项目首次接入 + 验收 |
| `upgrade-from-v10.py` | V10→V11 升级兼容性检查 | V10 项目升级 |
| `scan-templates.py` | 模板扫描 | 模板变更时 |
| `phase-gate.py` | 阶段门禁（V10 兼容） | V10 项目兼容 |
| `check_integration_contract.py` | 集成契约检查 | Stage 2 Contract |

---

## 脚本调用规则

- 主上下文亲自调用（不委派给子代理）
- 脚本输出必须真实保存（不接受口头宣称 PASS）
- 脚本失败 = 🛑 REJECT → 走 Article XV 阻塞报告
- 脚本 N/A → 必须在状态卡标注理由（不可静默跳过）

---

## 依赖

已实施脚本依赖 **PyYAML**（用于精确解析嵌套 YAML）：

```bash
pip install pyyaml
```

PyYAML 在大多数 Python 环境中已预装。

---

## V10 兼容性声明

V11 是独立版本，**不依赖** V10 脚本目录。V10 脚本由 V11 重写并增强，但部署时只需 V11 自身的 `scripts/` 目录。

---

## 阈值变更审计（V11.2 NEW — 蒸馏自 00-03-diagnostic）

> **问题**: 修改 `MIN_*` / `pass_count` / `THRESHOLD_*` 常量无审计，可能连续降级逃避验收（反例：visual-content-check.py MIN_QUADRANT_DIFF_DARK 2.5 → 1.5 → 0.9）。
> **铁律**: 任何 PR 修改阈值常量 → 必跑 `script-threshold-audit.py --check-git-diff`，连续降级 2 次 → 🛑 REJECT。

### 用法

```bash
# 只读扫描（无 git diff 检测）
python scripts/script-threshold-audit.py --project-root .

# PR 前必跑（检测 git diff + 连续降级阻断）
python scripts/script-threshold-audit.py --project-root . --check-git-diff --base-ref main

# JSON 输出（CI 集成）
python scripts/script-threshold-audit.py --project-root . --check-git-diff --json
```

### 阻断规则

- **连续降级 ≥ 2 次**（同一阈值名，连续 commit 都降低值）→ 🛑 阻断 PR
- 提示：重新审视验收方法（方案 A：修复真实问题 / 方案 B：接受 FAIL 标 WARN / 方案 C：换更合适的测试方法）—— **不是改阈值让 PASS**

### 反例（00-03-diagnostic）

```
Round 1: MIN_QUADRANT_DIFF_DARK = 2.5 (合理)
Round 2: MIN_QUADRANT_DIFF_DARK = 1.5 (降级 1 次,未审计)
Round 3: MIN_QUADRANT_DIFF_DARK = 0.9 (降级 2 次,接近无意义)
```

教训：阈值连续降级逃避验收 → 真实 FAIL 被掩盖 → 用户发现实际未达标。

### 关联引用

- [skills/09-review/SKILL.md §铁律 11](../skills/09-review/SKILL.md) — 必读 4 件套（含 scripts/README.md）
- 反例来源：2026-08-12 00-03-diagnostic session-distillation-report
- V11.2 NEW 铁律配套：state-card-protocol.md visual_evidence_verified（Stage 3.5 → 4 硬门槛）

---

## 原型双产物最低门禁（V11.2.1 NEW — 蒸馏自 V10 prototype.md）

> **问题**: spec-writer 跳过 design-prompt.md + ui-ux-logic.md 双产物，Stage 1.5 Prototype 仅做"双源校验"但 5 状态 + 4 项最低门禁缺失。
> **铁律（仅 UI 涉及 change）**: 涉及 UI 的 change → 必跑 `prototype-backfill-check.py --change-id {id}`，缺 1 项 → 🛑 P0 阻塞；**纯后端/API/CLI change → 自动 SKIP**（启发式检测 spec.md 是否含 UI 关键字）。

### 用法

```bash
# 单 change 检查(自动判定 UI 涉及;纯后端 → [SKIP])
python scripts/prototype-backfill-check.py --change-id 2026-08-12-feature

# 批量扫描所有 changes
python scripts/prototype-backfill-check.py --project-root . --all

# JSON 输出（CI 集成）
python scripts/prototype-backfill-check.py --change-id {id} --json
```

### 最低门禁（V10 prototype.md §最低门禁 + §反向补全）

**design-prompt.md**:
- 5 状态全覆盖：加载中 / 空数据 / 正常态 / 错误态 / 边界态
- 响应式断点 ≥ 2：Desktop / Tablet / Mobile

**ui-ux-logic.md**:
- 组件树章节 ≥ 1
- 交互流 ≥ 2 个（## 流 N:）
- 状态表行数 ≥ 3
- 错误与边界处理行数 ≥ 3

### 反向补全（Backfill）

详见 [skills/05-prototype/references/prototype-dual-source.md](../skills/05-prototype/references/prototype-dual-source.md) §反向补全。

### 关联引用

- [skills/05-prototype/references/prototype-dual-source.md](../skills/05-prototype/references/prototype-dual-source.md) — V11 双产物机制
- [skills/05-prototype/references/prototype-linkage.md](../skills/05-prototype/references/prototype-linkage.md) — HANDOFF 联动协议
- [skills/05-prototype/templates/design-prompt.md](../skills/05-prototype/templates/design-prompt.md) + [ui-ux-logic.md](../skills/05-prototype/templates/ui-ux-logic.md) — 模板
- 蒸馏来源：fullstack4TraeV10/references/prototype.md + prototype-linkage.md + designer-handoff.md

---

## 灵活度铁律 8（V11.3 NEW — 人工判定覆盖 — 蒸馏自 canvas-asset-folders）

> **核心**: 5% 视觉差异阈值（V11.3 收紧 4 倍）+ fidelity 等级 + 偏离理由 + 工具-人类分层判定。
> **设计哲学**: prototype 是"参考起点 + 单一真相源",但**承认合理灵活度**。

### 工具-人类分层判定（2026-08-12 用户决策记录）

> 工具反馈通过 → 主上下文直接标记通过；工具反馈未通过 → 由 agent 决定放行时必须附偏离理由（见 SKILL.md §8.3 正当理由清单）。无证据放行视为流程违规。

```
工具 PASS → 主上下文直接标记通过
工具 FAIL → 不阻塞,仅作"提示"交给 agent 决策
agent PASS  → 必写偏离理由（§8.3 正当理由清单之一）
agent FAIL  → 必写 FAIL 原因
```

### Fidelity 等级（必在 design-prompt.md 顶部标注）

| 等级 | 适用场景 | 视觉差异容许 |
|---|---|---|
| L1 wireframe | 早期探索、需求验证、低保真原型 | ≤ 50% |
| L2 mockup | 中后期实施、UI 细节对齐（默认）| ≤ 30% |
| L3 pixel-perfect | 精确还原、营销页、关键 UX 节点 | ≤ 5% |

**默认值**：design-prompt.md 无 fidelity 标注 → 视为 L2 mockup。

### 用法

```bash
# 默认 L2 mockup（视觉差异阈值 30%）
python scripts/visual-content-check.py --prototype-html docs/specs/changes/{id}/prototypes/design.html

# 指定 L3 pixel-perfect（阈值 5%）
python scripts/visual-content-check.py --prototype-html design.html --fidelity L3

# prototype-backfill-check 自动读取 design-prompt.md fidelity 等级
python scripts/prototype-backfill-check.py --change-id {id}
```

### 偏离理由（正当理由清单 — §8.3）

- **性能优化** — 实施用更高效算法
- **可访问性** — 实施用 ARIA 增强
- **国际化** — 实施 i18n 拆分
- **用户偏好** — 用户已确认偏离
- **prototype 演进** — 实施期间调整了 prototype（见 §8.2）
- **fidelity 等级允许的差异** — L1/L2 容许范围内
- **第三方库限制** — 实施用第三方库有特定约束

**NEVER 空洞偏离理由**（无证据的偏离裁定反例）：
- ❌ "差不多"
- ❌ "看起来对"
- ❌ "感觉 OK"

### 关联引用

- [SKILL.md §3.7.3 灵活度铁律 8](../SKILL.md) — 三段定义
- [skills/09-review/SKILL.md Step -1](../skills/09-review/SKILL.md) — 对照表 + fidelity + 偏离理由列
- [skills/05-prototype/templates/design-prompt.md](../skills/05-prototype/templates/design-prompt.md) — fidelity 字段模板
- 蒸馏来源：2026-08-12 canvas-asset-folders + 用户 2026-08-13 拍板
