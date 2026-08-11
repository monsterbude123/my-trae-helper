# 7 大腐烂分类 + 19 个腐烂点（Rot Classification）

> Stage 4.5 Rot Scan 必走。V10 process-rot-analysis.md 蒸馏。

---

## 7 大腐烂分类

1. **流程腐烂** — 流程漂移 / 跳过 / 任意裁剪
2. **代码腐烂** — TODO/FIXME 堆积 / 800 行超文件
3. **文档腐烂** — spec/合同/INDEX 不同步
4. **测试腐烂** — rot #12 孤儿测试 / 凑分覆盖
5. **构建腐烂** — Bundle Staleness / dist/ 不一致
6. **视觉腐烂** — 截图过期 / 无 PIL 校验
7. **状态腐烂** — state-card-staleness / 状态说谎

## 19 个腐烂点（V10 实战蒸馏）

| # | 名称 | 类型 | 检测 |
|:---:|------|------|------|
| 1 | spec 与代码漂移 | 文档 | drift-detect.py |
| 2 | state-card-staleness | 状态 | state-card-validator.py |
| 3 | archive/ 被修改 | 文档 | git diff archive/ |
| 4 | self-aggrandizing 报告 | 流程 | proactive-scan.py §6 |
| 5 | stub 堆积（rot #13）| 代码 | proactive-scan.py §8 |
| 6 | orphan tests（rot #12）| 测试 | orphan-detector.py |
| 7 | Bundle Staleness（rot #13）| 构建 | dist-hash-check.py |
| 8 | 截图过期（>7 天）| 视觉 | visual-content-check.py |
| 9 | 截图过暗/过亮 | 视觉 | PIL 直方图 |
| 10 | 截图 size <5KB | 视觉 | LS 验证 |
| 11 | 抽象理由（V10.10）| 流程 | reason-classifier.py |
| 12 | 状态卡说谎 | 状态 | proactive-scan.py §7 |
| 13 | config UI 假连通 | 文档 | 配置治理 §1 |
| 14 | 配置硬编码 | 代码 | hardcode-scanner.py |
| 15 | 注释 vs 代码软漂移 | 文档 | 配置治理 §2 |
| 16 | 目录树不一致 | 文档 | project-health-auditor |
| 17 | 版本残留（.bak / .old）| 代码 | proactive-scan.py §1 |
| 18 | git 未跟踪大文件 | 构建 | proactive-scan.py §5 |
| 19 | 测试断言为空 | 测试 | proactive-scan.py §4 |

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md)
- [scan-protocol.md](scan-protocol.md)
- V10 process-rot-analysis.md: `V10 来源` (已蒸馏到本文档)
