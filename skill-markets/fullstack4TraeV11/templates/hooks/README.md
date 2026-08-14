# V11 Hooks 配置（蒸馏自 V10 + V11 独有）

> TRAE IDE v3.5.66+ 支持 Hooks。V11 13 个 hook 覆盖 5 种事件。
> V11 vs V10: 13 vs 10（含 V11 gitnexus 双端 + V11 shell hook 3 个）。

---

## 13 hook 覆盖 5 种事件（V11.1）

| # | Hook | 事件 | 默认 | 关键能力 |
|---|------|------|:---:|------|
| 1 | **gitnexus-session-check** | `SessionStart` | ✅ | GitNexus 索引 staleness 检测 + 后台刷新 |
| 2 | **session-start** | `SessionStart` | ✅ | 6 层知识发现协议 + Article XVII secret 检查 + prototypes 完整性 |
| 3 | **complexity-guard** | `UserPromptSubmit` | ❌ | 复杂度评分 + GitNexus First 提醒 + Article XVII secret 警告 |
| 4 | **doc-sync-gate** | `PreToolUse` | ✅ | 写 src/ 前校验 DOC SYNC + spec-purge 历史感知 |
| 5 | **contract-gate** | `PreToolUse` | ✅ | 写代码前检查 contracts/ + spec-purge 历史区分 |
| 6 | **spec-validate-hook** | `PostToolUse` | ✅ | Delta Spec 格式 + Scenario + SHALL + prototypes/ 完整性 |
| 7 | **auto-test** | `PostToolUse` | ✅ | 自动跑 jest/vitest/pytest/cargo/go + Article XVII secret 字面量检测 + spec.md Acceptance 检测 |
| 8 | **drift-detect** | `PostToolUse` | ✅ | 契约漂移检测 + spec-purge 历史感知 |
| 9 | **pre-stage**（V11 独有）| shell | ✅ | Stage 切换前必跑 stage-gate.py |
| 10 | **post-stage**（V11 独有）| shell | ✅ | Stage 结束后必跑 state-card-validator.py |
| 11 | **pre-accept**（V11 独有）| shell | ✅ | Stage 5 Accept 前必跑 phase-gate.py --verify-rot-scan |
| 12 | **tasks-integrity** | `Stop` | ✅ | 任务完成度检查 + spec-purge 历史上下文 |
| 13 | **gitnexus-session-finalize** | `Stop` | ✅ | GitNexus 索引后台刷新（写端，与 #1 配对）|

---

## V11 vs V10 差异

| 维度 | V10 | V11 |
|------|-----|-----|
| Hook 数 | 10 | **13** |
| 蒸馏自 V10 | — | 8 个（session-start / auto-test / drift-detect / doc-sync-gate / contract-gate / spec-validate-hook / complexity-guard / tasks-integrity）|
| 独有设计 | — | 5 个（pre-stage / post-stage / pre-accept shell + gitnexus 双端蒸馏）|
| TRAE IDE event 覆盖 | SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop | 同上（5 种全覆盖）|
| Article XVII secret 检测 | ❌ | ✅ auto-test.py + complexity-guard.py |
| V11 gitnexus 双端 | ❌ | ✅ session-check + session-finalize |

---

## 触发流程

```
SessionStart
  ├─ ① gitnexus-session-check.py：HEAD vs meta.json → 后台 analyze（如过期）
  └─ ② session-start.py：注入 6 层知识发现协议 + Article XVII secret 检查
       （注: GitNexus 索引已由 ① 自动后台刷新）

用户 Prompt → complexity-guard.py（若启用）
  含"改 symbol" → V11 Article V.5 提醒跑 gitnexus impact()
  含 secret → V11 Article XVII 警告
     ↓
AI Agent 执行任务
     ├── PreToolUse (Write|Edit)
     │     ├── doc-sync-gate.py：DOC SYNC + spec-purge
     │     └── contract-gate.py：contracts/ + spec-purge
     ├── PostToolUse
     │     ├── spec-validate-hook.py：Delta Spec + Scenario + SHALL + prototypes/
     │     ├── auto-test.py：自动测试 + Article XVII secret 检测 + spec.md Acceptance
     │     └── drift-detect.py：契约漂移 + spec-purge 区分
     └── Stop
           ├─ tasks-integrity.py：完成度 + spec-purge 上下文
           └─ gitnexus-session-finalize.py：后台触发 analyze

Stage 切换
  ├─ pre-stage.sh：stage-gate.py 验证当前状态卡
  └─ post-stage.sh：state-card-validator.py 验证状态卡更新

Stage 5 Accept 前
  └─ pre-accept.sh：phase-gate.py --verify-rot-scan
```

---

## GitNexus 双端（V11 NEW）

| 端 | Hook | 职责 |
|----|------|------|
| 读（SessionStart）| `gitnexus-session-check.py` | 检测 staleness → 后台刷新 |
| 写（Stop）| `gitnexus-session-finalize.py` | 写新 HEAD → 后台刷新 |

**关键设计**:
- 用 `git rev-parse --show-toplevel` 找逻辑项目根
- 后台用 `subprocess.Popen + DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP`
- 跑前 HEAD 比对：lastCommit == HEAD 时跳过
- `GITNEXUS_AUTO_ANALYZE=0` 关闭
- 日志写 `.gitnexus/analyze.log`
- 禁止手动跑 analyze

---

## V11.1 安装

```bash
# 1. 部署 V11 skill 到 user-level
cp -r skill-markets/fullstack4TraeV11/* ~/.trae-cn/skills/fullstack4TraeV11/

# 2. 安装 hooks 到项目
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/install-hooks.py --project-root .

# 3. 验证
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .
```

---

## 自定义

- 修改 `.trae/hooks.json` 中的 `enabled` 字段启用/禁用
- 修改 `matcher` 字段限定触发范围
- 编写自己的 Hook 脚本放在 `.trae/hooks/` 目录下

---

## 关联引用

- [fullstack-hooks.json](fullstack-hooks.json) — TRAE IDE event 注册
- [scripts/install-hooks.py](../../scripts/install-hooks.py) — V11 13 hook 安装工具
- [scripts/hooks-fidelity.py](../../scripts/hooks-fidelity.py) — Hook 保真度门禁
- Article XVII — Secret 红化（V11 NEW，见 references/common-iron-rules.md）