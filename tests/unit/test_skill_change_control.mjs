/**
 * Unit tests for skill-change-control.mjs (Execution Layer)
 *
 * 用 Node 内置 assert — 0 依赖。运行: node tests/unit/test_skill_change_control.mjs
 */

import assert from 'node:assert/strict';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { mkdtempSync, rmSync, existsSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..', '..');

const {
  classifyRisk,
  precheckSkill,
  executeCreate,
  executeDelete,
  verifyChange,
} = await import(pathToFileURL(join(REPO_ROOT, 'src', 'execution', 'skill-change-control.mjs')).href);

const SKILL_MARKETS_DIR = join(REPO_ROOT, 'skill-markets');
const ARCHIVE_DIR = join(REPO_ROOT, '_archived_skills');

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

console.log('━━━ skill-change-control.mjs ━━━');

// 1. classifyRisk
await test('classifyRisk: delete 操作 → HIGH', () => {
  assert.equal(classifyRisk({ operation: 'delete', target: 'any' }), 'HIGH');
});

await test('classifyRisk: create 操作 → LOW', () => {
  assert.equal(classifyRisk({ operation: 'create', target: 'any' }), 'LOW');
});

await test('classifyRisk: modify + scripts 变更（已发布 ≥1.0.0 技能）→ HIGH', () => {
  // 2026-08-15: coding-xinfa 实际 version=1.0.0,先命中已发布分支返回 HIGH;
  //             scripts/dependencies 降级只在 0.x 未发布阶段生效。
  assert.equal(
    classifyRisk({ operation: 'modify', target: 'coding-xinfa', changes: { scripts: true } }),
    'HIGH'
  );
});

await test('classifyRisk: 未知 operation → MEDIUM (保守)', () => {
  assert.equal(classifyRisk({ operation: 'unknown', target: 'any' }), 'MEDIUM');
});

// 2. precheckSkill
await test('precheckSkill: create + 合规名 + 不存在 → passed', async () => {
  const r = await precheckSkill({ skillName: 'fake-test-skill-zzz', operation: 'create' });
  assert.equal(r.passed, true);
  assert.deepEqual(r.errors, []);
});

await test('precheckSkill: create + 非法名 → 阻断', async () => {
  const r = await precheckSkill({ skillName: 'BadName', operation: 'create' });
  assert.equal(r.passed, false);
  assert.ok(r.errors.some(e => e.includes('不合规')));
});

await test('precheckSkill: create + 已存在 → 阻断', async () => {
  const r = await precheckSkill({ skillName: 'acceptance-discipline', operation: 'create' });
  assert.equal(r.passed, false);
  assert.ok(r.errors.some(e => e.includes('已存在')));
});

await test('precheckSkill: delete + 不存在 → 阻断', async () => {
  const r = await precheckSkill({ skillName: 'non-existent-skill', operation: 'delete' });
  assert.equal(r.passed, false);
  assert.ok(r.errors.some(e => e.includes('不存在')));
});

// 3. executeCreate + verifyChange
const tmpSkill = 'fake-test-create-zzz';
const skillPath = join(SKILL_MARKETS_DIR, tmpSkill);

await test('executeCreate: 创建目录 + SKILL.md + 子目录', () => {
  executeCreate({ name: tmpSkill, description: '测试' });
  assert.ok(existsSync(skillPath));
  assert.ok(existsSync(join(skillPath, 'SKILL.md')));
  assert.ok(existsSync(join(skillPath, 'references')));
  assert.ok(existsSync(join(skillPath, 'scripts')));

  const content = readFileSync(join(skillPath, 'SKILL.md'), 'utf-8');
  assert.ok(content.startsWith('---'));
  assert.ok(content.includes(tmpSkill));
});

await test('verifyChange: create 后验证 → passed', async () => {
  const r = await verifyChange({ skillName: tmpSkill, operation: 'create' });
  assert.equal(r.passed, true);
  assert.deepEqual(r.errors, []);
});

await test('verifyChange: 目录不存在 → failed', async () => {
  const r = await verifyChange({ skillName: 'non-existent-zzz', operation: 'create' });
  assert.equal(r.passed, false);
  assert.ok(r.errors.length > 0);
});

// 4. executeDelete (清理)
await test('executeDelete: 删除创建的技能', () => {
  executeDelete({ skillName: tmpSkill });
  assert.ok(!existsSync(skillPath));
});

await test('executeDelete: 删除不存在的技能 → throw', () => {
  assert.throws(() => executeDelete({ skillName: 'never-existed' }), /不存在/);
});

console.log(`\n━━━ 通过: ${passed} / 失败: ${failed} ━━━`);
process.exit(failed > 0 ? 1 : 0);