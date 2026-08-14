#!/usr/bin/env node
// scripts/test-manifest.mjs
// 包装器:把 intent-classifier.mjs 的输出喂给 manifest-assert.py
// 解决 npm 脚本里管道 + JSON 引号转义的跨平台噩梦
//
// 用法:npm run test:manifest
//
// 退出码透传 manifest-assert.py 的退出码(0=PASS, 2=BLOCK)

import { execFileSync } from 'node:child_process';

const PROJECT_ROOT = process.cwd();

function run(cmd, args, opts = {}) {
  try {
    return { ok: true, stdout: execFileSync(cmd, args, { encoding: 'utf8', ...opts }) };
  } catch (e) {
    return { ok: false, stdout: (e.stdout || ''), stderr: (e.stderr || ''), code: e.status ?? 1 };
  }
}

// 1. 收集 intents
const intentsRes = run('node', ['scripts/intent-classifier.mjs', '--staged'], { cwd: PROJECT_ROOT });
if (!intentsRes.ok) {
  console.error('[test-manifest] intent-classifier 失败:');
  console.error(intentsRes.stderr);
  process.exit(3);
}
const intentsJson = intentsRes.stdout.trim();
if (!intentsJson) {
  console.log('[test-manifest] 无意图输出,跳过');
  process.exit(0);
}

// 2. 喂给 manifest-assert.py
const assertRes = run('python', [
  'scripts/manifest-assert.py',
  '--manifest', 'skill-markets/MANIFEST.yaml',
  '--intents', intentsJson,
], { cwd: PROJECT_ROOT, stdio: 'inherit' });

if (assertRes.ok) {
  console.log(assertRes.stdout);
  process.exit(0);
} else {
  process.exit(assertRes.code ?? 2);
}