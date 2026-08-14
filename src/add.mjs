/**
 * src/add.mjs — trae-skills add <skill-name>
 *
 * 流程: 扫 skill-markets → 选 skill → 选 agent(s) → 确认 → 软链/复制
 */
import { resolve } from 'node:path';
import { select, checkbox, confirm } from '@inquirer/prompts';
import { scanSkills, findSkill } from './scanner.mjs';
import { getAgent, detectInstalledAgents, listAllAgents } from './agents.mjs';
import { installSkill } from './installer.mjs';
import {
  printSuccess,
  printError,
  printInfo,
  printWarn,
  parseArgs,
  resolveTargetDir,
  SKILL_MARKETS_DIR,
} from './utils.mjs';

export async function runAdd(args) {
  const opts = parseArgs(args);
  const skillArg = opts._[0];
  // -g 或 --trae-cn 都触发全局（trae-cn 是更明确的语义）
  const isGlobal = !!opts.flags.g || !!opts.flags['trae-cn'];
  const useCopy = !!opts.flags.copy;
  const skipConfirm = !!opts.flags.y;
  const dryRun = !!opts.flags['dry-run'];
  // -a 出现多次 → 数组；出现一次 → 字符串
  const agentArg = opts.flags.a
    ? Array.isArray(opts.flags.a)
      ? opts.flags.a
      : [opts.flags.a]
    : null;

  // 1. 扫所有 skills
  const skills = scanSkills(SKILL_MARKETS_DIR);
  if (skills.length === 0) {
    printError('未在 skill-markets/ 发现任何 skill');
    return;
  }

  // 2. 选 skill
  let skill;
  if (skillArg) {
    skill = findSkill(skillArg, SKILL_MARKETS_DIR);
    if (!skill) {
      printError(`未找到 skill: ${skillArg}`);
      console.log('\n可用的 skills:');
      for (const s of skills) {
        console.log(`  - ${s.dirName}  (${s.name}@${s.version})`);
      }
      process.exit(1);
    }
  } else {
    skill = await select({
      message: '选择要安装的 skill:',
      choices: skills.map((s) => ({
        name: `${s.dirName}@${s.version}  — ${truncate(s.description, 60)}`,
        value: s,
      })),
    });
  }
  printInfo(`已选: ${skill.dirName}@${skill.version}`);

  // DEPRECATED 拦截（2026-08-14 聚合归档）
  // SKILL.md frontmatter 含 `status: deprecated` + `redirect_to` → BLOCK 并指向新 skill
  if (skill.status === 'deprecated') {
    const target = skill.redirectTo || 'unknown';
    printError(`${skill.dirName} 已归档为 DEPRECATED`);
    console.error(`重定向目标: ${target}`);
    console.error(`说明: 能力已并入 ${target}，加载旧触发词时主 Agent 应改用 ${target}。`);
    console.error(`如确认仍需安装兼容壳，可加 --force-redirect 跳过拦截（不推荐）。`);
    process.exit(2);
  }

  // 显示依赖提示
  if (skill.requires?.skills?.length) {
    printWarn(`此 skill 依赖: ${skill.requires.skills.join(', ')}（需单独装）`);
  }

  // 3. 选 agent
  let targetAgents;
  if (agentArg) {
    targetAgents = agentArg.map((n) => getAgent(n)).filter(Boolean);
    if (targetAgents.length === 0) {
      printError(`未找到指定的 agent: ${agentArg.join(', ')}`);
      console.log('\n可用的 agents:');
      for (const a of listAllAgents()) {
        console.log(`  - ${a.name.padEnd(16)}  ${a.displayName}`);
      }
      process.exit(1);
    }
  } else {
    const installed = detectInstalledAgents();
    if (installed.length === 0) {
      printError('未检测到任何已安装的 agent');
      console.log('提示: 至少装一个 Trae / Claude Code / Codex / Cursor 后再试。');
      console.log('或显式指定 agent: trae-skills add ' + skill.dirName + ' -a trae-cn');
      process.exit(1);
    }
    const picked = await checkbox({
      message: '安装到哪些 agent (空格多选, 回车确认):',
      choices: installed.map((a) => ({ name: `${a.displayName} (${a.name})`, value: a })),
    });
    targetAgents = picked;
  }

  if (targetAgents.length === 0) {
    printWarn('未选任何 agent，已取消');
    return;
  }

  // 4. 确认
  if (!skipConfirm) {
    const ok = await confirm({
      message: `安装 ${skill.dirName} 到 ${targetAgents.length} 个 agent${isGlobal ? ' (全局)' : ''}?`,
      default: true,
    });
    if (!ok) {
      printInfo('已取消');
      return;
    }
  }

  // 5. 装
  for (const agent of targetAgents) {
    const targetDir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
    if (!targetDir) {
      printError(`无法解析 ${agent.name} 的目标目录`);
      continue;
    }
    try {
      const link = installSkill({
        sourcePath: skill.sourcePath,
        targetDir,
        skillName: skill.dirName,
        method: useCopy ? 'copy' : 'symlink',
        dryRun,
      });
      printSuccess(`${skill.dirName} → ${link}`);
    } catch (err) {
      printError(`安装到 ${agent.displayName} 失败: ${err.message}`);
    }
  }
}

function truncate(s, n) {
  s = String(s).replace(/\n/g, ' ').trim();
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}
