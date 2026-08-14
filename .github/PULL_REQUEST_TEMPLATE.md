## 描述

<!-- 用 1-3 句话说明这个 PR 做了什么 -->

## 改动类型

<!-- 勾选所有适用的项 -->

- [ ] Bug 修复(patch, fix)
- [ ] 新功能(minor, feat)
- [ ] 破坏性变更(major, BREAKING CHANGE)
- [ ] 文档(docs)
- [ ] 重构(refactor, no functional change)
- [ ] 性能优化(perf)
- [ ] 测试(test)
- [ ] CI / 工作流(ci)

## 受影响的子包 / 技能

<!-- 列出此 PR 修改的 skill 或子包路径 -->

- [ ] 无 skill 变更(仅改 CLI / 文档 / CI)
- [ ] `skill-markets/agent-dev-control-kit/` ← 会触发 catalog-guard
- [ ] `skill-markets/<其他>/`(具体填入):

## 自检清单(PR 作者)

<!-- 在你合并前,先勾选每一项 -->

### L1 commit 必跑(本地)

- [ ] `npm run lint` 通过(17 个 .mjs + 8 个 wrapper)
- [ ] `npm run test:unit` 通过
- [ ] 改动技能时 `python scripts/skill-security-guard.py skill-markets/<name>` 通过
- [ ] 新建技能时 `python scripts/skill-structure-guard.py skill-markets/<name>` 通过
- [ ] 改了 agent-dev-control-kit 时 `python scripts/run-agent-dev-control-kit-tests.py` 通过

### L2 push 必跑(本地)

- [ ] `npm run test:integration` 通过
- [ ] `npm run test:coverage` 通过
- [ ] `node src/guards/skill-dependency-guard.mjs <skill>` 通过(改了 skill)
- [ ] `npm run build` 通过

### L3 CI(自动,无需手动)

- [ ] PR workflow `L3-merge-gate` 通过
- [ ] 若改了 agent-dev-control-kit,子 skill CI `agent-dev-control-kit CI` 通过
- [ ] `CAPABILITY-MAP.md` / `SECURITY-MAP.md` 已同步

## 反例自检(对应 §2.4)

- [ ] 我没有用 `--no-verify` 绕过 husky
- [ ] 我没有写 echo-skip 占位 gate(参考 `references/traps.md §AP-2`)
- [ ] 我没新增带 main 缺失的 CLI 脚本(参考 `references/traps.md §AP-3`)
- [ ] 我新增的功能模块都有对应 `references/` 文档

## 关联 Issue

<!-- 关联此 PR 对应的 issue 或 ticket -->

Closes #

## 额外上下文

<!-- 添加任何相关上下文、截图、决策记录 -->