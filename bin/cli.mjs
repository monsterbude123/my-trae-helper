#!/usr/bin/env node
/**
 * @my-trae-helper/cli — Trae IDE skills CLI
 *
 * Usage:
 *   trae-skills add <skill-name>       Install a skill
 *   trae-skills list                   List installed skills
 *   trae-skills remove <skill-name>    Remove a skill
 *   trae-skills update [skill-name]    Update skills
 *   trae-skills init <skill-name>      Create a new SKILL.md template
 *   trae-skills create <name>          Create a new skill package (三层控制)
 *   trae-skills verify <name>          Verify a skill (执行所有守卫)
 *
 * Entry point — only routes commands. Logic lives in src/*.mjs.
 */
import { printBanner, printHelp, printError, getPackageJson } from '../src/utils.mjs';
import { runAdd } from '../src/add.mjs';
import { runList } from '../src/list.mjs';
import { runRemove } from '../src/remove.mjs';
import { runUpdate } from '../src/update.mjs';
import { runInit } from '../src/init.mjs';
import { runCreate } from '../src/create.mjs';
import { runVerify } from '../src/verify.mjs';

const commands = {
  add: { run: runAdd, desc: 'Install a skill from skill-markets' },
  list: { run: runList, desc: 'List installed skills' },
  ls: { run: runList, desc: 'Alias for list' },
  remove: { run: runRemove, desc: 'Remove an installed skill' },
  rm: { run: runRemove, desc: 'Alias for remove' },
  update: { run: runUpdate, desc: 'Update installed skills' },
  up: { run: runUpdate, desc: 'Alias for update' },
  init: { run: runInit, desc: 'Create a new SKILL.md template' },
  create: { run: runCreate, desc: 'Create a new skill package (三层控制)' },
  verify: { run: runVerify, desc: 'Verify a skill (执行所有守卫)' },
};

async function main() {
  const [, , cmd, ...args] = process.argv;

  // --version
  if (cmd === '--version' || cmd === '-v') {
    const pkg = getPackageJson();
    console.log(`${pkg.name} v${pkg.version}`);
    process.exit(0);
  }

  // --help / 无命令
  if (!cmd || cmd === '--help' || cmd === '-h') {
    printBanner();
    printHelp(commands);
    process.exit(0);
  }

  // 路由
  const entry = commands[cmd];
  if (!entry) {
    printError(`未知命令: ${cmd}`);
    console.log('\n可用命令:');
    for (const [name, e] of Object.entries(commands)) {
      console.log(`  ${name.padEnd(8)} ${e.desc}`);
    }
    process.exit(1);
  }

  try {
    await entry.run(args);
  } catch (err) {
    if (err?.name === 'ExitPromptError') {
      // 用户 Ctrl+C
      process.exit(130);
    }
    printError(err.message || String(err));
    if (process.env.DEBUG) console.error(err.stack);
    process.exit(1);
  }
}

main();
