# 游戏安全审查清单

> 吸收自 CC Studio security-engineer Agent（5 领域 × 7 检查）。

覆盖游戏项目中常见的安全风险。在生产环境部署前完成。

## 审查时机

```
- Phase 4 门禁中（自动化可检测项）
- Phase 5 构建前（手动审查项）
- Phase 6 部署前（运行时安全检查）
```

## 1. 认证与授权

| # | 检查项 | 自动化？ |
|---|--------|---------|
| 1 | 没有硬编码的 API Key/Token 在代码或配置文件中 | ✅ `grep -r "apiKey\|token\|secret" --exclude=.env*` |
| 2 | 所有网络请求使用 HTTPS | ✅ `grep "http://" *.gd *.cs *.rs` |
| 3 | OAuth/Token 刷新逻辑正确 | ❌ 手动审查 |
| 4 | Session 过期后正确重定向 | ❌ 手动审查 |
| 5 | 密码/密钥不打印到日志 | ✅ `grep -r "console.log\|print\|GD.Print" | grep -i "password\|key"` |
| 6 | .env / .env.local / credentials.* 在 .gitignore | ✅ `git check-ignore .env .env.local credentials.json` |
| 7 | 管理 API 端点有认证中间件 | ❌ 手动审查 |

## 2. 输入验证

| # | 检查项 | 自动化？ |
|---|--------|---------|
| 8 | 所有用户输入有服务端验证（不依赖客户端） | ❌ 手动审查 |
| 9 | SQL/NoSQL 不使用字符串拼接查询 | ✅ `grep "SELECT.*+\|Mongo.*+"`  |
| 10 | 文件上传有类型/大小/数量限制 | ❌ 手动审查 |
| 11 | URL 参数经过转义（XSS 防护） | ❌ 手动审查 |
| 12 | WebSocket 消息有 schema 校验 | ❌ 手动审查 |
| 13 | 第三方 API 响应有字段校验 | ❌ 手动审查 |
| 14 | Rich Text/玩家输入有 HTML 标签过滤 | ❌ 手动审查 |

## 3. 素材安全

> 对游戏项目特别重要——素材是攻击面。

| # | 检查项 | 自动化？ |
|---|--------|---------|
| 15 | 上传的用户素材不保存在 web 可访问目录 | ❌ 手动审查 |
| 16 | PNG/GLTF/OBJ 加载时处理文件不存在/损坏 | ✅ 构建测试时检查 |
| 17 | 纹理/模型文件不包含可执行代码 | ✅ `file *.png *.glb` 检查 MIME type |
| 18 | 素材路径无目录穿越（如 `../../etc/passwd`） | ✅ `grep "\.\.\/\|\~/" *.gd *.cs` |
| 19 | AssetBundle/Addressables 远程加载验证签名 | ❌ 手动审查 |
| 20 | 第三方素材许可合规 | ❌ 手动审查 |

## 4. 网络与数据传输

| # | 检查项 | 自动化？ |
|---|--------|---------|
| 21 | 多人游戏使用 Server Authoritative 架构 | ❌ 手动审查 |
| 22 | 网络包有速率限制（防刷） | ❌ 手动审查 |
| 23 | WebSocket 连接有超时和重连上限 | ❌ 手动审查 |
| 24 | 敏感数据传输加密（排行榜/成就/存档） | ❌ 手动审查 |
| 25 | CORS 配置仅允许信任域名 | ✅ WebGAL/Web 项目检查 |
| 26 | Content Security Policy 已配置（Web 项目） | ✅ Web 项目检查 |
| 27 | WebGL/Emscripten 沙盒正确配置 | ❌ 手动审查 |

## 5. 构建与部署

| # | 检查项 | 自动化？ |
|---|--------|---------|
| 28 | Shipping/Release 构建剥离调试符号 | ✅ `grep "Development\|Debug" BuildSettings*` |
| 29 | 控制台命令在 Shipping 构建中禁用 | ❌ 手动审查 |
| 30 | 构建产物不包含 .git/ .pdb/ .map 文件 | ✅ `find dist/ -name "*.pdb" -o -name ".git"` |
| 31 | 第三方库无已知 CVE 漏洞 | ❌ 手动审查 (`npm audit` / `cargo audit`) |
| 32 | CI/CD pipeline 无权限过高 | ❌ 手动审查 |
| 33 | 部署后配置文件无开发环境变量 | ✅ `grep "localhost\|127.0.0.1" dist/config.*` |
| 34 | 日志级别在生产环境设为 WARN 或 ERROR | ✅ `grep "log_level\|LOG_LEVEL" dist/config.*` |

## 结果输出

`security-review.md`:

```markdown
# Security Review: {game-key} @ {build-tag}

## 自动化检查
| # | 检查项 | 结果 | 备注 |
|----|--------|------|------|
| 1 | 硬编码 API Key | PASS | 无硬编码密钥 |
| ... | | | |

## 手动审查（待确认）
| # | 检查项 | 状态 | 负责人 |
|----|--------|------|--------|
| 3 | OAuth Token 刷新 | 待确认 | @dev |
| ... | | | |

## 总体
- 自动化: {PASS}/{TOTAL}
- 手动: {CONFIRMED}/{TOTAL}
- 阻断项: {#}
- 判定: APPROVED / CONCERNS / REJECTED
```
