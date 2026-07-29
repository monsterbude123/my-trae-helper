# 技能依赖检查协议

> **核心铁律**：技能加载时，依赖缺失 = 🛑 阻断并提示用户，禁止 agent 自行降级。
> **根因**：agent 静默降级 → 用户不知道工作流被削弱 → 交付质量与预期严重偏离。

---

## §1 问题场景

```
用户触发 fullstack4TraeV9 流程
  │
  ├── fullstack4TraeV9 requires: [acceptance-discipline]
  │     optional: [ponytail4Trae, gitnexus4Trae, doc-map-manager]
  │
  ├── agent 检测: acceptance-discipline 未安装
  │     ❌ 现状: agent 自行跳过验收阶段，用户无感知
  │     ✅ 应: 🛑 阻断，提示用户安装缺失依赖
  │
  └── agent 检测: gitnexus4Trae 未安装（optional）
        ❌ 现状: agent 静默降级为 grep，用户不知道
        ✅ 应: ⚠️ 警告用户 "缺少 gitnexus4Trae，影响面分析降级为 grep"
```

---

## §2 依赖声明规范

### 2.1 YAML frontmatter 格式

```yaml
---
name: skill-name
requires:
  skills: [required-skill-1, required-skill-2]   # 缺失任一 → 🛑 阻断
  optional: [optional-skill-1, optional-skill-2]  # 缺失 → ⚠️ 警告 + 说明降级影响
---
```

### 2.2 `requires.skills` 与 `requires.optional` 区分

| 字段 | 含义 | 缺失行为 |
|------|------|---------|
| `skills` | 硬依赖：核心功能必需 | 🛑 阻断加载，提示用户安装 |
| `optional` | 软依赖：增强功能，缺失可降级运行 | ⚠️ 警告用户，说明降级后果，用户确认后继续 |

---

## §3 加载时检查流程

```
Skill 被触发加载
  ↓
Step 1 — 解析 YAML frontmatter 中的 requires 字段
  ↓
Step 2 — 逐项检查 requires.skills（硬依赖）:
  检查目标技能是否在 builtin_skills/ 或 .trae/skills/ 中存在
  ├── 全部存在 → 继续 Step 3
  └── 任一缺失 → 🛑 BLOCKED
        输出:
        ❌ 技能 "{当前技能}" 加载失败：缺少必需依赖
        缺失技能: {skill-name-1}, {skill-name-2}
        安装命令: Copy-Item -Recurse ".../{skill-name}" "$env:USERPROFILE\.trae-cn\builtin_skills\{skill-name}"
        提示: 这些技能是核心功能必需，不可跳过。安装后重试。
        停止加载，不继续。
  ↓
Step 3 — 逐项检查 requires.optional（软依赖）:
  ├── 全部存在 → 🟢 完整功能，继续加载
  └── 部分缺失 → ⚠️ WARNING
        输出:
        ⚠️ 技能 "{当前技能}" 缺少可选增强技能
        缺失: {skill-name-1} — 影响: {降级说明}
               {skill-name-2} — 影响: {降级说明}
        当前将以降级模式运行。建议安装以上技能以获得完整体验。
        用户选择:
          [1] 继续降级运行  [2] 中止，先安装技能
  ↓
Step 4 — 加载技能内容，注入降级标记:
  若有 optional 缺失 → 在技能上下文中注入:
  "⚠️ 当前会话降级模式: {skill-name} 不可用，相关功能已关闭。"
```

---

## §4 降级影响说明模板

每个 `optional` 依赖必须在 SKILL.md 或 CAPABILITY-MAP.md 中声明降级影响：

```yaml
# CAPABILITY-MAP.md 或 SKILL.md requires 段中记录:
# 依赖技能名: 降级影响一句话

示例 (fullstack4TraeV9):
requires:
  skills: [acceptance-discipline]    # 缺失 → 🛑 阻断（无此技能无法走验收门禁）
  optional:
    - ponytail4Trae                  # 缺失 → 无懒人模式提示，代码可能过度工程
    - gitnexus4Trae                  # 缺失 → 影响面分析降级为 grep，盲区风险 ↑
    - doc-map-manager                # 缺失 → 文档索引无法自动更新，DOC SYNC 不完整
```

---

## §5 禁止行为

| 禁止 | 后果 | 替代 |
|------|------|------|
| agent 发现 requires.skills 缺失后自行降级 | 用户不知道核心功能被跳过 | 🛑 阻断，提示安装 |
| agent 发现 optional 缺失后不告知用户 | 交付质量隐性下降 | ⚠️ 输出警告 + 降级说明 |
| agent 用 "应该也能跑" 判断依赖 | 不可靠的猜测 | 用 §3 机械检查流程 |
| 技能不声明 requires 但有跨技能引用 | CAPABILITY-MAP 无法维护依赖图 | 新建 Skill 时同步声明 requires |
| 修改依赖后不更新 CAPABILITY-MAP | 地图与 SKILL.md 不一致 | 同步更新（维护规则 §4） |

---

## §6 技能开发者自检

```
新增技能时:
  [ ] YAML frontmatter 声明了 requires 字段？
  [ ] requires.skills 中的每个依赖都确实不可缺失？
  [ ] requires.optional 中的每个依赖都标注了降级影响？
  [ ] CAPABILITY-MAP.md 的依赖图已更新？
  [ ] 技能加载后首段逻辑是依赖检查？（应用 §3 流程）
```
