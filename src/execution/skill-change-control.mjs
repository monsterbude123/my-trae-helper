/**
 * Skill Change Control — 技能变更控制 Execution Skill
 *
 * 继承自 agent-dev-control-kit/skills/data-change-control
 *
 * 控制对象: 新建/修改/删除 技能包
 * 风险分级: HIGH/MEDIUM/LOW
 */

import { join, dirname } from 'node:path';
import { existsSync, mkdirSync, cpSync, rmSync, writeFileSync, readFileSync } from 'node:fs';

const SKILL_MARKETS_DIR = join(process.cwd(), 'skill-markets');
const ARCHIVE_DIR = join(process.cwd(), '_archived_skills');

/**
 * CP1: 风险判定
 * @param {object} opts
 * @param {'create'|'modify'|'delete'} opts.operation
 * @param {string} opts.target — 技能名
 * @param {object} [opts.changes] — 变更详情（modify 时）
 * @returns {'HIGH'|'MEDIUM'|'LOW'}
 */
export function classifyRisk({ operation, target, changes }) {
  if (operation === 'delete') return 'HIGH';

  if (operation === 'modify') {
    const skillPath = join(SKILL_MARKETS_DIR, target);
    const skillMd = join(skillPath, 'SKILL.md');

    if (!existsSync(skillMd)) return 'LOW';

    const content = readFileSync(skillMd, 'utf-8');
    const meta = parseYAMLFrontmatter(content);

    if (meta.version && !meta.version.startsWith('0.')) {
      return 'HIGH';
    }

    if (changes?.scripts || changes?.dependencies) {
      return 'MEDIUM';
    }

    return 'LOW';
  }

  if (operation === 'create') return 'LOW';

  return 'MEDIUM';
}

/**
 * CP2: 前置检查（由 Guard Skills 执行）
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {'create'|'modify'|'delete'} opts.operation
 * @returns {Promise<{passed: boolean, errors: string[], warnings: string[]}>}
 */
export async function precheckSkill({ skillName, operation }) {
  const result = {
    passed: true,
    errors: [],
    warnings: []
  };

  const skillPath = join(SKILL_MARKETS_DIR, skillName);

  if (operation === 'create') {
    if (existsSync(skillPath)) {
      result.passed = false;
      result.errors.push(`技能已存在: ${skillName}`);
    }

    if (!skillName.match(/^[a-z][a-z0-9-]*$/)) {
      result.passed = false;
      result.errors.push(`技能名不合规: ${skillName}（应为 kebab-case）`);
    }
  }

  if (operation === 'modify' || operation === 'delete') {
    if (!existsSync(skillPath)) {
      result.passed = false;
      result.errors.push(`技能不存在: ${skillName}`);
    }

    const skillMd = join(skillPath, 'SKILL.md');
    if (!existsSync(skillMd)) {
      result.warnings.push(`技能缺少 SKILL.md: ${skillName}`);
    }
  }

  return result;
}

/**
 * CP3: 备份
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {number} opts.timestamp
 * @returns {string} 备份路径
 */
export function backupSkill({ skillName, timestamp }) {
  const skillPath = join(SKILL_MARKETS_DIR, skillName);

  if (!existsSync(skillPath)) {
    throw new Error(`技能不存在: ${skillName}`);
  }

  const archiveDir = join(ARCHIVE_DIR, `${skillName}_${timestamp}`);
  mkdirSync(dirname(archiveDir), { recursive: true });

  cpSync(skillPath, archiveDir, { recursive: true });

  return archiveDir;
}

/**
 * CP4: 执行变更 — 新建
 * @param {object} opts
 * @param {string} opts.name
 * @param {string} [opts.description]
 * @param {string} [opts.version='0.1.0']
 */
export function executeCreate({ name, description = '', version = '0.1.0' }) {
  const skillPath = join(SKILL_MARKETS_DIR, name);
  mkdirSync(skillPath, { recursive: true });

  const skillMdContent = `---
name: ${name}
description: ${description || `${name} 技能包`}
version: ${version}
---

# ${name}

> TODO: 技能描述

## 使用方式

\`\`\`bash
trae-skills add ${name} -a trae-cn
\`\`\`

## 铁律

1. TODO: 铁律 1
2. TODO: 铁律 2
`;

  writeFileSync(join(skillPath, 'SKILL.md'), skillMdContent);

  mkdirSync(join(skillPath, 'references'), { recursive: true });
  mkdirSync(join(skillPath, 'scripts'), { recursive: true });

  return skillPath;
}

/**
 * CP4: 执行变更 — 删除
 * @param {object} opts
 * @param {string} opts.skillName
 */
export function executeDelete({ skillName }) {
  const skillPath = join(SKILL_MARKETS_DIR, skillName);

  if (!existsSync(skillPath)) {
    throw new Error(`技能不存在: ${skillName}`);
  }

  rmSync(skillPath, { recursive: true, force: true });
}

/**
 * CP5: 后置验证
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {'create'|'modify'|'delete'} opts.operation
 * @returns {Promise<{passed: boolean, errors: string[]}>}
 */
export async function verifyChange({ skillName, operation }) {
  const result = {
    passed: true,
    errors: []
  };

  const skillPath = join(SKILL_MARKETS_DIR, skillName);

  if (operation === 'create') {
    if (!existsSync(skillPath)) {
      result.passed = false;
      result.errors.push('技能目录未创建');
      return result;
    }

    const skillMd = join(skillPath, 'SKILL.md');
    if (!existsSync(skillMd)) {
      result.passed = false;
      result.errors.push('SKILL.md 未创建');
      return result;
    }

    const content = readFileSync(skillMd, 'utf-8');
    if (!content.startsWith('---')) {
      result.passed = false;
      result.errors.push('SKILL.md 缺少 YAML frontmatter');
    }
  }

  if (operation === 'delete') {
    if (existsSync(skillPath)) {
      result.passed = false;
      result.errors.push('技能目录未删除');
    }
  }

  return result;
}

/**
 * CP6: 回滚
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {number} opts.timestamp
 */
export function rollbackSkill({ skillName, timestamp }) {
  const archiveDir = join(ARCHIVE_DIR, `${skillName}_${timestamp}`);
  const skillPath = join(SKILL_MARKETS_DIR, skillName);

  if (!existsSync(archiveDir)) {
    throw new Error(`备份不存在: ${archiveDir}`);
  }

  if (existsSync(skillPath)) {
    rmSync(skillPath, { recursive: true, force: true });
  }

  cpSync(archiveDir, skillPath, { recursive: true });

  rmSync(archiveDir, { recursive: true, force: true });
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
    const [key, value] = line.split(':').map(s => s.trim());
    if (key && value) {
      meta[key] = value;
    }
  }

  return meta;
}