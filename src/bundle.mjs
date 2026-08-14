/**
 * src/bundle.mjs — trae-skills bundle <pkg> <subcmd>
 *
 * 子 skills 批量装载/更新/卸载命令,专为"一个父包 + N 个子 skills"场景设计
 * (fullstack4TraeV11 / game-production-kit / agent-dev-control-kit 这类)。
 *
 * 子命令:
 *   bundle install <pkg>    批量安装父包 + 子 skills(子 skills 装到 <pkg>-<name> 命名空间)
 *   bundle update <pkg>     检查 + 更新已装的子 skills
 *   bundle uninstall <pkg>  批量卸载
 *   bundle list <pkg>       列出 marketplace 父包内的子 skills + 装载状态
 *
 * 关键设计:
 *   1. 命名空间隔离: 子 skills 装载后叫 <pkg>-<name>(如 fullstack4TraeV11-01-intake)
 *   2. 三道闸(deprecation / version / name-conflict)全部跑,block 立即拒绝
 *   3. 往期版本检查: 已装同名但版本 < marketplace → 提示 update
 *   4. 名称冲突: 跨包同名(frontmatter name) → block
 *
 * 关联:
 *   - skill-bundle/SKILL.md (装载规范)
 *   - install-guards.mjs (三道闸)
 *   - AGENTS.md §1 铁律 §3 CLI 命令
 */

import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { select, confirm, checkbox } from '@inquirer/prompts';
import yaml from 'yaml';

import { scanSkills, findSkill } from './scanner.mjs';
import { getAgent, detectInstalledAgents, listAllAgents } from './agents.mjs';
import { installSkill, uninstallSkill } from './installer.mjs';
import {
  deprecationGuard,
  versionGuard,
  nameConflictGuard,
  nestedSubSkillGuard,
  readInstalledVersion,
} from './install-guards.mjs';
import {
  printSuccess,
  printError,
  printInfo,
  printWarn,
  parseArgs,
  resolveTargetDir,
  SKILL_MARKETS_DIR,
} from './utils.mjs';
import { findBundles, listSubSkillDirs, parseSubSkillFrontmatter } from './bundle-helpers.mjs';

// ─── 入口路由 ─────────────────────────────────────────────

export async function runBundle(args) {
  const sub = args[0];
  const rest = args.slice(1);
  const handlers = {
    install: runBundleInstall,
    update: runBundleUpdate,
    uninstall: runBundleUninstall,
    rm: runBundleUninstall,
    list: runBundleList,
    ls: runBundleList,
    flatten: runBundleFlatten,
  };
  if (!sub || sub === '--help' || sub === '-h') {
    printHelp();
    return;
  }
  const handler = handlers[sub];
  if (!handler) {
    printError(`未知 bundle 子命令: ${sub}`);
    printHelp();
    process.exit(1);
  }
  await handler(rest);
}

function printHelp() {
  console.log('Usage: trae-skills bundle <subcmd> <pkg> [options]');
  console.log();
  console.log('子命令:');
  console.log('  install <pkg>     一键安装父包 + 子 skills(命名空间 <pkg>-<name>)');
  console.log('  update <pkg>      一键检查 + 更新已装子 skills');
  console.log('  uninstall <pkg>   一键卸载父包 + 子 skills');
  console.log('  list <pkg>        列出子 skills + 装载状态');
  console.log();
  console.log('Options:');
  console.log('  -g / --trae-cn    全局安装 (默认项目级)');
  console.log('  -a <agent>        目标 agent (trae-cn / claude-code / codex / cursor / ...)');
  console.log('  --select <n1,n2>  仅安装指定子 skill(index)');
  console.log('  --exclude <n>     排除指定子 skill(index)');
  console.log('  -y / --yes        跳过所有确认');
  console.log('  --dry-run         只打印,不实际操作');
  console.log('  --copy            copy 而非 symlink');
}

// ─── 工具: 扫父包内的子 skills(已抽到 bundle-helpers.mjs 复用) ───────────────────────────

// ─── 通用: 选定 bundle + agents ───────────────────────────

async function resolveBundleAndAgents(args) {
  const opts = parseArgs(args);
  const pkgArg = opts._[0];
  const isGlobal = !!opts.flags.g || !!opts.flags['trae-cn'];
  const useCopy = !!opts.flags.copy;
  const dryRun = !!opts.flags['dry-run'];
  const skipConfirm = !!opts.flags.y;
  const agentArg = opts.flags.a
    ? Array.isArray(opts.flags.a)
      ? opts.flags.a
      : [opts.flags.a]
    : null;
  const selectFlag = opts.flags.select;
  const excludeFlag = opts.flags.exclude;

  // 1. 选 bundle
  const bundles = findBundles();
  if (bundles.length === 0) {
    printError('skill-markets/ 中未发现任何含子 skills 的父包');
    return null;
  }
  let bundle;
  if (pkgArg) {
    bundle = bundles.find((b) => b.dirName === pkgArg);
    if (!bundle) {
      printError(`未找到父包: ${pkgArg}`);
      console.log('\n可用的 bundles:');
      for (const b of bundles) console.log(`  - ${b.dirName}  (${b.subSkills.length} 子 skills)`);
      return null;
    }
  } else {
    bundle = await select({
      message: '选择父包:',
      choices: bundles.map((b) => ({
        name: `${b.dirName}  (${b.subSkills.length} 子 skills) — ${truncate(b.skill.description, 50)}`,
        value: b,
      })),
    });
  }
  printInfo(`已选 bundle: ${bundle.dirName}  (${bundle.subSkills.length} 子 skills)`);

  // 2. 选 agents
  let targetAgents;
  if (agentArg) {
    targetAgents = agentArg.map((n) => getAgent(n)).filter(Boolean);
    if (targetAgents.length === 0) {
      printError(`未找到指定的 agent: ${agentArg.join(', ')}`);
      console.log('\n可用的 agents:');
      for (const a of listAllAgents()) console.log(`  - ${a.name}`);
      return null;
    }
  } else {
    const installed = detectInstalledAgents();
    if (installed.length === 0) {
      printError('未检测到任何已安装的 agent,显式指定: trae-skills bundle install <pkg> -a trae-cn');
      return null;
    }
    const picked = await checkbox({
      message: '安装到哪些 agent (空格多选):',
      choices: installed.map((a) => ({ name: `${a.displayName} (${a.name})`, value: a })),
    });
    targetAgents = picked;
  }
  if (targetAgents.length === 0) {
    printWarn('未选任何 agent,已取消');
    return null;
  }

  // 3. 过滤子 skills(--select / --exclude)
  let subSkills = bundle.subSkills;
  if (selectFlag) {
    const indices = String(selectFlag).split(',').map((n) => parseInt(n, 10) - 1);
    subSkills = indices.map((i) => bundle.subSkills[i]).filter(Boolean);
  }
  if (excludeFlag) {
    const indices = String(excludeFlag).split(',').map((n) => parseInt(n, 10) - 1);
    subSkills = subSkills.filter((_, i) => !indices.includes(i));
  }

  return {
    bundle,
    subSkills,
    targetAgents,
    isGlobal,
    useCopy,
    dryRun,
    skipConfirm,
  };
}

// ─── 子命令: install ──────────────────────────────────────

async function runBundleInstall(args) {
  const ctx = await resolveBundleAndAgents(args);
  if (!ctx) return;
  const { bundle, subSkills, targetAgents, isGlobal, useCopy, dryRun, skipConfirm } = ctx;

  // 跑父包 deprecation 闸
  const depGuard = deprecationGuard(bundle.skill);
  if (depGuard.severity === 'block') {
    printError(`[${depGuard.code}] ${depGuard.message}`);
    printInfo(`Fix: ${depGuard.fix}`);
    process.exit(2);
  }

  // 跑 BND-005 嵌套闸(运行时,深度防御,提示 flatten --plan)
  const nestedGuard = nestedSubSkillGuard(bundle.skill.sourcePath);
  if (nestedGuard.severity === 'block') {
    printError(`[BND-005] ${bundle.dirName} 包含 ${nestedGuard.violations.length} 个嵌套 sub-skill:`);
    for (const v of nestedGuard.violations) {
      printError(`  - ${v.parentChain.join('/')}/  (深度 ${v.depth})`);
    }
    printInfo(`Fix: trae-skills bundle flatten --plan ${bundle.dirName} 拿可执行 git mv 命令`);
    process.exit(2);
  }

  // 列出每个子 skill 详情 + 装载状态
  const allMarketplace = scanSkills(SKILL_MARKETS_DIR);
  const plan = [];
  for (let i = 0; i < subSkills.length; i++) {
    const sub = subSkills[i];
    const fm = parseSubSkillFrontmatter(join(sub.path, 'SKILL.md'));
    if (sub.nested) {
      printWarn(`[${i + 1}] ${sub.name} ⚠️ 嵌套 skills/ 目录,跳过(TRAE 协议只识别单层)`);
      continue;
    }
    if (!fm) {
      printWarn(`[${i + 1}] ${sub.name} ❌ SKILL.md frontmatter 解析失败`);
      continue;
    }
    // 子 skill 命名空间: <pkg>-<name>
    const targetSkillName = `${bundle.dirName}-${sub.name}`;
    plan.push({ index: i + 1, src: sub, fm, targetName: targetSkillName });
  }

  if (plan.length === 0) {
    printError('无可用子 skills');
    return;
  }

  console.log();
  console.log('--- 装载计划 ---');
  for (const p of plan) {
    console.log(`  [${p.index}] ${p.targetName}  v${p.fm.version}  user-invocable=${p.fm.userInvocable}  ${truncate(p.fm.description, 60)}`);
  }
  console.log();

  if (!skipConfirm && !dryRun) {
    const ok = await confirm({
      message: `安装 ${plan.length} 个子 skills 到 ${targetAgents.length} 个 agent${isGlobal ? ' (全局)' : ''}?`,
      default: true,
    });
    if (!ok) {
      printInfo('已取消');
      return;
    }
  }

  // 跑闸 + 装
  for (const p of plan) {
    for (const agent of targetAgents) {
      const targetDir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
      if (!targetDir) {
        printError(`无法解析 ${agent.name} 的目标目录`);
        continue;
      }
      // name conflict (含 cross-package)
      const conflict = nameConflictGuard(
        { dirName: p.targetName, name: p.fm.name || p.targetName },
        targetDir,
        allMarketplace,
      );
      if (conflict.severity === 'block') {
        printError(`[${p.targetName}] 命名冲突 → ${conflict.conflicts[0].detail}`);
        continue;
      }
      for (const c of conflict.conflicts) {
        printWarn(`[${p.targetName}] ${c.type}: ${c.detail}`);
      }
      // version
      const installedVer = readInstalledVersion(targetDir, p.targetName);
      const v = versionGuard(installedVer, p.fm.version);
      if (v.severity !== 'pass') {
        printInfo(`[${p.targetName}] ${v.message} → action: ${v.action}`);
      }
      // 装
      try {
        const link = installSkill({
          sourcePath: p.src.path,
          targetDir,
          skillName: p.targetName,
          method: useCopy ? 'copy' : 'symlink',
          dryRun,
        });
        printSuccess(`${p.targetName} → ${link}`);
      } catch (err) {
        printError(`安装失败: ${p.targetName} → ${agent.name}: ${err.message}`);
      }
    }
  }
}

// ─── 子命令: update ───────────────────────────────────────

async function runBundleUpdate(args) {
  const ctx = await resolveBundleAndAgents(args);
  if (!ctx) return;
  const { bundle, subSkills, targetAgents, isGlobal, dryRun, skipConfirm } = ctx;

  // 扫已装子 skills
  const allMarketplace = scanSkills(SKILL_MARKETS_DIR);
  const updatePlan = [];
  for (const sub of subSkills) {
    const targetName = `${bundle.dirName}-${sub.name}`;
    const fm = parseSubSkillFrontmatter(join(sub.path, 'SKILL.md'));
    if (!fm) continue;

    for (const agent of targetAgents) {
      const targetDir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
      if (!targetDir) continue;
      const installedVer = readInstalledVersion(targetDir, targetName);
      const v = versionGuard(installedVer, fm.version);
      if (v.action === 'update') {
        updatePlan.push({ sub, fm, targetName, agent, targetDir, installedVer });
      }
    }
  }

  if (updatePlan.length === 0) {
    printInfo('所有子 skills 已是最新');
    return;
  }

  console.log();
  console.log('--- 需要更新的子 skills ---');
  for (const u of updatePlan) {
    console.log(`  ${u.targetName}  ${u.installedVer || '未装'} → ${u.fm.version}  (${u.agent.displayName})`);
  }

  if (!skipConfirm && !dryRun) {
    const ok = await confirm({
      message: `更新 ${updatePlan.length} 个子 skills?`,
      default: true,
    });
    if (!ok) {
      printInfo('已取消');
      return;
    }
  }

  for (const u of updatePlan) {
    try {
      uninstallSkill({ targetDir: u.targetDir, skillName: u.targetName, dryRun });
      installSkill({
        sourcePath: u.sub.path,
        targetDir: u.targetDir,
        skillName: u.targetName,
        method: 'symlink',
        dryRun,
      });
      printSuccess(`已更新: ${u.targetName}  (${u.agent.displayName}) → ${u.fm.version}`);
    } catch (err) {
      printError(`更新失败: ${u.targetName} (${u.agent.displayName}): ${err.message}`);
    }
  }
}

// ─── 子命令: uninstall ────────────────────────────────────

async function runBundleUninstall(args) {
  const ctx = await resolveBundleAndAgents(args);
  if (!ctx) return;
  const { bundle, subSkills, targetAgents, isGlobal, dryRun, skipConfirm } = ctx;

  // 找所有匹配 <pkg>-<name> 的已装项
  const toUninstall = [];
  for (const agent of targetAgents) {
    const targetDir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
    if (!targetDir || !existsSync(targetDir)) continue;
    const { readdirSync, lstatSync } = await import('node:fs');
    for (const e of readdirSync(targetDir, { withFileTypes: true })) {
      try {
        if (!lstatSync(join(targetDir, e.name)).isDirectory()) continue;
      } catch {
        continue;
      }
      // 匹配 <pkg>-<sub> 前缀
      if (e.name.startsWith(bundle.dirName + '-')) {
        toUninstall.push({ name: e.name, agent, targetDir });
      }
    }
  }

  if (toUninstall.length === 0) {
    printInfo(`没有匹配 ${bundle.dirName}-* 的已装子 skills`);
    return;
  }

  console.log();
  console.log('--- 将卸载 ---');
  for (const u of toUninstall) {
    console.log(`  ${u.name}  (${u.agent.displayName})`);
  }

  if (!skipConfirm && !dryRun) {
    const ok = await confirm({
      message: `确认卸载 ${toUninstall.length} 个子 skills?`,
      default: false,
    });
    if (!ok) {
      printInfo('已取消');
      return;
    }
  }

  for (const u of toUninstall) {
    try {
      uninstallSkill({ targetDir: u.targetDir, skillName: u.name, dryRun });
      printSuccess(`已卸载: ${u.name}  (${u.agent.displayName})`);
    } catch (err) {
      printError(`卸载失败: ${u.name} (${u.agent.displayName}): ${err.message}`);
    }
  }
}

// ─── 子命令: list ──────────────────────────────────────────

async function runBundleList(args) {
  const ctx = await resolveBundleAndAgents(args);
  if (!ctx) return;
  const { bundle, subSkills, targetAgents, isGlobal } = ctx;

  console.log();
  console.log(`📦 ${bundle.dirName}  v${bundle.skill.version}`);
  console.log(`   ${truncate(bundle.skill.description, 80)}`);
  console.log(`   ${subSkills.length} 子 skills`);
  console.log();

  for (const sub of subSkills) {
    const fm = parseSubSkillFrontmatter(join(sub.path, 'SKILL.md'));
    if (!fm) {
      console.log(`  ❌ ${sub.name.padEnd(30)}  frontmatter 解析失败`);
      continue;
    }
    if (sub.nested) {
      console.log(`  ⚠️  ${sub.name.padEnd(28)}  嵌套 skills/ 目录,跳过`);
      continue;
    }
    const targetName = `${bundle.dirName}-${sub.name}`;

    // 装状态(只看第一个 agent)
    const statusParts = [];
    for (const agent of targetAgents) {
      const targetDir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
      const installedVer = readInstalledVersion(targetDir, targetName);
      const v = versionGuard(installedVer, fm.version);
      const symbol = v.action === 'equal' ? '✓' : v.action === 'install' ? ' ' : '↻';
      const ver = installedVer || '未装';
      statusParts.push(`${agent.name}: ${symbol} ${ver}`);
    }
    const inv = fm.userInvocable ? '📞' : '   ';
    console.log(`  ${inv} [${fm.version.padEnd(7)}] ${targetName.padEnd(40)}  ${truncate(fm.description, 50)}`);
    for (const s of statusParts) console.log(`         ${s}`);
  }
}

// ─── 工具 ─────────────────────────────────────────────────

function truncate(s, n) {
  s = String(s || '').replace(/\n/g, ' ').trim();
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}

// ─── flatten --plan(BND-005 自检辅助) ────────────────────────

/**
 * 递归扫描父包内的嵌套 sub-skill 树,返回所有嵌套层级的 leaf sub-skill。
 * 自动遍历深度 — 不只看一层,任意层数都报。
 *
 * @param {string} parentDir 父包根目录(如 skill-markets/game-production-kit)
 * @returns {Array<{path: string, depth: number, parentChain: string[]}>}
 *   path: 完整路径
 *   depth: 相对 skills/ 的嵌套深度(0 = 单层, 1+ = 嵌套)
 *   parentChain: 从父包名到当前目录的链
 */
function scanNestedSubSkills(parentDir) {
  const skillsDir = join(parentDir, 'skills');
  if (!existsSync(skillsDir)) return [];

  const nested = [];

  /**
   * 递归扫描
   * @param {string} current 当前目录
   * @param {string[]} chain 父链(从父包名开始)
   * @param {number} depth 当前深度
   */
  function walk(current, chain, depth) {
    let entries;
    try {
      entries = readdirSync(current, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name.startsWith('.')) continue;
      const full = join(current, entry.name);
      try {
        if (!statSync(full).isDirectory()) continue;
      } catch {
        continue;
      }
      const skillMd = join(full, 'SKILL.md');
      const hasSkillMd = existsSync(skillMd);
      const innerSkillsDir = join(full, 'skills');
      const hasInnerSkills = existsSync(innerSkillsDir) &&
        (() => { try { return statSync(innerSkillsDir).isDirectory(); } catch { return false; } })();

      if (hasInnerSkills) {
        // 嵌套: 继续递归
        walk(innerSkillsDir, [...chain, entry.name], depth + 1);
      } else if (hasSkillMd) {
        // leaf: 收集
        nested.push({
          path: full,
          depth: depth,
          parentChain: [...chain, entry.name],
        });
      }
    }
  }

  walk(skillsDir, [parentDir.split(/[/\\]/).pop()], 0);
  return nested;
}

/**
 * trae-skills bundle flatten --plan <pkg>
 * 报告 BND-005 嵌套结构 + 打印可执行拆扁 plan(不写盘,只读)。
 *
 * 设计:
 *   - 递归扫描所有嵌套层级的 leaf sub-skill
 *   - 输出可执行 git mv 命令,用户复制即可执行
 *   - 命名约定: <parent-name>-<leaf-name>,把父 skill 名作为前缀保留语义关联
 */
async function runBundleFlatten(args) {
  const planIdx = args.indexOf('--plan');
  if (planIdx === -1) {
    printError('用法: trae-skills bundle flatten --plan <pkg>');
    process.exit(1);
  }
  const pkgName = args[planIdx + 1];
  if (!pkgName) {
    printError('请指定 <pkg> 父包名');
    process.exit(1);
  }

  // 复用 findBundles() — 与 install/list 一致的父包查找逻辑
  const bundles = findBundles();
  const bundle = bundles.find((b) => b.dirName === pkgName);
  if (!bundle) {
    printError(`未找到父包: ${pkgName}`);
    console.log('\n可用的 bundles:');
    for (const b of bundles) console.log(`  - ${b.dirName}  (${b.subSkills.length} 子 skills)`);
    process.exit(1);
  }

  const target = bundle.skill.sourcePath;  // scanSkills() 返回的 sourcePath = 父包根
  const parentName = bundle.dirName;
  const nested = scanNestedSubSkills(target);

  // 只对 depth >= 1 (真嵌套) 才报
  if (nested.length === 0 || nested.every((n) => n.depth < 1)) {
    printSuccess(`✅ [BND-005] ${parentName} 无嵌套(TRAE 单层协议 PASS)`);
    return;
  }

  console.log(`🔍 [BND-005] ${parentName} 嵌套扫描:`);
  const violations = nested.filter((n) => n.depth >= 1);
  for (const n of violations) {
    const relPath = n.parentChain.slice(1).join('/');  // 去掉父包名,显示 skills/...
    console.log(`  ❌ skills/${relPath}/  ← 嵌套深度 ${n.depth},违反 TRAE 单层协议`);
  }
  console.log();
  console.log(`📋 拆扁 plan(只读,不写盘):`);

  // 按 parent group 排序输出
  const byParent = new Map();
  for (const n of nested) {
    // 父 chain 的第 1 个是父包,2+ 是嵌套层。例如
    // ['game-production-kit', 'voice-acting-skill', 'annotation-generator']
    // → 父 = 'voice-acting-skill', leaf = 'annotation-generator'
    if (n.parentChain.length < 3) continue;
    const nestedParent = n.parentChain[1];
    const leaf = n.parentChain[n.parentChain.length - 1];
    if (!byParent.has(nestedParent)) byParent.set(nestedParent, []);
    byParent.get(nestedParent).push(leaf);
  }

  let step = 1;
  for (const [nestedParent, leaves] of byParent) {
    const prefix = `${parentName}-${nestedParent}`;
    console.log(`  ${step}. mkdir ${parentName}/skills/${prefix}-{${leaves.join(',')}}`);
    step++;
    for (const leaf of leaves) {
      const newName = `${prefix}-${leaf}`;
      const oldPath = `${parentName}/skills/${nestedParent}/skills/${leaf}`;
      const newPath = `${parentName}/skills/${newName}`;
      console.log(`  ${step}. git mv ${oldPath}/SKILL.md ${newPath}/SKILL.md`);
      step++;
    }
    console.log(`  ${step}. 更新 ${parentName}/skills/${nestedParent}/SKILL.md 路由表:子 skill 入口改写为 skills/${prefix}-{...}`);
    step++;
    console.log(`  ${step}. 删除空目录 ${parentName}/skills/${nestedParent}/skills/`);
    step++;
    console.log();
  }
  console.log(`💡 命名约定: <父包>-<嵌套父>-<leaf>,如 ${parentName}-voice-acting-annotation-generator`);
  console.log(`💡 修复后跑 trae-skills verify ${parentName} 验证 BND-005 PASS`);

  // 退出 1 — 让 L1 commit hook / CI 能拿 plan 当提示(不阻断,只是 -1 让 grep 检出)
  // 设计: flatten --plan 是 diagnostic 工具,本身不应成功("发现违例"≠"通过")。
  // 实际 gate 拦截走 07_bundle_structure.py BND-005 自身,这里只是 stdout 提示。
  process.exit(0);
}
