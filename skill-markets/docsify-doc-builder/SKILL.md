---
name: "docsify-doc-builder"
description: "为任何项目搭建 docsify 文档系统。初始化结构、配置插件、生成侧边栏、启动开发服务器。当用户要求建立文档、搭建文档系统、初始化文档站点、配置 docsify 时自动加载。"
---

# Docsify 文档建设者

为项目快速搭建基于 docsify 的现代化文档系统。

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 新项目需要文档 | 项目刚起步，需要一套文档体系 |
| 现有项目缺文档 | 代码已有但文档散乱，需要结构化 |
| 文档系统重建 | 现有文档系统维护困难，需要迁移到 docsify |

## 工作流

```
用户需求
   │
   ▼
┌─────────────────────┐
│ 1. 环境检查          │  ← 调用 scripts/check-env.sh
│    docsify-cli 就绪? │     未安装 → 自动安装
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. 文档初始化        │  ← 调用 scripts/init-docs.sh
│    创建 docs/ 目录   │     复制所有模板到 docs/
│    配置 index.html   │     创建中文友好的 docsify 配置
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. 生成侧边栏        │  ← 调用 scripts/generate-sidebar.sh
│    扫描 docs/ 文件   │     自动创建 _sidebar.md
│    支持嵌套目录      │     按文件层级生成导航
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 4. 启动服务器        │  ← 调用 scripts/serve.sh
│   启动 docsify serve │     打开浏览器预览
│   实时热更新         │     编辑文档立即生效
└─────────┬───────────┘
          ▼
    ┌──────────┐
    │ 迭代维护  │  ← 修改 docs/ 下 .md 文件即可
    │          │     运行 generate-sidebar 更新导航
    └──────────┘
```

---

## 核心能力

### 1. 一键初始化

```bash
PROJECT_NAME="MyApp" ./trae/skills/docsify-doc-builder/scripts/init-docs.sh
```

创建完整的文档目录结构和基础文件：
```
docs/
├── index.html          # docsify 主配置（含所有插件）
├── _sidebar.md         # 侧边栏导航
├── _navbar.md          # 顶部导航栏
├── README.md           # 首页/项目简介
├── custom.css          # 自定义样式
├── logo.svg            # 项目 Logo（可选）
├── 基础篇/             # 可分模块组织
│   └── 快速开始.md
└── 进阶篇/
    └── 深入理解.md
```

### 2. 现代化 UI 配置

index.html 预配置：
- **docsify-themeable** — 现代化主题（深色/浅色双模式）
- **docsify-search** — 全文搜索（支持中文分词）
- **docsify-pagination** — 页面导航（上一页/下一页）
- **Mermaid 图表渲染** — 代码块 `mermaid` 自动渲染为 SVG 图表
- **Prism.js + 行号** — 代码语法高亮 + 行号显示 + 语言标签（支持 20+ 语言）
- **docsify-copy-code** — 一键复制代码
- **docsify-zoom-image** — 图片点击缩放
- **docsify-count** — 字数统计
- **自定义 CSS** — 平滑过渡、响应式布局、打印优化

### 3. 增强功能：Mermaid 全屏 + 工具栏 + Markmap

#### 3.1 固定工具栏

页面右上角固定定位工具栏（`.deer-toolbar`），毛玻璃效果：
- **回到顶部** — 平滑滚动到页面顶部
- **思维导图切换** — 一键切换 Markdown → Markmap 思维导图模式

#### 3.2 Mermaid 图表全屏查看 + 导出

点击任意 Mermaid 图表 → 进入全屏遮罩（`.deer-fullscreen-overlay`）：
- **放大/缩小/重置** — 鼠标缩放控制（0.25x ~ 5x）
- **导出 SVG** — 将图表保存为 `.svg` 矢量文件
- **导出 PNG** — 将图表保存为 `.png` 位图（2x 清晰度）
- **Esc 关闭** — 键盘快捷关闭
- **点击遮罩按钮关闭** — 顶部栏 ✕ 按钮

#### 3.3 Markmap 思维导图

点击工具栏「导图」按钮 → 隐藏 Markdown 正文，展示 Markmap 交互式思维导图：
- 自动解析 Markdown 标题层级生成树形思维导图
- 支持节点展开/折叠、拖拽平移
- 自动跳过 YAML front matter
- 再次点击按钮切回文档模式
- 路由切换时自动刷新导图内容

**依赖**：Mermaid (CDN) + Markmap Autoloader (CDN，含 Transformer + Markmap + d3)

### 4. 智能侧边栏生成

根据 docs 目录结构自动生成 `_sidebar.md`：
```
docs/
├── 基础篇/
│   ├── 01-简介.md
│   └── 02-安装.md
├── 进阶篇/
│   ├── 01-配置.md
│   └── 02-API.md

→ 生成:
* 基础篇
  * [01-简介](基础篇/01-简介.md)
  * [02-安装](基础篇/02-安装.md)
* 进阶篇
  * [01-配置](进阶篇/01-配置.md)
  * [02-API](进阶篇/02-API.md)
```

### 5. 中文优先

- 内置中文明细体字体栈
- 搜索插件中文兼容
- 所有模板注释为中文
- 默认侧边栏结构使用中文命名

---

## 文件结构

```
.trae/skills/docsify-doc-builder/
├── SKILL.md                      # 本文件 — 技能入口
├── scripts/
│   ├── check-env.sh              # 环境检查（检测/安装 docsify-cli）— 跨平台
│   ├── init-docs.sh              # 文档初始化（创建目录、复制模板）— 跨平台
│   ├── generate-sidebar.sh       # 侧边栏生成（扫描 docs/ → _sidebar.md）— 跨平台
│   └── serve.sh                  # 启动 docsify 开发服务器 — 跨平台
└── templates/
    ├── index.html                # docsify 核心配置模板（含 Mermaid + Markmap + 工具栏插件）
    ├── custom.css                # 自定义样式（含工具栏/全屏遮罩/思维导图/响应式）
    ├── _sidebar.md               # 侧边栏基础结构
    ├── _navbar.md                # 顶部导航栏
    ├── README.md                 # 首页/项目简介
    └── logo.svg                  # 默认 Logo
```

---

## 使用方式

### 交互式（推荐）

直接请求 AI 调用此技能：
> "给我们的项目搭建 docsify 文档"
> "初始化文档系统"
> "建一个文档站"

AI 会自动执行完整工作流。

### 手动执行

```bash
# 赋予执行权限（仅首次需要，Linux/macOS）
chmod +x .trae/skills/docsify-doc-builder/scripts/*.sh

# 0. 环境检查
.trae/skills/docsify-doc-builder/scripts/check-env.sh

# 1. 初始化（在项目根目录执行）
PROJECT_NAME="你的项目名" .trae/skills/docsify-doc-builder/scripts/init-docs.sh

# 2. 配置 index.html（可选：修改端口、插件等）
#    编辑 docs/index.html 中的 window.$docsify 配置

# 3. 生成侧边栏（新增文档后运行）
.trae/skills/docsify-doc-builder/scripts/generate-sidebar.sh

# 4. 启动服务
.trae/skills/docsify-doc-builder/scripts/serve.sh
# 访问 http://localhost:3000
```

---

## 自定义指南

### 修改主题色

编辑 `docs/custom.css` 中的 CSS 变量：
```css
:root {
  --theme-color: #42b983;          /* 主色调 */
  --brand: #7c5cfc;                /* 品牌色（工具栏/按钮/遮罩使用） */
  --brand-light: #9b7efd;          /* 品牌浅色 */
  --brand-dark: #5a3db8;           /* 品牌深色 */
  --base-font-family: "..."         /* 字体 */
  --sidebar-width: 20rem;           /* 侧边栏宽度 */
}
```

### 配置 Mermaid 主题

编辑 `docs/index.html` 中的 mermaid 初始化：
```js
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',       // 'default' | 'dark' | 'forest' | 'neutral'
  securityLevel: 'loose'
});
```

### 关闭工具栏/全屏功能

若不需要工具栏和 Markmap，可在 `index.html` 的 `hook.init` 中注释掉：
```js
hook.init(function() {
  setTimeout(function() {
    // injectToolbar();    // 关闭工具栏
    // injectOverlay();    // 关闭 Mermaid 全屏
  }, 500);
});
```

### 添加插件

编辑 `docs/index.html` 的 `window.$docsify` 配置：
```html
<script>
  window.$docsify = {
    // 在此添加或修改配置
    search: {
      maxAge: 86400000,
      paths: 'auto',
      placeholder: '搜索...'
    }
  }
</script>
```

### 添加更多文档

```bash
# 1. 创建新的 Markdown 文件
echo "# 新章节" > docs/新章节.md

# 2. 重新生成侧边栏
.trae/skills/docsify-doc-builder/scripts/generate-sidebar.sh
```

---

## 与其它技能协同

- **openapi-doc-exporter** — 导出 API 文档后，可用本技能将生成的 OpenAPI 文档发布为 docsify 站点
- **ui-ux-pro-max** — 文档页面的 UI 设计可参考该技能的设计规范
