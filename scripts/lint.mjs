#!/usr/bin/env node
/**
 * lint.mjs — 扫描所有 .mjs 文件做语法检查
 *
 * 排除:
 *   - node_modules/
 *   - skill-markets/  (技能库,各自维护)
 *   - examples/, docs/, examples/, tests/  (测试文件)
 *   - logs/, auto_reports/, .publish/  (临时产物)
 *
 * 运行: node scripts/lint.mjs
 */

import { execSync } from 'node:child_process';
import { readdirSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';

const ROOT = process.cwd();
const EXCLUDE_DIRS = new Set([
  'node_modules', 'skill-markets', 'example', 'examples', 'docs', 'logs',
  'auto_reports', '.publish', '.git', '.husky', '.github',
  'tests'  // 测试文件单独跑 test:unit
]);

const EXCLUDE_FILES = new Set([
  'src/utils.mjs',  // utils 已有,但 src/index.js 等已删
]);

let allFiles = [];

function walk(dir) {
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const entry of entries) {
    if (EXCLUDE_DIRS.has(entry)) continue;
    const full = join(dir, entry);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      walk(full);
    } else if (st.isFile() && entry.endsWith('.mjs')) {
      const rel = full.slice(ROOT.length + 1).replace(/\\/g, '/');
      if (!EXCLUDE_FILES.has(rel)) {
        allFiles.push(full);
      }
    }
  }
}

walk(ROOT);

if (allFiles.length === 0) {
  console.log('✅ No .mjs files to lint');
  process.exit(0);
}

console.log(`🔍 Lint ${allFiles.length} 个 .mjs 文件...\n`);

let failed = 0;
for (const file of allFiles) {
  const rel = file.slice(ROOT.length + 1).replace(/\\/g, '/');
  try {
    execSync(`node --check "${file}"`, { stdio: 'pipe' });
    console.log(`  ✅ ${rel}`);
  } catch (err) {
    console.log(`  ❌ ${rel}`);
    console.log(`     ${err.stderr?.toString() || err.message}`);
    failed++;
  }
}

console.log('');
if (failed > 0) {
  console.error(`❌ Lint 失败: ${failed} 个文件`);
  process.exit(1);
}
console.log(`✅ Lint 通过: ${allFiles.length} 个文件`);