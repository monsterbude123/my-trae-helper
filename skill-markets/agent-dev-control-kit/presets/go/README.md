# Go Preset

> Go 项目脚手架（标准库 / Gin / Echo / Fiber）。

## 适用场景

- 后端微服务（Gin / Echo / Fiber / chi）
- CLI 工具
- 系统工具 / 代理 / 网关
- gRPC 服务

## 工具链

| 组件 | 默认 | 备选 |
|------|------|------|
| 包管理 | Go modules（内置） | — |
| 运行时 | Go ≥1.21 | — |
| 测试 | go test | testify |
| Lint | golangci-lint | go vet / gofmt |
| 格式化 | gofmt | goimports |
| 类型检查 | go build（内置） | — |

## 目录约定（Go 社区惯用）

```
.
├── cmd/<app>/main.go   # 二进制入口（每个二进制一个子目录）
├── internal/           # 私有业务逻辑（不可被外部 import）
│   ├── services/
│   └── utils/
├── pkg/                # 可导出的库（可选）
├── tests/              # 集成 / E2E 测试
├── config/             # 配置
├── docs/
├── gates/
├── guards/
└── scripts/
```

## 使用

```bash
python scripts/init-from-preset.py --preset go --target ./my-app \
  --var module_path=github.com/me/my-app
```

## 关键脚本

- `template/scripts/init.sh` — `go mod tidy` + 创建 .env
- `template/gates/pre-commit.sh` — L1 门禁
- `template/guards/module-boundary-guard.sh` — 校验 internal/ 不被外部 import