# V11 CI Gate 模板

`v11-gate.yml` 在 CI 层实现四档 Git 门禁（L1-L4）：

- **L1/L2 兜底**：拦截 `git commit --no-verify` / `git push --no-verify` 绕过本地 husky 的情况。
- **L3（PR merge）**：`pull_request` 事件触发，跑 `run-gate-level.py --level L3`（Stage 2/4/4.5 归并 + E2E）。
- **L4（Release）**：`release` / `push tag v*` 事件触发，跑 `run-gate-level.py --level L4`（Stage 5 Accept + 安全审计）。

## 使用

1. 复制到项目 `.github/workflows/v11-gate.yml`：

```bash
cp templates/ci/v11-gate.yml <project>/.github/workflows/v11-gate.yml
```

2. 确保项目内有（由 scaffold `files/` 复制得到）：

- `gates/gate-config.json` — L1-L4 档位声明（单一权威源）
- `scripts/run-gate-level.py` — 按档位执行器

3. 推送到 GitHub，CI 会在 push / PR / release 时自动运行。

## 检查项

- **L1/L2 兜底 job**：状态卡存在性 + launch-guard 自校验 + lint/typecheck/test/build
- **L3 job**（PR merge）：`run-gate-level.py --level L3`
- **L4 job**（release/tag）：`run-gate-level.py --level L4`

## 配置

各档位的 checks / gates / timeout / blocking 全部定义在 `gates/gate-config.json`，
改门禁只改这一个文件，CI 与本地 husky 共享同一份声明（流程层单一权威源）。