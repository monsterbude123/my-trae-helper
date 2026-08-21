#!/usr/bin/env node
/**
 * user-self-improving shim v4 (A+B+C 组合,2026-08-14 创建,2026-08-21 迁移,D-7 彻底废弃旧路径)
 *
 * 三个子命令对应三个自动化路径:
 *   reflect     (B) 扫 logs/*.log 的 warn/error 行 + git log,append .learnings/*
 *   log         (A) 主 agent 显式调用,直接落一条 entry
 *   scan-hints  (C) 扫 logs/agent-hints.jsonl(主 agent 写入的会话级 hint)
 *
 * 数据落地: --home 指定路径/.learnings/{LEARNINGS,ERRORS,FEATURE_REQUESTS}.md
 * HOME 解析(D-7 彻底废弃 SELF_IMPROVING_HOME 旧名 + .self-improving-agent 旧路径,2026-08-21+):
 *   1. --home CLI
 *   2. USER_SELF_IMPROVING_HOME env(唯一接受,2026-08-21+)
 *   3. 默认 $HOME/.user-self-improving
 *
 * 已废弃(不再支持,2026-08-21 之前):旧 env `SELF_IMPROVING_HOME` + 旧路径 `.self-improving-agent`。
 * 旧数据已通过 2026-08-21 的 `migrate` 子命令一次性 cp 到新路径(代码已删除,旧数据继续可用)。
 *
 * 关联:
 *   - skill-markets/user-self-improving/SKILL.md
 *   - .husky/post-commit (调用方,D-7 已同步切到新路径)
 *   - 关联反例: skill-markets/agent-dev-control-kit/references/trap-instructions.yaml AP-8
 */

import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, appendFileSync, renameSync, cpSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

// HOME 解析(每次重新计算,因为 main() 会修改 process.env)
// 优先级(D-7 已彻底废弃 SELF_IMPROVING_HOME 旧名 + .self-improving-agent 旧路径,2026-08-21+):
//   1. --home CLI
//   2. USER_SELF_IMPROVING_HOME env(2026-08-21+ 唯一接受)
//   3. 默认 $HOME/.user-self-improving
// 注意: 跨平台时(homedir)Windows native node 返回 C:\Users\foo(正确);
//       WSL→Windows 调 node 时,如果想写到仓库内,显式传 --home "$PWD/.user-self-improving"
function getHome() {
  const argv = process.argv;
  for (let i = 0; i < argv.length - 1; i++) {
    if (argv[i] === '--home') return argv[i + 1];
  }
  // 唯一接受的新名 env(2026-08-21+)
  if (process.env.USER_SELF_IMPROVING_HOME) return process.env.USER_SELF_IMPROVING_HOME;
  // 默认路径
  return join(homedir(), '.user-self-improving');
}
function getLearnDir() {
  return join(getHome(), '.learnings');
}

// ─── 通用工具 ─────────────────────────────────────────────

function nowISO() { return new Date().toISOString(); }
function today() { return nowISO().slice(0, 10).replace(/-/g, ''); }

function nextId(prefix) {
  try {
    const learnDir = getLearnDir();
    const files = ['LEARNINGS.md', 'ERRORS.md', 'FEATURE_REQUESTS.md'];
    let max = 0;
    for (const f of files) {
      const p = join(learnDir, f);
      if (!existsSync(p)) continue;
      const txt = readFileSync(p, 'utf8');
      const re = new RegExp(`## \\[${prefix}-\\d{8}-(\\d{3})\\]`, 'g');
      let m;
      while ((m = re.exec(txt)) !== null) {
        const n = parseInt(m[1], 10);
        if (n > max) max = n;
      }
    }
    return `${prefix}-${today()}-${String(max + 1).padStart(3, '0')}`;
  } catch {
    return `${prefix}-${today()}-001`;
  }
}

function ensureHome() {
  const learnDir = getLearnDir();
  if (!existsSync(learnDir)) mkdirSync(learnDir, { recursive: true });
  for (const f of ['LEARNINGS.md', 'ERRORS.md', 'FEATURE_REQUESTS.md']) {
    const p = join(learnDir, f);
    if (!existsSync(p)) {
      const header =
        f === 'LEARNINGS.md'      ? '# Learnings\n\n> 跨会话经验沉淀(自动生成)\n' :
        f === 'ERRORS.md'         ? '# Errors\n\n> 命令/工具失败(自动生成)\n' :
                                    '# Feature Requests\n\n> 用户表态"应该能 XXX"(自动生成)\n';
      appendFileSync(p, header, 'utf8');
    }
  }
}

function appendEntry(file, header, body) {
  const p = join(getLearnDir(), file);
  ensureHome();
  appendFileSync(p, `\n---\n\n${header}\n${body}\n`, 'utf8');
}

// ─── B: 扫 .log 找 warn/error 行 → ERRORS.md ──────────────

function scanLogsForWarnings(logPaths) {
  const hits = [];
  const patterns = [
    /\bwarn[:：]\s+(.+)/i,
    /\bwarning[:：]\s+(.+)/i,
    /\[FATAL_ERROR\]/i,
    /\b(command not found|enoent|eacces|eperm)\b/i,
    /\bexit(?:ed)?\s+(?:with\s+)?(?:code\s+)?(?:1|2|127|128|130|137|139|143)\b/i,
  ];
  for (const logPath of logPaths) {
    if (!existsSync(logPath)) continue;
    const txt = readFileSync(logPath, 'utf8');
    const lines = txt.split('\n');
    const start = Math.max(0, lines.length - 200);
    for (let i = start; i < lines.length; i++) {
      const line = lines[i];
      for (const re of patterns) {
        if (re.test(line)) {
          hits.push({ source: logPath, line: i + 1, text: line.trim().slice(0, 240) });
          break;
        }
      }
    }
  }
  return hits;
}

function writeErrorsFromLogHits(hits, quiet) {
  if (hits.length === 0) return 0;
  ensureHome();
  let n = 0;
  for (const h of hits) {
    const sig = h.text.slice(0, 80);
    const errFile = join(getLearnDir(), 'ERRORS.md');
    const existing = existsSync(errFile) ? readFileSync(errFile, 'utf8') : '';
    if (existing.includes(sig)) continue;

    const id = nextId('ERR');
    const header = `## [${id}] post_commit_warn`;
    const body = [
      `**Logged**: ${nowISO()}`,
      `**Priority**: medium`,
      `**Status**: pending`,
      `**Area**: config`,
      ``,
      `### Summary`,
      `post-commit 钩子日志中检测到 warn/error`,
      ``,
      `### Error`,
      '```',
      h.text,
      '```',
      ``,
      `### Context`,
      `- Source log: ${h.source}`,
      `- Line: ${h.line}`,
      ``,
      `### Metadata`,
      `- Source: log_scan`,
      `- Tags: auto-captured, hook-warning`,
      ``,
    ].join('\n');
    appendEntry('ERRORS.md', header, body);
    n++;
    if (!quiet) console.log(`[sia-shim] wrote ${id} ← ${h.text.slice(0, 60)}`);
  }
  return n;
}

// ─── C: 扫 logs/agent-hints.jsonl ─────────────────────────

function scanAgentHints(hintPath, quiet) {
  if (!existsSync(hintPath)) return { errors: 0, features: 0, learnings: 0 };
  const txt = readFileSync(hintPath, 'utf8');
  const lines = txt.split('\n').filter(Boolean);
  if (lines.length === 0) return { errors: 0, features: 0, learnings: 0 };

  ensureHome();
  let errors = 0, features = 0, learnings = 0;

  for (const line of lines) {
    let h;
    try { h = JSON.parse(line); } catch { continue; }
    if (h.processed) continue;

    const type = (h.type || 'error').toLowerCase();
    const summary = h.summary || h.message || h.error || 'no summary';
    const detail = h.detail || h.context || '';
    const priority = h.priority || 'medium';
    const area = h.area || 'config';
    const source = h.source || 'agent_hint';

    let file, prefix, category;
    if (type === 'feature' || type === 'feat') {
      file = 'FEATURE_REQUESTS.md'; prefix = 'FEAT'; category = 'feature_request';
    } else if (type === 'learning' || type === 'learn') {
      file = 'LEARNINGS.md'; prefix = 'LRN'; category = 'best_practice';
    } else {
      file = 'ERRORS.md'; prefix = 'ERR'; category = 'agent_error';
    }
    const id = nextId(prefix);
    const header = `## [${id}] ${category}`;
    const body = [
      `**Logged**: ${nowISO()}`,
      `**Priority**: ${priority}`,
      `**Status**: pending`,
      `**Area**: ${area}`,
      ``,
      `### Summary`,
      summary,
      ``,
      `### Details`,
      detail || '(no detail)',
      ``,
      `### Metadata`,
      `- Source: ${source}`,
      `- Tags: agent-hint, auto-captured`,
      ``,
    ].join('\n');
    appendEntry(file, header, body);
    if (file === 'ERRORS.md') errors++;
    else if (file === 'FEATURE_REQUESTS.md') features++;
    else learnings++;
    if (!quiet) console.log(`[sia-shim] wrote ${id} ← ${summary.slice(0, 50)}`);
  }

  try {
    renameSync(hintPath, hintPath + '.processed.' + Date.now());
  } catch {}

  return { errors, features, learnings };
}

// ─── A: log 子命令(主 agent 显式调用) ───────────────────

function cmdLog(args) {
  let type = 'error';
  let summary = '';
  let detail = '';
  let priority = 'medium';
  let area = 'config';
  let quiet = false;

  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--type') type = args[++i];
    else if (a === '--summary' || a === '-s') summary = args[++i];
    else if (a === '--detail' || a === '-d') detail = args[++i];
    else if (a === '--priority' || a === '-p') priority = args[++i];
    else if (a === '--area' || a === '-a') area = args[++i];
    else if (a === '--quiet') quiet = true;
    else if (a.startsWith('--')) { /* skip unknown */ }
    else if (!summary) summary = a;
    else detail = (detail ? detail + ' ' : '') + a;
  }
  if (!summary) {
    console.error('[sia-shim] log: --summary is required');
    return 0;
  }

  let file, prefix, category;
  if (type === 'feature' || type === 'feat') {
    file = 'FEATURE_REQUESTS.md'; prefix = 'FEAT'; category = 'feature_request';
  } else if (type === 'learning' || type === 'learn') {
    file = 'LEARNINGS.md'; prefix = 'LRN'; category = 'best_practice';
  } else {
    file = 'ERRORS.md'; prefix = 'ERR'; category = 'agent_error';
  }

  const id = nextId(prefix);
  const header = `## [${id}] ${category}`;
  const body = [
    `**Logged**: ${nowISO()}`,
    `**Priority**: ${priority}`,
    `**Status**: pending`,
    `**Area**: ${area}`,
    ``,
    `### Summary`,
    summary,
    ``,
    `### Details`,
    detail || '(no detail)',
    ``,
    `### Metadata`,
    `- Source: explicit_log`,
    `- Tags: agent-cmd, auto-captured`,
    ``,
  ].join('\n');
  appendEntry(file, header, body);
  if (!quiet) console.log(`[sia-shim] wrote ${id} (${type}) ← ${summary.slice(0, 50)}`);
  return 0;
}

// ─── reflect 子命令(commit log + 日志扫描 + hint 扫描) ───

function readSince(sha) {
  try {
    const out = execFileSync('git', ['log', `${sha}..HEAD`, '--oneline', '--no-decorate'], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    return out.trim().split('\n').filter(Boolean);
  } catch { return []; }
}

function cmdReflect(args) {
  let since = null;
  let auto = false;
  let quiet = false;
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--since') since = args[++i];
    else if (a === '--auto') auto = true;
    else if (a === '--quiet') quiet = true;
  }

  let head;
  try {
    head = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
  } catch {
    if (!quiet) console.error('[sia-shim] not in a git repo, skip');
    return 0;
  }
  const sinceRef = since || `${head}~1`;

  ensureHome();

  // 1) commit log → LEARNINGS
  const commits = readSince(sinceRef);
  for (const line of commits) {
    const [sha, ...rest] = line.split(' ');
    const subject = rest.join(' ');
    const id = nextId('LRN');
    const header = `## [${id}] best_practice`;
    const body = [
      `**Logged**: ${nowISO()}`,
      `**Priority**: low`,
      `**Status**: pending`,
      `**Area**: config`,
      ``,
      `### Summary`,
      `Commit ${sha.slice(0, 7)}: ${subject}`,
      ``,
      `### Details`,
      `自动从 post-commit 钩子提取(自改进 shim)`,
      ``,
      `### Metadata`,
      `- Source: git_commit`,
      `- Related Files: ${sha}`,
      `- Tags: auto-captured`,
      ``,
    ].join('\n');
    appendEntry('LEARNINGS.md', header, body);
    if (!quiet) console.log(`[sia-shim] wrote ${id} ← ${sha.slice(0, 7)} ${subject.slice(0, 40)}`);
  }

  // 2) 日志扫描 → ERRORS
  const cwd = process.cwd();
  // 默认扫项目内 hooks 日志;支持 --log <file>... 追加(测试用)
  const logPaths = [
    join(cwd, 'logs', 'post-commit-self-improve.log'),
    join(cwd, 'logs', 'pre-commit.log'),
    join(cwd, 'logs', 'pre-push.log'),
  ];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--log' && i + 1 < args.length) {
      logPaths.push(args[++i]);
    }
  }
  const logHits = scanLogsForWarnings(logPaths);
  const errN = writeErrorsFromLogHits(logHits, quiet);
  if (!quiet && errN > 0) console.log(`[sia-shim] scan-logs: ${errN} entries written to ERRORS.md`);

  // 3) agent-hints.jsonl → ERRORS/FEATURE_REQUESTS
  //    扫两个位置: 仓库内 logs/ + $HOME/.user-self-improving/logs/(2026-08-21+ 唯一路径)
  const hintPaths = [
    join(cwd, 'logs', 'agent-hints.jsonl'),
    join(getHome(), 'logs', 'agent-hints.jsonl'),
  ];
  let stats = { errors: 0, features: 0, learnings: 0 };
  for (const hp of hintPaths) {
    const s = scanAgentHints(hp, quiet);
    stats.errors += s.errors;
    stats.features += s.features;
    stats.learnings += s.learnings;
  }
  if (!quiet && (stats.errors + stats.features + stats.learnings) > 0) {
    console.log(`[sia-shim] scan-hints: ${stats.errors}E / ${stats.features}F / ${stats.learnings}L`);
  }

  return 0;
}

function usage() {
  console.log('Usage: self-improving-agent [--home <path>] <command> [args]');
  console.log('');
  console.log('Global:');
  console.log('  --home <path>   覆盖 HOME 路径(WSL 调 Windows native node 用)');
  console.log('');
  console.log('Commands:');
  console.log('  reflect [--since <ref>] [--auto] [--quiet]');
  console.log('    综合: 提取 commit log + 扫 hooks 日志 warn + 扫 agent-hints.jsonl');
  console.log('  log --type <error|feature|learning> --summary <text> [--detail <text>]');
  console.log('    主 agent 显式调用,直接落一条 entry(A 路径)');
  console.log('  scan-hints [--quiet]');
    console.log('    单独扫 logs/agent-hints.jsonl(C 路径)');
  console.log('');
  console.log('Env:');
  console.log('  USER_SELF_IMPROVING_HOME  覆盖默认 $HOME/.user-self-improving(2026-08-21+ 唯一接受)');
  console.log('');
  console.log('Default home(2026-08-21+):$HOME/.user-self-improving/');
  console.log('');
  console.log('DEPRECATED(2026-08-21 之前):旧 env `SELF_IMPROVING_HOME` + 旧路径 `.self-improving-agent` 已彻底废弃');
  console.log('  旧数据如需访问,请手动 cp 到 $HOME/.user-self-improving/');
}

function main() {
  const argv = process.argv.slice(2);
  // 提取全局选项 --home
  const filteredArgv = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--home' && i + 1 < argv.length) {
      // 同步到 process.env,让 getHome() 也能读到
      process.env.USER_SELF_IMPROVING_HOME = argv[i + 1];
      i++;
    } else {
      filteredArgv.push(argv[i]);
    }
  }
  const cmd = filteredArgv[0];
  const rest = filteredArgv.slice(1);
  if (!cmd || cmd === '--help' || cmd === '-h') { usage(); return 0; }
  try {
    switch (cmd) {
      case 'reflect':     return cmdReflect(rest);
      case 'log':         return cmdLog(rest);
      case 'scan-hints':  return cmdScanHintsMain(rest);
      default:
        console.error(`[sia-shim] unknown command: ${cmd}`);
        usage();
        return 0;
    }
  } catch (e) {
    console.error(`[sia-shim] error: ${e.message}`);
    return 0;
  }
}

function cmdScanHintsMain(args) {
  let quiet = false;
  for (const a of args) if (a === '--quiet') quiet = true;
  const cwd = process.cwd();
  const hintPaths = [
    join(cwd, 'logs', 'agent-hints.jsonl'),
    join(getHome(), 'logs', 'agent-hints.jsonl'),
  ];
  let stats = { errors: 0, features: 0, learnings: 0 };
  for (const hp of hintPaths) {
    const s = scanAgentHints(hp, quiet);
    stats.errors += s.errors;
    stats.features += s.features;
    stats.learnings += s.learnings;
  }
  if (!quiet) console.log(`[sia-shim] scan-hints: ${stats.errors}E / ${stats.features}F / ${stats.learnings}L`);
  return 0;
}

main();
