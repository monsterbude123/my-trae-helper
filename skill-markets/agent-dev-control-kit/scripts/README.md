# Agent Dev Control Kit - Scripts 目录

> 本目录包含 agent-dev-control-kit 技能包的可执行工具脚本

---

## 脚本清单

| 脚本名称 | 用途 | 依赖 |
|---------|------|------|
| `init-control-kit.py` | 初始化控制体系 | Python 3.8+ |
| `validate-execution-skill.py` | 验证 Execution Skill 模板 | Python 3.8+ |
| `run-all-guards.py` | 批量运行 Guard 检查 | Python 3.8+ |
| `gate-check.py` | 门禁检查工具 | Python 3.8+ |
| `generate-skill-from-template.py` | 从模板生成新 Skill | Python 3.8+ |

---

## 使用方法

### 通用参数

所有脚本支持以下通用参数：

```bash
python <script>.py --help       # 显示帮助信息
python <script>.py --verbose    # 详细输出模式
python <script>.py --dry-run    # 试运行（不执行实际操作）
```

### init-control-kit.py

初始化 Agent 开发控制体系。

```bash
# 在当前目录初始化
python init-control-kit.py

# 在指定目录初始化
python init-control-kit.py --target /path/to/project

# 强制覆盖已有配置
python init-control-kit.py --force

# 仅检查不创建
python init-control-kit.py --check-only
```

**输出产物**：
- `.agents/` 目录结构
- `guards/` 目录结构
- `gates/` 目录结构
- `hooks/` 目录结构
- `guard-config.yaml` 配置文件

---

### validate-execution-skill.py

验证 Execution Skill 文件是否符合模板规范。

```bash
# 验证单个 Skill 文件
python validate-execution-skill.py --file path/to/SKILL.md

# 验证整个目录
python validate-execution-skill.py --dir skill-markets/my-skill

# 输出详细报告
python validate-execution-skill.py --file SKILL.md --report validation-report.md

# 仅检查必需章节
python validate-execution-skill.py --file SKILL.md --required-only
```

**检查项**：
- YAML frontmatter 完整性（name, description, version）
- 必需章节存在性（适用场景, 执行流程, 验收标准）
- 控制点规范性
- 流程图格式正确性

---

### run-all-guards.py

批量运行所有 Guard 检查。

```bash
# 运行所有 Guard
python run-all-guards.py

# 运行指定 Guard
python run-all-guards.py --guards api-contract,architecture

# 指定检查范围
python run-all-guards.py --scope src/api

# 输出汇总报告
python run-all-guards.py --report reports/guards-summary.json

# 设置失败阈值（WARNING 也视为失败）
python run-all-guards.py --fail-on WARN
```

**支持的 Guard 类型**：
- `api-contract` — API 契约检查
- `architecture` — 架构约束检查
- `test-coverage` — 测试覆盖检查
- `security` — 安全约束检查
- `performance` — 性能约束检查

---

### gate-check.py

门禁检查工具，支持不同级别的门禁检查。

```bash
# L1 门禁（基础检查）
python gate-check.py --level L1

# L2 门禁（进阶检查）
python gate-check.py --level L2

# L3 门禁（严格检查）
python gate-check.py --level L3

# L4 门禁（发布前完整检查）
python gate-check.py --level L4

# 自定义门禁配置
python gate-check.py --config custom-gate-config.yaml
```

**门禁级别说明**：

| 级别 | 检查内容 | 通过条件 |
|:----:|---------|---------|
| L1 | 基础结构检查 | 目录结构完整，配置文件存在 |
| L2 | 功能完整性检查 | Guard 检查通过，测试覆盖率 ≥ 60% |
| L3 | 质量门禁检查 | 所有 Guard 通过，覆盖率 ≥ 80%，无 BLOCK |
| L4 | 发布前完整检查 | L3 + 性能基线 + 安全扫描 + 文档同步 |

---

### generate-skill-from-template.py

交互式生成新的 Execution Skill。

```bash
# 交互式生成
python generate-skill-from-template.py

# 指定模板类型
python generate-skill-from-template.py --type execution

# 指定输出路径
python generate-skill-from-template.py --output skill-markets/my-new-skill

# 从配置文件生成（非交互）
python generate-skill-from-template.py --config skill-config.yaml
```

**交互式参数**：
- Skill 名称（kebab-case）
- 描述文本
- 触发词列表
- 适用场景列表
- 控制点定义
- 验收标准

---

## 依赖说明

### 系统要求

- Python 3.8 或更高版本
- Windows / macOS / Linux

### Python 包依赖

```txt
# requirements.txt
pyyaml>=6.0        # YAML 解析
colorama>=0.4.6    # 终端彩色输出（Windows 兼容）
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 可选依赖

部分功能需要额外依赖：

```bash
# 测试覆盖率分析
pip install pytest-cov

# 安全扫描
pip install pip-audit

# 性能分析
pip install pyinstrument
```

---

## 错误码说明

所有脚本使用统一的错误码：

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 参数错误 |
| 3 | 配置文件错误 |
| 4 | 验证失败 |
| 5 | Guard 检查失败 |
| 10 | 用户中断 |

---

## 输出格式

### 控制台输出

```
✅ PASS  — 检查通过
⚠️ WARN  — 警告，需人工确认
🛑 BLOCK — 阻断，必须修复
ℹ️ INFO  — 信息提示
```

### JSON 输出

所有脚本支持 JSON 格式输出：

```bash
python <script>.py --output json
```

```json
{
  "status": "success|error",
  "exit_code": 0,
  "summary": "...",
  "details": [...]
}
```

---

## 最佳实践

1. **在 CI/CD 中使用**：
   ```yaml
   # GitHub Actions
   - name: Run Guard Checks
     run: python scripts/run-all-guards.py --fail-on WARN
   
   - name: Gate Check
     run: python scripts/gate-check.py --level L3
   ```

2. **本地开发流程**：
   ```bash
   # 1. 创建新 Skill
   python scripts/generate-skill-from-template.py
   
   # 2. 验证 Skill 格式
   python scripts/validate-execution-skill.py --file skill-markets/my-skill/SKILL.md
   
   # 3. 运行 Guard 检查
   python scripts/run-all-guards.py
   
   # 4. 门禁检查
   python scripts/gate-check.py --level L2
   ```

3. **项目初始化**：
   ```bash
   # 新项目初始化
   python scripts/init-control-kit.py --target /path/to/new-project
   ```

---

## 故障排查

### 常见问题

**Q: 脚本在 Windows 上执行权限问题？**

A: 确保使用 `python` 命令执行脚本，或添加 `.py` 到 PATHEXT 环境变量。

**Q: YAML 解析错误？**

A: 检查配置文件编码是否为 UTF-8，避免使用 Tab 缩进。

**Q: Guard 检查失败但不确定原因？**

A: 使用 `--verbose` 参数查看详细输出，或查看生成的报告文件。

---

## 更新日志

| 版本 | 日期 | 变更说明 |
|-----|------|---------|
| 1.0.0 | 2025-08-13 | 初始版本，包含 5 个核心脚本 |

---

> **维护者**: agent-dev-control-kit
> **最后更新**: 2025-08-13