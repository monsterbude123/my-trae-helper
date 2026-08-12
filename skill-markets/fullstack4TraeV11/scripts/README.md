# V11 公共脚本说明

> 22 个公共脚本 + 各 stage 内部脚本。脚本失败 = 🛑 REJECT，不接受 AI 自评字符串。
> 主上下文亲自调用脚本（不委派给子代理，Article IV）。

---

## 公共脚本清单（scripts/）

| 脚本 | 用途 | 使用 stage |
|------|------|-----------|
| `stage-gate.py` | V11 阶段门禁（13 stage 统一） | 所有 stage 切换前 |
| `state-card-validator.py` | 状态卡字段 + 文件系统交叉验证 | 所有 stage 状态卡更新后 |
| `setup-feature.py` / `change-status.py` | 创建 change 骨架 / 读取 change 真实状态 | Stage -1 / 0 |
| `code-hygiene.py` / `orphan-detector.py` | 代码卫生 / 孤儿测试 | Stage 3 / 4 / 4.5 |
| `dist-hash-check.py` / `visual-content-check.py` | Bundle 一致性 / 视觉内容校验 | Stage 3.5 / 4 |
| `acceptance-audit.py` | 4 维验收审计 | Stage 4 |
| `proactive-scan.py` / `self-diagnose.py` | 5 项腐化扫描包 / Meta 自我诊断 | Stage 4.5 |
| `spec-purge.py` / `spec-knowledge-extract.py` | Spec 清除归档 / 知识沉淀 | Stage 5 |
| `reason-classifier.py` | 抽象理由分类器（6 类） | 所有 stage（被质疑时） |
| `init-from-zero.py` | 项目完整初始化（4 步:config+hooks+rules+AGENTS.md+docs 骨架） | 项目首次接入 V11 |
| `sync-after-upgrade.py` | 技能升级后覆盖性更新项目文件（hooks/config/rules/AGENTS.md 差异检查） | V11 技能升级后 |
| `install-hooks.py` | Hook 安装到项目 .trae/ | 项目首次接入 V11 |
| `hooks-fidelity.py` | Hook 完整性验证 | 项目首次接入 + 验收 |
| `upgrade-from-v10.py` | V10→V11 升级兼容性检查 | V10 项目升级 |
| `scan-templates.py` | 模板扫描 | 模板变更时 |
| `phase-gate.py` | 阶段门禁（V10 兼容） | V10 项目兼容 |
| `check_integration_contract.py` | 集成契约检查 | Stage 2 Contract |

---

## 脚本调用规则

- 主上下文亲自调用（不委派给子代理）
- 脚本输出必须真实保存（不接受口头宣称 PASS）
- 脚本失败 = 🛑 REJECT → 走 Article XV 阻塞报告
- 脚本 N/A → 必须在状态卡标注理由（不可静默跳过）

---

## 依赖

已实施脚本依赖 **PyYAML**（用于精确解析嵌套 YAML）：

```bash
pip install pyyaml
```

PyYAML 在大多数 Python 环境中已预装。

---

## V10 兼容性声明

V11 是独立版本，**不依赖** V10 脚本目录。V10 脚本由 V11 重写并增强，但部署时只需 V11 自身的 `scripts/` 目录。
