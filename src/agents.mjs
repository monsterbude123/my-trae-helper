/**
 * src/agents.mjs — supported agents mapping
 *
 * 每个 agent 记录:
 *   - name:          CLI 里用的 ID
 *   - displayName:   给人看的名字
 *   - skillsDir:     项目级 skills 目录（相对路径或绝对路径）
 *   - globalSkillsDir: 全局 skills 目录（绝对路径）
 *   - detectInstalled(): 检测本机是否已装
 */
import { existsSync } from 'node:fs';
import { homedir, platform } from 'node:os';
import { join } from 'node:path';

const home = homedir();
const isWindows = platform() === 'win32';

// 环境变量覆盖（参考 vercel-labs/skills 模式）
const claudeHome = process.env.CLAUDE_CONFIG_DIR?.trim() || join(home, '.claude');
const codexHome = process.env.CODEX_HOME?.trim() || join(home, '.codex');

/** @type {Record<string, {name: string, displayName: string, skillsDir: string, globalSkillsDir: string, detectInstalled: () => boolean}>} */
export const agents = {
  // ─── Trae 系列（项目核心） ───
  'trae-cn': {
    name: 'trae-cn',
    displayName: 'Trae CN',
    skillsDir: '.trae-cn/skills',
    globalSkillsDir: join(home, '.trae-cn/skills'),
    detectInstalled: () => existsSync(join(home, '.trae-cn')),
  },
  trae: {
    name: 'trae',
    displayName: 'Trae',
    skillsDir: '.trae/skills',
    globalSkillsDir: join(home, '.trae/skills'),
    detectInstalled: () => existsSync(join(home, '.trae')),
  },

  // ─── Universal（共享 ~/.agents/skills）───
  'claude-code': {
    name: 'claude-code',
    displayName: 'Claude Code',
    skillsDir: '.claude/skills',
    globalSkillsDir: join(claudeHome, 'skills'),
    detectInstalled: () => existsSync(claudeHome),
  },
  codex: {
    name: 'codex',
    displayName: 'Codex',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(codexHome, 'skills'),
    detectInstalled: () => existsSync(codexHome) || existsSync('/etc/codex'),
  },
  cursor: {
    name: 'cursor',
    displayName: 'Cursor',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(home, '.cursor/skills'),
    detectInstalled: () => existsSync(join(home, '.cursor')),
  },
  'gemini-cli': {
    name: 'gemini-cli',
    displayName: 'Gemini CLI',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(home, '.gemini/skills'),
    detectInstalled: () => existsSync(join(home, '.gemini')),
  },
  'github-copilot': {
    name: 'github-copilot',
    displayName: 'GitHub Copilot',
    skillsDir: '.github/skills',
    globalSkillsDir: join(home, '.copilot/skills'),
    detectInstalled: () => existsSync(join(home, '.copilot')),
  },
  opencode: {
    name: 'opencode',
    displayName: 'OpenCode',
    skillsDir: '.opencode/skills',
    globalSkillsDir: join(home, '.config/opencode/skills'),
    detectInstalled: () => existsSync(join(home, '.config/opencode')),
  },
  'kimi-code-cli': {
    name: 'kimi-code-cli',
    displayName: 'Kimi Code CLI',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(home, '.kimi-code/skills'),
    detectInstalled: () => existsSync(join(home, '.kimi-code')),
  },
  amp: {
    name: 'amp',
    displayName: 'Amp',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(home, '.config/agents/skills'),
    detectInstalled: () => existsSync(join(home, '.config/amp')),
  },
  openhands: {
    name: 'openhands',
    displayName: 'OpenHands',
    skillsDir: '.openhands/skills',
    globalSkillsDir: join(home, '.openhands/skills'),
    detectInstalled: () => existsSync(join(home, '.openhands')),
  },

  // ─── 独立目录 ───
  cline: {
    name: 'cline',
    displayName: 'Cline',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(home, '.agents/skills'),
    detectInstalled: () => existsSync(join(home, '.cline')),
  },
  windsurf: {
    name: 'windsurf',
    displayName: 'Windsurf',
    skillsDir: '.windsurf/skills',
    globalSkillsDir: join(home, '.windsurf/skills'),
    detectInstalled: () => existsSync(join(home, '.windsurf')),
  },
  continue: {
    name: 'continue',
    displayName: 'Continue',
    skillsDir: '.continue/skills',
    globalSkillsDir: join(home, '.continue/skills'),
    detectInstalled: () => existsSync(join(home, '.continue')),
  },
  roo: {
    name: 'roo',
    displayName: 'Roo Code',
    skillsDir: '.roo/skills',
    globalSkillsDir: join(home, '.roo/skills'),
    detectInstalled: () => existsSync(join(home, '.roo')),
  },
  'aider-desk': {
    name: 'aider-desk',
    displayName: 'AiderDesk',
    skillsDir: '.aider-desk/skills',
    globalSkillsDir: join(home, '.aider-desk/skills'),
    detectInstalled: () => existsSync(join(home, '.aider-desk')),
  },
  zed: {
    name: 'zed',
    displayName: 'Zed',
    skillsDir: '.zed/skills',
    globalSkillsDir: join(home, '.config/zed/skills'),
    detectInstalled: () => existsSync(join(home, '.config/zed')),
  },
  warp: {
    name: 'warp',
    displayName: 'Warp',
    skillsDir: '.warp/skills',
    globalSkillsDir: join(home, '.warp/skills'),
    detectInstalled: () => existsSync(join(home, '.warp')),
  },
  devin: {
    name: 'devin',
    displayName: 'Devin',
    skillsDir: '.devin/skills',
    globalSkillsDir: join(home, '.devin/skills'),
    detectInstalled: () => existsSync(join(home, '.devin')),
  },
  'qwen-code': {
    name: 'qwen-code',
    displayName: 'Qwen Code',
    skillsDir: '.qwen/skills',
    globalSkillsDir: join(home, '.qwen/skills'),
    detectInstalled: () => existsSync(join(home, '.qwen')),
  },
  'kiro-cli': {
    name: 'kiro-cli',
    displayName: 'Kiro CLI',
    skillsDir: '.kiro/skills',
    globalSkillsDir: join(home, '.kiro/skills'),
    detectInstalled: () => existsSync(join(home, '.kiro')),
  },
  augment: {
    name: 'augment',
    displayName: 'Augment',
    skillsDir: '.augment/skills',
    globalSkillsDir: join(home, '.augment/skills'),
    detectInstalled: () => existsSync(join(home, '.augment')),
  },
  'hermes-agent': {
    name: 'hermes-agent',
    displayName: 'Hermes Agent',
    skillsDir: '.hermes/skills',
    globalSkillsDir: join(home, '.hermes/skills'),
    detectInstalled: () => existsSync(join(home, '.hermes')),
  },
  antigravity: {
    name: 'antigravity',
    displayName: 'Antigravity',
    skillsDir: '.agents/skills',
    globalSkillsDir: join(home, '.gemini/antigravity/skills'),
    detectInstalled: () => existsSync(join(home, '.gemini/antigravity')),
  },
};

/**
 * 通过 name 拿 agent 定义
 */
export function getAgent(name) {
  return agents[name] || null;
}

/**
 * 检测本机已装的所有 agents
 */
export function detectInstalledAgents() {
  return Object.values(agents).filter((a) => {
    try {
      return a.detectInstalled();
    } catch {
      return false;
    }
  });
}

/**
 * 列出所有支持的 agents（用于 --help 之类）
 */
export function listAllAgents() {
  return Object.values(agents);
}
