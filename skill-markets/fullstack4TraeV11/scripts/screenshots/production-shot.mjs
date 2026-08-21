#!/usr/bin/env node
/**
 * fullstack4TraeV11 V11.8.7 — production-shot.mjs
 *
 * 跨项目生产路由截图模板。替代每个 change 内散落的 m3-production-shot.mjs。
 *
 * 用法:
 *   node scripts/screenshots/production-shot.mjs \
 *     --routes /zh/home,/zh/workspace \
 *     --base-url http://localhost:3000 \
 *     --change-id my-change-2026-08-18
 *
 * 输出:
 *   docs/evidence/<change-id>/<route>-<ISO>.png
 *
 * 退出码:
 *   0 = 全部成功
 *   1 = 至少一个路由失败
 *   2 = 部分成功(WARN)
 *
 * 实测锚点:
 *   ai-short-studio-monster 2026-08-18 m3-production-shot.mjs 反复改 3 次
 *   本脚本启用后,跨项目 0 改动,只传参
 */

import { mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { argv, exit } from 'node:process';

// ============ 参数解析 ============

function parseArgs() {
  const args = { routes: [], baseUrl: 'http://localhost:3000', changeId: 'default' };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    const v = argv[i + 1];
    if (k === '--routes') {
      args.routes = v.split(',').map((r) => r.trim()).filter(Boolean);
      i++;
    } else if (k === '--base-url') {
      args.baseUrl = v.replace(/\/$/, '');
      i++;
    } else if (k === '--change-id') {
      args.changeId = v;
      i++;
    }
  }
  return args;
}

function printHelp() {
  console.log(`fullstack4TraeV11 V11.8.7 — production-shot.mjs

用法:
  node scripts/screenshots/production-shot.mjs \\
    --routes <r1,r2,r3> \\
    --base-url <http://localhost:3000> \\
    --change-id <change-id>

示例:
  node scripts/screenshots/production-shot.mjs \\
    --routes /zh/home,/zh/workspace,/zh/admin \\
    --base-url http://localhost:3000 \\
    --change-id qa-loop-closure-2026-08-18

输出:
  docs/evidence/<change-id>/<route>-<ISO>.png`);
}

// ============ Playwright 动态加载 ============

async function loadPlaywright() {
  try {
    const pw = await import('playwright');
    return pw;
  } catch (err) {
    console.error('❌ playwright 未安装,跑: npm i playwright');
    console.error('   或: pnpm add -D playwright');
    exit(1);
  }
}

// ============ 主流程 ============

async function main() {
  if (argv.includes('--help') || argv.includes('-h')) {
    printHelp();
    exit(0);
  }

  const args = parseArgs();
  if (args.routes.length === 0) {
    console.error('🛑 --routes 不能为空');
    printHelp();
    exit(1);
  }

  console.log(`=== fullstack4TraeV11 V11.8.7 production-shot ===`);
  console.log(`baseUrl: ${args.baseUrl}`);
  console.log(`routes: ${args.routes.length} (${args.routes.join(', ')})`);
  console.log(`changeId: ${args.changeId}`);
  console.log();

  const pw = await loadPlaywright();
  const browser = await pw.chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  const outDir = resolve(process.cwd(), 'docs/evidence', args.changeId);
  mkdirSync(outDir, { recursive: true });

  const results = [];
  const iso = new Date().toISOString().replace(/[:.]/g, '-');

  for (const route of args.routes) {
    const url = `${args.baseUrl}${route}`;
    const safeRoute = route.replace(/[^a-zA-Z0-9]/g, '_');
    const outFile = join(outDir, `${safeRoute}-${iso}.png`);
    try {
      const page = await context.newPage();
      await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      await page.screenshot({ path: outFile, fullPage: true });
      const title = await page.title().catch(() => '');
      await page.close();
      results.push({ route, status: 'PASS', file: outFile, title });
      console.log(`✅ ${route} → ${outFile}${title ? ` (${title})` : ''}`);
    } catch (err) {
      results.push({ route, status: 'FAIL', error: err.message });
      console.log(`🛑 ${route} → FAIL: ${err.message}`);
    }
  }

  await context.close();
  await browser.close();

  const passes = results.filter((r) => r.status === 'PASS').length;
  const fails = results.length - passes;
  console.log();
  console.log(`总结: ${passes}/${results.length} PASS, ${fails} FAIL`);
  if (fails === 0) exit(0);
  if (passes === 0) exit(1);
  exit(2); // 部分成功 → WARN
}

main().catch((err) => {
  console.error('🛑 production-shot fatal:', err);
  exit(1);
});