/**
 * Skill Install Control — 技能安装控制 Execution Skill
 *
 * 继承自 agent-dev-control-kit/skills/config-sync-control
 *
 * 控制对象: 安装/卸载/更新 技能到 Agent
 */

import { join, dirname, basename } from 'node:path';
import { existsSync, mkdirSync, cpSync, rmSync, lstatSync, symlinkSync, readFileSync, appendFileSync } from 'node:fs';
import { platform } from 'node:os';

const isWindows = platform() === 'win32';
const SKILL_MARKETS_DIR = join(process.cwd(), 'skill-markets');
const BACKUP_DIR = join(process.cwd(), 'logs', 'skill-install-backups');
const AUDIT_LOG = join(process.cwd(), 'logs', 'skill-market-audit.jsonl');

/**
 * CP1: 依赖验证
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} opts.agentName
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

  // CP1.5: DEPRECATED 拦截（2026-08-14 聚合归档）
  // SKILL.md frontmatter 含 `status: deprecated` + `redirect_to` → BLOCK 并指向新 skill
  if (meta.status === 'deprecated') {
    result.passed = false;
    result.missing.push(
      `DEPRECATED: ${skillName} 已归档，请改用 \`${meta.redirect_to || 'unknown'}\``
    );
    return result;
  }

  if (!meta.requires) return result;

  if (meta.requires.skills) {
    const hardDeps = Array.isArray(meta.requires.skills) ? meta.requires.skills : [meta.requires.skills];

    for (const dep of hardDeps) {
      if (!await checkInstalled({ skillName: dep, agentName })) {
        result.passed = false;
        result.missing.push(dep);
      }
    }
  }

  if (meta.requires.optional) {
    const optionalDeps = Array.isArray(meta.requires.optional) ? meta.requires.optional : [meta.requires.optional];

    for (const dep of optionalDeps) {
      if (!await checkInstalled({ skillName: dep, agentName })) {
        result.missingOptional.push(dep);
        result.impacts.push(getDowngradeImpact(dep));
      }
    }
  }

  return result;
}

/**
 * CP2: 冲突检查
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} opts.agentName
 * @param {string} opts.agentSkillsDir
 * @returns {{installed: boolean, version?: string}}
 */
export function checkInstalled({ skillName, agentName, agentSkillsDir }) {
  const targetDir = agentSkillsDir || getDefaultSkillsDir(agentName);
  const target = join(targetDir, skillName);
  const st = safeLstat(target);

  if (!st) return { installed: false };

  if (st.isSymbolicLink()) {
    return { installed: true, version: 'symlink' };
  }

  const skillMd = join(target, 'SKILL.md');
  if (existsSync(skillMd)) {
    const content = readFileSync(skillMd, 'utf-8');
    const meta = parseYAMLFrontmatter(content);
    return { installed: true, version: meta.version || 'unknown' };
  }

  return { installed: true, version: 'unknown' };
}

/**
 * CP3: 备份当前
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} opts.agentName
 * @param {string} opts.agentSkillsDir
 * @param {number} opts.timestamp
 * @returns {string} 备份路径
 */
export function backupInstalled({ skillName, agentName, agentSkillsDir, timestamp }) {
  const targetDir = agentSkillsDir || getDefaultSkillsDir(agentName);
  const source = join(targetDir, skillName);

  if (!existsSync(source)) {
    return null;
  }

  mkdirSync(BACKUP_DIR, { recursive: true });
  const backupPath = join(BACKUP_DIR, `${agentName}_${skillName}_${timestamp}`);

  cpSync(source, backupPath, { recursive: true });

  return backupPath;
}

/**
 * CP4: 执行安装
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} opts.agentName
 * @param {string} opts.agentSkillsDir
 * @param {'symlink'|'copy'} [opts.method='symlink']
 * @returns {string} 安装路径
 */
export function executeInstall({ skillName, agentName, agentSkillsDir, method = 'symlink' }) {
  const sourcePath = join(SKILL_MARKETS_DIR, skillName);
  const targetDir = agentSkillsDir || getDefaultSkillsDir(agentName);
  const target = join(targetDir, skillName);

  if (!existsSync(sourcePath)) {
    throw new Error(`技能不存在: ${skillName}`);
  }

  if (!existsSync(targetDir)) {
    mkdirSync(targetDir, { recursive: true });
  }

  if (existsSync(target) || safeLstat(target)) {
    rmSync(target, { recursive: true, force: true });
  }

  if (method === 'symlink') {
    if (isWindows) {
      symlinkSync(sourcePath, target, 'junction');
    } else {
      symlinkSync(sourcePath, target, 'dir');
    }
  } else if (method === 'copy') {
    cpSync(sourcePath, target, { recursive: true });
  } else {
    throw new Error(`未知安装方式: ${method}`);
  }

  return target;
}

/**
 * CP4: 执行卸载
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} opts.agentName
 * @param {string} opts.agentSkillsDir
 */
export function executeUninstall({ skillName, agentName, agentSkillsDir }) {
  const targetDir = agentSkillsDir || getDefaultSkillsDir(agentName);
  const target = join(targetDir, skillName);

  if (existsSync(target) || safeLstat(target)) {
    rmSync(target, { recursive: true, force: true });
  }
}

/**
 * CP5: 后置验证
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} opts.agentName
 * @param {string} opts.agentSkillsDir
 * @returns {{passed: boolean, errors: string[]}}
 */
export function verifyInstall({ skillName, agentName, agentSkillsDir }) {
  const result = {
    passed: true,
    errors: []
  };

  const targetDir = agentSkillsDir || getDefaultSkillsDir(agentName);
  const target = join(targetDir, skillName);

  if (!existsSync(target) && !safeLstat(target)) {
    result.passed = false;
    result.errors.push('安装目录未创建');
    return result;
  }

  const skillMd = join(target, 'SKILL.md');
  if (!existsSync(skillMd)) {
    result.passed = false;
    result.errors.push('SKILL.md 未安装');
    return result;
  }

  return result;
}

/**
 * CP6: 审计记录
 * @param {object} opts
 * @param {'install'|'uninstall'} opts.action
 * @param {string} opts.skill
 * @param {string} opts.agent
 * @param {string} [opts.result='success']
 * @param {number} [opts.duration_ms]
 * @param {object} [opts.details]
 */
export function auditLog({ action, skill, agent, result = 'success', duration_ms, details }) {
  const logDir = dirname(AUDIT_LOG);
  if (!existsSync(logDir)) {
    mkdirSync(logDir, { recursive: true });
  }

  const logEntry = {
    timestamp: new Date().toISOString(),
    action,
    skill,
    agent,
    user: process.env.USER || process.env.USERNAME || 'unknown',
    result,
    duration_ms,
    details
  };

  appendFileSync(AUDIT_LOG, JSON.stringify(logEntry) + '\n');
}

/**
 * 回滚安装
 * @param {object} opts
 * @param {string} opts.skillName
 * @param {string} opts.agentName
 * @param {string} opts.agentSkillsDir
 * @param {number} opts.timestamp
 */
export function rollbackInstall({ skillName, agentName, agentSkillsDir, timestamp }) {
  const backupPath = join(BACKUP_DIR, `${agentName}_${skillName}_${timestamp}`);
  const targetDir = agentSkillsDir || getDefaultSkillsDir(agentName);
  const target = join(targetDir, skillName);

  if (!existsSync(backupPath)) {
    throw new Error(`备份不存在: ${backupPath}`);
  }

  if (existsSync(target) || safeLstat(target)) {
    rmSync(target, { recursive: true, force: true });
  }

  cpSync(backupPath, target, { recursive: true });

  rmSync(backupPath, { recursive: true, force: true });
}

/**
 * Helper: 获取 Agent 默认技能目录
 */
function getDefaultSkillsDir(agentName) {
  const home = process.env.USERPROFILE || process.env.HOME;
  const agentMap = {
    'trae-cn': join(home, '.trae-cn', 'skills'),
    'trae': join(home, '.trae', 'skills'),
    'claude': join(home, '.claude', 'skills'),
    'cursor': join(home, '.cursor', 'skills')
  };
  return agentMap[agentName] || join(home, `.${agentName}`, 'skills');
}

/**
 * Helper: 安全 lstat
 */
function safeLstat(p) {
  try {
    return lstatSync(p);
  } catch {
    return null;
  }
}

/**
 * Helper: 解析 YAML frontmatter
 */
function parseYAMLFrontmatter(content) {
  // 兼容 CRLF（Windows）+ LF（Unix）两种换行（2026-08-14 修复）
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};

  const yaml = match[1];
  const meta = {};

  for (const line of yaml.split(/\r?\n/)) {
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
 * Helper: 降级影响
 */
function getDowngradeImpact(skillName) {
  const impactMap = {
    'acceptance-discipline': '验收门禁不可用',
    'gitnexus4Trae': '影响分析降级为 grep',
    'doc-map-manager': '文档索引无法自动更新',
    'ponytail4Trae': '代码可能过度工程'
  };
  return impactMap[skillName] || '功能可能受限';
}