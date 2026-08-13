# Rigor Patterns — 严谨用词扫描词库

> 与 `scan_skills_dir.py` 并列的**内容质量**扫描组件。
> 关注"用词情绪化 / 规则存在死角"两类风格缺陷，不检测技术安全风险。
> 目标：让 Skill 文档保持可证伪、可执行、可量化的中性表达。

---

## §1 风险类别总览

| Code | 类别 | 严重度 | 触发示例（应避免） | 替换示例（推荐） |
|------|------|--------|-------------------|------------------|
| `EMOTIONAL_TONE` | 情绪化用词 | LOW | "非常好用"、"非常强大"、"完美" | "实测通过"、"通过 X 项验证" |
| `ABSOLUTE_CLAIM` | 绝对断言 | LOW | "100% 安全"、"零风险"、"完全可靠" | "在 X 条件下验证通过" |
| `VAGUE_QUANTIFIER` | 模糊量化 | LOW | "少量"、"大量"、"很多"、"不少" | "≤ N / ≥ N / N = ..." |
| `INCLUSIVE_HEDGE` | 兜底模糊 | MEDIUM | "等"、"等等"、"诸如此类"、"等等等" | 列举全部或注明省略条件 |
| `UNDEFINED_TERM` | 未定义术语 | MEDIUM | "特殊情况"、"极端情况"、"相关" 等不指代具体对象 | 给出具体触发条件或枚举 |
| `DEAD_ANGLE_MARKER` | 死角提示词 | MEDIUM | "一般情况下"、"通常情况下"、"大多数情况下" | 给出统计或显式边界 |
| `PERSONAL_OPINION` | 主观判断 | LOW | "我觉得"、"我认为"、"应当" 等主观 | "依据 X 规范 / 实测 N = ..." |
| `PROHIBITED_PHRASE` | 禁用短语 | LOW | "显而易见"、"毫无疑问"、"显然" | 删除或提供证据 |
| `OVER_PROMISE` | 过度承诺 | MEDIUM | "一键搞定"、"轻松实现"、"速成" | 注明先决条件和代价 |
| `UNMEASURED_BENEFIT` | 不可量化收益 | LOW | "提升效率"、"改善体验"、"优化性能" | "延迟从 X 降到 Y ms" |

---

## §2 工程化规则

```
1. 匹配粒度：行级（中文整句；英文按 word boundary）
2. 中文：依靠常用短语列表（zh_patterns）；不含分词依赖
3. 英文：使用 \b 词边界正则
4. 豁免：
   - 代码块（```...```）自动豁免
   - 行内代码（`...`）自动豁免
   - HTML 注释豁免（与 scan_skills_dir.py 复用白名单）
5. 文档自动豁免范围：与 scan_skills_dir.py 一致（.md/.txt 默认豁免技术 CODE；本工具不豁免）
6. 计数阈值：
   - 总命中 ≥ 30 → WARNING
   - EMOTIONAL_TONE / PROHIBITED_PHRASE 总数 ≥ 10 → WARNING
   - 其它任一类别 ≥ 5 → WARNING
   - 判定：WARNING 提示人工复核；PASS 不阻断 commit
```

---

## §3 反例对照

### 反例（应避免）

```markdown
本工具非常好用，能 100% 解决所有 Skill 安全隐患。
一般情况下，直接执行即可；特殊情况请自行判断。
显而易见，这是最佳实践。
```

### 正例（应采用）

```markdown
本工具覆盖 8 类风险（见 references/risk-patterns.md）。
在 `python >= 3.8` 与上述三层白名单配置下，命中判定见 `verdict` 字段。
未覆盖的边界：动态语言插件、未引用的本地脚本（已知 0 项）。
```

---

## §4 维护

新增类别 → 在 §1 加一行 + 在 `scripts/lib/rigor_patterns.py` 注册 →
跑 `python scripts/scan_rigor.py --self-test` 自检通过 → 提交。
