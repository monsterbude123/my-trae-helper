/**
 * Unit tests for skill-dependency-guard.mjs (Guard Layer)
 *
 * 运行: node tests/unit/test_dependency_guard.mjs
 */

import assert from 'node:assert/strict';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..', '..');

const { checkDependencies } = await import(
  pathToFileURL(join(REPO_ROOT, 'src', 'guards', 'skill-dependency-guard.mjs')).href
);

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

console.log('━━━ skill-dependency-guard.mjs ━━━');

await test('checkDependencies: 不存在技能 → 阻断', async () => {
  const r = await checkDependencies({ skillName: 'never-existed-zzz' });
  assert.equal(r.passed, false);
});

await test('checkDependencies: trae-security-review (无硬依赖) → passed', async () => {
  const r = await checkDependencies({ skillName: 'trae-security-review' });
  assert.equal(r.passed, true);
});

await test('checkDependencies: agent-dev-control-kit (optional) → 检查软依赖降级', async () => {
  const r = await checkDependencies({ skillName: 'agent-dev-control-kit' });
  assert.equal(r.passed, true);
  assert.ok(Array.isArray(r.missingOptional));
});

console.log(`\n━━━ 通过: ${passed} / 失败: ${failed} ━━━`);
process.exit(failed > 0 ? 1 : 0);