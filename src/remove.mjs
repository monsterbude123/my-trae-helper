/**
 * src/remove.mjs — trae-skills remove <skill-name>
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { checkbox, confirm } from '@inquirer/prompts';
import { getAgent, detectInstalledAgents, listAllAgents } from './agents.mjs';
import { uninstallSkill } from './installer.mjs';
import {
  printSuccess,
  printError,
  printInfo,
  printWarn,
  parseArgs,
  resolveTargetDir,
} from './utils.mjs';

export async function runRemove(args) {
  const opts = parseArgs(args);
  const skillArg = opts._[0];
  const isGlobal = !!opts.flags.g || !!opts.flags['trae-cn'];
  const skipConfirm = !!opts.flags.y;
  const dryRun = !!opts.flags['dry-run'];
  const agentArg = opts.flags.a
    ? Array.isArray(opts.flags.a)
      ? opts.flags.a
      : [opts.flags.a]
    : null;

  const targetAgents = agentArg
    ? agentArg.map((n) => getAgent(n)).filter(Boolean)
    : detectInstalledAgents();

  if (targetAgents.length === 0) {
    printError('未检测到任何 agent');
    return;
  }

  // 收集所有位置的所有已装 skills
  const matrix = []; // [{ agent, dir, name, method }]
  for (const agent of targetAgents) {
    const dir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
    if (!dir || !existsSync(dir)) continue;
    const { readdirSync, lstatSync, statSync } = await import('node:fs');
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      let isDir = false;
      try {
        isDir = statSync(join(dir, e.name)).isDirectory();
      } catch {
        continue;
      }
      if (!isDir) continue;
      matrix.push({ agent, dir, name: e.name });
    }
  }

  // 过滤
  let targets = matrix;
  if (skillArg) {
    const lower = skillArg.toLowerCase();
    targets = matrix.filter((m) => m.name.toLowerCase() === lower);
    if (targets.length === 0) {
      printError(`未找到已装的 skill: ${skillArg}`);
      return;
    }
  } else {
    if (matrix.length === 0) {
      printInfo('没有可卸载的 skill');
      return;
    }
    // 交互选择
    const labels = matrix.map((m) => ({
      name: `${m.name}  (${m.agent.displayName})`,
      value: m,
    }));
    const picked = await checkbox({
      message: '选择要卸载的 skill (空格多选):',
      choices: labels,
    });
    targets = picked;
  }

  if (targets.length === 0) {
    printWarn('未选任何 skill，已取消');
    return;
  }

  if (!skipConfirm) {
    const ok = await confirm({
      message: `确认卸载 ${targets.length} 个 skill?`,
      default: false,
    });
    if (!ok) {
      printInfo('已取消');
      return;
    }
  }

  for (const t of targets) {
    try {
      const result = uninstallSkill({ targetDir: t.dir, skillName: t.name, dryRun });
      if (typeof result === 'string') {
        // dryRun 返回字符串
        printInfo(result);
      } else if (result) {
        printSuccess(`已卸载: ${t.name}  (从 ${t.agent.displayName})`);
      }
    } catch (err) {
      printError(`卸载失败: ${t.name} (${t.agent.displayName}): ${err.message}`);
    }
  }
}
