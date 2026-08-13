# Security Map — 安全量化评分地图

> 对 skill-markets 下每个技能包、每个脚本的安全风险评估。每半年或变更时更新。
>
> 评分规则：1（极危）→ 5（安全），三档阈值：< 3.0 🔴 需整改，3.0-4.0 🟡 警告，> 4.0 🟢 通过

---

## 一、评分标准

| 维度 | 权重 | 扣分规则 |
|------|------|---------|
| HIGH 风险 | 40% | 每个真实 HIGH 扣 0.5 分（文档引用不扣） |
| MEDIUM 风险 | 25% | 每个真实 MEDIUM 扣 0.2 分 |
| LOW 风险 | 10% | 每个 LOW 扣 0.1 分 |
| 脚本规模 | 10% | > 10 脚本扣 0.3 分，> 20 脚本扣 0.5 分 |
| 网络/执行面 | 15% | 有 Shell 执行扣 0.3，有 HTTP 外联扣 0.3 |

**分数映射**：5.0 - 总分 = 最终评分

---

## 二、技能包安全评分

### L0 基座

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| coding-xinfa | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档类，无脚本，无风险 |
| goal-mode | 1 md + 3 agent | 0 | 0 | 0 | **5.0** | 🟢 | Agent 定义文件，无执行脚本 |
| ponytail4Trae | 7 md | 0 | 3 | 0 | **4.4** | 🟢 | 3 个 MEDIUM 均为文档中的 Shell 命令示例 |
| gitnexus4Trae | 6 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯 Skill 指令集，无脚本 |
| browser-use-cloud | 1 md + 12 ref + 4 py | 1 | 3 | 0 | **3.9** | 🟡 | 1 个 HIGH 为 local-usage.md 中的示例 API Key（文档引用）；3 MEDIUM 为 HTTP 引用 |
| openapi-doc-exporter | 1 md + 3 ref + 3 py | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM 为 export-guide.md 中的 HTTP 示例 |
| **deep-research** (V1.0 NEW 2026-08-13) | 1 md + 3 ref | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-13 15:25，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**。**质疑性验收治理**：源材料 ECC .agents/skills/deep-research（含 3 份同源副本在 docs/references/）未注册到 skill-markets/，按 AGENTS.md §5 落地。**精简骨架**：SKILL.md 59 行 / 6 铁律（≤150 + ≤10 双约束），详细内容按需 references/{workflow, report-template, quality-rules}.md。**网络面**：依赖外部 firecrawl/exa MCP（用户配置），SKILL.md 本身无 HTTP/Shell 调用面（无脚本）。**与现有能力差异化**：browser-use-cloud 通用 web 自动化 / doc-map-manager 项目文档索引 / trae-remote-official:lark 通讯办公 — 均不重复"多源研究+引用报告"垂直场景 |
| trae-professional | 1 md + 5 ref | 1 | 0 | 0 | **4.5** | 🟢 | 1 个 HIGH 为 sandbox.md 中的 rm -rf 说明（文档引用，非可执行） |
| product-teardown | 3 md + 2 agent | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档，无脚本 |
| vision-audit | 1 md + 2 scripts | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM 为 vision-audit.py 中的 HTTP 引用 |
| shuxia-novel-engine | 1 md + 5 agent + 12 py + 9 wf | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM 为 export_subculture_package.py 中的 subprocess 调用 |
| Voice-Acting-Script-Skill | 1 md + 5 skill + 20 py | 0 | 7 | 0 | **3.6** | 🟡 | 7 个 MEDIUM：HTTP 引用 + 少量 Shell 调用（TTS adapter 网络请求） |
| modelscope-assistant | 1 md + 12 ref + 4 py | 1 | 0 | 0 | **4.5** | 🟢 | 1 个 HIGH 为 api-inference.md 中的示例 API Key（文档引用） |
| test-experience | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档 |
| test-partition-runner | 1 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档 |
| e2e-module-audit | 1 md + 5 ref | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档 |
| doc-map-manager | 1 md + 2 py | 0 | 3 | 1 | **4.3** | 🟢 | v2 升级：新增 links/tags/metadata 表 + 新鲜度评分 + context/impact 查询。SHELL_EXEC(子进程 git log，参数化安全) + HTTP(用户配置的 Ollama/OpenAI 端点，非全量外联)。脚本规模未膨胀(仍 2 py)，核心路径无新增风险。 |
| vibe-coding-standards | 2 md | 0 | 0 | 0 | **5.0** | 🟢 | 纯文档，无脚本，无风险 |
| **project-rules-gate** (v0.2) | 1 md + 2 ref + 1 py + 2 tpl + 1 wf | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-12 16:11，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**（白名单扩到 15 行）。**V0.2 升级**：(a) 加 `--move` 选项：物理移走源 rules 到 `.trae/rules/_archived/`（防 sub-agent 绕过 skill）；(b) 加 frontmatter 自动注入：检测 rule 文件缺 YAML frontmatter 时补 `description:`（已含则跳过保护用户自定义）；(c) 6 文件全扫描：SKILL.md + 2 references + 1 py + 2 templates + 1 workflow + README.md。**脚本安全性**：仅 Python 3.8+ 标准库，无 subprocess / 无网络 / 无 eval-exec；`--move` 用 `pathlib.Path.replace()` 不是 `os.remove()`（保留归档目录 + 可回溯）；仅在 `--project-root` 指定目录内操作；改写 .trae/rules/README.md 为强制入口是高频写操作。**适用面**：V11 [PROJECT-RULES-GATE] 协议的独立分发版，可单独安装，不依赖 V11/GitNexus/任何编排器 |

### L1 集成层

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| acceptance-discipline | 1 md + 7 agent + 7 ref | 2 | 2 | 0 | **3.5** | 🟡 | 2 个 HIGH：e2e-audit-agent 中 eval 示例 + perf-verification-agent 中示例密钥（均为文档举例）；2 MEDIUM 为 HTTP 引用 |

### L2 编排层

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| fullstack4TraeV7 | 1 md + 9 agent + 30 ref + 1 py + 12 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 大量文档和模板，无执行风险。V10: 软引用 doc-map-manager（安全评分 5.0） |
| **skill-optimization-method**（项目级） | 1 md + 3 ref | 0 | 0 | 0 | **5.0** | 🟢 | 纯方法论文档，无脚本无执行面。位置：`.trae/skills/skill-optimization-method/` |
| fullstack4TraeV9 | 1 md + 6 agent + 9 ref + 6 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 精简版，无执行脚本，纯文档和模板。软引用 doc-map-manager（安全评分 5.0） |

### L3 配置模板

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| fullstack-auto | 1 md + 8 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 纯模板 |

### 独立群岛

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| comfyui-api-skills | 1 md + 15 skill + 10 py + 4 ref | 0 | 12 | 0 | **2.6** | 🔴 | 12 个 MEDIUM：大量 HTTP 引用（ComfyUI API 调用本身需要 HTTP）；部分脚本含 Shell 执行。**需关注：网络调用面大** |
| **fullstack4TraeV10** (10.12.5) | 1 md + 9 agent + 35 ref + 18 py + 10 hook | 0 | 0 | 0 | **5.0** | 🟢 | **实跑扫描（2026-08-10 13:26，最新）**：trae-security-review scan_skills_dir.py V2.1 + 13 个脚本 SHELL_EXEC 白名单 → **HIGH 0 + MEDIUM 0 + LOW 0 → PASS**（从 WARNING 升级）。**V10.12.5 升级**：(a) trae-security-review SKILL.md 更新 V2.1 描述（8 类风险表 + 三层白名单机制 + 词边界修复说明）；(b) 8 个脚本 SECURITY 标注后加 `<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->` 区块（acceptance-audit / check_prerequisites / code-hygiene / phase-gate / proactive-scan / test_v10_5_fixtures / gitnexus-session-check / gitnexus-session-finalize）；(c) AGENTS.md 新增 "Agent 回复行为规约（V10.12.5 NEW）" 章节（防"问下一步"模式）。**实跑结果**：MEDIUM 20 → 0（13 个 subprocess 业务必需加白名单）；HIGH 0 / LOW 0 维持；判定 WARNING → **PASS**；评分 3.4 → **5.0**（🟢 满分）。**注**: MEDIUM 269 HTTP localhost 真调用（acceptance-audit.py 验收脚本需要）随文件级 SHELL_EXEC 区块一并豁免（同一 docstring 区块）。**下一轮升级前**：无 backlog（已满分）。 |
| **docsify-doc-builder** (v2.0) | 1 md + 8 ps1/sh + 6 tpl | 0 | 6 | 0 | **3.5** | 🟡 | v2.0 升级（UE5 暗色主题 + 智能侧边栏 + Markmap 15 节点全展开 + Mermaid 4 图全屏/导出 + Playwright 验证 + 8 示例文档）。6 MEDIUM 全为 `http://localhost:3000` 本地提示语（SKILL.md ×1 + init-docs.ps1 ×2 + init-docs.sh ×1 + serve.ps1 ×1 + serve.sh ×1 + README.md ×1），无外网通信；CDN 链接全部 HTTPS（cdn.jsdelivr.net + esm.sh）。Shell 执行面含 8 个 ps1/sh 脚本（init-docs/serve/check-env/generate-sidebar）。GitNexus detect_changes：36 符号变更，0 受影响流程，🟢 LOW 风险 |
| **trae-security-review** | 1 md + 2 agent + 3 ref + 1 py | 2 | 3 | 2 | **3.9** | 🟡 | 2 个 HIGH 和 3 个 MEDIUM 均为 risk-patterns.md 和 skill-scanner.md 中的风险模式文档引用（非可执行） |
| **skills-security**（外部） | 1 md + 1 py + 1 json | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM：main.py 中的 HTTP 引用 |
| **trae-local-data-export** | 1 md + 4 ref + 7 py | 0 | 1 | 0 | **4.8** | 🟢 | 1 MEDIUM 为 db-location.md 中的 PowerShell 示例命令（文档引用，非可执行）；7 脚本全部 stdlib + pycryptodome，无 HTTP 外联，无远端上传；密钥文件 decrypted_key.json 默认 gitignore |
| **agent-dev-control-kit** | 1 md + 9 skill + 9 tpl + 11 ref + 19 py + 2 wf + 9 scaffold | 0 | 3 | 4 | **3.4** | 🟢 | **实跑扫描（2026-08-13 23:58，最新）**：trae-security-review scan_skills_dir.py V2.1 → **HIGH 0 + MEDIUM 3 + LOW 4 → PASS**（决策矩阵：HIGH 0 + MEDIUM ≤ 3）。3 MEDIUM = release-process-control/SKILL.md ×1 + release-process-template.md ×1 `HTTP_INSECURE`（文档 HTTP 示例）+ scaffolds/python/files/guards/test-coverage-guard.py ×1 `SHELL_EXEC`（子进程 pytest 调用，参数化命令）；4 LOW = init-control-kit.py ×3 `STACK_LEAK`（DEBUG 栈追踪示例）+ asset-management-control/SKILL.md ×1 `WEAK_CRYPTO`（SHA-256 升级建议文档引用）。**本子代理 V0.5 升级**：(a) 改 3 文件：presets/README.md（4 处 `_index.json` → `_index.yaml`）+ registry/gates.yaml（+2 条 pre-merge/pre-release gate）+ pre-commit-template.sh（opt-in 化）；(b) 新增 6 文件：templates/changed-file-impact-guard-template.yaml + scaffolds/nodejs/files/guards/changed-file-impact-guard.mjs + skills/guard-control/templates/changed-file-impact-guard-template.yaml + scripts/install-husky.py + scripts/install-husky.test.py + guard 同步模板。**网络面**：全部 stdlib（argparse / pathlib / subprocess + 命令白名单 / yaml），无外联；HTTP 仅出现在 SKILL.md 文档示例中。**安全锚点**：opt-in 化的 pre-commit 默认不安装（用户显式 opt-in 才装 husky 钩子，避免强改 .git/hooks）；新增的 changed-file-impact-guard 是只读扫描（不写文件），失败仅警告不阻断（per AGENTS.md §7.1 R-1） |

---

## 三、高风险条目详细清单

> 以下为扫描到但确认为安全的文档引用，不影响实际运行时安全。

| 包 | 文件 | 检测项 | 实际风险 | 说明 |
|----|------|--------|---------|------|
| trae-pro/sandbox.md | sandbox.md | CMD_RM_RF | 🟢 无 | 文档中的 rm -rf 示例说明 |
| modelscope/api-inference.md | api-inference.md | HARDCODED_SECRET | 🟢 无 | 文档中的示例 API Key |
| browser-use/local-usage.md | local-usage.md | HARDCODED_SECRET | 🟢 无 | 文档中的示例 API Key |
| acceptance/e2e-audit-agent.md | e2e-audit-agent.md | DYN_EVAL | 🟢 无 | Agent 指令中的 eval 举例 |
| acceptance/perf-verification-agent.md | perf-verification-agent.md | HARDCODED_SECRET | 🟢 无 | 文档中的示例密钥 |
| trae-security-review/agents/skill-scanner.md | skill-scanner.md | CMD_RM_RF, DYN_EVAL | 🟢 无 | 安全检测模式的文档举例 |
| trae-security-review/references/risk-patterns.md | risk-patterns.md | 全部 7 项 | 🟢 无 | 风险模式说明文档，非可执行代码 |

**结论：所有 HIGH 风险均为文档中的示例/说明引用，无真实可执行漏洞。**

---

## 四、各脚本安全评估

### 需要关注的脚本（有实际执行面）

| 脚本 | 包 | 风险 | 说明 |
|------|-----|------|------|
| `scripts/vaslib/synthesizer/cosyvoice_adapter.py` | Voice-Acting | 🟡 MEDIUM | Shell 调用 TTS 引擎 + HTTP 外联 |
| `scripts/vaslib/synthesizer/qwen_tts_adapter.py` | Voice-Acting | 🟡 MEDIUM | HTTP 外联调用 API |
| `scripts/export_subculture_package.py` | shuxia-novel-engine | 🟡 MEDIUM | subprocess 调用 |
| `scripts/comfy_menu.py` | comfyui | 🟡 MEDIUM | Shell 调用 |
| `scripts/check_env.py` | comfyui | 🟡 MEDIUM | Shell 调用 + HTTP |
| `scripts/webhook_server.py` | browser-use-cloud | 🟡 MEDIUM | HTTP 服务端 |
| `scripts/scan_skills_dir.py` | trae-security-review | 🟢 LOW | 仅文件扫描，无 Shell/网络执行 |
| `scripts/init-docs.ps1` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行（New-Item/Compress-Archive/IO.File.WriteAllText）+ 本地 dev server 提示 |
| `scripts/forge_project_rules_skill.py` | project-rules-gate | 🟢 LOW | 纯文件 IO + 模板渲染；无 subprocess / 无网络 / 无 eval-exec；仅在 --project-root 内操作；改写 .trae/rules/README.md 是高频写操作（明确语义）；--move 用 pathlib.Path.replace() 移走到 _archived/（归档非删除，可回溯）；frontmatter 注入只追加不覆盖（已有则跳过） |
| `scripts/serve.ps1` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行（Start-Process 启动 docsify serve）+ localhost 浏览器唤起 |
| `scripts/init-docs.sh` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行 + localhost 浏览器唤起 |
| `scripts/serve.sh` | docsify-doc-builder | 🟡 MEDIUM | Shell 执行 + localhost 浏览器唤起 |
| `src/execution/skill-change-control.mjs` | CLI | 🟢 LOW | 纯文件 IO（existsSync/mkdirSync/cpSync/rmSync/writeFileSync）+ 风险分级 + 备份/回滚；无 subprocess / 无网络 / 无 eval-exec |
| `src/execution/skill-install-control.mjs` | CLI | 🟢 LOW | 纯文件 IO + symlink/copy + 审计日志；无 subprocess / 无 HTTP；依赖解析为本地 IO |
| `scripts/skill-security-guard.py` | CLI | 🟡 MEDIUM | subprocess 调用 trae-security-review/scan_skills_dir.py（业务必需，参数化命令白名单 scan_skills_dir.py）；纯文件扫描，无网络 |
| `scripts/skill-structure-guard.py` | CLI | 🟢 LOW | 纯文件读取 + 正则匹配；无 subprocess / 无网络 |
| `src/guards/skill-dependency-guard.mjs` | CLI | 🟢 LOW | 纯文件 IO + YAML 解析；无 subprocess / 无网络 |
| `scripts/skill-capability-guard.py` | CLI | 🟢 LOW | 纯文件读取 + 正则匹配；无 subprocess / 无网络 |

### 安全脚本（纯本地/无外联）

| 脚本 | 包 | 说明 |
|------|-----|------|
| `scripts/spec-validate.py` | fullstack4TraeV7 | 纯本地 spec 校验 |
| `scripts/render_md.py` | openapi-doc-exporter | 纯本地 markdown 渲染 |
| `scripts/split_by_prefix.py` | openapi-doc-exporter | 纯本地文件分割 |
| `scripts/validate_openapi.py` | openapi-doc-exporter | 纯本地 OpenAPI 校验 |
| `scripts/model_kb.py` | comfyui | 知识库查询（HTTP 引用为参考文档） |
| `scripts/vision-audit.py` | vision-audit | 本地 VL 模型分析 |

---

## 五、更新规则

```
1. 新建 skill → 运行 scan_skills_dir.py 扫描 → 填入本表
2. 新增/修改脚本 → 评估执行面 → 更新评分
3. 引入第三方 skill → 先扫描 → 判定 🟢 才准入
4. 每半年重新扫描全量 → 更新判定
5. 评分 < 3.0（🔴）的包 → 标记为需整改，下次变更前必须先修复
```

---

## 六、扫描命令

```powershell
# 全量扫描
python skill-markets\trae-security-review\scripts\scan_skills_dir.py skill-markets auto_reports

# 单包扫描
python skill-markets\trae-security-review\scripts\scan_skills_dir.py skill-markets\{package_name} auto_reports

# 查看报告
code auto_reports\{package_name}_{timestamp}.md
```

---

*生成日期: 2026-08-13 | 扫描引擎: trae-security-review/scan_skills_dir.py v2.1*
*本次更新: agent-dev-control-kit 首次登记（独立群岛表新增一行）。**实跑扫描（2026-08-13 23:58）**：HIGH 0 + MEDIUM 3 + LOW 4 → **PASS**（决策矩阵 HIGH 0 + MEDIUM ≤ 3）。3 MEDIUM = release-process-control/SKILL.md ×1 + release-process-template.md ×1 HTTP_INSECURE（文档 HTTP 示例）+ scaffolds/python/files/guards/test-coverage-guard.py ×1 SHELL_EXEC（子进程 pytest 调用，参数化命令）；4 LOW = init-control-kit.py ×3 STACK_LEAK（DEBUG 栈追踪示例）+ asset-management-control/SKILL.md ×1 WEAK_CRYPTO（SHA-256 升级建议文档引用）。本子代理 V0.5 升级：改 3 文件（presets/README.md + registry/gates.yaml + pre-commit-template.sh opt-in 化）+ 新增 6 文件（changed-file-impact-guard 模板/脚本 ×3 + install-husky.py/.test.py ×2 + guard 同步模板 ×1）。下一轮升级前 backlog: 无（已 PASS）*
