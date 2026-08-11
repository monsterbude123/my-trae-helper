# V11 公共脚本说明

## 已实施（Task 17 完成）

| 脚本 | 状态 | 测试 |
|------|------|------|
| `stage-gate.py` | ✅ 实施 + Fresh 验证 | PASS（test_card.md） |
| `state-card-validator.py` | ✅ 实施 + Fresh 验证 | PASS（test_card.md） |

## 占位待实施（V11 部署时按需补全）

| 脚本 | 来源 | 状态 |
|------|------|------|
| `acceptance-audit.py` | V10 4 维评分 | 待实施 |
| `proactive-scan.py` | V10 5 维度 + V10.4 扩展 | 待实施 |
| `self-diagnose.py` | V10 Meta 元检测 | 待实施 |
| `orphan-detector.py` | V10 rot #12 修复 | 待实施 |
| `dist-hash-check.py` | V10 rot #13 修复 | 待实施 |
| `visual-content-check.py` | V10 视觉证据 | 待实施 |
| `code-hygiene.py` | V10 行数 + 函数 + 魔法数字 | 待实施 |
| `spec-purge.py` | V10 归档隔离 | 待实施 |
| `spec-knowledge-extract.py` | V10 知识沉淀 | 待实施 |
| `reason-classifier.py` | V10 6 类抽象理由 | 待实施 |
| `setup-feature.py` | V10 change 骨架创建 | 待实施 |
| `change-status.py` | V10 change 状态读取 | 待实施 |

## 依赖

两个已实施脚本均依赖 **PyYAML**（用于精确解析嵌套 YAML）：

```bash
pip install pyyaml
```

PyYAML 在大多数 Python 环境中已预装。

## V10 兼容性声明

V11 是独立版本，**不依赖** V10 脚本目录。V10 脚本由 V11 重写并增强，但部署时只需 V11 自身的 `scripts/` 目录。