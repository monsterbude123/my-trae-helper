## §8 通用 Self-Check Iron Law(2026-08-21 NEW)

> **核心命题**:每个 skill 应自带 `scripts/<name>-self-check.sh`(POSIX sh,无 Python/Node 依赖),
> 在 `SKILL.md` §X 明示:**触发时机 / 检测项 / 失败 remediation**。
> 用户加载 skill 后,hook 自我监控自己是否已 installed + 配置是否完整 — 不写 self-check = 用户永远不知道 skill 是否生效或已 broken。

### 8.1 必备三段(在 SKILL.md §X 明文)

| 段 | 内容 | 示例 |
|----|------|------|
| **触发时机** | 何时跑(session start / 关键操作前 / pre-commit / 手动) | "每个 agent 加载本 skill 后自动跑一次" |
| **检测项** | 检查哪些维度(配置完整性 / 文件存在 / 协议兼容) | "检测 `.trae/hooks.json` / `.claude/settings.json`" |
| **失败 remediation** | 失败时给用户看的单行 stdout + 详细 stderr | "stdout 单行 `[HOOK-MISSING] 跑 install-snippet.sh`" |

### 8.2 三态设计(标杆实现)

> 标杆:`skill-markets/project-self-improving/scripts/hook-self-check.sh`(详见 [references/hook-self-check.md](references/hook-self-check.md))

| 状态 | 含义 | exit code | 用户操作 |
|------|------|-----------|----------|
| `INSTALLED` | hook 已配置 + 指向本 skill | `0` | 继续 |
| `MISSING_CONFIG_FILE` | 无 hook config 文件(active agent 对应) | `1` | 跑 `install-snippet.sh` |
| `MISSING_HOOK_ENTRY` | config 文件存在但无本 skill 的 entry | `1` | 从 `references/<agent>-integration.md` 复制 snippet |

### 8.3 反例库

| 反例 | 后果 |
|------|------|
| 不写 self-check | 用户永远不会知道 skill 是否生效 / hook 是否 broken — 静默失败是 worst outcome |
| self-check 永远返回 0 | 无任何验证价值 = 没写 |
| self-check 静默退出(无 stdout) | 用户看不到状态变化,无法决定下一步 |
| self-check 自动改 config 文件 | 违反 "installation is the human's call" — agent 不应该替用户决策 |
| self-check 依赖 Python / Node | 与 §7.6 共享脚本探测不通用 — 跨平台时容易断 |
| self-check 无三态 | 失败/成功二态无法区分"完全没装"vs"装了但没启用",remediation 不精准 |

### 8.4 与 §7 Gate 自验收铁律的差别

```
§7 Gate 自验收铁律:
  适用对象:Gate / Guard 脚本自身(.husky/* / *.guard.py / workflow)
  时机:写完 Gate 后必须用真反例验证其能真阻断(防"假通过")
  关注点:Gate 自身的 BLOCK 能力是否生效

§8 通用 Self-Check Iron Law(本节):
  适用对象:Skill 自身的 hook / 依赖完整性
  时机:Skill 加载后由 agent / hook 自动跑
  关注点:Skill 自身的"我装了吗" / "我配了吗"自检能力

两者正交:
  §7 = "Gate 真的能阻断"
  §8 = "Skill 真的被启用"
```

### 8.5 标杆实现引用

- `skill-markets/project-self-improving/scripts/hook-self-check.sh` — 第一个按 §8 落地的 skill
- `skill-markets/project-self-improving/references/hook-self-check.md` — 协议规范
- `skill-markets/common-project-coding-conf/scripts/cpcc-self-check.mjs` — Node 版等价实现(供 JS-only 环境)

### 8.6 落地检查清单(新 skill 创建时)

```
□ scripts/<name>-self-check.sh 存在 + POSIX sh + 无 Python/Node 硬依赖
□ SKILL.md §X 明文:触发时机 + 检测项 + 失败 remediation 三段
□ self-check 三态(INSTALLED / MISSING_CONFIG_FILE / MISSING_HOOK_ENTRY 等)
□ self-check stdout 单行 + stderr 详细(remediation 直接可复制)
□ self-check 不自动改 config(交给人类决策)
□ 安装说明在 references/<agent>-integration.md(可选)
```
