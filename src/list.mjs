/**
 * src/list.mjs — trae-skills list
 *
 * 列出指定 agent 已装的 skills
 */
import { existsSync, lstatSync, readdirSync, statSync } from 'node:fs';
import { join, basename } from 'node:path';
import { getAgent, detectInstalledAgents, listAllAgents } from './agents.mjs';
import { printInfo, parseArgs, resolveTargetDir } from './utils.mjs';

export async function runList(args) {
  const opts = parseArgs(args);
  const isGlobal = !!opts.flags.g || !!opts.flags['trae-cn'];
  const agentArg = opts.flags.a
    ? Array.isArray(opts.flags.a)
      ? opts.flags.a
      : [opts.flags.a]
    : null;

  // 要列的 agents: 显式指定 > 自动检测本机已装 > 全部
  let targetAgents;
  if (agentArg) {
    targetAgents = agentArg.map((n) => getAgent(n)).filter(Boolean);
  } else if (isGlobal) {
    // 全局模式列出本机所有已装 agent
    targetAgents = detectInstalledAgents();
  } else {
    // 项目模式：列出本机所有已装 agent
    targetAgents = detectInstalledAgents();
  }

  if (targetAgents.length === 0) {
    printInfo('未检测到任何 agent（试试 -a <name> 强制指定）');
    return;
  }

  let totalCount = 0;
  for (const agent of targetAgents) {
    const dir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
    if (!dir) continue;
    const items = listSkillsIn(dir);
    totalCount += items.length;
    printAgentSkills(agent, dir, items, isGlobal);
  }
  console.log();
  console.log(`总计: ${totalCount} 个 skill`);
}

function listSkillsIn(dir) {
  if (!existsSync(dir)) return [];
  try {
    return readdirSync(dir, { withFileTypes: true })
      .filter((e) => {
        // On Windows, junctions: isSymbolicLink=true but lstat.isDirectory=false.
        // Use statSync (follows link) to detect real type.
        try {
          return statSync(join(dir, e.name)).isDirectory();
        } catch {
          return false;
        }
      })
      .map((e) => {
        const full = join(dir, e.name);
        let method = '?';
        try {
          method = lstatSync(full).isSymbolicLink() ? 'symlink' : 'copy';
        } catch {}
        return { name: e.name, method };
      });
  } catch {
    return [];
  }
}

function printAgentSkills(agent, dir, items, isGlobal) {
  console.log();
  console.log(`[${agent.displayName}] ${dir}${isGlobal ? '  (global)' : '  (project)'}`);
  if (items.length === 0) {
    console.log('  (空)');
    return;
  }
  for (const it of items) {
    const icon = it.method === 'symlink' ? '🔗' : '📁';
    console.log(`  ${icon}  ${it.name}`);
  }
}
