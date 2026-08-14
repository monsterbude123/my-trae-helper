#!/usr/bin/env node
/**
 * src/guards/skill-registration-guard.mjs — Skill Registration Guard
 *
 * 设计目的（2026-08-14 §3 三层控制收紧方案 A）：
 *   每个 skill 必须在本仓库 registry/skills.yaml 中按同名条目注册 guard + gate 路由。
 *   任何 "skill-markets/<x>/ 存在但未注册" 或 "注册条目指向的文件不存在" → BLOCK。
 *
 * 触发时机：pre-commit / pre-push / L3 PR merge
 * 调用方式：
 *   node src/guards/skill-registration-guard.mjs             # 全市场检查
 *   node src/guards/skill-registration-guard.mjs <name>      # 单 skill
 *
 * 退出码：
 *   0 = PASS
 *   1 = BLOCK（注册缺失 / 文件缺失 / schema 错误）
 *   2 = WARN（仅警告，不阻断 — 留给 deprecated 过渡期）
 */

import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, resolve, dirname, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse as parseYaml } from 'yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// REPO_ROOT 可被环境变量覆盖(测试用)
// 默认从 import.meta.url 反推(src/guards/<file> → 仓库根)
const REPO_ROOT = process.env.REG_GUARD_REPO_ROOT
  ? resolve(process.env.REG_GUARD_REPO_ROOT)
  : resolve(__dirname, '..', '..');

const REGISTRY = join(REPO_ROOT, 'registry', 'skills.yaml');
const SKILL_MARKETS_DIR = join(REPO_ROOT, 'skill-markets');
const VALID_STATUS = new Set(['active', 'deprecated', 'archived']);
const VALID_LEVEL = new Set(['L1', 'L2', 'L3', 'L4']);
const MAINTAINER_ALLOWLIST = new Set(['guard-smith']);

/**
 * 列出 skill-markets 下所有根 skill 目录
 *
 * 识别规则:
 *   - 含 SKILL.md → 标准 skill
 *   - 仅含 AGENTS.md → bundle skill (e.g. ponytail4Trae / gitnexus4Trae / product-teardown)
 *   - docs/ / 空目录 / 其他脚手架目录 → 跳过
 */
const NON_SKILL_DIRS = new Set(['docs', 'my-deep-research', 'skill-scaffold']);

function listRootSkills() {
  if (!existsSync(SKILL_MARKETS_DIR)) return [];
  return readdirSync(SKILL_MARKETS_DIR)
    .filter(name => !NON_SKILL_DIRS.has(name))
    .filter(name => {
      try {
        const st = statSync(join(SKILL_MARKETS_DIR, name));
        if (!st.isDirectory()) return false;
      } catch {
        return false;
      }
      const dir = join(SKILL_MARKETS_DIR, name);
      const hasSkill = existsSync(join(dir, 'SKILL.md'));
      const hasAgents = existsSync(join(dir, 'AGENTS.md'));
      return hasSkill || hasAgents;
    })
    .sort();
}

/**
 * 单 skill 注册校验
 */
function checkSkill(entry, rootSkillsSet) {
  const errors = [];
  const warnings = [];

  if (!entry || !entry.skill) {
    errors.push('注册条目缺少 skill 字段');
    return { errors, warnings };
  }

  // 1. 目录存在
  const skillDir = join(SKILL_MARKETS_DIR, entry.skill);
  if (!existsSync(skillDir)) {
    errors.push(`skill 目录不存在: skill-markets/${entry.skill}/`);
  }

  // 2. status 合法
  if (!entry.status) {
    errors.push(`${entry.skill}: 缺 status 字段`);
  } else if (!VALID_STATUS.has(entry.status)) {
    errors.push(`${entry.skill}: status 不合法: ${entry.status}`);
  }

  // 3. guards 非空 + 每个 guard 字段完整 + script 存在
  if (!Array.isArray(entry.guards) || entry.guards.length === 0) {
    errors.push(`${entry.skill}: 缺 guards 注册（"无防护" → BLOCK）`);
  } else {
    entry.guards.forEach((g, idx) => {
      const tag = `[guard #${idx + 1}]`;
      if (!g.id) errors.push(`${entry.skill} ${tag}: 缺 id`);
      if (!g.script) {
        errors.push(`${entry.skill} ${tag}: 缺 script 字段`);
      } else {
        const abs = isAbsolute(g.script) ? g.script : join(REPO_ROOT, g.script);
        if (!existsSync(abs)) {
          errors.push(`${entry.skill} ${tag}: 脚本不存在: ${g.script}`);
        }
      }
      if (!g.category) warnings.push(`${entry.skill} ${tag}: 建议填 category`);
      if (!Array.isArray(g.triggers) || g.triggers.length === 0) {
        warnings.push(`${entry.skill} ${tag}: 建议填 triggers`);
      }
    });
  }

  // 4. gates 非空 + 每个 gate 字段完整 + hook 文件存在
  if (!Array.isArray(entry.gates) || entry.gates.length === 0) {
    errors.push(`${entry.skill}: 缺 gates 注册（"无门禁" → BLOCK）`);
  } else {
    entry.gates.forEach((gt, idx) => {
      const tag = `[gate #${idx + 1}]`;
      if (!gt.id) errors.push(`${entry.skill} ${tag}: 缺 id`);
      if (!gt.level) {
        errors.push(`${entry.skill} ${tag}: 缺 level`);
      } else if (!VALID_LEVEL.has(gt.level)) {
        errors.push(`${entry.skill} ${tag}: level 不合法: ${gt.level}`);
      }
      if (!Array.isArray(gt.hooks) || gt.hooks.length === 0) {
        errors.push(`${entry.skill} ${tag}: 缺 hooks 列表（门禁挂在哪里？）`);
      } else {
        gt.hooks.forEach(h => {
          const abs = isAbsolute(h) ? h : join(REPO_ROOT, h);
          if (!existsSync(abs)) {
            errors.push(`${entry.skill} ${tag}: hook 文件不存在: ${h}`);
          }
        });
      }
      if (!Array.isArray(gt.runs_guards) || gt.runs_guards.length === 0) {
        errors.push(`${entry.skill} ${tag}: 缺 runs_guards（门禁运行哪些 guard？）`);
      }
    });
  }

  // 5. maintainer 白名单
  if (!entry.maintainer) {
    errors.push(`${entry.skill}: 缺 maintainer 字段（必须填 guard-smith）`);
  } else if (!MAINTAINER_ALLOWLIST.has(entry.maintainer)) {
    errors.push(`${entry.skill}: maintainer=${entry.maintainer} 不在白名单 ${[...MAINTAINER_ALLOWLIST].join('|')}`);
  }

  return { errors, warnings };
}

/**
 * 反向校验：所有 skill-markets 下的根 skill 都必须在注册表里
 */
function checkUnregisteredSkills(registrySkills, rootSkills) {
  const regSet = new Set(registrySkills.map(s => s && s.skill).filter(Boolean));
  const errors = [];
  for (const skill of rootSkills) {
    if (!regSet.has(skill)) {
      errors.push(`skill-markets/${skill}/ 存在但未在 registry/skills.yaml 注册（"无防护" → BLOCK）`);
    }
  }
  return errors;
}

/**
 * 反向校验：注册表里的 skill 必须真实存在
 */
function checkPhantomSkills(registrySkills, rootSkillsSet) {
  const errors = [];
  for (const entry of registrySkills) {
    if (entry && entry.skill && !rootSkillsSet.has(entry.skill)) {
      errors.push(`注册表条目指向不存在的 skill: ${entry.skill}`);
    }
  }
  return errors;
}

function main() {
  const arg = process.argv[2]; // 单 skill 名 or 全量

  if (!existsSync(REGISTRY)) {
    console.error(`❌ 注册表不存在: registry/skills.yaml`);
    console.error(`请运行: mkdir -p registry && 创建 skills.yaml`);
    process.exit(1);
  }

  const text = readFileSync(REGISTRY, 'utf-8');
  let registry;
  try {
    registry = parseYaml(text);
  } catch (e) {
    console.error(`❌ 注册表 YAML 解析失败: ${e.message}`);
    process.exit(1);
  }

  const rootSkills = listRootSkills();
  const rootSkillsSet = new Set(rootSkills);
  const registeredSkills = Array.isArray(registry.skills) ? registry.skills : [];

  console.log(`🔍 Skill Registration Guard`);
  console.log(`   registry: registry/skills.yaml`);
  console.log(`   skill-markets: ${rootSkills.length} 个根 skill`);
  console.log(`   registered: ${registeredSkills.length} 条目\n`);

  const allErrors = [];
  const allWarnings = [];

  // 模式 1: 单 skill
  if (arg) {
    const entry = registeredSkills.find(s => s && s.skill === arg);
    if (!entry) {
      allErrors.push(`注册表未找到 skill 条目: ${arg}`);
      console.log(`❌ BLOCK — ${arg} 未注册`);
      console.log(allErrors.map(e => `   - ${e}`).join('\n'));
      process.exit(1);
    }
    const r = checkSkill(entry, rootSkillsSet);
    allErrors.push(...r.errors);
    allWarnings.push(...r.warnings);
    console.log(`[${arg}]`);
    console.log(`  status: ${entry.status || '(missing)'}`);
    console.log(`  guards: ${(entry.guards || []).length}`);
    console.log(`  gates: ${(entry.gates || []).length}`);
    console.log(`  maintainer: ${entry.maintainer || '(missing)'}`);
  } else {
    // 模式 2: 全量
    // 2a. 每条目 schema 校验
    for (const entry of registeredSkills) {
      const r = checkSkill(entry, rootSkillsSet);
      allErrors.push(...r.errors);
      allWarnings.push(...r.warnings);
    }
    // 2b. 反向: 未注册 skill
    const unregErrors = checkUnregisteredSkills(registeredSkills, rootSkills);
    allErrors.push(...unregErrors);
    // 2c. 反向: 幻影 skill(注册了但不存在)
    const phantomErrors = checkPhantomSkills(registeredSkills, rootSkillsSet);
    allErrors.push(...phantomErrors);
  }

  console.log('');
  if (allWarnings.length > 0) {
    console.log(`⚠️  WARNINGS (${allWarnings.length}):`);
    allWarnings.forEach(w => console.log(`   - ${w}`));
  }

  if (allErrors.length > 0) {
    console.log(`\n❌ BLOCK (${allErrors.length} errors):`);
    allErrors.forEach(e => console.log(`   - ${e}`));
    console.log(`\n🛠  修复：仅 guard-smith agent 可改 registry/skills.yaml + scripts/<name>-guard.* + .husky/<name>-gate`);
    process.exit(1);
  }

  console.log(`✅ PASS — registry/skills.yaml 完整性校验通过`);
  process.exit(0);
}

const isMain = import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`;
if (isMain) {
  main();
}

export { listRootSkills, checkSkill, checkUnregisteredSkills, checkPhantomSkills };