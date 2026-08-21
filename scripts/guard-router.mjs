#!/usr/bin/env node
/**
 * scripts/guard-router.mjs — 守卫路由器
 *
 * 设计目的（2026-08-14 §3 三层控制收紧方案 A）：
 *   按 skill 名从 registry/skills.yaml 取其注册的 guards,按序执行。
 *   每个 skill 必须有自己的 guard 注册（最简:指向上述 3 个共享脚本之一；
 *   长期:guard-smith 拆分到各自 scripts/<name>-guard.<ext>）。
 *
 * 用法：
 *   node scripts/guard-router.mjs <skill-name> [skill-name ...]   # 单或多 skill
 *   node scripts/guard-router.mjs --all                          # 全市场
 *
 * 退出码：
 *   0 = 所有 guard PASS
 *   1 = 任一 guard BLOCK / skill 未注册 / 脚本执行失败
 */

import { spawn, execFileSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { join, resolve, dirname, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { platform } from 'node:os';
import { parse as parseYaml } from 'yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..');

const REGISTRY = join(REPO_ROOT, 'registry', 'skills.yaml');
const SKILL_MARKETS_DIR = join(REPO_ROOT, 'skill-markets');

// 2026-08-21 修复:复用 with-python.mjs 同款探测逻辑(env → PATH → Windows 典型位置),
// 避免 'python' ENOENT。直接 import 同目录 wrapper 而不是重复实现。
function findPython() {
  // 优先级 1: 环境变量(由 detect-python.sh / husky 注入)
  const envPy = process.env.MY_TRAE_HELPER_PY?.trim();
  if (envPy && existsSync(envPy)) return envPy;
  // 优先级 2: 当前 PATH 上的 python3 / python
  for (const name of ['python3', 'python', 'python3.exe', 'python.exe']) {
    try {
      const out = execFileSync(platform() === 'win32' ? 'where' : 'which', [name], {
        encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'],
      });
      const p = out.split(/\r?\n/)[0]?.trim();
      if (p && existsSync(p)) return p;
    } catch { /* not found */ }
  }
  // 优先级 3: Windows 典型位置(覆盖 npm spawn 时 PATH 只剩 system32)
  if (platform() === 'win32') {
    const home = process.env.USERPROFILE || process.env.HOME || '';
    const candidates = [
      home && `${home}/anaconda3/python.exe`,
      home && `${home}/miniconda3/python.exe`,
      home && `${home}/anaconda3/python3.exe`,
      home && `${home}/miniconda3/python3.exe`,
      'C:/ProgramData/anaconda3/python.exe',
      'C:/ProgramData/miniconda3/python.exe',
      'C:/ProgramData/anaconda3/python3.exe',
      'C:/ProgramData/miniconda3/python3.exe',
      'C:/Python313/python.exe',
      'C:/Python312/python.exe',
      'C:/Python311/python.exe',
      'C:/Python310/python.exe',
    ].filter(Boolean);
    for (const p of candidates) if (existsSync(p)) return p;
  }
  return null;
}
const PYTHON_BIN = findPython();
if (!PYTHON_BIN) {
  console.error('ERR: 找不到 python / python3 (请设置 MY_TRAE_HELPER_PY 或安装 Python)');
  process.exit(2);
}

if (!existsSync(REGISTRY)) {
  console.error(`❌ 注册表不存在: registry/skills.yaml`);
  process.exit(1);
}

const registry = parseYaml(readFileSync(REGISTRY, 'utf-8'));
const registered = new Map();
for (const entry of registry.skills || []) {
  if (entry && entry.skill) registered.set(entry.skill, entry);
}

/**
 * 运行单个 guard 脚本
 */
function runGuardScript(scriptPath, skillName) {
  return new Promise((resolve) => {
    const abs = isAbsolute(scriptPath) ? scriptPath : join(REPO_ROOT, scriptPath);
    if (!existsSync(abs)) {
      console.error(`❌ 守卫脚本不存在: ${scriptPath}`);
      return resolve({ code: 1, stdout: '', stderr: 'script not found' });
    }

    const ext = abs.split('.').pop();
    const cmd = ext === 'py' ? PYTHON_BIN : 'node';
    const args = ext === 'py'
      ? [abs, join(SKILL_MARKETS_DIR, skillName)]
      : [abs, skillName];

    console.log(`   ▶ ${cmd} ${args.join(' ')}`);
    const proc = spawn(cmd, args, { cwd: REPO_ROOT, env: process.env });
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', d => stdout += d.toString());
    proc.stderr.on('data', d => stderr += d.toString());
    proc.on('close', code => resolve({ code: code ?? 1, stdout, stderr }));
  });
}

/**
 * 处理单个 skill
 */
async function processSkill(skillName) {
  const entry = registered.get(skillName);
  if (!entry) {
    console.error(`❌ BLOCK — skill "${skillName}" 未在 registry/skills.yaml 注册`);
    console.error(`   → 调用 guard-smith agent 添加注册条目`);
    return { passed: false, errors: 1 };
  }

  console.log(`\n🔍 [${skillName}] (status: ${entry.status || '?'}, maintainer: ${entry.maintainer || '?'})`);
  if (!entry.guards || entry.guards.length === 0) {
    console.error(`❌ BLOCK — ${skillName} 注册表无 guards 条目`);
    return { passed: false, errors: 1 };
  }

  let totalErrors = 0;
  let totalWarnings = 0;

  for (const g of entry.guards) {
    console.log(`  📋 guard[${g.id}] category=${g.category} triggers=${(g.triggers || []).join('|')}`);
    const result = await runGuardScript(g.script, skillName);
    if (result.code === 0) {
      console.log(`     ✅ PASS`);
    } else if (result.code === 2) {
      console.log(`     ⚠️  WARN (exit 2)`);
      totalWarnings++;
    } else {
      console.log(`     ❌ FAIL (exit ${result.code})`);
      if (result.stderr) console.log(`     stderr: ${result.stderr.split('\n').slice(0, 5).join('\n           ')}`);
      if (result.stdout) console.log(`     stdout: ${result.stdout.split('\n').slice(0, 5).join('\n           ')}`);
      totalErrors++;
    }
  }

  return {
    passed: totalErrors === 0,
    errors: totalErrors,
    warnings: totalWarnings,
  };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('用法: node scripts/guard-router.mjs <skill-name> [...]');
    console.error('       node scripts/guard-router.mjs --all');
    process.exit(1);
  }

  let skillsToProcess = [];
  if (args.includes('--all')) {
    skillsToProcess = [...registered.keys()].sort();
    console.log(`🌐 全市场模式: ${skillsToProcess.length} 个注册 skill`);
  } else {
    skillsToProcess = args;
    console.log(`🎯 指定模式: ${skillsToProcess.length} 个 skill`);
  }

  let totalErrors = 0;
  let totalWarnings = 0;
  let totalPassed = 0;

  for (const skill of skillsToProcess) {
    const r = await processSkill(skill);
    if (r.passed) totalPassed++;
    totalErrors += r.errors || 0;
    totalWarnings += r.warnings || 0;
  }

  console.log('\n' + '='.repeat(60));
  console.log(`汇总: ✅ ${totalPassed} 通过  ❌ ${totalErrors} 错误  ⚠️  ${totalWarnings} 警告`);
  console.log('='.repeat(60));

  if (totalErrors > 0) {
    console.error('\n❌ guard-router BLOCK');
    process.exit(1);
  }
  console.log('\n✅ guard-router PASS');
  process.exit(0);
}

main().catch(err => {
  console.error(`❌ guard-router FATAL: ${err.message}`);
  console.error(err.stack);
  process.exit(1);
});