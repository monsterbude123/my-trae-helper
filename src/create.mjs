/**
 * src/create.mjs — trae-skills create <name>
 *
 * 流程: 风险判定 → 前置检查 → 备份 → 执行 → 验证 → 审计
 */

import { classifyRisk, precheckSkill, backupSkill, executeCreate, verifyChange } from './execution/skill-change-control.mjs';
import { printSuccess, printError, printInfo, printWarn } from './utils.mjs';
import { spawn } from 'node:child_process';
import { promisify } from 'node:util';

const execAsync = promisify(spawn);

export async function runCreate(args) {
  const name = args[0];
  const description = args[1] || '';
  const skipConfirm = args.includes('-y');

  if (!name) {
    printError('用法: trae-skills create <name> [description]');
    console.log('\n示例:');
    console.log('  trae-skills create my-new-skill "我的新技能"');
    process.exit(1);
  }

  printInfo(`🔨 创建技能: ${name}`);

  // CP1: 风险判定
  const risk = classifyRisk({ operation: 'create', target: name });
  printInfo(`风险等级: ${risk}`);

  // CP2: 前置检查（仅做命名冲突检查,不做结构检查）
  printInfo('🔍 执行前置检查...');

  const precheck = await precheckSkill({ skillName: name, operation: 'create' });
  if (!precheck.passed) {
    printError('前置检查失败:');
    precheck.errors.forEach(err => console.log(`  ❌ ${err}`));
    process.exit(1);
  }

  if (precheck.warnings.length > 0) {
    precheck.warnings.forEach(warn => printWarn(warn));
  }

  // CP3: 备份（LOW 风险可选）
  if (risk === 'HIGH' || risk === 'MEDIUM') {
    printInfo('📦 备份...');
    const timestamp = Date.now();
    try {
      const backupPath = backupSkill({ skillName: name, timestamp });
      printInfo(`已备份到: ${backupPath}`);
    } catch (err) {
      printWarn(`备份失败: ${err.message}`);
    }
  }

  // CP4: 执行变更
  printInfo('✍️ 创建目录和文件...');
  const skillPath = executeCreate({ name, description });

  // CP5: 后置验证（结构守卫 + 完整性检查）
  printInfo('✅ 验证技能...');

  const verification = await verifyChange({ skillName: name, operation: 'create' });
  if (!verification.passed) {
    printError('验证失败:');
    verification.errors.forEach(err => console.log(`  ❌ ${err}`));
    process.exit(1);
  }

  // 结构守卫（创建后验证）
  const structureGuard = await runGuard('scripts/skill-structure-guard.py', `skill-markets/${name}`);
  if (!structureGuard.passed) {
    printError('结构检查失败:');
    structureGuard.errors.forEach(err => console.log(`  ❌ ${err}`));
    printInfo('回滚...');
    process.exit(1);
  }

  if (structureGuard.warnings.length > 0) {
    structureGuard.warnings.forEach(warn => printWarn(warn));
  }

  // CP6: 审计记录
  // TODO: 实现审计日志

  printSuccess(`技能 ${name} 创建成功`);
  console.log('\n📖 下一步:');
  console.log(`  1. 编辑 skill-markets/${name}/SKILL.md`);
  console.log(`  2. 运行: trae-skills verify ${name}`);
  console.log(`  3. 更新 skill-markets/CAPABILITY-MAP.md`);
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
          const result = JSON.parse(stdout);
          resolve({
            passed: result.passed || result.status === 'PASS',
            errors: result.errors || [],
            warnings: result.warnings || []
          });
        } catch {
          resolve({
            passed: false,
            errors: [stderr || stdout || '未知错误'],
            warnings: []
          });
        }
      }
    });
  });
}