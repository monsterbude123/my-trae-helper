# 技能市场三层控制体系 — 快速参考

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> **一句话铁律**: 技能管理 = Execution（执行） + Guard（守卫） + Gate（门禁）

---

## 快速开始

### 1. 创建新技能

```bash
# 自动执行: 风险判定 → 结构检查 → 创建 → 验证
trae-skills create my-new-skill "我的新技能"
```

### 2. 验证技能

```bash
# 执行所有守卫: 安全 + 结构 + 依赖 + 能力
trae-skills verify my-new-skill
```

### 3. 安装技能（带依赖检查）

```bash
# 自动执行: 依赖检查 → 冲突检查 → 备份 → 安装 → 审计
trae-skills add my-new-skill -a trae-cn
```

---

## CLI 命令对照表

| 命令 | Execution | Guard | Gate |
|------|-----------|-------|------|
| `create` | ✅ Skill Change Control | ✅ Structure Guard | - |
| `verify` | - | ✅ All Guards | - |
| `add` | ✅ Skill Install Control | ✅ Dependency Guard | - |
| `remove` | ✅ Skill Install Control | - | - |

---

## Guard 检查清单

### 安全守卫（Security Guard）

- ✅ HIGH 风险 = 0（文档引用除外）
- ✅ 硬编码密钥 = 0
- ✅ 未参数化 Shell = 0

**触发**: `pre-commit` / `trae-skills verify`

### 结构守卫（Structure Guard）

- ✅ 目录名 kebab-case
- ✅ SKILL.md 有 YAML frontmatter
- ✅ SKILL.md ≤ 500 行
- ✅ agents 文件名无 -agent 后缀

**触发**: `pre-commit` (新建) / `trae-skills verify`

### 依赖守卫（Dependency Guard）

- ✅ 硬依赖已安装（缺失则阻断）
- ✅ 软依赖缺失时警告

**触发**: `pre-add` / `pre-push` / `trae-skills verify`

### 能力守卫（Capability Guard）

- ✅ 脚本不重复（复用共享注册表）
- ✅ CAPABILITY-MAP.md 已同步

**触发**: `pre-create` / `trae-skills verify`

---

## Gate 门禁层级

### L1 Commit Gate（提交前）

**触发**: `git commit`

**检查**:
1. Lint
2. TypeCheck
3. Unit Tests
4. 技能安全守卫（仅变更的技能）
5. 技能结构守卫（仅新建技能）

### L2 Push Gate（推送前）

**触发**: `git push`

**检查**:
1. Integration Tests
2. Coverage
3. 技能依赖守卫（全部技能）
4. Build

### L3 Merge Gate（合并前）

**触发**: PR merge

**检查**:
1. L2 全部
2. Code Review
3. CAPABILITY-MAP.md 同步
4. SECURITY-MAP.md 同步
5. GitNexus 影响分析

### L4 Publish Gate（发布前）

**触发**: Release

**检查**:
1. L3 全部
2. 性能基准
3. 安全扫描（全量）
4. 技能市场完整性检查

---

## 文件位置速查

### Execution Skills

| 文件 | 功能 |
|------|------|
| [src/execution/skill-change-control.mjs](../../../src/execution/skill-change-control.mjs) | 新建/修改/删除技能 |
| [src/execution/skill-install-control.mjs](../../../src/execution/skill-install-control.mjs) | 安装/卸载技能 |

### Guard Skills

| 文件 | 功能 |
|------|------|
| [scripts/skill-security-guard.py](../../../scripts/skill-security-guard.py) | 安全扫描 |
| [scripts/skill-structure-guard.py](../../../scripts/skill-structure-guard.py) | 结构检查 |
| [src/guards/skill-dependency-guard.mjs](../../../src/guards/skill-dependency-guard.mjs) | 依赖检查 |
| [scripts/skill-capability-guard.py](../../../scripts/skill-capability-guard.py) | 能力去重 |

### Gate Hooks

| 文件 | 功能 |
|------|------|
| [.husky/pre-commit](../../../.husky/pre-commit) | L1 提交门禁 |
| [.husky/pre-push](../../../.husky/pre-push) | L2 推送门禁 |

### 设计文档

| 文件 | 内容 |
|------|------|
| [skill-market-control-design.md](skill-market-control-design.md) | 完整设计文档 |

---

## 审计日志

**位置**: `logs/skill-market-audit.jsonl`

**格式**:
```json
{
  "timestamp": "2026-08-14T10:30:00Z",
  "action": "install",
  "skill": "fullstack4TraeV11",
  "agent": "trae-cn",
  "user": "septe",
  "result": "success",
  "duration_ms": 1234
}
```

---

## 与现有体系联动

| 体系 | 联动方式 |
|------|---------|
| CAPABILITY-MAP.md | 新建/修改/删除技能时自动同步 |
| SECURITY-MAP.md | 新建/修改技能时重新评估安全评分 |
| GitNexus | L3 门禁调用影响分析 |

---

## 常见问题

### Q: 如何绕过门禁？

**A**: 不建议绕过。如确需绕过，使用 `--no-verify`（Git）或 `-y`（CLI），但需承担风险。

### Q: 安全扫描失败怎么办？

**A**:
1. 检查是否为文档引用（白名单）
2. 修复真实风险代码
3. 重新运行 `trae-skills verify`

### Q: 依赖检查失败怎么办？

**A**:
1. 硬依赖缺失 → 先安装依赖: `trae-skills add <dep>`
2. 软依赖缺失 → 确认可接受降级影响

---

**维护者**: my-trae-helper team
**最后更新**: 2026-08-14
