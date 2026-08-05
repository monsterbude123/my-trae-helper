---
name: "docsify-doc-builder"
description: "为任何项目搭建虚幻引擎 5 风格的 docsify 文档系统。集成顶栏 + 多级分类 + 面包屑 + 右侧页内目录 + Mermaid 全屏 + Markmap 思维导图（默认全部展开）。当用户要求建立文档、搭建文档系统、初始化文档站点、配置 docsify、UE 风格文档站时自动加载。"
---

# Docsify 文档建设者（v2.0 — UE 5 风格）

为项目快速搭建基于 docsify 的**虚幻引擎 5 风格**现代化文档系统：顶栏 + 多级分类树 + 面包屑 + 右侧页内目录 + Mermaid 全屏 + Markmap 思维导图。

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 新项目需要文档 | 项目刚起步，需要一套 UE 5 风格的文档体系 |
| 现有项目缺文档 | 代码已有但文档散乱，需要结构化 |
| UE 风格接入示例 | 模仿 Unreal Engine 5 / JetBrains / Stripe 文档站布局 |
| 文档系统重建 | 现有文档系统维护困难，需要迁移到 docsify |

## 工作流

```
用户需求
   │
   ▼
┌─────────────────────┐
│ 1. 环境检查          │  ← 调用 scripts/check-env
│    docsify-cli 就绪? │     未安装 → 自动安装
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. 文档初始化        │  ← 调用 scripts/init-docs
│    创建 docs/ 目录   │     复制所有模板到 docs/
│    UE 5 风格配置     │     创建顶栏/侧边栏/右侧目录/Markmap 全功能
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. 生成侧边栏        │  ← 调用 scripts/generate-sidebar
│    扫描 docs/ 文件   │     自动创建 _sidebar.md
│    多级嵌套支持      │     按文件层级生成导航
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 4. 启动服务器        │  ← 调用 scripts/serve
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

### 1. UE 5 风格布局（核心特性）

参考虚幻引擎 5 文档站设计，三段式布局：

```
┌────────────────────────────────────────────────────────┐
│ [Logo] 项目名  首页 文档 入门 进阶 FAQ   [v2.0▼] [GitHub] │  ← 顶栏（固定 56px）
├────────────┬─────────────────────────────────┬──────────┤
│ 分类树      │ 首页 / 文档 / 入门 / 快速开始    │ 在这个    │  ← 右侧 TOC
│ - 入门指南  │ ─────────────────────────────  │ 页面上    │  滚动高亮
│   - 快速    │ # 快速开始                      │  • 安装   │
│   - 安装    │ > 5 分钟搭建你的第一个项目        │  • 使用   │
│ - 进阶篇    │                                  │  • 下一步 │
│   - 配置    │ ## 安装                          │           │
│   - API     │ [代码块]                         │           │
│ - 附录      │                                  │           │
└────────────┴─────────────────────────────────┴──────────┘
```

**布局元素**：

| 元素 | 位置 | 实现 |
|------|------|------|
| 顶栏 | 顶部 56px 固定 | 自定义注入 `.deer-topbar` |
| 面包屑 | 内容顶部 H1 上方 | 自动基于路由生成 `.deer-breadcrumb` |
| 多级分类 | 左侧 18rem | docsify `subMaxLevel: 4` + `sidebarSubLevel: 4` |
| 右侧目录 | 内容右侧 200px | 滚动监听高亮 `.deer-right-toc` |
| 当前项高亮 | 左侧栏 + 右侧 TOC | 紫色竖条 + 背景 |
| 工具栏 | 右下浮动 | 回到顶部 + 思维导图切换 |
| 多版本 | 顶栏下拉 | `<select>` 占位，hook 自定义切换 |

### 2. 一键初始化

```bash
PROJECT_NAME="MyApp" ./scripts/init-docs
```

创建完整的文档目录结构和基础文件：
```
docs/
├── index.html          # docsify 主配置（UE 5 风格全功能）
├── _sidebar.md         # 多级嵌套侧边栏
├── _navbar.md          # 顶部导航（已合并到自定义顶栏）
├── README.md           # 首页（含大图 banner + Mermaid 示例）
├── custom.css          # UE 5 深色主题（紫色品牌色）
├── logo.svg            # 项目 Logo
├── 基础篇/             # 入门指南
│   ├── 快速开始.md
│   ├── 核心概念.md
│   ├── 核心概念-进阶.md
│   └── 安装指南.md
├── 进阶篇/
│   ├── 配置详解.md
│   ├── API参考.md
│   ├── 最佳实践.md
│   ├── Mermaid图表.md
│   └── 思维导图.md
└── 附录/
    ├── 常见问题.md
    ├── 更新日志.md
    └── 贡献指南.md
```

### 3. 现代化 UI 配置

index.html 预配置：
- **docsify-themeable simple-dark** — UE 5 深色主题
- **docsify-search** — 全文搜索（中文分词 + `按标题筛选`占位）
- **docsify-pagination** — 页面导航（上一页/下一页）
- **Mermaid 10** — 流程图/时序图/甘特图/类图
- **Prism.js + 行号 + autoloader** — 12+ 语言高亮
- **docsify-copy-code** — 一键复制代码
- **docsify-zoom-image** — 图片点击缩放
- **docsify-count** — 字数统计
- **自定义 CSS** — UE 5 深色 + 紫色品牌色 + 玻璃顶栏 + 多级侧边栏

### 4. 增强功能：Mermaid 全屏 + 工具栏 + Markmap

#### 4.1 固定工具栏

页面右下角浮动工具栏（`.deer-toolbar`），毛玻璃效果：
- **回到顶部** — 平滑滚动到页面顶部
- **思维导图切换** — 一键切换 Markdown → Markmap 思维导图模式

#### 4.2 Mermaid 图表全屏查看 + 导出

点击任意 Mermaid 图表 → 进入全屏遮罩：
- **放大/缩小/重置** — 鼠标缩放控制（0.25x ~ 5x）
- **导出 SVG / PNG** — 矢量图 / 2x 清晰度位图
- **Esc 关闭** — 键盘快捷关闭
- **顶栏 ✕ 关闭**

#### 4.3 Markmap 思维导图（v2.0 升级）

点击工具栏「导图」按钮 → 隐藏 Markdown 正文 + 右侧目录，展示 Markmap 交互式思维导图：

- **默认全部展开** — `initialExpandLevel: -1`，进入即看到完整树形结构
- **拖拽平移 / 滚轮缩放** — d3 完整交互
- **节点展开/折叠** — 点击节点切换
- **自动跳过 YAML front matter**
- **路由切换时自动刷新导图内容**
- **深色适配** — 节点文字 + 紫色连接线

**v2.0 修复的 markmap 渲染问题**：
- 旧版使用 `markmap-autoloader` 单一脚本，加载顺序不稳定导致偶发失败
- v2.0 改用 **d3 + markmap-lib + markmap-view 分模块 ESM 加载**：
  ```html
  <script type="module">
    import * as d3 from 'https://cdn.jsdelivr.net/npm/d3@7/+esm';
    import { Transformer, Markmap, defaultPlugins } from 'https://cdn.jsdelivr.net/npm/markmap-lib@0.17.0/+esm';
    window.markmap = { Transformer, Markmap };
    window.markmapPluginDefault = defaultPlugins;  // 启用 link/code/katex 钩子
    window.dispatchEvent(new Event('deer-markmap-ready'));
  </script>
  ```
- 渲染函数监听 `deer-markmap-ready` 事件，**库就绪后才渲染**，避免"有的能渲染有的不能"的偶发问题

#### 4.4 面包屑 + 右侧页内目录

- **面包屑** — 自动基于 `vm.route.path` 生成 `首页 / 分类 / 当前页` 路径，H1 作为当前页名
- **右侧 TOC** — 提取当前页 H2/H3，IntersectionObserver 滚动监听高亮当前章节
- **小屏自适应** — `≤1280px` 自动隐藏右侧 TOC

### 5. 智能侧边栏生成

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
  * [简介](基础篇/01-简介.md)
  * [安装](基础篇/02-安装.md)
* 进阶篇
  * [配置](进阶篇/01-配置.md)
  * [API](进阶篇/02-API.md)
```

### 6. 中文优先

- 内置中文明细体字体栈（PingFang SC / 微软雅黑）
- 搜索插件中文兼容
- 所有模板注释为中文
- 默认侧边栏结构使用中文命名（基础篇/进阶篇/附录）

---

## 文件结构

```
skill-markets/docsify-doc-builder/
├── SKILL.md                      # 本文件 — 技能入口
├── scripts/
│   ├── check-env.{ps1,sh}        # 环境检查（检测/安装 docsify-cli）
│   ├── init-docs.{ps1,sh}        # 文档初始化（创建目录、复制模板）
│   ├── generate-sidebar.{ps1,sh} # 侧边栏生成（扫描 docs/ → _sidebar.md）
│   └── serve.{ps1,sh}            # 启动 docsify 开发服务器
└── templates/
    ├── index.html                # docsify 核心配置（UE 5 风格全功能）
    ├── custom.css                # UE 5 深色主题 + 顶栏/侧边栏/右侧 TOC 样式
    ├── _sidebar.md               # 侧边栏基础结构（多级嵌套）
    ├── _navbar.md                # 顶部导航（已被自定义顶栏替代）
    ├── README.md                 # 首页（含大图 banner + Mermaid 示例）
    └── logo.svg                  # 默认 Logo（书籍图标）
```

---

## 使用方式

### 交互式（推荐）

直接请求 AI 调用此技能：
> "给我们的项目搭建 docsify 文档"
> "初始化文档系统，要 UE 5 风格"
> "建一个像虚幻引擎那样的文档站"

AI 会自动执行完整工作流。

### 手动执行

```powershell
# 0. 环境检查（首次）
.trae/skills/docsify-doc-builder/scripts/check-env.ps1

# 1. 初始化
$env:PROJECT_NAME="MyApp"; .trae/skills/docsify-doc-builder/scripts/init-docs.ps1

# 2. 配置 index.html（可选：修改端口、版本号、GitHub 链接）

# 3. 生成侧边栏
.trae/skills/docsify-doc-builder/scripts/generate-sidebar.ps1

# 4. 启动服务
.trae/skills/docsify-doc-builder/scripts/serve.ps1
# 访问 http://localhost:3000
```

---

## 自定义指南

### 修改品牌色

编辑 `docs/custom.css` 中的 CSS 变量：
```css
:root {
  --brand: #9b7efd;          /* 主品牌色 */
  --brand-light: #b69cff;    /* 亮色（hover） */
  --brand-dark: #7c5cfc;     /* 深色（active） */
  --bg-primary: #1c1c1c;     /* 主背景 */
  --text-primary: #f5f5f5;   /* 主文本 */
  --border: #3a3a3a;         /* 边框 */
}
```

### 配置多版本（顶栏下拉）

编辑 `docs/index.html` 中 `injectTopbar()` 函数的 `<select>` 内容：
```html
<select id="deerVersionSelect">
  <option value="v2.0" selected>v2.0（最新）</option>
  <option value="v1.9">v1.9</option>
  ...
</select>
```
在 `change` 事件中实现版本切换逻辑（默认仅打日志，可对接 docsify 内置 `window.$docsify.version`）。

### 关闭工具栏 / Markmap / 右侧 TOC

在 `docs/custom.css` 末尾添加：
```css
/* 关闭 Markmap 工具栏按钮 */
.deer-tb-btn[data-action="toggle-markmap"] { display: none; }

/* 关闭右侧页内目录 */
.deer-right-toc { display: none !important; }

/* 关闭面包屑 */
.deer-breadcrumb { display: none !important; }

/* 关闭顶栏 */
.deer-topbar { display: none !important; }
```

### 添加更多文档

```bash
# 1. 创建新的 Markdown 文件
echo "# 新章节" > docs/新章节.md

# 2. 重新生成侧边栏
.trae/skills/docsify-doc-builder/scripts/generate-sidebar.ps1
```

---

## 升级日志

### v2.0 (2026-07-31) — UE 5 风格接入示例

- ✨ 新增：虚幻引擎 5 风格布局（顶栏 + 多级分类 + 面包屑 + 右侧 TOC）
- ✨ 新增：顶栏版本下拉器（多版本占位）
- ✨ 新增：面包屑导航（自动基于路由）
- ✨ 新增：右侧"在这个页面上"页内目录（IntersectionObserver 滚动高亮）
- ✨ 新增：Markmap **默认全部展开**（`initialExpandLevel: -1`）
- 🐛 修复：Markmap 渲染偶发失败 — 改用 d3 + markmap-lib + markmap-view 分模块 ESM 加载，渲染函数监听 `deer-markmap-ready` 事件
- 🐛 修复：Markmap 插件缺失 — 引入 `defaultPlugins` 启用 link/code/katex 钩子
- 🎨 UI：深色主题（UE 5 紫 + 深灰），玻璃顶栏，圆角 + 过渡动画
- 📚 文档：新增 Mermaid / 思维导图章节示例

### v0.1.0 (2024-01-01)

- 初始版本（基础 docsify 模板）

---

## 与其它技能协同

- **openapi-doc-exporter** — 导出 API 文档后，可用本技能将生成的 OpenAPI 文档发布为 UE 5 风格 docsify 站点
- **ui-ux-pro-max** — 文档页面的 UI 设计可参考该技能的设计规范
- **doc-map-manager** — 大型文档站可叠加 doc-map-manager 做二级索引
