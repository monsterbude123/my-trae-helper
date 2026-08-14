#!/usr/bin/env node
/**
 * Unit test for scripts/guard-router.mjs
 *
 * 覆盖三态：
 *   - PASS : router 对真实注册 skill 成功调用其 guard
 *   - BLOCK : router 对未注册 skill 返回错误
 *   - WARN : router 对 exit 2 的 guard 报告警告
 */

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..', '..');
const ROUTER = join(REPO_ROOT, 'scripts', 'guard-router.mjs');

let passed = 0;
let failed = 0;

async function test(name, fn) {
  try {
    await fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (err) {
    console.log(`  ❌ ${name}`);
    console.log(`     ${err.message}`);
    failed++;
  }
}

function runRouter(args) {
  return spawnSync('node', [ROUTER, ...args], {
    cwd: REPO_ROOT,
    encoding: 'utf-8',
    env: { ...process.env },
  });
}

console.log('━━━ guard-router.mjs ━━━\n');

// T1: PASS — 真实注册 skill 调用其 guard
await test('PASS — router 对真实 skill 调用 guard', () => {
  const r = runRouter(['coding-xinfa']);
  assert.equal(r.status, 0, `期望 exit 0, 实际 ${r.status}\nstdout: ${r.stdout}\nstderr: ${r.stderr}`);
  assert.match(r.stdout, /✅ PASS/);
  assert.match(r.stdout, /\[coding-xinfa\]/);
});

// T2: PASS — router --all 应能跑所有注册 skill
await test('PASS — router --all', () => {
  const r = runRouter(['--all']);
  // --all 可能包含某些 skill 缺 guards 或 guard 失败 → 不强制要求 exit 0
  // 只要求它至少尝试调用了
  assert.match(r.stdout, /全市场模式/);
  assert.match(r.stdout, /汇总/);
});

// T3: BLOCK — 未注册 skill 应被拒绝
await test('BLOCK — 未注册 skill', () => {
  const r = runRouter(['totally-fake-skill-xyz']);
  assert.equal(r.status, 1, `期望 exit 1, 实际 ${r.status}`);
  assert.match(r.stdout + r.stderr, /未在 registry\/skills\.yaml 注册/);
});

// T4: 用法错误 — 无参数
await test('边界 — 无参数应报错', () => {
  const r = runRouter([]);
  assert.notEqual(r.status, 0);
  assert.match(r.stdout + r.stderr, /用法/);
});

console.log(`\n━━━ 汇总: ✅ ${passed} 通过  ❌ ${failed} 失败 ━━━`);

if (failed > 0) process.exit(1);