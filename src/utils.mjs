/**
 * src/utils.mjs — shared helpers (paths, output, arg parsing)
 */
import { readFileSync, lstatSync, statSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// src/utils.mjs → repo root is one level up.
export const REPO_ROOT = resolve(__dirname, '..');
export const SKILL_MARKETS_DIR = join(REPO_ROOT, 'skill-markets');

/**
 * 读取根 package.json — 给 banner / version 用
 */
export function getPackageJson() {
  return JSON.parse(readFileSync(join(REPO_ROOT, 'package.json'), 'utf-8'));
}

// ─── 输出 ────────────────────────────────────────────────────────
// 简洁 ASCII 输出，不引第三方颜色库（保持 0 颜色依赖）
const C = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  gray: '\x1b[90m',
  bold: '\x1b[1m',
};
const noColor = process.env.NO_COLOR || !process.stdout.isTTY;

function c(color, text) {
  return noColor ? text : `${C[color]}${text}${C.reset}`;
}

export function printBanner() {
  const pkg = getPackageJson();
  console.log();
  console.log(c('cyan', `┌─ ${pkg.name} v${pkg.version}`));
  console.log(c('gray', '│  Trae IDE skills CLI'));
  console.log();
}

export function printHelp(commands) {
  console.log('Usage: ' + c('bold', 'trae-skills <command> [options]'));
  console.log();
  console.log('Commands:');
  for (const [name, entry] of Object.entries(commands)) {
    console.log(`  ${c('green', name.padEnd(10))} ${entry.desc}`);
  }
  console.log();
  console.log('Options:');
  console.log(`  ${c('yellow', '-g, --global')}         Install to user home (alias for --trae-cn)`);
  console.log(`  ${c('yellow', '--trae-cn')}            Install to ~/.trae-cn/skills/ explicitly (implies global)`);
  console.log(`  ${c('yellow', '-a, --agent <name>')}   Target agent (trae-cn, trae, claude-code, codex, cursor, ...)`);
  console.log(`  ${c('yellow', '-y, --yes')}            Skip all confirmation prompts`);
  console.log(`  ${c('yellow', '--copy')}               Copy files instead of symlink`);
  console.log(`  ${c('yellow', '-l, --list')}           List skills in marketplace without installing`);
  console.log();
  console.log('Examples:');
  console.log('  ' + c('gray', 'trae-skills add fullstack4TraeV11'));
  console.log('  ' + c('gray', 'trae-skills add fullstack4TraeV11 -a trae-cn -a claude-code'));
  console.log('  ' + c('gray', 'trae-skills add fullstack4TraeV11 -g -y'));
  console.log('  ' + c('gray', 'trae-skills list -g'));
  console.log('  ' + c('gray', 'trae-skills remove fullstack4TraeV11'));
}

export function printError(msg) {
  console.error(c('red', `✗ ${msg}`));
}

export function printWarn(msg) {
  console.warn(c('yellow', `! ${msg}`));
}

export function printSuccess(msg) {
  console.log(c('green', `✓ ${msg}`));
}

export function printInfo(msg) {
  console.log(c('blue', `ℹ ${msg}`));
}

// ─── 参数解析 ────────────────────────────────────────────────────
/**
 * 解析命令行参数
 * 输入: ['fullstack4TraeV11', '-g', '-a', 'trae-cn', '-a', 'claude-code', '--copy']
 * 输出: { _: ['fullstack4TraeV11'], flags: { g: true, a: ['trae-cn', 'claude-code'], copy: true } }
 */
export function parseArgs(args) {
  const opts = { _: [], flags: {} };
  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const eq = arg.indexOf('=');
      if (eq !== -1) {
        const key = arg.slice(2, eq);
        const value = arg.slice(eq + 1);
        addFlag(opts.flags, key, value);
        i += 1;
      } else {
        const key = arg.slice(2);
        const next = args[i + 1];
        if (next !== undefined && !next.startsWith('-')) {
          addFlag(opts.flags, key, next);
          i += 2;
        } else {
          addFlag(opts.flags, key, true);
          i += 1;
        }
      }
    } else if (arg.startsWith('-') && arg.length > 1) {
      const key = arg.slice(1);
      const next = args[i + 1];
      if (next !== undefined && !next.startsWith('-')) {
        addFlag(opts.flags, key, next);
        i += 2;
      } else {
        addFlag(opts.flags, key, true);
        i += 1;
      }
    } else {
      opts._.push(arg);
      i += 1;
    }
  }
  return opts;
}

function addFlag(flags, key, value) {
  if (flags[key] === undefined) {
    flags[key] = value;
  } else if (Array.isArray(flags[key])) {
    flags[key].push(value);
  } else {
    flags[key] = [flags[key], value];
  }
}

// ─── 路径辅助 ────────────────────────────────────────────────────
/**
 * 解析 agent 目标目录
 * - .claude/skills  → 相对 cwd（项目级）
 * - ~/.claude/skills → 绝对路径（全局）
 */
export function resolveTargetDir(skillsDir, isGlobal) {
  if (skillsDir.startsWith('~')) {
    return skillsDir.replace('~', process.env.HOME || process.env.USERPROFILE || '');
  }
  if (skillsDir.startsWith('.')) {
    return isGlobal ? null : resolve(process.cwd(), skillsDir);
  }
  // 绝对路径
  return skillsDir;
}

/**
 * 列出已安装 skills（在某个目录下）
 * 注意: Windows junction 在 lstat 下报 isDirectory()=false,必须用 statSync 跟随
 *       (见 trap-instructions.yaml 7 月新增 junction 模式)
 */
export function listDirSkills(dir) {
  if (!dir) return [];
  try {
    return readdirSync(dir, { withFileTypes: true })
      .filter((e) => {
        if (!e.isDirectory() && !e.isSymbolicLink()) return false;
        try {
          // 用 statSync 跟随 reparse point(junction / symlink to dir)
          return statSync(join(dir, e.name)).isDirectory();
        } catch {
          return false;
        }
      })
      .map((e) => e.name);
  } catch {
    return [];
  }
}
