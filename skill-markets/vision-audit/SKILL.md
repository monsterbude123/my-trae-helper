---
name: vision-audit
description: UI/UX 视觉验收 — 用本地 Qwen3-VL 模型分析 Playwright 截图，自动识别布局异常、样式错误、空白占位，输出结构化审计报告
intent: UI/UX 视觉验收 — 用本地 Qwen3-VL 模型分析 Playwright 截图，自动识别布局异常、样式错...
category: gate
audience: [designer]
---
# vision-audit

用本地视觉语言模型（Qwen3-VL via local llm）分析 E2E 截图，自动检测 UI/UX 异常。

**目录结构**:
```
.trae/skills/vision-audit/
├── SKILL.md                  # 本文件
├── PROMPT-CHEATSHEET.md      # 提示词模板参考
├── .env.vision.example       # 配置模板
├── scripts/
│   ├── vision-audit.mjs      # Node.js 版（零依赖）
│   └── vision-audit.py       # Python 版（支持图片缩放 --resize）
└── reports/                  # 输出报告（可选）
```

---

## AI Agent 强制前置检查

> **此节优先级最高。AI Agent 加载此技能后，必须先完成本检查，否则禁止继续。**

1. **只检查项目根目录下的 `.env.vision`**，路径固定为 `<项目根>/.env.vision`。**禁止去其他目录找。**

2. **如果不存在** → **立即阻塞**，输出以下信息并停止：

```
❌ vision-audit 阻塞：项目根目录下未找到 .env.vision

请创建配置文件：
  cp .trae/skills/vision-audit/.env.vision.example .env.vision

然后编辑项目根目录下的 .env.vision 填入配置：
  VISION_API_BASE_URL  — local llm 服务地址（默认 http://localhost:1234/v1）
  VISION_MODEL_NAME    — 模型名称（默认 qwen3-vl-8b-instruct）
  VISION_API_KEY       — local llm API token（新版需从 UI 获取，非 "lm-studio"）

⚠️ 禁止用 cp/copy 覆盖已存在的 .env.vision。
```

3. **如果存在** → 读取并确认 `VISION_API_KEY` 非空，然后继续。**不再去其他目录找。**

---

## 前置条件

1. **local llm** 已安装并运行
2. **Qwen3-VL-8B-Instruct** 模型已下载并加载（或 4B 临时替代）
3. **`.env.vision`** 已配置（脚本自动搜索：项目根 > 技能目录 > CWD）

```bash
# 仅在首次配置时执行！如果 .env.vision 已存在，直接编辑即可，不要覆盖。
cp .trae/skills/vision-audit/.env.vision.example .env.vision
# 编辑 .env.vision 填入实际配置（尤其是 local llm API token）
```

> ⚠️ **安全警告**: `.env.vision` 在 `.gitignore` 中被 `.env.*` 规则忽略，AI 工具的文件搜索可能无法发现已有文件。
> **AI Agent 使用此技能前必须先确认 `.env.vision` 是否已存在，禁止用 `cp` / `copy` 覆盖已有配置。**
> local llm 新版需从 UI 获取实际 API token，`VISION_API_KEY=lm-studio` 不再有效。

4. E2E 截图已生成（先跑 `npm run test:e2e`）

---

## 模型推荐

| 模型 | 适用性 | 上下文 |
|------|--------|--------|
| `Qwen3-VL-8B-Instruct` (GGUF) | **推荐** — 布局/颜色/异常检测均可靠 | 需 100K+ 上下文 |
| `Qwen3-VL-4B-Instruct` (GGUF) | 可用 — 会漏掉细微的样式问题 | 同上 |
| `qwen3-vl-4b-thinking` (GGUF) | 可用 — 需剥离 `/think` 标记 | 同上 |

---

## 工作流

### 标准工作流（E2E 批量）

```
截图生成 (test:e2e)
     ↓
vision-audit 脚本读取截图
     ↓
交错启动 worker（避免瞬时负载冲击）
     ↓
逐张发送给 Qwen3-VL（信号量限流 + 指数退避重试）
     ↓
VL 模型返回结构化分析 JSON
     ↓
汇总生成 <report>.md + <report>.json
     ↓
人工复核 HIGH 级别问题
```

### 人类交互工作流（逐张审查）⭐

> **推荐**：与 `screenshot` skill 配合，一次只截一张、看一张。

```
循环直到验收完成:
  1. screenshot skill 截一张图
     node .trae/skills/screenshot/scripts/screenshot.mjs <url> <out> [--click ...]
  2. vision-audit --single 分析内容
     node .trae/skills/vision-audit/scripts/vision-audit.mjs --single <file> --prompt "描述实际可见内容"
  3. 阅读 VL 返回的内容描述
  4. 根据内容决定下一步操作
  5. 回到第1步
```

**Prompt 原则**：
```
✅ "描述页面上实际可见的文字、按钮、输入框、弹窗内容"
✅ "当前激活的是哪个标签？编辑器里有几段文字？"
❌ "检查布局是否合理"
❌ "评估页面是否正常"
```

详见 `.trae/rules/human-workflow-rule.md`。

### 线框图识别工作流（--describe）⭐ NEW

> **用途**：给定一张截图，用 ASCII 线框图描述页面内容和布局。自带降级机制 + Agent 能力检测。

```
用户: "这张截图是什么内容？"（指定截图路径）
     ↓
Agent 检查自己是否有视觉能力
     ├─ 有 → 调用 vision-audit --describe <截图> --agent-has-vision
     │        ↓
     │   ┌─ Tier 0: Agent 声明有视觉能力 ───────────
     │   │  输出 JSON: { status: "agent_vision", prompt: "..." }
     │   │  Agent 直接用自己的视觉能力分析图片
     │   └────────────────────────────────────────────
     │
     └─ 无 → 调用 vision-audit --describe <截图>
              ↓
         ┌─ Tier 1: 本地 VL 模型可用 ─────────────────
         │  Qwen3-VL 分析截图 → 输出 JSON:
         │  { status: "ok", diagram: "┌────┐...", zones: {...}, verdict: "..." }
         │  其中 diagram 用 ┌┐└┘├┤│┬┴┼─ 画线框图，标实际文字
         └────────────────────────────────────────────
              │ VL 不可用 ↓
         ┌─ Tier 2: 降级到 AI Agent 视觉 ─────────────
         │  输出 JSON:
         │  { status: "fallback", mcp_call: {...}, prompt: "..." }
         │  AI Agent 收到后调用 read_media_file MCP 读取图片，
         │  用返回的 prompt 分析截图并输出线框图。
         └────────────────────────────────────────────
```

**Agent 能力检测参数**：
- `--agent-has-vision` — Agent 声明自己有视觉能力时使用，跳过本地 VL 模型直接用自己的能力

**降级原理**：
- **Tier 0**（优先）：Agent 知道自己有视觉能力时，直接传入 `--agent-has-vision` 参数，脚本跳过所有检查直接返回分析指令，Agent 用自己的视觉能力处理图片
- **Tier 2**（降级）：当 Agent 无视觉能力 + 本地 local llm 未运行或 .env.vision 未配置时，脚本输出结构化指令告诉 AI Agent 使用 `read_media_file` MCP 工具读取图片

**输出格式**：
- `status: "agent_vision"` — Agent 主动用自己的视觉能力处理
- `status: "ok"` — 本地 VL 分析成功，`diagram` 字段包含 ASCII 线框图
- `status: "fallback"` — VL 不可用，Agent 按 `mcp_call` 指令调用 read_media_file
- `status: "error"` — 文件不存在等错误

---

## 命令

### Node.js（零依赖，已集成到 npm scripts）

```bash
# 1. 全量审计（从项目根目录运行）
npm run test:e2e:vision

# 2. 单张截图分析（调试用）
node .trae/skills/vision-audit/scripts/vision-audit.mjs --single frontend/debug/screenshots/route-01-HomeView.png

# 3. 目录批量分析
node .trae/skills/vision-audit/scripts/vision-audit.mjs --dir frontend/debug/screenshots

# 4. 限制并发数（4B thinking 模型建议 --concurrency 1）
node .trae/skills/vision-audit/scripts/vision-audit.mjs --dir frontend/debug/screenshots --concurrency 1

# 5. 仅分析失败截图
node .trae/skills/vision-audit/scripts/vision-audit.mjs --dir frontend/test-results --failed-only

# 6. 自定义 prompt 分析
node .trae/skills/vision-audit/scripts/vision-audit.mjs --single <file> --prompt "检查 TopBar 高度是否为 44px"
```

### Python（需 `pip install httpx pillow`，支持 `--resize` 缩放）

```bash
# 全量审计（自动缩放以适应小上下文模型）
python .trae/skills/vision-audit/scripts/vision-audit.py --dir frontend/debug/screenshots --resize 720

# 限制并发数
python .trae/skills/vision-audit/scripts/vision-audit.py --dir frontend/debug/screenshots --concurrency 1

# 单张调试
python .trae/skills/vision-audit/scripts/vision-audit.py --single frontend/debug/screenshots/route-01-HomeView.png

# 线框图识别（新）— 截图内容 → ASCII 线框图，VL 不可用时自动降级
python .trae/skills/vision-audit/scripts/vision-audit.py --describe frontend/debug/screenshots/route-01-HomeView.png

# Agent 有视觉能力时 — 直接用自己的能力，跳过本地 VL 模型
python .trae/skills/vision-audit/scripts/vision-audit.py --describe frontend/debug/screenshots/route-01-HomeView.png --agent-has-vision
```

---

## VL 分析维度

脚本向 Qwen3-VL 发送以下维度的审查指令：

### Prompt 编写原则（AI Agent 使用此技能时）

**必须客观描述，禁止主观判断：**
- ✅ 正确: "页面左上角有一个深色导航栏，高度约 36px，包含 3 个文字链接"
- ✅ 正确: "中央内容区域显示空白，无文字或图像"
- ❌ 错误: "布局合格，样式正常"（主观判断，缺乏事实依据）
- ❌ 错误: "这个页面看起来没问题"（无具体描述）

### VL 不可靠场景（必须 DOM 检测补充）

> 详细案例与改进 prompt 见 [PROMPT-CHEATSHEET.md](./PROMPT-CHEATSHEET.md)。

| 场景 | VL 不可靠 | 补充检测 |
|------|-----------|----------|
| 按钮 disabled 状态 | ❌ 误判为"可点击" | Playwright 检查 `class` 含 `n-button--disabled` |
| Input 文本溢出 | ❌ 误判为"完整显示" | `el.scrollWidth > el.clientWidth` |
| 元素精确计数 | ❌ 数量偏差 | `locator.count()` |
| Hover/Loading/焦点 | ❌ | 用 `page.hover()` 后截图 / 检查 class |

**原则**：VL 描述视觉事实（颜色、文字、位置），由 Agent 结合 DOM 检测做状态判断。不要让 VL 直接判断"按钮是否禁用""文字是否被截断""有几个表单项"。

**分析维度：**

### 1. 布局结构
- 页面包含哪些可见区域（顶栏 / 侧栏 / 内容区 / 底栏），各自大致尺寸
- 元素排列方式（横向/纵向/网格），区域之间是否有分隔线
- 是否有元素被截断、溢出或重叠

### 2. 内容状态
- 页面上实际可见的文字内容（标题、段落、标签文本）
- 图像/图标的位置和大致内容
- 是否存在空白区域（无内容渲染）

### 3. 样式特征
- 主要颜色（背景色、文字色、强调色）
- 间距特征（元素之间的间隙、边距）
- 字体大小差异（标题 vs 正文 vs 辅助文字）

### 4. 交互元素
- 可见按钮的位置、文字标签、大致尺寸
- 输入框/下拉菜单/滑块等表单控件的位置
- 是否有明显的 clickable 区域（链接、卡片）

### 5. 脚本内部使用（非 VL prompt 部分）
- **LOW**: 可接受的空态、品牌色正常
- **MEDIUM**: 布局轻微偏移、间距不一致
- **HIGH**: 白屏、内容缺失、样式严重错误、崩溃占位

---

## 报告格式

### 输出文件

```
frontend/debug/reports/vision/
├── vision-report-<timestamp>.md    # 人读报告
└── vision-report-<timestamp>.json  # 机器读，供 CI 消费
```

### JSON Schema

```ts
interface VisionReport {
  generatedAt: string
  model: string
  summary: {
    total: number
    low: number
    medium: number
    high: number
  }
  findings: Array<{
    screenshot: string
    risk: "LOW" | "MEDIUM" | "HIGH"
    dimensions: {
      layout: string
      content: string
      style: string
      interactions: string
    }
    verdict: string
  }>
}
```

---

## 与现有 E2E 流水线集成

```bash
npm run test:e2e              # Phase 1-3 + smoke → 生成截图
npm run test:e2e:report       # 生成 HTML/JSON/MD 报告
npm run test:e2e:vision       # Vision 审计（用 Node.js 脚本）
npm run test:e2e:vision-full  # 全套：E2E + 报告 + Vision 审计
```

---

## 配置参考 (.env.vision)

> ⚠️ 此文件包含 API 密钥，已在 `.gitignore` 中排除。不要提交到 Git。

```ini
VISION_API_BASE_URL=http://localhost:1234/v1
VISION_MODEL_NAME=qwen3-vl-8b-instruct
# local llm 新版需从 UI 获取实际 token（非 "lm-studio"）
VISION_API_KEY=sk-lm-xxxxx:xxxxxxxxxxxxx
VISION_REQUEST_TIMEOUT=30000
VISION_MAX_CONCURRENCY=2
VISION_WORKER_START_DELAY=500
VISION_MAX_RETRIES=2
VISION_RETRY_DELAY_MS=2000
VISION_SCREENSHOTS_DIR=frontend/debug/screenshots
VISION_REPORT_DIR=frontend/debug/reports/vision
```

---

## 注意事项

- local llm 必须保持运行，且模型已加载
- 脚本自动搜索 `.env.vision`：项目根 → 技能目录 → CWD
- ⚠️ **`.env.vision` 被 `.gitignore` 忽略**，AI 文件搜索工具可能无法发现已有文件。配置前必须先检查文件是否存在，禁止覆盖。
- 配置中路径相对于**项目根目录**（即 `.trae/` 所在目录）
- 单张 1440x900 截图分析约 5-15 秒（取决于 GPU）
- **Prompt 规范**: 提交给 VL 模型的 prompt 必须客观描述，禁止使用"合格/不合格/通过/不通过"等主观判断词
- **并发控制**（三重保障）：
  - `VISION_MAX_CONCURRENCY` — 信号量限流（4B thinking 建议 1，8B instruct 可用 2）
  - `VISION_WORKER_START_DELAY` — worker 交错启动间隔，避免瞬时负载冲击
  - `VISION_MAX_RETRIES` + `VISION_RETRY_DELAY_MS` — 超时/5xx 自动指数退避重试
- CLI 可覆盖并发：`--concurrency 1`
- 4B thinking 模型需 ≥ 4096 max_tokens，8B instruct 模型 1024 足够
- 分析结果是辅助性的，HIGH 级别问题需要人工确认
- 不可替代手动 UI review，仅作为第一轮自动筛查

---

## 故障排查

| 症状 | 根因 | 解决 |
|------|------|------|
| 脚本超时退出（exit code `-1073741510` / 0xC000013A） | 模型响应慢或本地内存不足，进程被强制中断 | 调大 `VISION_REQUEST_TIMEOUT`（如 120000），降并发 `--concurrency 1`，关闭其他占显存进程 |
| 找不到 `.env.vision` | 搜索顺序未命中或文件被 `.gitignore` 隐藏 | 确认文件在**项目根目录**；AI 工具可能搜不到，需手动 `ls -la` 验证 |
| local llm 返回 `invalid_api_key` | 用了旧占位符 `lm-studio` 或未带 Authorization | 从 local llm UI 复制真实 token（形如 `sk-lm-xxx:xxx`）写入 `VISION_API_KEY` |
| 分析结果明显不准（漏报/误报） | 4B 模型能力有限，或 prompt 含主观词 | 换 `qwen3-vl-8b-instruct`；prompt 改为客观描述（"页面左上角有 X"而非"布局是否合理"） |
| 按钮 disabled / 文本溢出 / 元素计数错误 | VL 视觉判断这些场景不可靠 | 必须用 DOM 检测补充（见上方"VL 不可靠场景"表） |
| `ImportError: cannot import name 'X'` | browser-use / 依赖版本不匹配 | `pip show browser-use` 确认版本，对照官方文档调整导入路径 |

**local llm 连接验证**（带 Authorization Header）：

```bash
curl -s -H "Authorization: Bearer sk-lm-xxx:xxx" http://localhost:1234/v1/models
```
