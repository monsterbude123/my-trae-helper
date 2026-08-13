# Git Hooks — 门禁执行器

> 由 `.husky/` 目录托管的 Git 钩子。
> 启用方式：`git config core.hooksPath .husky`

---

## pre-commit

每次 `git commit` 前自动：

1. **技术安全扫描**（`scan_skills_dir.py`）—— 8 类风险（rm -rf / eval / 硬编码密钥 / Shell / HTTP / 提权 / 栈泄露 / 弱加密）
   - HIGH 命中 → 阻断 commit
2. **严谨用词扫描**（`scan_rigor.py`）—— 10 类模式（情绪化 / 绝对断言 / 模糊量化 / 兜底模糊 / 未定义术语 / 死角提示词 / 主观判断 / 禁用短语 / 过度承诺 / 不可量化收益）
   - WARNING → 仅警告，不阻断；提示人工复查

扫描范围：本次 commit 涉及的 `.py/.sh/.ps1/.js/.ts/.md/.yaml/.yml/.json/.toml` 文件。

详细用词规则：[references/rigor-patterns.md](../skill-markets/trae-security-review/references/rigor-patterns.md)

报告落点：`audit_reports/`。
