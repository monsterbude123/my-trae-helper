/**
 * src/verify.mjs — trae-skills verify <name>
 *
 * 流程: 执行所有守卫检查
 */

import { printSuccess, printError, printInfo, printWarn } from './utils.mjs';
import { spawn } from 'node:child_process';
import { join } from 'node:path';

const SKILL_MARKETS_DIR = join(process.cwd(), 'skill-markets');

export async function runVerify(args) {
  const name = args[0];

  if (!name) {
    printError('用法: trae-skills verify <name>');
    console.log('\n示例:');
    console.log('  trae-skills verify my-skill');
    process.exit(1);
  }

  printInfo(`🔍 验证技能: ${name}`);

  const skillPath = join(SKILL_MARKETS_DIR, name);

  const results = {
    'security': { passed: false, errors: [], warnings: [] },
    'structure': { passed: false, errors: [], warnings: [] },
    'dependency': { passed: false, errors: [], warnings: [] },
    'capability': { passed: false, errors: [], warnings: [] }
  };

  // 1. 安全守卫
  printInfo('\n1️⃣ 执行安全守卫...');
  results.security = await runGuard('scripts/skill-security-guard.py', skillPath);

  // 2. 结构守卫
  printInfo('\n2️⃣ 执行结构守卫...');
  results.structure = await runGuard('scripts/skill-structure-guard.py', skillPath);

  // 3. 依赖守卫
  printInfo('\n3️⃣ 执行依赖守卫...');
  results.dependency = await runDependencyGuard(name);

  // 4. 能力守卫
  printInfo('\n4️⃣ 执行能力守卫...');
  results.capability = await runGuard('scripts/skill-capability-guard.py', skillPath);

  // 汇总结果
  console.log('\n' + '='.repeat(60));
  console.log('验证结果汇总:');
  console.log('='.repeat(60));

  let passed = 0;
  let failed = 0;
  let warned = 0;

  for (const [guard, result] of Object.entries(results)) {
    const errors = result.errors || [];
    const warnings = result.warnings || [];

    if (result.passed) {
      console.log(`  ✅ ${guard}`);
      passed++;
    } else {
      console.log(`  ❌ ${guard}`);
      failed++;

      errors.forEach(err => console.log(`      - ${err}`));
    }

    if (warnings.length > 0) {
      warned++;
      warnings.forEach(warn => console.log(`      ⚠️ ${warn}`));
    }
  }

  console.log('='.repeat(60));
  console.log(`\n结果: ${passed} 通过, ${failed} 失败, ${warned} 警告`);

  if (failed > 0) {
    printError('\n验证失败，请修复上述问题');
    process.exit(1);
  } else {
    printSuccess('\n验证通过');
    process.exit(0);
  }
}

/**
 * 执行守卫脚本
 */
async function runGuard(scriptPath, arg) {
  return new Promise((resolve) => {
    const proc = spawn('python', [scriptPath, arg], { shell: true });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      if (code === 0) {
        resolve({ passed: true, errors: [], warnings: [] });
      } else {
        try {
          // 尝试解析最后一个 JSON 对象（兼容多 JSON 输出）
          const jsonMatches = stdout.match(/\{[\s\S]*?\}/g);
          if (jsonMatches && jsonMatches.length > 0) {
            const lastJson = jsonMatches[jsonMatches.length - 1];
            const result = JSON.parse(lastJson);
            resolve({
              passed: result.passed === true,
              errors: result.errors || [],
              warnings: result.warnings || (result.missing_entries || [])
            });
            return;
          }
          resolve({
            passed: false,
            errors: [stderr || stdout || '未知错误'],
            warnings: []
          });
        } catch {
          resolve({
            passed: false,
            errors: [stderr || stdout || '解析失败'],
            warnings: []
          });
        }
      }
    });
  });
}

/**
 * 执行依赖守卫
 */
async function runDependencyGuard(skillName) {
  const { checkDependencies } = await import('./guards/skill-dependency-guard.mjs');
  return await checkDependencies({ skillName });
}