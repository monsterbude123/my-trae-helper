#!/usr/bin/env node
/**
 * cpcc-self-check.mjs — common-project-coding-conf 自检脚本
 *
 * 6 项健康检查：
 *   1. 关键 skill 是否安装
 *   2. description 是否含触发词
 *   3. gitnexus MCP 探活（可选 — 不阻断）
 *   4. gitnexus 索引新鲜度（可选）
 *   5. 项目 rules 入口 forge 状态
 *   6. 市场 skill description 健康度扫描
 *
 * 用法：
 *   node cpcc-self-check.mjs              # 完整检查
 *   node cpcc-self-check.mjs --quick      # 只跑关键 3 项
 *   node cpcc-self-check.mjs --json       # JSON 输出
 *   node cpcc-self-check.mjs --cwd <dir>  # 指定项目根
 *
 * 输出：人类可读报告 + 退出码（0=PASS，1=FAIL）
 */
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

// 配置
const REQUIRED_SKILLS_BASE = [
  'coding-xinfa',
  'goal-mode',
  'fullstack4traev11',
  'gitnexus4Trae',
  'acceptance-discipline',
  'trae-security-review',
];
const SELF_SKILL = 'common-project-coding-conf';

const TRIGGER_PATTERN = /(触发|触发词|触发场景|when to use|加载时机|use when)/i;

const SKILLS_ROOT_CANDIDATES = [
  path.join(process.env.USERPROFILE || process.env.HOME || '', '.trae-cn', 'skills'),
  path.join(process.env.HOME || '', '.trae-cn', 'skills'),
  path.join(process.env.HOME || '', '.agents', 'skills'),
];

const RESULTS = {
  fail: 0,
  warn: 0,
  pass: 0,
  checks: [],
};

function pass(id, msg) {
  RESULTS.pass++;
  RESULTS.checks.push({ id, status: 'PASS', msg });
  return '✅';
}

function warn(id, msg) {
  RESULTS.warn++;
  RESULTS.checks.push({ id, status: 'WARN', msg });
  return '⚠️ ';
}

function fail(id, msg) {
  RESULTS.fail++;
  RESULTS.checks.push({ id, status: 'FAIL', msg });
  return '🛑';
}

function resolveSkillsRoot() {
  for (const candidate of SKILLS_ROOT_CANDIDATES) {
    if (fs.existsSync(candidate)) return candidate;
  }
  return null;
}

function checkSkillInstalled(skillsRoot, skillName) {
  if (!skillsRoot) {
    return warn('skill_installed', `无法定位 skills 根目录（尝试: ${SKILLS_ROOT_CANDIDATES.join(', ')}）`);
  }
  const skillPath = path.join(skillsRoot, skillName);
  if (fs.existsSync(skillPath)) {
    return pass(`skill_installed:${skillName}`, `${skillName} installed`);
  }
  return fail(`skill_installed:${skillName}`, `${skillName} 未安装（期望在 ${skillPath}）`);
}

/**
 * 提取 SKILL.md frontmatter 的 description 字段（2026-08-19 修复）
 *
 * 旧实现有 bug：用单行正则 `^description:\s*(.+?)(?=\n[a-z\-]+:|$)` 匹配首个 description 字段，
 *   - 对含重复 description 字段（如 fullstack4TraeV11 行 4 + 行 12）的 frontmatter,
 *     只取第一行(行 4)误报"无触发词",而 YAML 解析应取最后一条
 *   - 对多行 description 格式截断
 *
 * 新实现：扫描 frontmatter 段,取最后一个 description 字段(同 yaml.safe_load 语义,
 * 重复键时取最后一条)。只处理单行 description(本仓库 skill 实际格式)。
 * 块标量/多行用 compact 形式,不展开。
 */
function extractDescription(content) {
  // 1. 提取 --- 包裹的 frontmatter 段
  const m = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!m) return null;
  const fmBody = m[1];

  // 2. 扫描 frontmatter 找最后一个 description 字段(单行格式)
  const lineMatches = [...fmBody.matchAll(/^description:\s*(.+?)\s*$/gm)];
  if (lineMatches.length === 0) return null;
  const last = lineMatches[lineMatches.length - 1][1];
  // 去引号
  return last.replace(/^["']|["']$/g, '').trim();
}

function checkDescriptionTriggers(skillsRoot, skillName) {
  if (!skillsRoot) return warn(`desc_trigger:${skillName}`, 'skills 根目录不可用，跳过');
  const skillMd = path.join(skillsRoot, skillName, 'SKILL.md');
  if (!fs.existsSync(skillMd)) {
    return warn(`desc_trigger:${skillName}`, `${skillName}/SKILL.md 不存在，跳过`);
  }
  const content = fs.readFileSync(skillMd, 'utf8');
  const desc = extractDescription(content);
  if (!desc) {
    return warn(`desc_trigger:${skillName}`, `${skillName} description 字段缺失（TRAE 不会自动加载）`);
  }
  if (!TRIGGER_PATTERN.test(desc)) {
    return warn(`desc_trigger:${skillName}`, `${skillName} description 无触发词（建议加"触发词/触发场景/use when"）`);
  }
  return pass(`desc_trigger:${skillName}`, `${skillName} description 含触发词`);
}

async function checkGitnexusMCP() {
  // MCP 探活：通过 stdin 试探调用 list_repos（不依赖全局 MCP SDK）
  // 实现简化：探测环境变量或 cli 是否存在
  const cliAvailable = await checkCli('npx gitnexus --version');
  if (!cliAvailable) {
    return warn('gitnexus_mcp', 'gitnexus CLI 不可用（npx gitnexus --version 失败）');
  }
  return pass('gitnexus_mcp', 'gitnexus CLI 可用');
}

async function checkCli(cmd) {
  try {
    const { execSync } = await import('node:child_process');
    execSync(cmd, { stdio: 'ignore', timeout: 10000 });
    return true;
  } catch {
    return false;
  }
}

function checkGitnexusIndex(cwd) {
  const idxPath = path.join(cwd, '.gitnexus');
  if (!fs.existsSync(idxPath)) {
    return warn('gitnexus_index', `.gitnexus/ 目录不存在（未跑过 analyze）`);
  }
  const stat = fs.statSync(idxPath);
  const ageDays = (Date.now() - stat.mtimeMs) / (1000 * 60 * 60 * 24);
  if (ageDays > 7) {
    return warn('gitnexus_index', `.gitnexus/ last update ${Math.round(ageDays)} days ago（建议重跑 npx gitnexus analyze）`);
  }
  return pass('gitnexus_index', `.gitnexus/ fresh (${Math.round(ageDays)} days)`);
}

function checkProjectRulesForged(cwd) {
  const forgedPath = path.join(cwd, '.trae', 'skills', 'project_rules_skills', 'SKILL.md');
  if (fs.existsSync(forgedPath)) {
    return pass('project_rules_forged', `已 forge: ${forgedPath}`);
  }
  return warn('project_rules_forged', `未 forge，请跑 cpcc §3 Step 1（预期产物: ${forgedPath}）`);
}

function checkMarketDescriptions(cwd) {
  const marketsRoot = path.join(cwd, 'skill-markets');
  if (!fs.existsSync(marketsRoot)) {
    return warn('market_desc_audit', 'skill-markets 目录不存在');
  }
  const skillDirs = fs.readdirSync(marketsRoot, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
  const issues = [];
  for (const dir of skillDirs) {
    const skillMd = path.join(marketsRoot, dir, 'SKILL.md');
    if (!fs.existsSync(skillMd)) continue;
    const content = fs.readFileSync(skillMd, 'utf8');
    const desc = extractDescription(content);
    if (!desc) {
      issues.push({ skill: dir, issue: '缺 description 字段' });
    } else if (!TRIGGER_PATTERN.test(desc)) {
      issues.push({ skill: dir, issue: 'description 无触发词' });
    }
  }
  if (issues.length === 0) {
    return pass('market_desc_audit', `${skillDirs.length} skills 全部 description 完整`);
  }
  return warn('market_desc_audit',
    `${issues.length}/${skillDirs.length} skills description 不完整（首 5: ${issues.slice(0, 5).map(i => i.skill).join(', ')}）`);
}

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const quickMode = args.includes('--quick');
  const skipSelf = args.includes('--skip-self') || quickMode;
  const cwdIdx = args.indexOf('--cwd');
  const cwd = cwdIdx >= 0 ? args[cwdIdx + 1] : process.cwd();

  // 默认对守卫调用 (cpcc-self-check.mjs common-project-coding-conf) 也跳过 self install 检查
  // — 因为 git hook 上下文里 cpcc 自身尚未必安装。
  // 启用 full 自检(含 self): 显式传 --include-self。
  const includeSelf = args.includes('--include-self');
  const REQUIRED_SKILLS = (skipSelf || !includeSelf)
    ? REQUIRED_SKILLS_BASE
    : [...REQUIRED_SKILLS_BASE, SELF_SKILL];

  if (!jsonMode) {
    console.log(`[CPCC-SELFCHECK ${new Date().toISOString().replace('T', ' ').slice(0, 19)}]`);
    console.log('═'.repeat(50));
    console.log('');
  }

  const skillsRoot = resolveSkillsRoot();

  // Check 1: skill 安装
  if (!jsonMode) console.log('📋 Skill 安装检查');
  for (const skill of REQUIRED_SKILLS) {
    const icon = checkSkillInstalled(skillsRoot, skill);
    if (!jsonMode) console.log(`  ${icon} ${skill}`);
  }

  // Check 2: description 触发词
  if (!jsonMode) console.log('');
  if (!jsonMode) console.log('📝 Description 触发词检查');
  for (const skill of REQUIRED_SKILLS) {
    const icon = checkDescriptionTriggers(skillsRoot, skill);
    if (!jsonMode) console.log(`  ${icon} ${icon.includes('缺') || icon.includes('无') ? '' : ''}${skill}`);
  }

  // Check 3: gitnexus MCP
  if (!jsonMode) console.log('');
  if (!jsonMode) console.log('🔌 GitNexus MCP 探活');
  {
    const icon = await checkGitnexusMCP();
    if (!jsonMode) console.log(`  ${icon}`);
  }

  // Check 4: gitnexus 索引
  if (!jsonMode) console.log('');
  if (!jsonMode) console.log('🗂️  GitNexus 索引新鲜度');
  {
    const icon = checkGitnexusIndex(cwd);
    if (!jsonMode) console.log(`  ${icon}`);
  }

  // Check 5: 项目 rules forge
  if (!jsonMode) console.log('');
  if (!jsonMode) console.log('🏠 项目 Rules Forge 状态');
  {
    const icon = checkProjectRulesForged(cwd);
    if (!jsonMode) console.log(`  ${icon}`);
  }

  // Check 6: 市场 description 扫描
  if (!jsonMode) console.log('');
  if (!jsonMode) console.log('📊 市场 Description 健康度扫描');
  {
    const icon = checkMarketDescriptions(cwd);
    if (!jsonMode) console.log(`  ${icon}`);
  }

  if (!jsonMode) {
    console.log('');
    console.log('═'.repeat(50));
    console.log(`Summary: ${RESULTS.fail} FAIL, ${RESULTS.warn} WARN, ${RESULTS.pass} PASS`);
  } else {
    console.log(JSON.stringify(RESULTS, null, 2));
  }

  process.exit(RESULTS.fail > 0 ? 1 : 0);
}

main().catch(err => {
  console.error('CPCC-SELFCHECK fatal:', err);
  process.exit(1);
});