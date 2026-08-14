/**
 * src/install-guards.mjs — install/update/uninstall 的三道闸
 *
 * 抽出来作为独立模块被 add/update/remove/bundle 四个命令复用。
 * 每道闸返回 { ok: boolean, severity: 'pass'|'warn'|'block', code, message, fix? }。
 *
 * 闸门清单(按执行顺序):
 *   1. deprecation-guard  — DEPRECATED + redirect_to 强制拦截
 *   2. version-guard      — 已装版本 vs marketplace 版本比对
 *   3. name-conflict-guard — 跨包同名 / 相似名 / 自覆盖检测
 *
 * 设计: 三道闸都是纯函数,接受显式入参,不读全局状态,便于单测。
 * 关联:
 *   - skill-bundle/SKILL.md (装载规范)
 *   - skill-acceptance 守卫 (结构层校验)
 */

import { readFileSync, readdirSync, statSync, lstatSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import yaml from 'yaml';

// ─── 1. Deprecation Guard ────────────────────────────────────────

/**
 * 检查是否应当被 DEPRECATED 拦截
 * @param {{name: string, status?: string, redirectTo?: string}} skill
 * @returns {{ok: boolean, severity: 'pass'|'block', code: string, message: string, fix?: string}}
 */
export function deprecationGuard(skill) {
  if (skill.status !== 'deprecated') {
    return { ok: true, severity: 'pass', code: 'DEP-001', message: 'not deprecated' };
  }
  const target = skill.redirectTo || 'unknown';
  return {
    ok: false,
    severity: 'block',
    code: 'DEP-002',
    message: `${skill.name} 已归档为 DEPRECATED → 重定向至 ${target}`,
    fix: `改用 ${target};如必须装兼容壳,加 --force-redirect`,
  };
}

// ─── 2. Version Guard ─────────────────────────────────────────────

/**
 * 比对已装版本 vs marketplace 版本
 * @param {string} versionInstalled — 已装版本号,无则 null
 * @param {string} versionAvailable — marketplace 版本号
 * @returns {{ok: boolean, severity: 'pass'|'warn'|'block', code, message, action: 'install'|'update'|'downgrade'|'equal'}}
 */
export function versionGuard(versionInstalled, versionAvailable) {
  if (!versionInstalled) {
    return {
      ok: true,
      severity: 'pass',
      code: 'VER-001',
      message: '未安装',
      action: 'install',
    };
  }
  const cmp = compareSemver(versionInstalled, versionAvailable);
  if (cmp === 0) {
    return {
      ok: true,
      severity: 'pass',
      code: 'VER-002',
      message: `已装 ${versionInstalled} = 最新 ${versionAvailable}`,
      action: 'equal',
    };
  }
  if (cmp < 0) {
    return {
      ok: true,
      severity: 'warn',
      code: 'VER-003',
      message: `已装 ${versionInstalled} < 最新 ${versionAvailable}`,
      action: 'update',
    };
  }
  return {
    ok: true,
    severity: 'warn',
    code: 'VER-004',
    message: `已装 ${versionInstalled} > marketplace ${versionAvailable} (本地回退?marketplace 待同步?)`,
    action: 'downgrade',
  };
}

/**
 * 简化 semver 比较: 支持 1.2.3 / 1.2.3-beta.1
 * 缺失字段补 0
 */
function compareSemver(a, b) {
  const [aMain, aPre] = String(a).split('-', 2);
  const [bMain, bPre] = String(b).split('-', 2);
  const aN = aMain.split('.').map((n) => parseInt(n, 10) || 0);
  const bN = bMain.split('.').map((n) => parseInt(n, 10) || 0);
  for (let i = 0; i < Math.max(aN.length, bN.length); i++) {
    const av = aN[i] ?? 0;
    const bv = bN[i] ?? 0;
    if (av !== bv) return av - bv;
  }
  // 相等的主版本号,带 pre-release 的 < 正式版
  if (aPre && !bPre) return -1;
  if (!aPre && bPre) return 1;
  if (aPre && bPre) return aPre.localeCompare(bPre);
  return 0;
}

// ─── 3. Name Conflict Guard ───────────────────────────────────────

/**
 * 检测三种命名冲突:
 *   A. self-overwrite   — 已装同名,准备覆盖(由 versionGuard 已处理,但 name 完全相同额外提示)
 *   B. cross-package    — 不同包但同名(frontmatter name 相同)
 *   C. similar-name     — 名字仅大小写 / 短横线差异(Linux 路径敏感场景)
 *
 * @param {{dirName: string, name: string}} skill           — 准备装的
 * @param {string} targetDir                                — 目标目录
 * @param {Array<{dirName: string, name: string}>} allMarketplace — 同次扫描的全部 marketplace skills
 * @returns {{ok: boolean, severity: 'pass'|'warn'|'block', conflicts: Array<{type, detail}>}}
 */
export function nameConflictGuard(skill, targetDir, allMarketplace = []) {
  const conflicts = [];

  // A. self-overwrite: 目标目录里同名
  if (existsSync(targetDir)) {
    const installed = listSubdirs(targetDir);
    if (installed.some((n) => n.toLowerCase() === skill.dirName.toLowerCase())) {
      // 已有同名 — 由 versionGuard 决策 update/skip,这里只 warn
      conflicts.push({
        type: 'self-overwrite',
        severity: 'warn',
        detail: `目标目录已存在 ${skill.dirName},将走 update 流程`,
      });
    }
  }

  // B. cross-package: 不同 dirName 但 frontmatter name 相同
  const sameName = allMarketplace.filter(
    (s) =>
      s.dirName !== skill.dirName &&
      s.name.toLowerCase() === skill.name.toLowerCase(),
  );
  if (sameName.length > 0) {
    conflicts.push({
      type: 'cross-package',
      severity: 'block',
      detail: `frontmatter name="${skill.name}" 在其他包中重复: ${sameName.map((s) => s.dirName).join(', ')}`,
    });
  }

  // C. similar-name: 同一目标目录中已装,名字仅大小写或短横线差异
  if (existsSync(targetDir)) {
    const norm = (n) => n.toLowerCase().replace(/[-_]/g, '');
    const skillNorm = norm(skill.dirName);
    const similar = listSubdirs(targetDir).filter(
      (n) => n !== skill.dirName && norm(n) === skillNorm,
    );
    if (similar.length > 0) {
      conflicts.push({
        type: 'similar-name',
        severity: 'warn',
        detail: `目标目录存在相似名(忽略大小写/短横线): ${similar.join(', ')} → 装载时 AI 可能混淆`,
      });
    }
  }

  const blocked = conflicts.some((c) => c.severity === 'block');
  return {
    ok: !blocked,
    severity: blocked ? 'block' : conflicts.length > 0 ? 'warn' : 'pass',
    conflicts,
  };
}

// ─── 工具: 读已装 skill 的 version ──────────────────────────────

/**
 * 读已装 skill 的 version(从 SKILL.md frontmatter 读)
 * @param {string} targetDir
 * @param {string} skillName
 * @returns {string|null}
 */
export function readInstalledVersion(targetDir, skillName) {
  const skillMd = join(targetDir, skillName, 'SKILL.md');
  if (!existsSync(skillMd)) return null;
  try {
    const content = readFileSync(skillMd, 'utf-8');
    const m = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!m) return null;
    const fm = yaml.parse(m[1]) || {};
    return String(fm.version || '').replace(/^["']|["']$/g, '') || null;
  } catch {
    return null;
  }
}

// ─── 4. BND-005 Nested Guard (BND-005 嵌套守卫) ──────────────────────

/**
 * 检测父包内是否存在嵌套 sub-skill(depth >= 1,自动遍历)。
 * 与 07_bundle_structure.py BND-005 一致,但在 install 阶段也拦,深度防御。
 *
 * 设计:
 *   - 不维护白名单(与 skill-bundle/SKILL.md §BND-005 对齐)
 *   - 递归遍历整个 skills/ 树,任何 depth >= 1 立即报
 *   - 提示运行 `trae-skills bundle flatten --plan <pkg>` 拿可执行 plan
 *
 * @param {string} parentDir 父包根目录路径(如 skill-markets/game-production-kit)
 * @returns {{ok: boolean, severity: 'pass'|'block', violations: Array<{path: string, depth: number, parentChain: string[]}>}}
 */
export function nestedSubSkillGuard(parentDir) {
  if (!existsSync(parentDir)) {
    return { ok: true, severity: 'pass', violations: [] };
  }
  const skillsDir = join(parentDir, 'skills');
  if (!existsSync(skillsDir)) {
    return { ok: true, severity: 'pass', violations: [] };
  }

  const violations = [];

  /**
   * 递归收集所有 depth >= 1 的 leaf
   * @param {string} current 当前目录
   * @param {string[]} chain 父链(从父包名开始)
   * @param {number} depth 当前深度(0 = 单层)
   */
  function collectNested(current, chain, depth) {
    let entries;
    try {
      entries = readdirSync(current, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name.startsWith('.')) continue;
      const full = join(current, entry.name);
      let isDir = false;
      try {
        isDir = statSync(full).isDirectory();
      } catch {
        continue;
      }
      if (!isDir) continue;
      const innerSkills = join(full, 'skills');
      let hasInner = false;
      try {
        hasInner = statSync(innerSkills).isDirectory();
      } catch {
        // not exists
      }
      if (hasInner) {
        collectNested(innerSkills, [...chain, entry.name], depth + 1);
      } else if (depth >= 1) {
        violations.push({
          path: full,
          depth,
          parentChain: [...chain, entry.name],
        });
      }
    }
  }

  collectNested(skillsDir, [parentDir.split(/[/\\]/).pop()], 0);
  return {
    ok: violations.length === 0,
    severity: violations.length === 0 ? 'pass' : 'block',
    violations,
  };
}

// ─── 工具: 列子目录 ─────────────────────────────────────────────

function listSubdirs(dir) {
  try {
    return readdirSync(dir, { withFileTypes: true })
      .filter((e) => {
        try {
          return lstatSync(join(dir, e.name)).isDirectory();
        } catch {
          return false;
        }
      })
      .map((e) => e.name);
  } catch {
    return [];
  }
}
