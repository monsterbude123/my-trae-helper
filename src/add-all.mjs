/**
 * src/add-all.mjs — trae-skills add-all [options]  (alias: install-all)
 *
 * 批量把 skill-markets/ 全部 skill 装到目标 agent,重点支持 trae-cn 全局。
 *
 * 流程:
 *   Step 1: 扫 skill-markets(Scan) + 找 bundles(父包)
 *   Step 2: 过滤顶层(全部)— 白名单 / 黑名单 / deprecated
 *   Step 3: 跑三道闸(deprecation / version / name-conflict)— block 立即终止, warn 继续
 *   Step 4: 装顶层(含父包本体,40 个左右)到每个目标 agent
 *   Step 5: 装子 skill(对每个指定父包,遍历 bundle.subSkills,装到 <pkg>-<subName>)
 *   Step 6: 输出汇总(success / skip / fail)
 *
 * 设计要点:
 *   - 父包与顶层并存 — 父包本体(SKILL.md)装为 <pkg>,子 skill 装为 <pkg>-<subName>
 *     命名空间隔离,互不冲突
 *   - 子 skill 装入后命名空间 = `<pkg>-<subName>`
 *   - 跨平台:统一走 installer.mjs(Windows junction / POSIX symlink),禁止自写 fs.symlinkSync
 *   - 重复 agent 通过 Set 去重
 *   - dry-run 不写盘,只 print
 *   - 单 skill 失败 → printError + continue;致命错误 → process.exit(1)
 *
 * 关联:
 *   - AGENTS.md §3 CLI 命令(add-all)
 *   - src/add.mjs(单装模板)
 *   - src/bundle.mjs(批量子 skill 模板)
 */

import { join } from 'node:path';

import { scanSkills } from './scanner.mjs';
import { getAgent, detectInstalledAgents, listAllAgents } from './agents.mjs';
import { installSkill } from './installer.mjs';
import {
  deprecationGuard,
  versionGuard,
  nameConflictGuard,
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
import { findBundles, parseSubSkillFrontmatter } from './bundle-helpers.mjs';

// ─── Help ───────────────────────────────────────────────────────

function printHelp() {
  console.log('Usage: trae-skills add-all [options]');
  console.log('       trae-skills install-all [options]');
  console.log();
  console.log('批量把 skill-markets/ 全部 skill 装到目标 agent(顶层 + 子 skill)。');
  console.log();
  console.log('Options:');
  console.log('  -g / --trae-cn         全局安装 (默认项目级)');
  console.log('  -a <agent>             目标 agent,可重复 (默认探测 detectInstalledAgents)');
  console.log('  -y / --yes             跳过所有 confirm');
  console.log('  --copy                 copy 而非 symlink');
  console.log('  --dry-run              只打印,不实际操作');
  console.log('  --include <a,b,c>      顶层白名单(只装这些顶层 dirName)');
  console.log('  --exclude <a,b,c>      顶层黑名单');
  console.log('  --skip-deprecated      跳过 deprecated 的顶层 skill(默认 true)');
  console.log('  --bundles <pkg1,pkg2>  指定要装子 skill 的父包;空字符串 = 跳过所有 bundle');
  console.log('                         默认 = 全部父包');
  console.log();
  console.log('Examples:');
  console.log('  trae-skills add-all -a trae-cn --dry-run -y');
  console.log('  trae-skills add-all -g -y');
  console.log('  trae-skills add-all --include trae-security-review,skill-bundle');
  console.log('  trae-skills add-all --bundles ""   # 跳过所有子 skill');
}

// ─── 入口 ───────────────────────────────────────────────────────

export async function runAddAll(args) {
  // 仅 --help / -h
  if (!args.length || args.includes('--help') || args.includes('-h')) {
    printHelp();
    return;
  }

  const opts = parseArgs(args);

  const isGlobal = !!opts.flags.g || !!opts.flags['trae-cn'];
  const useCopy = !!opts.flags.copy;
  const dryRun = !!opts.flags['dry-run'];
  const skipConfirm = !!opts.flags.y;
  const skipDeprecated = opts.flags['skip-deprecated'] !== false; // 默认 true

  const agentArg = opts.flags.a
    ? Array.isArray(opts.flags.a)
      ? opts.flags.a
      : [opts.flags.a]
    : null;

  const includeList = parseCsv(opts.flags.include);
  const excludeList = parseCsv(opts.flags.exclude);

  // --bundles 空串 = 跳过所有 bundle;未指定 = 全装
  let bundleList;
  if (opts.flags.bundles === '') {
    bundleList = [];
  } else if (opts.flags.bundles === undefined) {
    bundleList = null; // sentinel: 全部父包
  } else {
    bundleList = parseCsv(opts.flags.bundles);
  }

  // Step 1: 扫所有顶层 skill + 找 bundles
  printInfo('扫描 skill-markets/ ...');
  const allTop = scanSkills(SKILL_MARKETS_DIR);
  if (allTop.length === 0) {
    printError('未在 skill-markets/ 发现任何 skill');
    process.exit(1);
  }
  const bundles = findBundles(SKILL_MARKETS_DIR);

  // Step 2: 过滤顶层 — 白/黑名单 + deprecated
  // 注意:父包(bundle)也是合法顶层 skill,必须保留 — 它的 SKILL.md 可独立加载
  // 子 skill 装到 <bundle.dirName>-<subName> 命名空间,不与父包冲突
  let topSkills = allTop;
  if (includeList.length > 0) {
    const includeSet = new Set(includeList.map((n) => n.toLowerCase()));
    topSkills = topSkills.filter((s) => includeSet.has(s.dirName.toLowerCase()));
  }
  if (excludeList.length > 0) {
    const excludeSet = new Set(excludeList.map((n) => n.toLowerCase()));
    topSkills = topSkills.filter((s) => !excludeSet.has(s.dirName.toLowerCase()));
  }
  if (skipDeprecated) {
    const before = topSkills.length;
    topSkills = topSkills.filter((s) => s.status !== 'deprecated');
    const skipped = before - topSkills.length;
    if (skipped > 0) printInfo(`跳过 ${skipped} 个 deprecated 顶层 skill`);
  }

  // 解析父包子集(bundleList null = 全装)
  let targetBundles = bundles;
  if (bundleList !== null) {
    const set = new Set(bundleList);
    targetBundles = bundles.filter((b) => set.has(b.dirName));
    const missing = bundleList.filter((n) => !bundles.some((b) => b.dirName === n));
    if (missing.length > 0) {
      printWarn(`未找到父包: ${missing.join(', ')} (忽略)`);
    }
  }

  // 选 agents
  const targetAgents = resolveTargetAgents(agentArg);
  if (targetAgents.length === 0) {
    printError('未选任何 agent,已取消');
    return;
  }

  // 汇总预览
  console.log();
  console.log('--- 装载计划 ---');
  console.log(`  顶层 skill:  ${topSkills.length} 个`);
  console.log(`  父包(子 skill): ${targetBundles.length} 个 bundle`);
  let totalSub = 0;
  for (const b of targetBundles) totalSub += b.subSkills.length;
  console.log(`  子 skill 总数:  ${totalSub} 个`);
  console.log(`  目标 agent:   ${targetAgents.map((a) => a.name).join(', ')} (${isGlobal ? '全局' : '项目级'})`);
  console.log(`  模式:         ${useCopy ? 'copy' : 'symlink/junction'}${dryRun ? ' [DRY-RUN]' : ''}`);
  console.log();

  if (topSkills.length === 0 && targetBundles.length === 0) {
    printWarn('无任何可装 skill,已取消');
    return;
  }

  if (!skipConfirm && !dryRun) {
    const ok = await confirm(
      `批量装载 ${topSkills.length} 顶层 + ${totalSub} 子 skill 到 ${targetAgents.length} agent${isGlobal ? ' (全局)' : ''}?`,
    );
    if (!ok) {
      printInfo('已取消');
      return;
    }
  }

  // 计数器
  const stats = { topOk: 0, topSkip: 0, topFail: 0, subOk: 0, subSkip: 0, subFail: 0 };

  // Step 3+4: 装顶层
  console.log('--- 装顶层 skill ---');
  for (const skill of topSkills) {
    // deprecation 闸
    const dep = deprecationGuard(skill);
    if (dep.severity === 'block') {
      printError(`[${skill.dirName}] [${dep.code}] ${dep.message}`);
      stats.topSkip++;
      continue;
    }

    // 对每个 agent 跑冲突 + 版本 + 装
    let allBlocked = true;
    for (const agent of targetAgents) {
      const targetDir = resolveAgentDir(agent, isGlobal);
      if (!targetDir) {
        printError(`无法解析 ${agent.name} 的目标目录`);
        stats.topFail++;
        allBlocked = false;
        continue;
      }
      // name conflict
      const conflict = nameConflictGuard(skill, targetDir, allTop);
      if (conflict.severity === 'block') {
        const detail = conflict.conflicts[0]?.detail || 'conflict';
        printError(`[${skill.dirName}] 命名冲突 → ${detail}`);
        stats.topSkip++;
        continue;
      }
      for (const c of conflict.conflicts) {
        printWarn(`[${skill.dirName}] ${c.type}: ${c.detail}`);
      }
      // version
      const installedVer = readInstalledVersion(targetDir, skill.dirName);
      const v = versionGuard(installedVer, skill.version);
      if (v.severity !== 'pass') {
        printInfo(`[${skill.dirName} → ${agent.name}] ${v.message} → ${v.action}`);
      }
      // 装
      try {
        const res = installSkill({
          sourcePath: skill.sourcePath,
          targetDir,
          skillName: skill.dirName,
          method: useCopy ? 'copy' : 'symlink',
          dryRun,
        });
        printSuccess(`[${skill.dirName}] → ${res}`);
        stats.topOk++;
        allBlocked = false;
      } catch (err) {
        printError(`[${skill.dirName} → ${agent.name}] 装失败: ${err.message}`);
        stats.topFail++;
        allBlocked = false;
      }
    }
    if (allBlocked && topSkills.length > 0) {
      // nothing actually installed for this skill
    }
  }

  // Step 5: 装子 skill
  if (targetBundles.length > 0) {
    console.log();
    console.log('--- 装子 skill ---');
    for (const bundle of targetBundles) {
      // 父包 deprecation 闸
      const dep = deprecationGuard(bundle.skill);
      if (dep.severity === 'block') {
        printError(`[bundle:${bundle.dirName}] [${dep.code}] ${dep.message}`);
        stats.subSkip += bundle.subSkills.length * targetAgents.length;
        continue;
      }
      for (const sub of bundle.subSkills) {
        const fm = parseSubSkillFrontmatter(join(sub.path, 'SKILL.md'));
        if (sub.nested) {
          printWarn(`[${bundle.dirName}-${sub.name}] 嵌套 skills/,跳过`);
          stats.subSkip += targetAgents.length;
          continue;
        }
        if (!fm) {
          printWarn(`[${bundle.dirName}-${sub.name}] SKILL.md frontmatter 解析失败`);
          stats.subSkip += targetAgents.length;
          continue;
        }
        // 子 skill deprecated
        if (skipDeprecated && fm.status === 'deprecated') {
          printWarn(`[${bundle.dirName}-${sub.name}] deprecated,跳过`);
          stats.subSkip += targetAgents.length;
          continue;
        }
        const targetName = `${bundle.dirName}-${sub.name}`;
        for (const agent of targetAgents) {
          const targetDir = resolveAgentDir(agent, isGlobal);
          if (!targetDir) {
            printError(`无法解析 ${agent.name} 的目标目录`);
            stats.subFail++;
            continue;
          }
          // name conflict(基于顶层 allTop + 子 skill 命名空间)
          const conflict = nameConflictGuard(
            { dirName: targetName, name: fm.name || targetName },
            targetDir,
            allTop,
          );
          if (conflict.severity === 'block') {
            printError(`[${targetName}] 命名冲突 → ${conflict.conflicts[0]?.detail || ''}`);
            stats.subSkip++;
            continue;
          }
          for (const c of conflict.conflicts) {
            printWarn(`[${targetName}] ${c.type}: ${c.detail}`);
          }
          // version
          const installedVer = readInstalledVersion(targetDir, targetName);
          const v = versionGuard(installedVer, fm.version);
          if (v.severity !== 'pass') {
            printInfo(`[${targetName} → ${agent.name}] ${v.message} → ${v.action}`);
          }
          // 装
          try {
            const res = installSkill({
              sourcePath: sub.path,
              targetDir,
              skillName: targetName,
              method: useCopy ? 'copy' : 'symlink',
              dryRun,
            });
            printSuccess(`[${targetName}] → ${res}`);
            stats.subOk++;
          } catch (err) {
            printError(`[${targetName} → ${agent.name}] 装失败: ${err.message}`);
            stats.subFail++;
          }
        }
      }
    }
  }

  // Step 6: 汇总
  console.log();
  console.log('--- 汇总 ---');
  console.log(
    `  顶层: ok=${stats.topOk}  skip=${stats.topSkip}  fail=${stats.topFail}  (计划 ${topSkills.length} × ${targetAgents.length} agent)`,
  );
  console.log(
    `  子 skill: ok=${stats.subOk}  skip=${stats.subSkip}  fail=${stats.subFail}`,
  );

  const fatal = stats.topFail > 0 || stats.subFail > 0;
  if (fatal) {
    printWarn('部分 skill 安装失败,详见上方 ERROR');
  } else {
    printSuccess(`${dryRun ? '[DRY-RUN] ' : ''}批量装载完成`);
  }
}

// 别名 — install-all 直接走 add-all
export async function runInstallAll(args) {
  return runAddAll(args);
}

// ─── 内部工具 ───────────────────────────────────────────────────

function parseCsv(v) {
  if (v === undefined || v === null || v === '') return [];
  return String(v)
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
}

/**
 * 解析 agent 列表 — 重复去重 + 未知报错。
 * @param {string[]|null} agentArg
 * @returns {Array}
 */
function resolveTargetAgents(agentArg) {
  if (agentArg && agentArg.length > 0) {
    const seen = new Set();
    const out = [];
    for (const name of agentArg) {
      if (seen.has(name)) continue;
      seen.add(name);
      const a = getAgent(name);
      if (!a) {
        printError(`未知的 agent: ${name}`);
        continue;
      }
      out.push(a);
    }
    if (out.length === 0) {
      console.log('\n可用的 agents:');
      for (const a of listAllAgents()) {
        console.log(`  - ${a.name.padEnd(16)}  ${a.displayName}`);
      }
    }
    return out;
  }
  const installed = detectInstalledAgents();
  if (installed.length === 0) {
    printError('未检测到任何已安装的 agent');
    console.log('提示: 显式指定 agent:`trae-skills add-all -a trae-cn`');
    console.log('或装一个 Trae / Claude Code / Codex / Cursor 后再试。');
    return [];
  }
  // 默认探测 → 全选,但仍按 name 去重
  const seen = new Set();
  return installed.filter((a) => {
    if (seen.has(a.name)) return false;
    seen.add(a.name);
    return true;
  });
}

/**
 * 解析 agent 目标目录 — 全局 vs 项目级。
 * @param {{globalSkillsDir: string, skillsDir: string}} agent
 * @param {boolean} isGlobal
 * @returns {string|null}
 */
function resolveAgentDir(agent, isGlobal) {
  if (isGlobal) return agent.globalSkillsDir;
  const dir = resolveTargetDir(agent.skillsDir, false);
  return dir;
}

// inquirer confirm 抽象 — 仅在确实需要 confirm 时用
async function confirm(message) {
  const { confirm } = await import('@inquirer/prompts');
  return confirm({ message, default: true });
}