/**
 * src/update.mjs — trae-skills update [skill-name]
 *
 * 因为本 CLI 默认 symlink 安装，update = 重新创建链接（让源文件生效）
 * 如果是 copy 安装，update = 删除后重新复制
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { getAgent, detectInstalledAgents } from './agents.mjs';
import { installSkill, uninstallSkill } from './installer.mjs';
import { scanSkills, findSkill } from './scanner.mjs';
import {
  printSuccess,
  printError,
  printInfo,
  parseArgs,
  resolveTargetDir,
  SKILL_MARKETS_DIR,
} from './utils.mjs';

export async function runUpdate(args) {
  const opts = parseArgs(args);
  const skillArg = opts._[0];
  const isGlobal = !!opts.flags.g;
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

  // 找所有已装的 skills
  const matrix = [];
  for (const agent of targetAgents) {
    const dir = isGlobal ? agent.globalSkillsDir : resolveTargetDir(agent.skillsDir, false);
    if (!dir || !existsSync(dir)) continue;
    const { readdirSync, statSync } = await import('node:fs');
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
  }

  if (targets.length === 0) {
    printInfo('没有需要 update 的 skill');
    return;
  }

  // 扫本地 marketplace 找匹配源
  const allSkills = scanSkills(SKILL_MARKETS_DIR);

  for (const t of targets) {
    const source = allSkills.find((s) => s.dirName === t.name);
    if (!source) {
      printError(`找不到源: ${t.name}（可能已从 skill-markets 移除，跳过）`);
      continue;
    }
    try {
      // 重新安装（uninstall + install）
      uninstallSkill({ targetDir: t.dir, skillName: t.name });
      installSkill({
        sourcePath: source.sourcePath,
        targetDir: t.dir,
        skillName: t.name,
        method: 'symlink',
      });
      printSuccess(`已更新: ${t.name}  (${t.agent.displayName}) → ${source.version}`);
    } catch (err) {
      printError(`更新失败: ${t.name}: ${err.message}`);
    }
  }
}
