# Common Anti-Patterns — 公共反模式库

> V11 所有 stage 必读的公共反模式索引。每个反例指向具体 stage 的 anti-patterns/ 目录。

---

## 反例索引（按严重度）

### P0 阻断类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 1 | **跳过必走 stage**（V11 §0 硬门禁）| 各 stage SKILL.md §铁律 |
| 2 | **编造证据**（V10.12 ANTI-反模式）| Stage 3 implement/anti-patterns/02-fabricate-evidence.md |
| 3 | **reviewer 帮忙修代码**（REVIEWER DOES NOT FIX）| Stage 9 review/anti-patterns/02-reviewer-fix-code.md |
| 4 | **不可证伪理由**（如未定义术语、未指明位置的偏差、未量化裁剪、未测量心理负担、未定义的概念迁移）| 公共铁律 Article XV §15.4 |
| 19 | **循环 PASS 模式**（不止一次"我搞错了"+ 重新委派，无具体改进）| [./loop-pass-pattern.md](./loop-pass-pattern.md) |
| 20 | **甩锅用户模式**（"请你去做 X"代替自己能做的部分）| [./user-orchestration-pattern.md](./user-orchestration-pattern.md) |
| 21 | **未读 rule 就自评 PASS**（rule 太长不读 + 反复踩同一雷）| [./unread-rule-pass.md](./unread-rule-pass.md) |
| 22 | **secret 写入工具调用参数**（V11 实战 P0 安全事件）| [./secret-in-tool-arg.md](./secret-in-tool-arg.md)（Article XVII）|

### P1 高优类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 5 | **虚假绿灯**（修改测试让用例通过）| Stage 3 implement/anti-patterns/01-skip-red.md |
| 6 | **漂移静默**（实现与契约不一致不报告）| Stage 3 implement/anti-patterns/04-drift-silent.md |
| 7 | **跳过 rot-scan 直接 Accept** | Stage 10 rot-scan/anti-patterns/01-skip-rot-scan.md |
| 8 | **修复完不改 bug 单** | Stage 12 bug-fix/anti-patterns/03-not-update-bug.md |
| 9 | **跳过 e2e 先行直接修** | Stage 12 bug-fix/anti-patterns/01-skip-e2e-first.md |

### P2 中优类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 10 | **跳过 DOMAIN FIRST 直接写 API** | Stage 6 contract/anti-patterns/01-skip-domain.md |
| 11 | **跳过孤儿契约测试清理** | Stage 6 contract/anti-patterns/02-skip-orphan-sweep.md |
| 12 | **BREAKING 变更不用户确认** | Stage 6 contract/anti-patterns/03-breaking-without-confirm.md |
| 13 | **契约漂移**（代码与契约不一致）| Stage 6 contract/anti-patterns/04-contract-drift.md |
| 14 | **"非阻塞 FAIL" 放水** | Stage 9 review/anti-patterns/01-non-blocking-fail.md |
| 15 | **编造测试覆盖** | Stage 9 review/anti-patterns/03-fabricate-coverage.md |
| 23 | **GitNexus 可用却 grep / glob**（V10 process-rot-analysis.md 蒸馏） | [02-grep-instead-of-gitnexus.md](02-grep-instead-of-gitnexus.md)（Article V.5）+ [.gitnexus-降级-replace-by-grep.md](.gitnexus-降级-replace-by-grep.md) |

### P3 低优类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 16 | **跳过知识沉淀直接归档** | Stage 11 accept/anti-patterns/01-skip-knowledge-extract.md |
| 17 | **修改归档文件** | Stage 11 accept/anti-patterns/02-modify-archive.md |
| 18 | **"启动 = 完成" 软指标** | Stage 8 real-verify/anti-patterns/01-startup-equals-done.md |

---

## 反例自检清单

```yaml
anti_patterns_checklist:
  P0:
    - [ ] 不跳 stage？
    - [ ] 不编证据？
    - [ ] reviewer 不改代码？
    - [ ] 无抽象理由？
    - [ ] 不循环 PASS（无具体改进的"我搞错了"+ 重新委派）？
    - [ ] 不甩锅用户（自己能做的部分不交给用户）？
    - [ ] rule 通读后才自评 PASS？
    - [ ] secret 不写入工具调用参数？
  P1:
    - [ ] 不虚假绿灯？
    - [ ] 漂移必报告？
    - [ ] 必跑 rot-scan？
    - [ ] 修复回写 bug 单？
    - [ ] e2e 必先 FAIL？
  P2:
    - [ ] DOMAIN FIRST？
    - [ ] 孤儿契约测试清理？
    - [ ] BREAKING 用户确认？
    - [ ] 契约三方同步？
    - [ ] 无"非阻塞 FAIL"？
    - [ ] 真实覆盖？
    - [ ] GitNexus 可用却 grep？（Article V.5 不可降级）
  P3:
    - [ ] 知识沉淀先于归档？
    - [ ] 归档不可修改？
    - [ ] 启动有可见产物？
```

---

## 关联引用

- [constitution.md](constitution.md) — 17 Articles 宪法
- [common-iron-rules.md](common-iron-rules.md) — 公共铁律
- 各 stage anti-patterns/: skills/{NN}-{name}/anti-patterns/README.md