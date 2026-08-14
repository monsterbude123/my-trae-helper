/**
 * src/scanner.mjs — scan skill-markets/ for SKILL.md files
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, basename } from 'node:path';
import yaml from 'yaml';
import { SKILL_MARKETS_DIR } from './utils.mjs';

/**
 * 扫整个 skill-markets 目录，返回所有 skill 清单
 * @param {string} [rootDir]
 * @returns {Array<{name: string, dirName: string, version: string, description: string, requires: object, sourcePath: string}>}
 */
export function scanSkills(rootDir = SKILL_MARKETS_DIR) {
  if (!existsSync(rootDir)) {
    return [];
  }
  const skills = [];
  for (const entry of readdirSync(rootDir, { withFileTypes: true })) {
    // 跳过隐藏目录
    if (entry.name.startsWith('.')) continue;
    // 跳过明显不是目录的（文件/链接到外部）
    // 注意：Windows 上 dirent.isDirectory() 对某些特殊目录返回 false，
    // 需用 statSync 跟随链接再判（与 src/list.mjs 同样的处理）。
    try {
      const st = statSync(join(rootDir, entry.name));
      if (!st.isDirectory()) continue;
    } catch {
      continue;
    }
    const skillMd = join(rootDir, entry.name, 'SKILL.md');
    if (!existsSync(skillMd)) continue;
    try {
      const skill = parseSkill(skillMd, rootDir, entry.name);
      if (skill) skills.push(skill);
    } catch (err) {
      // 解析失败跳过，但继续扫
      if (process.env.DEBUG) console.error(`[scanner] skip ${entry.name}: ${err.message}`);
    }
  }
  return skills;
}

/**
 * 解析单个 SKILL.md
 */
function parseSkill(skillMdPath, rootDir, dirName) {
  const content = readFileSync(skillMdPath, 'utf-8');
  const fm = parseFrontmatter(content);
  return {
    name: fm.name || dirName,
    dirName,
    version: String(fm.version || '0.0.0').replace(/^["']|["']$/g, ''),
    description: String(fm.description || '').replace(/^["']|["']$/g, ''),
    status: fm.status || null,           // "deprecated" 时被 add.mjs 拦截
    redirectTo: fm.redirect_to || null,  // 重定向目标 skill 名
    requires: fm.requires || {},
    sourcePath: join(rootDir, dirName),
  };
}

/**
 * 解析 YAML frontmatter（只取 --- 之间的部分）
 */
function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  try {
    return yaml.parse(match[1]) || {};
  } catch {
    return {};
  }
}

/**
 * 找单个 skill（按 name 或 dirName 匹配，忽略大小写）
 */
export function findSkill(name, rootDir = SKILL_MARKETS_DIR) {
  const all = scanSkills(rootDir);
  const lower = String(name).toLowerCase();
  return all.find((s) => s.name.toLowerCase() === lower || s.dirName.toLowerCase() === lower) || null;
}
