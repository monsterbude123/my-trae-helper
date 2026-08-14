#!/usr/bin/env node
/**
 * self-improving-agent shim (本地实现,非外部 CLI)
 *
 * 设计:
 *   - 这不是真正的 SIA CLI,是 .husky/post-commit 调用的轻量 shim
 *   - 把"会话级 hint"(git log / 反例)沉淀到 $HOME/.self-improving-agent/.learnings/
 *   - 符合 SIA SKILL.md 的日志格式 (LRN- / ERR- / FEAT- 前缀)
 *
 * 子命令:
 *   reflect [--since <commit>] [--auto] [--quiet]
 *     读 git log --since=<commit> 之后未落盘的反例/经验,append 到 .learnings/*.md
 *
 * 退码:
 *   0 = 成功或无变更
 *   1 = 致命错误(仅 --strict 才用,默认永不返回 1)
 *
 * 关联:
 *   - .trae/rules/learning.md §5 路径 C
 *   - .husky/post-commit (调用方)
 *   - .agents/skills/self-improving-agent/SKILL.md (格式参考)
 */

import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, appendFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';

const HOME = process.env.SELF_IMPROVING_HOME || join(homedir(), '.self-improving-agent');
const LEARN_DIR = join(HOME, '.learnings');

function nowISO() { return new Date().toISOString(); }
function today() {
  return nowISO().slice(0, 10).replace(/-/g, '');
}
function nextId(prefix) {
  // LRN-20260814-001 风格,扫同前缀找 max
  try {
    const files = ['LEARNINGS.md', 'ERRORS.md', 'FEATURE_REQUESTS.md'];
    let max = 0;
    for (const f of files) {
      const p = join(LEARN_DIR, f);
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
  if (!existsSync(LEARN_DIR)) {
    mkdirSync(LEARN_DIR, { recursive: true });
  }
  for (const f of ['LEARNINGS.md', 'ERRORS.md', 'FEATURE_REQUESTS.md']) {
    const p = join(LEARN_DIR, f);
    if (!existsSync(p)) {
      // 仅首次创建带 header
      const header =
        f === 'LEARNINGS.md'      ? '# Learnings\n\n> 跨会话经验沉淀(自动生成)\n' :
        f === 'ERRORS.md'         ? '# Errors\n\n> 命令/工具失败(自动生成)\n' :
                                    '# Feature Requests\n\n> 用户表态"应该能 XXX"(自动生成)\n';
      appendFileSync(p, header, 'utf8');
    }
  }
}

function appendEntry(file, header, body) {
  const p = join(LEARN_DIR, file);
  appendFileSync(p, `\n---\n\n${header}\n${body}\n`, 'utf8');
}

function readSince(sha) {
  // git log <sha>..HEAD --oneline (反向:从 <sha> 到当前)
  // --since 用 ref~1 也行,这里用 ref..HEAD 更稳
  try {
    const out = execFileSync('git', ['log', `${sha}..HEAD`, '--oneline', '--no-decorate'], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    return out.trim().split('\n').filter(Boolean);
  } catch (e) {
    return [];
  }
}

function cmdReflect(args) {
  // 解析参数
  let since = null;
  let auto = false;
  let quiet = false;
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--since') since = args[++i];
    else if (a === '--auto') auto = true;
    else if (a === '--quiet') quiet = true;
  }

  // 当前 commit
  let head;
  try {
    head = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
  } catch {
    if (!quiet) console.error('[sia-shim] not in a git repo, skip');
    return 0;
  }
  const sinceRef = since || `${head}~1`;

  // 读 commit log
  const commits = readSince(sinceRef);
  if (commits.length === 0) {
    if (!quiet) console.log('[sia-shim] no new commits since', sinceRef);
    return 0;
  }

  ensureHome();

  // 每条 commit 写一条 LRN
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

  return 0;
}

function usage() {
  console.log('Usage: self-improving-agent <command> [args]');
  console.log('');
  console.log('Commands:');
  console.log('  reflect [--since <ref>] [--auto] [--quiet]');
  console.log('    提取 git log 自 <ref> 起的 commits,写入 ~/.self-improving-agent/.learnings/LEARNINGS.md');
  console.log('');
  console.log('Env:');
  console.log('  SELF_IMPROVING_HOME  覆盖默认 $HOME/.self-improving-agent');
}

function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  const rest = argv.slice(1);
  if (!cmd || cmd === '--help' || cmd === '-h') {
    usage();
    return 0;
  }
  try {
    switch (cmd) {
      case 'reflect':
        return cmdReflect(rest);
      default:
        console.error(`[sia-shim] unknown command: ${cmd}`);
        usage();
        return 0; // 不阻断
    }
  } catch (e) {
    console.error(`[sia-shim] error: ${e.message}`);
    return 0; // 不阻断
  }
}

main();
