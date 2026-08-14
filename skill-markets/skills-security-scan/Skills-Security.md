# skills-security-scan 完整说明（安装 + 分析 + GitHub 发布）

## 1. 项目定位

`skills-security-scan` 是一个本地优先（Local-First）的 Skill 安全评估工具，面向 Trae、OpenClaw、Claude Code（cc）、Cursor 等生态。  
核心能力是对指定 Skill 目录做静态规则扫描，输出结构化风险报告，帮助你做：

- 第三方 Skill 准入审查
- 发布前安全自检
- 周期性批量巡检

## 2. 当前包内容核对（已解压）

你当前目录 `d:\trea\skills开发` 已包含以下关键文件：

- `main.py`：扫描入口与报告生成逻辑
- `SKILL.md`：Skill 描述与触发场景
- `skill.json`：技能元数据（名称、输入输出、平台）
- `checklists/`、`docs/`、`examples/`、`templates/`：配套文档和模板
- `README.md`、`LICENSE.txt`

结论：压缩包内容完整，可直接运行和发布。

## 3. 安装与使用

### 3.1 本地运行要求

- Windows 下建议使用 Python 启动器：`py -3`
- Python 3.8+（无需第三方依赖）

### 3.2 命令行运行

```bash
py -3 main.py d:\trea\skills开发
```

指定输出目录：

```bash
py -3 main.py d:\trea\skills开发 d:\trea\skills开发\auto_reports
```

### 3.3 已验证结果（本地实测）

已成功执行扫描，退出码 `0`，并生成：

- `auto_reports\skills开发_security_report.json`
- `auto_reports\skills开发_security_report.md`
- `auto_reports\assessment_summary.txt`

## 4. 安全检测能力（基于源码分析）

`main.py` 当前内置 5 条规则：

### 高风险（High）

1. `CMD_RM_RF`：检测 `rm -rf`
2. `DYN_EVAL`：检测 `eval(...)`
3. `HARDCODED_SECRET`：检测硬编码密钥关键词（api_key/token/secret/password）

### 中风险（Medium）

4. `SHELL_EXEC`：检测 `child_process.exec/execSync(...)`

### 低风险（Low）

5. `HTTP_INSECURE`：检测 `http://` 明文链接

## 5. 工作机制解读

### 5.1 文件扫描范围

- 递归扫描文本文件后缀：`.md/.txt/.json/.js/.ts/.py/.sh/.ps1/.yaml/.yml`
- 默认忽略目录：`node_modules/.git/dist/build/coverage/__pycache__`

### 5.2 Skill 识别逻辑

- 检测 `SKILL.md` / `skill.json` / `package.json`
- 自动判定技能类型：
  - `trae-skill`
  - `claude-skill`
  - `json-skill`
  - `node-skill`
- 自动推断平台兼容并输出中英文平台名

### 5.3 报告输出

- JSON：机器可读，适合 CI/CD
- Markdown：人工审阅
- summary 文本：快速总览

## 6. 这次实测看到的风险解释

本次扫描命中高风险/低风险，主要来源于文档示例文本中出现了如 `rm -rf`、`eval(`、`http://` 关键词。  
这是规则匹配行为，不一定代表你项目中真的执行了危险代码。上线前建议：

- 在报告中增加“示例文本命中”说明
- 后续可升级为“按文件类型差异化风险权重”（例如 Markdown 仅提示，不直接记高危）

## 7. 上传 GitHub 的建议结构

建议仓库根目录保持如下结构：

```text
skills-security-scan/
├── main.py
├── SKILL.md
├── skill.json
├── README.md
├── LICENSE.txt
├── checklists/
├── docs/
├── examples/
└── templates/
```

如果你用当前目录直接做仓库，建议保留核心文件，视需要处理这些本地文件：

- `skills-security_1.zip`：可不提交
- `skills-security-scan.md`：作为中文发布说明可提交
- `.history/`：通常不提交
- `auto_reports/`：通常不提交（除非你要展示样例报告）

## 8. GitHub 发布步骤（可直接执行）

```bash
git init
git add .
git commit -m "feat: add skills-security-scan local skill scanner"
git branch -M main
git remote add origin <你的仓库地址>
git push -u origin main
```

推荐 `.gitignore` 至少包含：

```text
.history/
auto_reports/
__pycache__/
*.pyc
skills-security_1.zip
```

## 9. 发布前检查清单

- 可以正常运行：`py -3 main.py <skills_dir>`
- `SKILL.md` 与 `skill.json` 信息一致（名称/描述/输入输出）
- 示例命令路径改成通用路径，不写本机特定目录
- 报告产物不误提交（或仅提交样例）

---

如果你后续要我继续，我可以直接帮你把当前目录整理成“可一键推送 GitHub 的干净仓库状态”（包含 `.gitignore`、可选示例报告保留策略、提交前文件筛选）。
