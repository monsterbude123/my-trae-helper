#!/usr/bin/env node
// scripts/intent-classifier.mjs
// 识别"本次 git commit / push 改了啥 → 抽成可机读的 intents"
//
// 用法:
//   node scripts/intent-classifier.mjs --staged    # 解析 git diff --cached
//   node scripts/intent-classifier.mjs --commits <sha1> <sha2>   # 解析两 commit 间 diff
//   node scripts/intent-classifier.mjs --files <file1> <file2>    # 直接给文件列表
//
// 输出(单行 JSON,manifest-assert 直接 parse):
//   {"intents":[{"kind":"add-skill","skill":"trae-security-review","path":"skill-markets/trae-security-review/SKILL.md"}, ...]}
//
// 分类规则(沿用 AGENTS.md §1 铁律 #7:最少规则覆盖 ≥80% 真实场景):
//   skill-markets/<x>/SKILL.md                  → add-skill / fix-skill / refactor-skill
//     kind 由 commit msg 前缀决定(add: / fix: / refactor:),缺省视为 modify-skill
//   skill-markets/<x>/scripts/<y>.<ext>         → add-script / modify-script
//   skill-markets/<x>/schemas/<y>.<ext>         → add-schema / modify-schema
//   skill-markets/<x>/pages/<y>.<ext>           → add-page / modify-page
//   skill-markets/<x>/tests/<y>.<ext>           → add-test / modify-test
//   skill-markets/<x>/references/<y>.<ext>      → modify-doc
//
// 退出码:0 总是成功(分类失败也只是空 intents,不阻断)

// 只用 node 内置,绝无依赖
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

// ---------- 参数解析 ----------
function parseArgs(argv) {
  const args = { mode: null, commits: [], files: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--staged') args.mode = 'staged';
    else if (a === '--commits') {
      args.mode = 'commits';
      args.commits = [argv[++i], argv[++i]];
    }
    else if (a === '--files') {
      args.mode = 'files';
      for (i++; i < argv.length; i++) args.files.push(argv[i]);
      break;
    }
  }
  return args;
}

// ---------- 取文件列表 ----------
function getFiles(args) {
  try {
    if (args.mode === 'staged') {
      const out = execFileSync('git', ['diff', '--name-only', '--cached'], { encoding: 'utf8' });
      return out.split('\n').filter(Boolean);
    }
    if (args.mode === 'commits') {
      const out = execFileSync('git', ['diff', '--name-only', args.commits[0], args.commits[1]], { encoding: 'utf8' });
      return out.split('\n').filter(Boolean);
    }
    if (args.mode === 'files') return args.files;
  } catch (e) {
    // git 命令失败(非 git 仓库 / 没 commit 等)→ 安静降级为空
    return [];
  }
  return [];
}

// ---------- 取最近一次 commit msg(用于细分 add/fix/refactor) ----------
function getLastCommitPrefix() {
  try {
    const msg = execFileSync('git', ['log', '-1', '--pretty=%s'], { encoding: 'utf8' }).trim();
    const m = msg.match(/^(add|fix|refactor|docs|test|chore):/i);
    return m ? m[1].toLowerCase() : null;
  } catch { return null; }
}

// ---------- 分类主逻辑 ----------
function classify(files, commitPrefix) {
  const intents = [];
  for (const f of files) {
    // 只处理 skill-markets/<x>/... 路径
    const m = f.match(/^skill-markets\/([^/]+)\/(.+)$/);
    if (!m) continue;
    const [, skill, rest] = m;
    let kind = 'modify-skill';
    let target = skill;

    if (rest === 'SKILL.md') {
      kind = commitPrefix === 'fix' ? 'fix-skill'
           : commitPrefix === 'refactor' ? 'refactor-skill'
           : 'add-skill';
      target = skill;
    } else if (rest.startsWith('scripts/')) {
      kind = commitPrefix === 'fix' ? 'fix-script' : 'add-script';
      target = `${skill}/${rest}`;
    } else if (rest.startsWith('schemas/')) {
      kind = commitPrefix === 'fix' ? 'fix-schema' : 'add-schema';
      target = `${skill}/${rest}`;
    } else if (rest.startsWith('pages/')) {
      kind = commitPrefix === 'fix' ? 'fix-page' : 'add-page';
      target = `${skill}/${rest}`;
    } else if (rest.startsWith('tests/')) {
      kind = commitPrefix === 'fix' ? 'fix-test' : 'add-test';
      target = `${skill}/${rest}`;
    } else if (rest.startsWith('references/')) {
      kind = 'modify-doc';
      target = `${skill}/${rest}`;
    } else {
      // 其他子路径(reports / audit_reports / scenarios 等)— 不参与 Manifest 断言
      continue;
    }

    intents.push({ kind, skill, target, path: f });
  }
  return intents;
}

// ---------- 入口 ----------
const args = parseArgs(process.argv.slice(2));
const files = getFiles(args);
const prefix = getLastCommitPrefix();
const intents = classify(files, prefix);

process.stdout.write(JSON.stringify({ intents }) + '\n');