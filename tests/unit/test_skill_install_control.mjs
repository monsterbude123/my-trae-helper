/**
 * Unit tests for skill-install-control.mjs (Execution Layer)
 *
 * 运行: node tests/unit/test_skill_install_control.mjs
 */

import assert from 'node:assert/strict';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { mkdtempSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..', '..');

const {
  checkDependencies,
  checkInstalled,
  executeInstall,
  executeUninstall,
  verifyInstall,
} = await import(pathToFileURL(join(REPO_ROOT, 'src', 'execution', 'skill-install-control.mjs')).href);

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

console.log('━━━ skill-install-control.mjs ━━━');

// 1. checkDependencies
await test('checkDependencies: 技能不存在 → 阻断', async () => {
  const r = await checkDependencies({ skillName: 'never-existed-zzz' });
  assert.equal(r.passed, false);
  assert.ok(r.missing.length > 0);
});

await test('checkDependencies: trae-security-review (无硬依赖) → passed', async () => {
  const r = await checkDependencies({ skillName: 'trae-security-review' });
  assert.equal(r.passed, true);
  assert.equal(r.missing.length, 0);
});

// 2. checkInstalled
await test('checkInstalled: 不存在的技能 → not installed', () => {
  const r = checkInstalled({ skillName: 'never-existed-zzz', agentName: 'trae-cn' });
  assert.equal(r.installed, false);
});

await test('checkInstalled: trae-cn 全局目录 → not installed (CI 环境)', () => {
  const r = checkInstalled({ skillName: 'trae-security-review', agentName: 'trae-cn' });
  assert.equal(r.installed, false);
});

// 3. executeInstall / executeUninstall (用临时目录)
const tmpDir = mkdtempSync(join(tmpdir(), 'skill-install-test-'));
const sourceSkill = 'trae-security-review';

await test('executeInstall: symlink 到临时目录 → 成功', () => {
  executeInstall({
    skillName: sourceSkill,
    agentName: 'trae-cn',
    agentSkillsDir: tmpDir,
    method: 'symlink'
  });
  assert.ok(existsSync(join(tmpDir, sourceSkill)));
});

await test('verifyInstall: 验证安装 → passed', () => {
  const r = verifyInstall({ skillName: sourceSkill, agentName: 'trae-cn', agentSkillsDir: tmpDir });
  assert.equal(r.passed, true);
});

await test('executeUninstall: 删除 symlink', () => {
  executeUninstall({ skillName: sourceSkill, agentName: 'trae-cn', agentSkillsDir: tmpDir });
  assert.ok(!existsSync(join(tmpDir, sourceSkill)));
});

// 清理
rmSync(tmpDir, { recursive: true, force: true });

await test('verifyInstall: 卸载后验证 → failed', () => {
  const r = verifyInstall({ skillName: sourceSkill, agentName: 'trae-cn', agentSkillsDir: tmpDir });
  assert.equal(r.passed, false);
});

await test('executeInstall: 未知 method → throw', () => {
  assert.throws(
    () => executeInstall({ skillName: sourceSkill, agentName: 'trae-cn', agentSkillsDir: tmpDir, method: 'unknown' }),
    /未知安装方式/
  );
});

console.log(`\n━━━ 通过: ${passed} / 失败: ${failed} ━━━`);
process.exit(failed > 0 ? 1 : 0);