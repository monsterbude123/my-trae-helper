# Python Preset

> Python 项目脚手架（FastAPI / Django / Flask / 通用库）。

## 适用场景

- Web 后端（FastAPI / Django / Flask / Starlette）
- 数据处理 / ETL 脚本
- 通用 Python 库 / CLI 工具
- ML 推理服务

## 工具链

| 组件 | 默认 | 备选 |
|------|------|------|
| 包管理 | uv | pip / poetry / pdm |
| 运行时 | Python ≥3.10 | — |
| 测试 | pytest | unittest |
| Lint | ruff | flake8 / pylint |
| 格式化 | ruff (format) | black |
| 类型检查 | mypy（可选） | pyright |

## 目录约定

```
.
├── src/<package>/     # 源码（包名按项目调整）
├── tests/
│   ├── unit/
│   └── integration/
├── config/            # 可选
├── docs/
├── gates/
├── guards/
└── scripts/
```

## 使用

```bash
python scripts/init-from-preset.py --preset python --target ./my-app
```

## 关键脚本

- `template/scripts/init.sh` — 创建 venv（uv）+ 安装依赖
- `template/gates/pre-commit.sh` — L1 门禁
- `template/guards/import-boundary-guard.py` — 跨层 import 守卫（Python 特有）