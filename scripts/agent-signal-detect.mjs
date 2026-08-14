#!/usr/bin/env node
/**
 * agent-signal-detect v1 (C 路径辅助,2026-08-14)
 *
 * 检测 AGENTS.md §4 列出的"用户表态信号",自动写 logs/agent-hints.jsonl
 * 供 post-commit 钩子落盘到 ERRORS/FEATURE_REQUESTS.md
 *
 * 用法:
 *   node scripts/agent-signal-detect.mjs "用户原始消息"
 *   echo "用户消息" | node scripts/agent-signal-detect.mjs
 *
 * 检测的信号(AGENTS.md §4):
 *   纠正类 → error hint (priority=high):
 *     "懂了吗" / "能懂了吗" / "你到底做啥" / "你确定" / "什么"
 *     "不对" / "错了" / "太复杂" / "简化" / "重构"
 *     [FATAL_ERROR] / ERROR: / 失败 / 报错
 *
 *   特性请求类 → feature hint (priority=medium):
 *     "能 XXX 吗" / "可以 XXX 吗" / "怎么" / "为什么"
 *     "应该" / "需要" / "希望" / "想要" / "再加" / "新增"
 *
 *   无命中 → noop(exit 0,不写文件)
 *
 * 关联:
 *   - AGENTS.md §4 用户表态信号
 *   - .trae/rules/learning.md §5 路径 C
 *   - self-improving-agent.mjs scan-hints 子命令
 */

import { appendFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';

// --home 支持: 写在 $HOME/.self-improving-agent/logs/agent-hints.jsonl
// 默认: homedir()/.self-improving-agent/logs/agent-hints.jsonl
function getHintPath() {
  const argv = process.argv;
  for (let i = 0; i < argv.length - 1; i++) {
    if (argv[i] === '--home') {
      return join(argv[i + 1], 'logs', 'agent-hints.jsonl');
    }
  }
  return join(homedir(), '.self-improving-agent', 'logs', 'agent-hints.jsonl');
}

async function readStdin() {
  return new Promise((resolve) => {
    let buf = '';
    try {
      process.stdin.setEncoding('utf8');
      process.stdin.on('data', (c) => { buf += c; });
      process.stdin.on('end', () => resolve(buf.trim()));
      process.stdin.on('error', () => resolve(''));
    } catch {
      resolve('');
    }
  });
}

async function main() {
  // 读取输入: 跳过 --home <path> 选项,只看真正的文本 argv
  // 优先 stdin,fallback 非 --home 的 argv 元素
  let text = '';
  const textArgs = process.argv.slice(2).filter((a, i, arr) => {
    if (a === '--home') return false;
    if (arr[i - 1] === '--home') return false;  // --home 的 value 跳过
    return true;
  });
  if (process.stdin && process.stdin.readable && textArgs.length === 0) {
    text = await readStdin();
  }
  if (!text && textArgs.length > 0) {
    text = textArgs.join(' ');
  }
  if (!text) {
    process.exit(0);
  }

  const CORRECTION_PATTERNS = [
    /(懂了吗|能懂了吗|你到底做啥|你确定)/,
    /(不对|错了|错了)/,
    /(太复杂|简化|重构|瘦身|革命性)/,
    /\[FATAL_ERROR\]/,
    /(ERROR|失败|报错|异常|panic)/i,
  ];

  const FEATURE_PATTERNS = [
    /(能\s*.+|可以\s*.+|怎么|为什么|为什么不|能不能|能否)/,
    /(应该|需要|希望|想要|再加|新增)/,
  ];

  let detected = null;
  let priority = 'low';

  if (CORRECTION_PATTERNS.some(re => re.test(text))) {
    detected = 'error';
    priority = 'high';
  } else if (FEATURE_PATTERNS.some(re => re.test(text))) {
    detected = 'feature';
    priority = 'medium';
  }

  if (!detected) process.exit(0);

  // 写 hint(用 getHintPath() 拿正确的路径,支持 --home)
  const hintPath = getHintPath();
  const logDir = dirname(hintPath);
  if (!existsSync(logDir)) mkdirSync(logDir, { recursive: true });

  const hint = {
    type: detected,
    summary: text.slice(0, 200),
    detail: '',
    priority,
    area: 'config',
    source: 'signal_detect',
    ts: new Date().toISOString(),
  };
  appendFileSync(hintPath, JSON.stringify(hint) + '\n', 'utf8');
  process.stderr.write(`[agent-signal] detected ${detected} ← ${text.slice(0, 50)}\n`);
}

main().catch(e => {
  process.stderr.write(`[agent-signal] error: ${e.message}\n`);
  process.exit(0);
});
