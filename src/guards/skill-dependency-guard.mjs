/**
 * Skill Dependency Guard — 技能依赖守卫
 *
 * 继承自 agent-dev-control-kit/skills/guard-control
 *
 * 检查维度: 硬依赖完整性 / 软依赖降级影响
 * 触发时机: pre-add (安装技能前) / pre-publish (发布前)
 */

import { join } from 'node:path';
import { existsSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';

const SKILL_MARKETS_DIR = join(process.cwd(), 'skill-markets');

/**
 * 检查依赖
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} [opts.agentName]
 * @returns {Promise<{passed: boolean, missing: string[], missingOptional: string[], impacts: string[]}>}
 */
export async function checkDependencies({ skillName, agentName }) {
  const result = {
    passed: true,
    missing: [],
    missingOptional: [],
    impacts: []
  };

  const skillPath = join(SKILL_MARKETS_DIR, skillName, 'SKILL.md');
  if (!existsSync(skillPath)) {
    result.passed = false;
    result.missing.push(`技能不存在: ${skillName}`);
    return result;
  }

  const content = readFileSync(skillPath, 'utf-8');
  const meta = parseYAMLFrontmatter(content);

  if (!meta.requires) return result;

  if (meta.requires.skills) {
    const hardDeps = Array.isArray(meta.requires.skills) ? meta.requires.skills : [meta.requires.skills];

    for (const dep of hardDeps) {
      if (agentName && !await checkInstalledForAgent({ skillName: dep, agentName })) {
        result.passed = false;
        result.missing.push(dep);
      } else if (!agentName && !checkInstalledGlobal(dep)) {
        result.passed = false;
        result.missing.push(dep);
      }
    }
  }

  if (meta.requires.optional) {
    const optionalDeps = Array.isArray(meta.requires.optional) ? meta.requires.optional : [meta.requires.optional];

    for (const dep of optionalDeps) {
      const isInstalled = agentName
        ? await checkInstalledForAgent({ skillName: dep, agentName })
        : checkInstalledGlobal(dep);

      if (!isInstalled) {
        result.missingOptional.push(dep);
        result.impacts.push(getDowngradeImpact(dep));
      }
    }
  }

  return result;
}

/**
 * 检查技能是否已安装（指定 Agent）
 */
async function checkInstalledForAgent({ skillName, agentName }) {
  const home = homedir();
  const agentMap = {
    'trae-cn': join(home, '.trae-cn', 'skills'),
    'trae': join(home, '.trae', 'skills'),
    'claude': join(home, '.claude', 'skills'),
    'cursor': join(home, '.cursor', 'skills')
  };

  const skillsDir = agentMap[agentName];
  if (!skillsDir) return false;

  const skillDir = join(skillsDir, skillName);
  return existsSync(skillDir);
}

/**
 * 检查技能是否已安装（全局，skill-markets）
 */
function checkInstalledGlobal(skillName) {
  const skillDir = join(SKILL_MARKETS_DIR, skillName);
  return existsSync(skillDir);
}

/**
 * 解析 YAML frontmatter
 */
function parseYAMLFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};

  const yaml = match[1];
  const meta = {};

  for (const line of yaml.split('\n')) {
    const [key, ...rest] = line.split(':');
    if (key && rest.length > 0) {
      const value = rest.join(':').trim();
      if (value.startsWith('[') && value.endsWith(']')) {
        meta[key.trim()] = value.slice(1, -1).split(',').map(s => s.trim());
      } else {
        meta[key.trim()] = value;
      }
    }
  }

  return meta;
}

/**
 * 降级影响
 */
function getDowngradeImpact(skillName) {
  const impactMap = {
    'acceptance-discipline': '验收门禁不可用',
    'gitnexus4Trae': '影响分析降级为 grep',
    'doc-map-manager': '文档索引无法自动更新',
    'ponytail4Trae': '代码可能过度工程',
    'test-experience': '测试编写质量降低',
    'e2e-module-audit': 'E2E 验收降级为手动',
    'test-partition-runner': '测试阻塞时无法自动分区定位'
  };
  return impactMap[skillName] || '功能可能受限';
}

/**
 * CLI 入口
 */
export async function runDependencyGuard(args) {
  const skillName = args[0];
  const agentName = args[1];

  if (!skillName) {
    console.error('用法: trae-skills dependency-guard <skill-name> [agent-name]');
    process.exit(1);
  }

  const result = await checkDependencies({ skillName, agentName });

  console.log(JSON.stringify(result, null, 2));

  if (!result.passed) {
    console.error(`\n❌ 缺失硬依赖: ${result.missing.join(', ')}`);
    console.log(`请先安装: trae-skills add ${result.missing.join(' ')}`);
    process.exit(1);
  }

  if (result.missingOptional.length > 0) {
    console.warn(`\n⚠️ 软依赖缺失: ${result.missingOptional.join(', ')}`);
    result.impacts.forEach((impact, i) => {
      console.warn(`  - ${result.missingOptional[i]}: ${impact}`);
    });
  }

  console.log('\n✅ 依赖检查通过');
  process.exit(0);
}