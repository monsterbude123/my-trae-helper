// src/bundle-helpers.mjs — bundle 的纯函数(被 bundle.mjs 和测试共享)
// 拆出来是为了让 _test_bundle_e2e.mjs 能直接复用核心逻辑,避免 mock 整个 @inquirer/prompts
import { existsSync, readdirSync, statSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import yaml from 'yaml';
import { scanSkills } from './scanner.mjs';
import { SKILL_MARKETS_DIR } from './utils.mjs';

/** 扫父包(有 skills/<sub>/SKILL.md 的) */
export function findBundles(rootDir = SKILL_MARKETS_DIR) {
  const all = scanSkills(rootDir);
  const bundles = [];
  for (const skill of all) {
    const skillsDir = join(skill.sourcePath, 'skills');
    if (!existsSync(skillsDir)) continue;
    const subSkills = listSubSkillDirs(skillsDir);
    if (subSkills.length === 0) continue;
    bundles.push({ dirName: skill.dirName, skill, subSkills });
  }
  return bundles;
}

export function listSubSkillDirs(skillsDir) {
  const result = [];
  for (const entry of readdirSync(skillsDir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const full = join(skillsDir, entry.name);
    try {
      if (!statSync(full).isDirectory()) continue;
    } catch { continue; }
    const skillMd = join(full, 'SKILL.md');
    if (!existsSync(skillMd)) continue;
    const nested = existsSync(join(full, 'skills')) && statSafe(join(full, 'skills'))?.isDirectory();
    result.push({ name: entry.name, path: full, nested });
  }
  return result;
}

function statSafe(p) {
  try { return statSync(p); } catch { return null; }
}

export function parseSubSkillFrontmatter(skillMdPath) {
  try {
    const content = readFileSync(skillMdPath, 'utf-8');
    const m = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!m) return null;
    const fm = yaml.parse(m[1]) || {};
    return {
      name: fm.name || null,
      version: String(fm.version || '0.0.0').replace(/^["']|["']$/g, ''),
      description: String(fm.description || '').replace(/^["']|["']$/g, ''),
      userInvocable: fm['user-invocable'] === true,
      status: fm.status || null,
    };
  } catch { return null; }
}
