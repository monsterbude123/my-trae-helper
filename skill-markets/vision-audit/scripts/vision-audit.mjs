/**
 * Vision Audit — Qwen3-VL 视觉验收脚本 (Node.js)
 *
 * 技能目录: .trae/skills/vision-audit/
 * 读取 E2E 截图 → 调用本地 VL 模型 → 输出结构化审计报告
 *
 * 用法:
 *   node .trae/skills/vision-audit/scripts/vision-audit.mjs --dir frontend/debug/screenshots
 *   node .trae/skills/vision-audit/scripts/vision-audit.mjs --single frontend/debug/screenshots/route-01-HomeView.png
 *   node .trae/skills/vision-audit/scripts/vision-audit.mjs --dir frontend/test-results --failed-only
 *   npm run test:e2e:vision
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs'
import { join, resolve, dirname, basename, extname, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url))
const SKILL_DIR = resolve(SCRIPT_DIR, '..')

// ═══════════════════════════════════════
// 项目根目录探测（向上查找 .trae/ 或 .git/）
// ═══════════════════════════════════════

function findProjectRoot() {
  let dir = SCRIPT_DIR
  for (let i = 0; i < 6; i++) {
    if (existsSync(join(dir, '.trae')) || existsSync(join(dir, '.git'))) return dir
    const parent = dirname(dir)
    if (parent === dir) break
    dir = parent
  }
  // 兜底：假设 standard layout
  return resolve(SCRIPT_DIR, '../../../..')
}

const PROJECT_ROOT = findProjectRoot()

// ═══════════════════════════════════════
// 配置加载（多路径搜索）
// ═══════════════════════════════════════

function loadEnv() {
  const candidates = [
    join(PROJECT_ROOT, '.env.vision'),
    join(SKILL_DIR, '.env.vision'),
    join(process.cwd(), '.env.vision'),
  ]

  let envPath = null
  for (const p of candidates) {
    if (existsSync(p)) { envPath = p; break }
  }

  if (!envPath) {
    console.error('❌ 未找到 .env.vision 配置文件')
    console.error(`   搜索路径: ${candidates.join(', ')}`)
    console.error(`   请从 ${join(SKILL_DIR, '.env.vision.example')} 复制并配置`)
    safeExit(1)
  }

  console.log(`📋 配置: ${envPath}`)

  const raw = readFileSync(envPath, 'utf-8')
  const config = {}
  for (const line of raw.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const eqIdx = trimmed.indexOf('=')
    if (eqIdx === -1) continue
    config[trimmed.slice(0, eqIdx)] = trimmed.slice(eqIdx + 1)
  }

  const apiKey = config.VISION_API_KEY
  if (!apiKey) {
    console.error('❌ 未配置 VISION_API_KEY，请在 .env.vision 中设置')
    console.error('   提示: 新版 local llm 需从 UI 获取实际 API token')
    console.error('   配置后 VISION_API_KEY 非空即可')
    safeExit(1)
  }

  return {
    apiBaseUrl: config.VISION_API_BASE_URL || 'http://localhost:1234/v1',
    modelName: config.VISION_MODEL_NAME || 'qwen3-vl-8b-instruct',
    apiKey,
    timeout: parseInt(config.VISION_REQUEST_TIMEOUT || '30000', 10),
    maxConcurrency: parseInt(config.VISION_MAX_CONCURRENCY || '2', 10),
    workerStartDelay: parseInt(config.VISION_WORKER_START_DELAY || '500', 10),
    retries: parseInt(config.VISION_MAX_RETRIES || '2', 10),
    retryDelay: parseInt(config.VISION_RETRY_DELAY_MS || '2000', 10),
    screenshotsDir: config.VISION_SCREENSHOTS_DIR || 'frontend/debug/screenshots',
    reportDir: config.VISION_REPORT_DIR || 'frontend/debug/reports/vision',
  }
}

// ═══════════════════════════════════════
// CLI 参数解析
// ═══════════════════════════════════════

function parseArgs() {
  const args = process.argv.slice(2)
  const opts = { single: null, dir: null, failedOnly: false, customPrompt: null, concurrency: null }

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--single': opts.single = args[++i]; break
      case '--dir': opts.dir = args[++i]; break
      case '--failed-only': opts.failedOnly = true; break
      case '--prompt': opts.customPrompt = args[++i]; break
      case '--concurrency': opts.concurrency = parseInt(args[++i], 10); break
    }
  }

  return opts
}

// ═══════════════════════════════════════
// VL 模型调用
// ═══════════════════════════════════════

function buildAuditPrompt(customPrompt) {
  if (customPrompt) return customPrompt

  return `描述这张网页截图。用中文回复。

输出 JSON，无多余文字：
{
  "diagram": "用 ┌┐└┘├┤│┬┴┼─ 画页面布局，标出实际文字和按钮",
  "zones": { "titlebar":"", "left_panel":"", "center":"", "right_panel":"", "bottom_panel":"", "statusbar":"" },
  "risk": "LOW",
  "verdict": "一句描述当前页面状态",
  "issues": []
}`
}

async function callVLModel(config, imageBase64, prompt) {
  const controller = new AbortController()
  let timer = null

  try {
    // 用 setTimeout 替代 AbortSignal.timeout 避免 Windows uv_handle closing 断言
    timer = setTimeout(() => {
      try { controller.abort() } catch {}
    }, config.timeout)

    const response = await fetch(`${config.apiBaseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
      },
      body: JSON.stringify({
        model: config.modelName,
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'image_url',
                image_url: { url: `data:image/png;base64,${imageBase64}` },
              },
              { type: 'text', text: prompt },
            ],
          },
        ],
        max_tokens: 4096,
        temperature: 0.1,
        // local llm: 禁用推理思考，直接输出
        thinking: { type: 'disabled' },
      }),
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`API ${response.status}: ${await response.text().then(t => t.slice(0, 200))}`)
    }

    const data = await response.json()
    const msg = data.choices?.[0]?.message || {}
    // 推理模型（Qwen3.6）把输出放在 reasoning_content，标准模型在 content
    const rawContent = msg.content || msg.reasoning_content || ''
    const content = rawContent.replace(/<think[\s\S]*?<\/think>/gi, '').trim()

    return parseVLResponse(content)
  } finally {
    if (timer != null) {
      clearTimeout(timer)
      timer = null
    }
    // 确保 abort controller 被清理
    try { controller.abort() } catch {}
  }
}

function parseVLResponse(content) {
  const clean = content.replace(/```json\n?|\n?```/g, '').trim()

  // 尝试 JSON 解析
  let parsed = null
  try { parsed = JSON.parse(clean) } catch {}

  // 没有直接JSON，尝试用正则提取
  if (!parsed) {
    const jsonMatch = clean.match(/\{[\s\S]*\}/)
    if (jsonMatch) {
      try { parsed = JSON.parse(jsonMatch[0]) } catch {}
    }
  }

  // 非 JSON 响应：将原始文本作为 verdict 返回
  if (!parsed) {
    return {
      diagram: clean.slice(0, 300),
      zones: { titlebar: clean.slice(0, 300) },
      risk: 'LOW',
      verdict: clean.slice(0, 800),
      issues: [],
    }
  }

  // 字段别名兼容（35B 模型可能用 di 代替 diagram）
  const diagram = parsed.diagram || parsed.di || ''
  const risk = ['LOW', 'MEDIUM', 'HIGH'].includes(parsed.risk) ? parsed.risk : 'LOW'
  const verdict = parsed.verdict || (diagram ? `页面: ${diagram.slice(0, 80)}` : clean.slice(0, 200))
  const issues = Array.isArray(parsed.issues) ? parsed.issues : []

  // 从原始响应中重新提取 zones（避免模型生成的嵌套JSON被二次序列化）
  let zones = parsed.zones
  if (typeof zones === 'string') {
    try { zones = JSON.parse(zones) } catch {}
  }
  if (!zones || typeof zones !== 'object') {
    zones = { titlebar: '', left_panel: '', center: '', right_panel: '', bottom_panel: '', statusbar: '' }
  }

  return { diagram, zones, risk, verdict, issues }
}

// ═══════════════════════════════════════
// 截图文件工具
// ═══════════════════════════════════════

function resolvePath(relPath) {
  // 支持相对于 project root 或 cwd 的路径
  const fromRoot = resolve(PROJECT_ROOT, relPath)
  if (existsSync(fromRoot)) return fromRoot
  return resolve(process.cwd(), relPath)
}

function gatherScreenshots(dirPath, failedOnly) {
  const absDir = resolvePath(dirPath)
  if (!existsSync(absDir)) {
    console.error(`❌ 目录不存在: ${absDir}`)
    return []
  }

  /** 递归收集目录下所有 .png 文件 */
  function walk(dir) {
    const results = []
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name)
      if (entry.isDirectory()) {
        results.push(...walk(full))
      } else if (extname(entry.name).toLowerCase() === '.png') {
        if (!failedOnly || entry.name.includes('failed')) {
          results.push(full)
        }
      }
    }
    return results
  }

  const files = walk(absDir).sort()
  // 模块子目录打印摘要
  const byModule = new Map()
  for (const f of files) {
    const rel = relative(absDir, f)
    const mod = rel.includes(sep) ? rel.split(sep)[0] : '(root)'
    if (!byModule.has(mod)) byModule.set(mod, [])
    byModule.get(mod).push(rel)
  }
  console.log(`   截图分布: ${[...byModule.entries()].map(([k, v]) => `${k}: ${v.length}`).join(' | ')}`)

  return files
}

function imageToBase64(filePath) {
  const buffer = readFileSync(filePath)
  return buffer.toString('base64')
}

// ═══════════════════════════════════════
// 并发控制（交错启动 + 指数退避重试）
// ═══════════════════════════════════════

/** 等待指定毫秒 */
function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

/**
 * 安全退出 — Windows 上 process.exit(0) 可能触发
 * UV_HANDLE_CLOSING 断言（libuv 未清理完 timer/controller）。
 * 加 100ms 延迟让 I/O 循环自然结束。
 */
function safeExit(code) {
  setTimeout(() => process.exit(code), 100)
}

/** 带指数退避的重试（仅重试超时/5xx/连接错误） */
async function withRetry(fn, maxRetries = 3, baseDelayMs = 2000) {
  let lastErr
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn()
    } catch (err) {
      lastErr = err
      // 不重试 4xx 错误（配置错误不应重试）
      if (err.message?.includes('API 4')) {
        throw err
      }
      if (i < maxRetries) {
        const delay = baseDelayMs * Math.pow(2, i)
        console.log(`🔄 第${i + 1}次重试（${delay}ms 后）`)
        await sleep(delay)
      }
    }
  }
  throw lastErr
}

/**
 * 并发执行器：
 * 1. 交错启动 worker（每个间隔 startDelayMs），避免瞬时负载冲击
 * 2. worker 内部保持串行拉取队列
 * 3. 保证结果按入栈顺序排列
 * 4. 单 request 超时/5xx 自动指数退避重试
 */
async function runConcurrently(items, concurrency, fn, { startDelayMs = 500, retries = 2, retryDelayMs = 2000 } = {}) {
  const queue = items.map((item, idx) => ({ item, idx }))
  const results = new Array(items.length)

  async function worker() {
    while (queue.length > 0) {
      const entry = queue.shift()
      if (!entry) break
      const { item, idx } = entry
      results[idx] = await withRetry(() => fn(item), retries, retryDelayMs)
    }
  }

  // 交错启动 worker
  const workers = []
  for (let i = 0; i < Math.min(concurrency, items.length); i++) {
    workers.push(worker())
    if (i < Math.min(concurrency, items.length) - 1) {
      await sleep(startDelayMs)
    }
  }
  await Promise.all(workers)

  // 过滤 undefined（理论上不应出现）
  return results.filter(Boolean)
}

// ═══════════════════════════════════════
// 报告生成
// ═══════════════════════════════════════

function generateMarkdown(summary, findings, model) {
  const lines = [
    `# Vision Audit Report`,
    ``,
    `> **生成时间**: ${new Date().toISOString()}`,
    `> **模型**: ${model}`,
    `> **总计**: ${summary.total} | 🟢 LOW: ${summary.low} | 🟡 MEDIUM: ${summary.medium} | 🔴 HIGH: ${summary.high}`,
    ``,
    `---`,
    ``,
    `## 问题汇总`,
    ``,
  ]

  const highFindings = findings.filter(f => f.risk === 'HIGH')
  const mediumFindings = findings.filter(f => f.risk === 'MEDIUM')
  const lowFindings = findings.filter(f => f.risk === 'LOW')

  if (highFindings.length > 0) {
    lines.push(`### 🔴 HIGH (${highFindings.length})`, '')
    for (const f of highFindings) {
      lines.push(`#### ${f.screenshot}`)
      if (f.diagram) { lines.push('', '```', f.diagram, '```', '') }
      if (f.zones) {
        for (const [zone, desc] of Object.entries(f.zones)) {
          lines.push(`- **${zone}**: ${desc}`)
        }
      }
      if (f.issues && f.issues.length > 0) {
        lines.push(`- **问题**: ${f.issues.join('; ')}`)
      }
      lines.push(`- **结论**: ${f.verdict}`, '')
    }
  } else {
    lines.push('✅ 无 HIGH 级别问题', '')
  }

  if (mediumFindings.length > 0) {
    lines.push(`### 🟡 MEDIUM (${mediumFindings.length})`, '')
    for (const f of mediumFindings) {
      lines.push(`#### ${f.screenshot}`)
      if (f.diagram) { lines.push('', '```', f.diagram, '```', '') }
      if (f.issues && f.issues.length > 0) {
        lines.push(`- **问题**: ${f.issues.join('; ')}`)
      }
      lines.push(`- **结论**: ${f.verdict}`, '')
    }
  }

  lines.push(`### 🟢 LOW (${lowFindings.length})`, '')
  for (const f of lowFindings) {
    lines.push(`#### ${f.screenshot}`)
    if (f.diagram) { lines.push('', '```', f.diagram, '```', '') }
    lines.push(`- **结论**: ${f.verdict}`, '')
  }

  return lines.join('\n')
}

function generateJson(summary, findings, model) {
  return JSON.stringify({
    generatedAt: new Date().toISOString(),
    model,
    summary,
    findings: findings.map(f => ({
      screenshot: f.screenshot,
      risk: f.risk,
      diagram: f.diagram,
      zones: f.zones,
      issues: f.issues,
      verdict: f.verdict,
    })),
  }, null, 2)
}

// ═══════════════════════════════════════
// 主入口
// ═══════════════════════════════════════

async function main() {
  const opts = parseArgs()

  if (!opts.single && !opts.dir) {
    console.error('用法: node .trae/skills/vision-audit/scripts/vision-audit.mjs --dir <directory> [--failed-only]')
    console.error('  或: node .trae/skills/vision-audit/scripts/vision-audit.mjs --single <file> [--prompt "..."]')
    safeExit(1)
  }

  const config = loadEnv()
  // CLI 参数可覆盖配置文件的并发数
  if (opts.concurrency != null) { config.maxConcurrency = opts.concurrency }

  console.log(`🔍 Vision Audit — 模型: ${config.modelName}`)
  console.log(`   服务地址: ${config.apiBaseUrl}`)
  console.log(`   项目根: ${PROJECT_ROOT}`)
  console.log(`   并发: ${config.maxConcurrency} | 启动间隔: ${config.workerStartDelay}ms | 重试: ${config.retries}次/间隔${config.retryDelay}ms`)

  // 收集截图
  let files
  if (opts.single) {
    files = [resolvePath(opts.single)]
  } else {
    files = gatherScreenshots(opts.dir, opts.failedOnly)
  }

  if (files.length === 0) {
    console.error('❌ 未找到 PNG 截图')
    safeExit(1)
  }

  console.log(`📸 待分析: ${files.length} 张截图`)
  console.log(`🔄 最大并发: ${config.maxConcurrency}`)

  // 预热 API
  console.log('🔌 连接 VL 模型...')
  try {
    const healthCtl = new AbortController()
    const healthTimer = setTimeout(() => { try { healthCtl.abort() } catch {} }, 5000)
    const healthCheck = await fetch(`${config.apiBaseUrl}/models`, {
      headers: { 'Authorization': `Bearer ${config.apiKey}` },
      signal: healthCtl.signal,
    })
    clearTimeout(healthTimer)
    if (healthCheck.ok) {
      console.log('   ✅ 模型服务可用')
    }
  } catch {
    console.warn('   ⚠️ 模型服务连接超时，继续尝试...')
  }

  console.log('')

  // 逐张分析
  const prompt = buildAuditPrompt(opts.customPrompt)

  const results = await runConcurrently(files, config.maxConcurrency, async (filePath) => {
    const fileName = basename(filePath)
    process.stdout.write(`  📷 ${fileName} ... `)

    try {
      const imageBase64 = imageToBase64(filePath)
      const result = await callVLModel(config, imageBase64, prompt)

      const finding = {
        screenshot: fileName,
        risk: result.risk || 'MEDIUM',
        diagram: result.diagram || '',
        zones: result.zones || {},
        issues: result.issues || [],
        verdict: result.verdict || '无结论',
      }

      const emoji = { LOW: '🟢', MEDIUM: '🟡', HIGH: '🔴' }[finding.risk] || '⚪'
      console.log(`${emoji} ${finding.risk} — ${finding.verdict}`)
      return finding
    } catch (err) {
      console.log(`❌ 失败: ${err.message}`)
      return {
        screenshot: fileName,
        risk: 'MEDIUM',
        diagram: '分析失败',
        zones: { titlebar: err.message },
        issues: [`VL 调用失败: ${err.message}`],
        verdict: `VL 调用失败: ${err.message}`,
      }
    }
  }, {
    startDelayMs: config.workerStartDelay,
    retries: config.retries,
    retryDelayMs: config.retryDelay,
  })

  // 汇总
  const findings = results
  const summary = {
    total: findings.length,
    low: findings.filter(f => f.risk === 'LOW').length,
    medium: findings.filter(f => f.risk === 'MEDIUM').length,
    high: findings.filter(f => f.risk === 'HIGH').length,
  }

  console.log('')
  console.log(`📊 汇总: ${summary.total} | 🟢 ${summary.low} | 🟡 ${summary.medium} | 🔴 ${summary.high}`)

  // 写入报告
  const reportDir = resolvePath(config.reportDir)
  if (!existsSync(reportDir)) {
    mkdirSync(reportDir, { recursive: true })
  }

  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const mdPath = join(reportDir, `vision-report-${ts}.md`)
  const jsonPath = join(reportDir, `vision-report-${ts}.json`)

  writeFileSync(mdPath, generateMarkdown(summary, findings, config.modelName), 'utf-8')
  writeFileSync(jsonPath, generateJson(summary, findings, config.modelName), 'utf-8')

  console.log(`📄 报告: ${mdPath}`)
  console.log(`📄 JSON: ${jsonPath}`)

  if (summary.high > 0) {
    console.log(`\n⚠️ 发现 ${summary.high} 个 HIGH 级别问题，需人工复核`)
    safeExit(1)
  } else {
    console.log('\n✅ Vision Audit 通过')
    safeExit(0)
  }
}

main().catch(err => {
  console.error('💥 未捕获错误:', err)
  safeExit(2)
})
