<#
.SYNOPSIS
  初始化 docsify 文档目录结构和配置。

.DESCRIPTION
  在项目根目录创建 docs/ 文件夹，从技能模板复制所有必要的文件：
    - index.html（docsify 核心配置 + 插件）
    - README.md（首页/项目简介）
    - _sidebar.md（侧边栏导航）
    - _navbar.md（顶部导航栏）
    - custom.css（自定义样式）
    - logo.svg（项目 Logo）

  模板中的 {{PROJECT_NAME}} 和 {{PROJECT_DESCRIPTION}} 会被替换为实际值。

.PARAMETER ProjectName
  项目名称（必填）。可通过 $env:PROJECT_NAME 传入。
  优先级：参数 > 环境变量

.PARAMETER ProjectDescription
  项目描述（可选）。可通过 $env:PROJECT_DESCRIPTION 传入。
  优先级：参数 > 环境变量

.EXAMPLE
  $env:PROJECT_NAME="DeerFlow"; .trae/skills/docsify-doc-builder/scripts/init-docs.ps1

.EXAMPLE
  .trae/skills/docsify-doc-builder/scripts/init-docs.ps1 -ProjectName "MyApp"
#>

param(
    [string]$ProjectName = "",
    [string]$ProjectDescription = ""
)

$ErrorActionPreference = "Stop"

# ── 获取项目名称 ──
if (-not $ProjectName) {
    $ProjectName = $env:PROJECT_NAME
}
if (-not $ProjectName) {
    $ProjectName = Split-Path -Leaf (Get-Location)
    Write-Host "  ℹ️ 未指定项目名，使用当前目录名: $ProjectName" -ForegroundColor Yellow
}

# ── 获取项目描述 ──
if (-not $ProjectDescription) {
    $ProjectDescription = $env:PROJECT_DESCRIPTION
}
if (-not $ProjectDescription) {
    $ProjectDescription = ""
}

# ── 路径配置 ──
$skillRoot = Split-Path -Parent $PSScriptRoot
$templatesDir = Join-Path $skillRoot "templates"
$docsDir = Join-Path (Get-Location) "docs"

Write-Host "`n[文档初始化] 开始..." -ForegroundColor Cyan
Write-Host "  项目: $ProjectName" -ForegroundColor White
Write-Host "  输出: $docsDir" -ForegroundColor White

# ── 创建 docs 目录 ──
if (Test-Path $docsDir) {
    Write-Host "  ℹ️ docs/ 目录已存在，将覆盖同名文件" -ForegroundColor Yellow
}
else {
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
    Write-Host "  ✅ 创建 docs/ 目录" -ForegroundColor Green
}

# ── 创建子目录结构 ──
$subDirs = @("基础篇", "进阶篇", "附录")
foreach ($dir in $subDirs) {
    $dirPath = Join-Path $docsDir $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}
Write-Host "  ✅ 创建文档子目录: $($subDirs -join ', ')" -ForegroundColor Green

# ── 复制模板文件并替换变量 ──
$templateFiles = @(
    "index.html",
    "README.md",
    "_sidebar.md",
    "_navbar.md",
    "custom.css",
    "logo.svg"
)

$fileCount = 0
foreach ($file in $templateFiles) {
    $src = Join-Path $templatesDir $file
    $dst = Join-Path $docsDir $file

    if (Test-Path $src) {
        $content = Get-Content $src -Raw -Encoding UTF8
        $content = $content.Replace("{{PROJECT_NAME}}", $ProjectName)
        $content = $content.Replace("{{PROJECT_DESCRIPTION}}", $ProjectDescription)
        [System.IO.File]::WriteAllText($dst, $content, [System.Text.UTF8Encoding]::new($false))
        $fileCount++
    }
}

Write-Host "  ✅ 复制 $fileCount 个模板文件" -ForegroundColor Green

# ── 创建示例文档 ──
# 说明：使用单引号 here-string（@'...'@）+ Write-SampleDoc 函数，
#      内容完全是字面量，避免 PowerShell 解析器对 **、--、|、`、$(...) 等符号的歧义。
function Write-SampleDoc {
    param(
        [string]$Path,
        [string]$Content
    )
    $dir = Split-Path $Path -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $content = $Content -replace '{{PROJECT_NAME}}', $ProjectName
    [System.IO.File]::WriteAllText($Path, $content, [System.Text.UTF8Encoding]::new($false))
}

$sampleFiles = @(
    @{
        Path = "基础篇/快速开始.md"
        Content = @'
# 快速开始

> 5 分钟搭建你的第一个项目。

## 安装

```bash
# 安装命令
npm install -g {{PROJECT_NAME}}
```

## 使用

```bash
# 使用命令
{{PROJECT_NAME}} init my-project
```

## 下一步

- 阅读 [核心概念](核心概念.md) 理解整体设计
- 查看 [API 参考](../进阶篇/API参考.md) 了解完整接口
- 遇到问题先看 [常见问题](../附录/常见问题.md)
'@
    }
    @{
        Path = "基础篇/核心概念.md"
        Content = @'
# 核心概念

本文介绍 {{PROJECT_NAME}} 的四大核心概念。

## 概念一：模块化

`{{PROJECT_NAME}}` 将功能拆分为独立模块，每个模块只负责一件事。

### 模块加载顺序

```mermaid
graph LR
    A[core] --> B[config]
    A --> C[logger]
    A --> D[router]
    B --> E[plugins]
    D --> F[handlers]
```

## 概念二：声明式配置

所有配置通过 YAML / JSON / TOML 声明，**无需编写命令式代码**。

## 概念三：事件驱动

`{{PROJECT_NAME}}` 基于事件总线（Event Bus）解耦模块，模块之间通过事件通信。

## 概念四：插件化

通过 `plugins/` 目录扩展功能，无需修改核心代码。
'@
    }
    @{
        Path = "基础篇/核心概念-进阶.md"
        Content = @'
# 核心概念（进阶）

## 扩展点

| 扩展点 | 用途 | 优先级 |
|--------|------|--------|
| `before_init` | 初始化前钩子 | 高 |
| `after_init` | 初始化后钩子 | 中 |
| `on_event` | 事件订阅 | 低 |

## 实战示例

```typescript
// plugins/my-plugin/index.ts
export default {
  name: 'my-plugin',
  hooks: {
    after_init(ctx) {
      console.log('plugin loaded', ctx);
    }
  }
};
```
'@
    }
    @{
        Path = "基础篇/安装指南.md"
        Content = @'
# 安装指南

## 环境要求

- Node.js 16+（推荐 LTS）
- npm 8+ / pnpm 7+ / yarn 1.22+
- 现代浏览器（Chrome / Edge / Firefox / Safari）

## 安装步骤

1. **安装 Node.js**
   - 访问 [nodejs.org](https://nodejs.org/) 下载 LTS 版本
   - 安装后运行 `node --version` 验证

2. **安装 docsify-cli**
   ```bash
   npm install -g docsify-cli
   ```

3. **克隆模板仓库**
   ```bash
   git clone https://github.com/your/project
   cd project
   ```

4. **启动开发服务器**
   ```bash
   docsify serve docs
   ```

5. **访问** [http://localhost:3000](http://localhost:3000)
'@
    }
    @{
        Path = "进阶篇/配置详解.md"
        Content = @'
# 配置详解

`{{PROJECT_NAME}}` 通过 `config.yml` 进行集中配置。

## 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `port` | number | `3000` | 监听端口 |
| `theme` | string | `dark` | 主题（dark/light） |
| `plugins` | array | `[]` | 启用的插件列表 |
| `cache` | object | `{}` | 缓存配置 |

## 主题配置

主题文件位于 `docs/custom.css`，可通过修改 CSS 变量定制：

```css
:root {
  --brand: #9b7efd;       /* 品牌色 */
  --bg-primary: #1c1c1c;  /* 背景色 */
  --text-primary: #f5f5f5; /* 主文本色 */
}
```

## 插件配置

在 `index.html` 的 `window.$docsify.plugins` 数组中注册自定义插件：

```javascript
window.$docsify = {
  plugins: [
    function(hook, vm) {
      hook.doneEach(function() {
        console.log('page loaded:', vm.route.path);
      });
    }
  ]
};
```
'@
    }
    @{
        Path = "进阶篇/API参考.md"
        Content = @'
# API 参考

## 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |
| GET | `/api/v1/users` | 用户列表 |
| POST | `/api/v1/users` | 创建用户 |
| GET | `/api/v1/users/:id` | 用户详情 |
| PUT | `/api/v1/users/:id` | 更新用户 |
| DELETE | `/api/v1/users/:id` | 删除用户 |

## 请求示例

```bash
# 获取用户列表
curl https://api.example.com/v1/users

# 创建用户
curl -X POST https://api.example.com/v1/users \
  -H 'Content-Type: application/json' \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

## 响应格式

所有接口统一返回 JSON：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```
'@
    }
    @{
        Path = "进阶篇/最佳实践.md"
        Content = @'
# 最佳实践

## 项目结构

```
my-project/
├── src/              # 源代码
│   ├── components/   # 组件
│   ├── utils/        # 工具
│   └── index.ts      # 入口
├── tests/            # 测试
├── docs/             # 文档
├── package.json
└── tsconfig.json
```

## 命名规范

- **文件**：kebab-case（`my-file.ts`）
- **类**：PascalCase（`MyClass`）
- **函数/变量**：camelCase（`myFunction`）
- **常量**：UPPER_SNAKE_CASE（`MAX_COUNT`）

## 性能优化

1. **懒加载** — 按需加载大模块
2. **缓存** — 启用 LRU 缓存
3. **压缩** — 生产环境启用 gzip
4. **CDN** — 静态资源走 CDN
'@
    }
    @{
        Path = "进阶篇/Mermaid图表.md"
        Content = @'
# Mermaid 图表

> 点击任意图表可进入全屏查看、缩放、导出 SVG/PNG。

## 流程图

```mermaid
graph TD
    A[开始] --> B{条件判断}
    B -- 是 --> C[执行 X]
    B -- 否 --> D[执行 Y]
    C --> E[结束]
    D --> E
```

## 时序图

```mermaid
sequenceDiagram
    participant U as 用户
    participant A as 应用
    participant D as 数据库
    U->>A: 发起请求
    A->>D: 查询数据
    D-->>A: 返回结果
    A-->>U: 响应
```

## 甘特图

```mermaid
gantt
    title 项目排期
    dateFormat YYYY-MM-DD
    section 设计
    需求分析 :a1, 2026-01-01, 7d
    原型设计 :a2, after a1, 5d
    section 开发
    后端开发 :a3, 2026-01-15, 14d
    前端开发 :a4, after a3, 10d
    section 测试
    集成测试 :a5, after a4, 5d
```

## 类图

```mermaid
classDiagram
    class Animal {
        +name: string
        +age: int
        +makeSound()
    }
    class Dog {
        +breed: string
        +bark()
    }
    Animal <|-- Dog
```
'@
    }
    @{
        Path = "进阶篇/思维导图.md"
        Content = @'
# 思维导图

> 点击页面右上角 **导图** 按钮可将任意页面切换为思维导图模式。
> 思维导图**默认全部展开**，可拖拽平移、滚轮缩放。

## 启用方式

无需任何配置 — 任何 Markdown 页面都可一键切换为思维导图：

1. 阅读文档时点击右上角 **导图** 按钮
2. 页面内容自动解析为树形结构
3. 再次点击按钮切回文档模式

## 支持的特性

- **全部展开** — 初次进入自动展开所有节点
- **拖拽平移** — 鼠标拖动画布
- **滚轮缩放** — 滚轮缩放视图
- **节点折叠** — 点击节点切换展开/折叠
- **YAML 跳过** — 自动忽略 front matter

## 适用场景

- 复习整章结构
- 给团队做内容速览
- 快速跳转到感兴趣的章节（点击节点跳转）
'@
    }
    @{
        Path = "附录/常见问题.md"
        Content = @'
# 常见问题 (FAQ)

## Q1: 如何修改主题色？

编辑 `docs/custom.css` 中的 `--brand` 变量：

```css
:root {
  --brand: #your-color;
  --brand-light: #lighter;
  --brand-dark: #darker;
}
```

## Q2: 思维导图不显示？

1. 检查浏览器控制台是否有 JS 错误
2. 确认 markmap 依赖已加载（查看 Network 面板）
3. 刷新页面或硬刷新（Ctrl + Shift + R）

## Q3: 端口 3000 被占用？

```bash
# Linux/macOS
DOCSIFY_PORT=8080 docsify serve docs

# Windows PowerShell
$env:DOCSIFY_PORT=8080; docsify serve docs
```

## Q4: 如何禁用右侧目录？

在 `docs/custom.css` 末尾添加：

```css
.deer-right-toc { display: none !important; }
```
'@
    }
    @{
        Path = "附录/更新日志.md"
        Content = @'
# 更新日志

## v2.0.0 (2026-07-31)

### ✨ 新增
- **虚幻引擎 5 文档站风格** — 顶栏（Logo + 顶导 + 版本下拉 + GitHub）+ 左侧多级分类 + 中间内容 + 右侧页内目录
- **面包屑导航** — 自动基于路由生成
- **右侧 "在这个页面上"** — 自动提取 H2/H3 标题 + 滚动监听高亮
- **思维导图（Markmap）默认全部展开** — `initialExpandLevel: -1`
- **Markmap 完整依赖链** — d3 + markmap-lib + markmap-view（分模块 ESM 加载）
- **Markdown 渲染插件补全** — 集成 link/code/math 钩子

### 🐛 修复
- Markmap 渲染不稳定的根因（autoloader 加载顺序问题）

## v0.1.0 (2024-01-01)

### ✨ 新增
- 初始版本
'@
    }
    @{
        Path = "附录/贡献指南.md"
        Content = @'
# 贡献指南

## 如何参与

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feat/my-feature`
3. 提交变更：`git commit -m 'feat: add new feature'`
4. 发起 Pull Request

## 提交规范

- `feat:` — 新功能
- `fix:` — 修复
- `docs:` — 文档变更
- `refactor:` — 重构
- `test:` — 测试
- `chore:` — 构建/工具

## 代码风格

- TypeScript 严格模式
- 2 空格缩进
- 单引号优先
- 行尾分号
'@
    }
)

$sampleCount = 0
foreach ($sample in $sampleFiles) {
    $fullPath = Join-Path $docsDir $sample.Path
    if (-not (Test-Path $fullPath)) {
        Write-SampleDoc -Path $fullPath -Content $sample.Content
        $sampleCount++
    }
}

Write-Host "  ✅ 创建 $sampleCount 个示例文档文件" -ForegroundColor Green
Write-Host "`n[文档初始化] 完成！" -ForegroundColor Green
Write-Host ""
Write-Host "  下一步操作：" -ForegroundColor Cyan
Write-Host "  1. 编辑 docs/ 下的 Markdown 文件完善文档内容" -ForegroundColor White
Write-Host "  2. 运行 generate-sidebar.ps1 生成侧边栏" -ForegroundColor White
Write-Host "  3. 运行 serve.ps1 启动预览服务器" -ForegroundColor White
Write-Host "  4. 访问 http://localhost:3000 查看效果" -ForegroundColor White
