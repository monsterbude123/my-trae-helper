/**
 * screenshot — 通用 Playwright 截图工具
 *
 * 设计原则：一次只做一件事。导航 → (可选点击) → 截图 → 退出。
 *
 * 用法 (从项目根运行):
 *   node screenshot/scripts/screenshot.mjs <url> <output> [--click sel] [--wait sel]
 *
 * 示例:
 *   node screenshot/scripts/screenshot.mjs /workbench-unified out/01.png
 *   node screenshot/scripts/screenshot.mjs /workbench-unified out/02.png --click "button:has-text('智能体')"
 */
import { existsSync, mkdirSync } from 'fs'
import { resolve, dirname, join } from 'path'
import { fileURLToPath } from 'url'
import { createRequire } from 'module'

const __dirname = dirname(fileURLToPath(import.meta.url))

// ── 查找 Playwright 安装位置 ──
function findPlaywright() {
  // 向上查找 frontend/node_modules/playwright
  let dir = __dirname
  for (let i = 0; i < 8; i++) {
    const candidate = join(dir, 'frontend', 'node_modules', 'playwright')
    if (existsSync(candidate)) return candidate
    const parent = dirname(dir)
    if (parent === dir) break
    dir = parent
  }
  // fallback: 尝试当前 cwd
  return join(process.cwd(), 'frontend', 'node_modules', 'playwright')
}

const pwDir = findPlaywright()
if (!existsSync(pwDir)) {
  console.error('ERROR: 找不到 playwright，请确认 frontend 目录已 npm install')
  process.exit(1)
}

const _require = createRequire(join(pwDir, 'package.json'))
const { chromium } = _require('playwright-core')

// ── 参数解析 ──
const args = process.argv.slice(2)
if (args.length < 2 || args.includes('--help') || args.includes('-h')) {
  console.log('用法: node screenshot/scripts/screenshot.mjs <url> <output> [options]')
  console.log('  --base    基础URL (默认 http://127.0.0.1:5173)')
  console.log('  --click   截图前点击的CSS选择器')
  console.log('  --wait    等待出现的CSS选择器')
  console.log('  --delay   导航后延迟ms (默认 800)')
  console.log('  --viewport 视口 WxH (默认 1440x900)')
  console.log('  --full    全页截图')
  process.exit(0)
}

const positional = []
const opts = {}
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].slice(2)
    opts[key] = args[++i] ?? 'true'
  } else {
    positional.push(args[i])
  }
}

const urlArg = positional[0]
const outArg = positional[1]
const base = opts.base || 'http://127.0.0.1:5173'
const fullUrl = urlArg.startsWith('http') ? urlArg : `${base}${urlArg}`
const outPath = resolve(outArg)
const delay = parseInt(opts.delay || '800', 10)
const [vw, vh] = (opts.viewport || '1440x900').split('x').map(Number)
const fullPage = opts.full === 'true' || opts.full === '1'

mkdirSync(dirname(outPath), { recursive: true })

// ── 执行 ──
const browser = await chromium.launch({ headless: true })
let exitCode = 0

try {
  const page = await browser.newPage({ viewport: { width: vw, height: vh } })

  await page.goto(fullUrl, { waitUntil: 'networkidle', timeout: 15000 })
  await page.waitForTimeout(delay)

  // 可选：等待元素
  if (opts.wait) {
    await page.waitForSelector(opts.wait, { timeout: 5000 }).catch(() => {})
  }

  // 可选：点击元素
  if (opts.click) {
    try {
      await page.click(opts.click, { timeout: 5000 })
      await page.waitForTimeout(500)
    } catch {
      // 点击失败也继续截图
    }
  }

  await page.screenshot({ path: outPath, fullPage })
  console.log(outPath)
} catch (err) {
  console.error(`ERROR: ${err.message}`)
  exitCode = 1
} finally {
  await browser.close()
  process.exit(exitCode)
}
