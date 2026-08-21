# fullstack4TraeV11 V11.8.7 — 顶层截图脚本索引

> **职责**: 替代每个项目 change 内散落的 `m3-production-shot.mjs` / `visual-bible-modal-shot.mjs` 等零散脚本,统一走 V11 顶层 scripts/screenshots/。
> **跨项目复用**: 任何 V11 项目直接复用,不发明新脚本。
> **SSOT**: [role-protocol.md §I+](../../references/role-protocol.md) + [common-anti-patterns.md §22](../../references/common-anti-patterns.md)

---

## 1. verify-screenshots.mjs — 自动化视觉抽样

**职责**: 替代主代理人工 Read 5 张截图(2-3min → 10s)。

**用法**:
```bash
node scripts/screenshots/verify-screenshots.mjs \
  --evidence-dir docs/evidence/<change-id> \
  --spec-keywords "欢迎回来,进行中,剧集列表"
```

**输入**:
- `--evidence-dir`: 截图目录(PNG 文件)
- `--spec-keywords`: 关键文本断言关键词(逗号分隔)

**输出**:
- 每张 PNG OCR 关键文本
- 与 spec keywords 匹配 PASS/FAIL
- 总结报告 + 退出码(PASS=0 / FAIL=1 / WARN=2)

**依赖**: Node.js 18+ + tesseract.js(本地 OCR,无云端依赖)

---

## 2. production-shot.mjs — 生产路由截图模板

**职责**: 替代 change 内散落的 production 截图脚本。

**用法**:
```bash
node scripts/screenshots/production-shot.mjs \
  --routes /zh/home,/zh/workspace,/zh/admin \
  --base-url http://localhost:3000 \
  --change-id my-change-2026-08-18
```

**输入**:
- `--routes`: 路由列表(逗号分隔)
- `--base-url`: 目标 base URL
- `--change-id`: change ID(输出目录命名)

**输出**:
- `docs/evidence/<change-id>/<route>-<ISO>.png`
- 每路由 1 张 PNG
- 总结报告(成功/失败路由数)

**依赖**: Node.js 18+ + playwright(自动 install)

---

## 3. 用法约定

```yaml
MUST:
  - 所有 V11 项目截图脚本走本目录,不发明 change 内 mjs
  - 截图前必 playwright_get_visible_text 验证可见正文(避免 signin-redirect 截图污染)
  - 截图后必 verify-screenshots.mjs 自动 OCR + 关键文本断言
NEVER:
  - 在 change 内造 `m3-production-shot.mjs` / `visual-bible-modal-shot.mjs` 等散落脚本
  - 主代理手动 Read 5 张截图(用 verify-screenshots.mjs 自动化)
  - 用 Playwright MCP 手工点页面出 VERIFIED/REOPENED 结论(对标 role-protocol §2.8 反例)
```

---

## 4. 实测锚点

```
ai-short-studio-monster 2026-08-18:
  - m3-production-shot.mjs 反复改 3 次(每次 change 内)
  - visual-bible-modal-shot.mjs 新增(每次 change 内)
  - 主代理手动 Read 5 张图,2-3min
  本目录 + 本脚本启用后预期:
  - 截图脚本 0 改动(传参复用)
  - 抽样验证 10s(verify-screenshots 自动)
```