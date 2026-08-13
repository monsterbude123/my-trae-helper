/**
 * src/installer.mjs — install / uninstall via symlink or copy
 *
 * Windows 上默认用 junction 避免权限问题。
 * 所有破坏性操作支持 dryRun 预演(AGENTS.md §10 R-2 兜底)。
 */
import { symlinkSync, mkdirSync, existsSync, rmSync, cpSync, lstatSync } from 'node:fs';
import { join } from 'node:path';
import { platform } from 'node:os';

const isWindows = platform() === 'win32';

/**
 * 安装一个 skill
 * @param {object} opts
 * @param {string} opts.sourcePath  源 skill 目录
 * @param {string} opts.targetDir   目标父目录
 * @param {string} opts.skillName   skill 目录名（在 targetDir 下）
 * @param {'symlink'|'copy'} [opts.method]
 * @param {boolean} [opts.dryRun]   true = 只打印,不实际操作
 * @returns {string} 实际安装路径(非 dryRun) / 预演消息(dryRun)
 */
export function installSkill({ sourcePath, targetDir, skillName, method = 'symlink', dryRun = false }) {
  if (!existsSync(sourcePath)) {
    throw new Error(`源路径不存在: ${sourcePath}`);
  }

  if (!existsSync(targetDir)) {
    mkdirSync(targetDir, { recursive: true });
  }

  const target = join(targetDir, skillName);

  if (dryRun) {
    const existed = safeLstat(target);
    const action = existed ? `覆盖 (${existed.isSymbolicLink() ? 'symlink' : 'dir'})` : '新建';
    return `[DRY-RUN] install ${method}: ${target} ${action} (source: ${sourcePath})`;
  }

  // 已存在则先清理（兼容旧链接/旧目录）
  if (existsSync(target) || safeLstat(target)) {
    rmSync(target, { recursive: true, force: true });
  }

  if (method === 'symlink') {
    if (isWindows) {
      // Windows: junction 不需要开发者模式/管理员
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
 * 卸载一个 skill
 * @param {object} opts
 * @param {string} opts.targetDir
 * @param {string} opts.skillName
 * @param {boolean} [opts.dryRun]
 * @returns {boolean} 是否真的删了
 */
export function uninstallSkill({ targetDir, skillName, dryRun = false }) {
  const target = join(targetDir, skillName);
  const st = safeLstat(target);

  if (!st) {
    if (dryRun) return `[DRY-RUN] uninstall: skip (不存在) ${target}`;
    return false;
  }

  if (dryRun) {
    const kind = st.isSymbolicLink() ? 'symlink' : 'dir';
    return `[DRY-RUN] uninstall: would remove ${kind} ${target}`;
  }

  rmSync(target, { recursive: true, force: true });
  return true;
}

/**
 * 检查是否已装
 */
export function isInstalled({ targetDir, skillName }) {
  const target = join(targetDir, skillName);
  return safeLstat(target) !== null;
}

function safeLstat(p) {
  try {
    return lstatSync(p);
  } catch {
    return null;
  }
}
