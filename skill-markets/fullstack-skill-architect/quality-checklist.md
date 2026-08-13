# Quality Checklist — fullstack-skill-architect 自检清单

> 蒸馏完成后,必须逐项检查。

---

## §1 验证性检查

```
[ ] 每条铁律都有验证方法?
    - 9 条铁律 × 验证命令 = ✓
    - 例: "门禁硬化" → "stage-gate-pre-stage.sh --check exit 0 = 放行"
[ ] 无法验证的已标注为 "建议"?
[ ] 有具体阈值(如: ≤ 10 铁律 ≤ 150 行)而非抽象描述?
```

## §2 具体性检查

```
[ ] 有具体命令/路径而非 "某个文件"?
    - §2 5 步流程 + §5 借鉴来源汇总 全部含具体路径
[ ] 有具体流程而非 "先思考一下"?
    - §2 每步有明确动作 + 验证标准
[ ] 有具体判定标准而非 "视情况而定"?
    - 二元判定表 + 5 把刀启用矩阵
```

## §3 完整性检查

```
[ ] 适用范围已界定?
    - §4 适用场景 vs 不适用场景(5 类适用 + 4 类不适用)
[ ] 不适用场景已列出?
    - 见上
[ ] 前置依赖已声明?
    - requires.skills + requires.optional + references 必读清单
```

## §4 反例检查

```
[ ] 每个最佳实践至少配 1 个失败案例?
    - 9 条铁律中 5 条有陷阱编号引用(陷阱 1-7)
    - traps.md 7 个陷阱 = 7 个失败案例
[ ] 失败案例有根因分析?
    - traps.md 每个陷阱含: 现象 + 根因 + 避坑方案
[ ] 有 "避坑指南" 而非只有 "成功路径"?
    - traps.md 全文 200+ 行,避坑指南专章
```

## §5 可执行性检查

```
[ ] Agent 加载后可立即执行?
    - SKILL.md §1 9 铁律 + §2 5 步流程 + templates/output-template.md
[ ] 无歧义表述?
    - 所有铁律用 MUST/NEVER/MUST NOT 明确
[ ] 无缺失前置条件?
    - §0 触发协议 + requires + 必读 references
```

---

## §6 总体评分

| 维度 | 评分 | 说明 |
|---|:-:|---|
| 验证性 | 5/5 | 9 铁律均有验证命令 |
| 具体性 | 5/5 | 5 把刀 + 借鉴来源 + 命令模板 |
| 完整性 | 5/5 | 适用 + 不适用 + 依赖 + 反例全覆盖 |
| 反例价值 | 5/5 | 7 大陷阱 = 7 个真实失败案例 |
| 可执行性 | 5/5 | SKILL.md ≤ 200 行 + templates/output-template.md 配套 |
| **总分** | **5.0/5.0** | ✅ 合格 |

---

## §7 必跑项(交付前最后检查)

```bash
# 1. SKILL.md 行数 ≤ 200
wc -l SKILL.md
  # 必须 ≤ 200

# 2. 必读 references 存在
ls references/{methodology,patterns,traps}.md
  # 3 文件全在

# 3. templates/ 存在
ls templates/output-template.md
  # 必须存在

# 4. quality-checklist.md 存在(本文件)
ls quality-checklist.md
  # 必须存在

# 5. YAML frontmatter 完整
head -10 SKILL.md
  # name / version / description / requires 必填
```

---

## §8 已知限制

```
- 本 skill 价值为多 stage + 多 sub-agent 协同场景
- 单 agent 单任务场景不适用(用 trae-security-review / gitnexus-debugging)
- 项目级配置模板场景不适用(用 fullstack-auto)
- 纯搜索研究场景不适用(用 deep-research)
```

---

*版本: 1.0.0 配套 quality-checklist*