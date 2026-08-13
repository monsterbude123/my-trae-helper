#!/usr/bin/env node
/**
 * validate-config.mjs — Build 时验证 CLI 配置完整性
 *
 * 检查项:
 *   - package.json 必需字段 (name/version/bin/scripts)
 *   - bin/cli.mjs 可执行 (入口存在)
 *   - src/ 所有命令文件存在
 *   - .husky/ hooks 可执行
 *   - .github/workflows/ GitHub Actions 存在
 */

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { resolve, join } from 'node:path';

const ROOT = process.cwd();
let ok = true;

function check(label, condition) {
  console.log(`${condition ? '✅' : '❌'} ${label}`);
  return condition;
}

// 1. package.json
const pkgPath = resolve(ROOT, 'package.json');
if (existsSync(pkgPath)) {
  const pkg = JSON.parse(readFileSync(pkgPath, 'utf-8'));
  ok &= check('package.json has name', !!pkg.name);
  ok &= check('package.json has version', !!pkg.version);
  ok &= check('package.json has bin trae-skills', !!pkg.bin?.['trae-skills']);
  ok &= check('package.json has lint script', !!pkg.scripts?.lint);
  ok &= check('package.json has test:unit script', !!pkg.scripts?.['test:unit']);
  ok &= check('package.json has build script', !!pkg.scripts?.build);
} else {
  ok &= check('package.json exists', false);
}

// 2. CLI 入口
ok &= check('bin/cli.mjs exists', existsSync(resolve(ROOT, 'bin/cli.mjs')));

// 3. 所有命令文件
const requiredCommands = ['add', 'list', 'remove', 'update', 'init', 'create', 'verify'];
for (const cmd of requiredCommands) {
  ok &= check(`src/${cmd}.mjs exists`, existsSync(resolve(ROOT, `src/${cmd}.mjs`)));
}

// 4. 三层控制核心模块
const requiredCore = [
  'src/execution/skill-change-control.mjs',
  'src/execution/skill-install-control.mjs',
  'src/guards/skill-dependency-guard.mjs'
];
for (const f of requiredCore) {
  ok &= check(`${f} exists`, existsSync(resolve(ROOT, f)));
}

// 5. 守卫脚本
const requiredGuards = [
  'scripts/skill-security-guard.py',
  'scripts/skill-structure-guard.py',
  'scripts/skill-capability-guard.py'
];
for (const f of requiredGuards) {
  ok &= check(`${f} exists`, existsSync(resolve(ROOT, f)));
}

// 6. Git Hooks
ok &= check('.husky/pre-commit exists', existsSync(resolve(ROOT, '.husky/pre-commit')));
ok &= check('.husky/pre-push exists', existsSync(resolve(ROOT, '.husky/pre-push')));

// 7. GitHub Actions
ok &= check('.github/workflows/skill-market-gate.yml exists',
  existsSync(resolve(ROOT, '.github/workflows/skill-market-gate.yml')));

// 8. CAPABILITY-MAP.md + SECURITY-MAP.md
ok &= check('skill-markets/CAPABILITY-MAP.md exists',
  existsSync(resolve(ROOT, 'skill-markets/CAPABILITY-MAP.md')));
ok &= check('SECURITY-MAP.md exists', existsSync(resolve(ROOT, 'SECURITY-MAP.md')));

if (!ok) {
  console.error('\n❌ Validation FAILED');
  process.exit(1);
}
console.log('\n✅ Validation PASSED');
process.exit(0);