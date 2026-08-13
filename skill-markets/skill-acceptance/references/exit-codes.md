# exit-codes.md — 退出码矩阵

> 5 个退出码严格区分失败语义，避免 CI 把"参数错"误判为"代码坏"。

## §1 退出码表

| Code | 语义 | 触发条件 | CI 行为 | 推荐动作 |
|:----:|------|----------|---------|----------|
| 0 | PASS | 6 项全过、无 warn 无 block | ✅ 准入 | merge / release |
| 2 | WARN | MEDIUM ≥ 3 或单检查 score<60 或 ≥ 1 检查 WARN | ⚠️ 警告放行（人工 review） | 阅读 `--report` JSON 决定是否放行 |
| 4 | BLOCK | 任一 HIGH finding 或 `--strict` 模式下 MEDIUM ≥ 3 | 🛑 阻断 PR | 修 skill 包，重跑 |
| 5 | ARG_ERROR | `--target` 路径不存在 / 非目录 / 参数拼错 | 🔧 修复命令 | 检查 CLI 参数拼写 + 路径 |
| 6 | INTERNAL_ERROR | verify.py 自身异常（除被 `INTERNAL_ERROR` 包裹的检查函数外） | 🐛 修脚本 | 提交 issue（附堆栈） |

## §2 退出码互斥规则

```
exit=0 → 仅当 6 项全 PASS（无任何 MEDIUM 命中）
exit=2 → 6 项无 BLOCK + 至少 1 个 WARN 或 MEDIUM 累计 ≥ 3
exit=4 → 6 项中 ≥ 1 个 BLOCK（HIGH 触发）
exit=5 → 启动期校验失败（参数 / 路径）—— 永远不会和 0/2/4 同时出现
exit=6 → 脚本顶层 try/except 捕获的异常 —— 永远不会和 0/2/4/5 同时出现
```

## §3 fail-on 阈值（--fail-on）

| 取值 | 含义 | 退出映射 |
|------|------|----------|
| `PASS` | 任何非 PASS 即非 0 | 0 之外全退出 |
| `WARN`（默认 `BLOCK`） | WARN 以上退出 | 0/2 → 0；4/5/6 → 原值 |
| `BLOCK`（默认） | 仅 BLOCK 及以上退出 | 0/2 → 0；4/5/6 → 原值 |

## §4 CI 集成示例（GitHub Actions）

```yaml
# .github/workflows/skill-acceptance.yml
name: skill-acceptance
on:
  pull_request:
    paths: ['skill-markets/**']
jobs:
  verify:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: extract skill name
        id: detect
        run: |
          $changed = (git diff --name-only HEAD~1 HEAD | Select-String '^skill-markets/([^/]+)/').Matches.Groups[1].Value
          echo "skill=$changed" | Out-File -Encoding ascii $env:GITHUB_OUTPUT -Append
      - name: verify (block=4 ⇒ fail)
        run: |
          python skill-markets/skill-acceptance/scripts/verify.py `
            --target skill-markets/${{ steps.detect.outputs.skill }} `
            --json --report .trae/tmp/sa-${{ steps.detect.outputs.skill }}.json
        # exit=4 / 5 / 6 自动失败 job；exit=2 仅警告（不阻断）
      - name: upload report on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: sa-report
          path: .trae/tmp/sa-*.json
```

## §5 本地调试退出码

```bash
# 模拟 5 类退出
python verify.py                              # exit=5 ARG_ERROR (缺 --target)
python verify.py --target D:/not/exist       # exit=5 ARG_ERROR
python verify.py --target ../<bad-skill>     # exit=4 BLOCK
python verify.py --target ../<ok-skill>      # exit=0 PASS
python verify.py --target ../<mid-skill> --strict --fail-on WARN  # exit=2 WARN
```