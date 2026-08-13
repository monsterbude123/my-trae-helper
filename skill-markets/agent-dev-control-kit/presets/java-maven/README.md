# Java (Maven) Preset

> Java 项目脚手架，标准 Maven 布局，支持 Spring / Jakarta EE / 通用 Java 应用。

## 适用场景

- Spring Boot / Spring Cloud 微服务
- Jakarta EE / JSF / Servlet 应用
- Java 库 / SDK
- 命令行工具（picocli / JCommander）

## 工具链

| 组件 | 默认 | 备选 |
|------|------|------|
| 包管理 | Maven | Gradle（不在本选型内） |
| 运行时 | JDK ≥17 | — |
| 测试 | JUnit 5 | TestNG / Spock |
| Lint | checkstyle | spotless / pmd |
| 格式化 | spotless | google-java-format |
| 覆盖率 | JaCoCo | — |

## 目录约定（Maven 标准）

```
.
├── src/
│   ├── main/
│   │   ├── java/<group_path>/      # 源码
│   │   └── resources/              # 配置/资源
│   └── test/
│       ├── java/<group_path>/      # 测试
│       └── resources/
├── config/                         # 项目配置（可选）
├── docs/
├── gates/
├── guards/
└── scripts/
```

## 使用

```bash
python scripts/init-from-preset.py --preset java-maven --target ./my-app \
  --var group_id=com.example \
  --var artifact_id=my-app
```

## 关键脚本

- `template/scripts/init.sh` — `mvn dependency:resolve` + 跑 sanity test
- `template/gates/pre-commit.sh` — L1 门禁
- `template/guards/package-boundary-guard.sh` — 跨包依赖守卫