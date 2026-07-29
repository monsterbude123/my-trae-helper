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

### L1 集成层

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| acceptance-discipline | 1 md + 7 agent + 7 ref | 2 | 2 | 0 | **3.5** | 🟡 | 2 个 HIGH：e2e-audit-agent 中 eval 示例 + perf-verification-agent 中示例密钥（均为文档举例）；2 MEDIUM 为 HTTP 引用 |

### L2 编排层

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| fullstack4TraeV7 | 1 md + 9 agent + 30 ref + 1 py + 12 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 大量文档和模板，无执行风险。V10: 软引用 doc-map-manager（安全评分 5.0） |
| fullstack4TraeV9 | 1 md + 6 agent + 9 ref + 6 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 精简版，无执行脚本，纯文档和模板。软引用 doc-map-manager（安全评分 5.0） |

### L3 配置模板

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| fullstack-auto | 1 md + 8 tpl | 0 | 0 | 0 | **5.0** | 🟢 | 纯模板 |

### 独立群岛

| 技能包 | 文件数 | HIGH | MED | LOW | 评分 | 判定 | 点评 |
|--------|--------|------|-----|-----|------|------|------|
| comfyui-api-skills | 1 md + 15 skill + 10 py + 4 ref | 0 | 12 | 0 | **2.6** | 🔴 | 12 个 MEDIUM：大量 HTTP 引用（ComfyUI API 调用本身需要 HTTP）；部分脚本含 Shell 执行。**需关注：网络调用面大** |
| **fullstack4TraeV10** (10.3.4) | 1 md + 6 agent + 19 ref + 12 py + 8 hook | 0 | 6 | 5 | **2.4** | 🔴 | 6 MEDIUM：SHELL_EXEC ×5（acceptance-audit/code-hygiene/phase-gate/auto-test/contract-check 跑 cargo/npm/curl/grep），HTTP_INSECURE ×1（acceptance-audit 本地 curl localhost:18080）。**10.3.3 新增 integration-contract 硬门禁（直 fetch / 直 keydown / 缺 ModuleDef / 缺 Rust trait / 事件命名违规）；10.3.4 腐烂点清理 — Trae Plan/Spec 引用跟随 spec-kit（11 处文档 + 1 处函数重命名）**。设计意图：acceptance-audit 真实验收必需，按 AGENTS.md 量化评分规则严格扣分落到 🔴 档。处理：本地工具且无外网通信，保留 SHELL_EXEC 不修；HTTP_INSECURE 仅限 localhost，加白名单豁免 |
| **trae-security-review** | 1 md + 2 agent + 3 ref + 1 py | 2 | 3 | 2 | **3.9** | 🟡 | 2 个 HIGH 和 3 个 MEDIUM 均为 risk-patterns.md 和 skill-scanner.md 中的风险模式文档引用（非可执行） |
| **skills-security**（外部） | 1 md + 1 py + 1 json | 0 | 1 | 0 | **4.8** | 🟢 | 1 个 MEDIUM：main.py 中的 HTTP 引用 |

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

*生成日期: 2026-07-02 | 扫描引擎: trae-security-review/scan_skills_dir.py v1.0*
