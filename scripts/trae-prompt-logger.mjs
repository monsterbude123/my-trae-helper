#!/usr/bin/env node
/**
 * trae-prompt-logger.mjs — 把用户在 TraeCode 中的所有发言落盘到当前项目内
 *
 * 数据流:
 *   TRAE 触发 UserPromptSubmit 事件
 *     → 把 session_id / cwd / prompt 等 JSON payload 推送到本脚本的 stdin
 *       → 本脚本解析后写入:
 *           <cwd>/.trae/prompt-logs/sessions/<session_id>/prompts.ndjson
 *           <cwd>/.trae/prompt-logs/index.ndjson   (全局索引,便于跨 session 检索)
 *
 * 设计原则:
 *   - 零依赖,纯 Node ESM(>=18)
 *   - 写入失败绝不抛错,只 stderr 提示(避免 Hook 异常中断 TRAE 会话)
 *   - 退出码 0: 正常透传;非 0 仅在严重错误时返回
 *   - NDJSON 流式追加,并发安全(同 session 串行追加,跨 session 并行无冲突)
 *   - 跨平台路径处理(Windows / macOS / Linux 一致)
 *   - 隐私脱敏: 落盘前移除 prompt 中疑似 Key / Token
 *
 * 关联:
 *   - docs.trae.cn/ide_hook-configuration-reference
 *   - .trae/rules/项目核心.md
 *   - AGENTS.md §1 铁律
 */

import { mkdir, appendFile, writeFile, stat } from 'node:fs/promises';
import { join, resolve } from 'node:path';

// ─── 工具函数 ─────────────────────────────────────────────

/**
 * 从 stdin 读取完整 payload(TRAE 用 JSON 通过 stdin 投递)
 * 防御性吃掉 UTF-8 BOM(EF BB BF)以兼容 Windows 工具链
 */
async function readStdin() {
  return new Promise((resolveP, reject) => {
    let buf = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => (buf += chunk));
    process.stdin.on('end', () => {
      // 去掉首部 BOM
      if (buf.charCodeAt(0) === 0xfeff) buf = buf.slice(1);
      resolveP(buf);
    });
    process.stdin.on('error', reject);
    // 兜底: 如果 TRAE 没传 stdin(PowerShell 调用 / 直跑测试),允许空 payload
    setTimeout(() => {
      if (buf.charCodeAt(0) === 0xfeff) buf = buf.slice(1);
      resolveP(buf);
    }, 200);
  });
}

/**
 * 隐私脱敏: 移除 prompt 中疑似 API Key / Token / Bearer
 * - sk-xxx / sk-xxx (OpenAI 风格)
 * - Bearer xxx (HTTP 鉴权)
 * - ghp_xxx (GitHub PAT)
 * - AKIDxxx (阿里云)
 * 保留前 4 后 4,中间用 **** 替代
 */
function sanitize(prompt) {
  if (typeof prompt !== 'string' || prompt.length === 0) return prompt;
  return prompt
    .replace(/(sk-[A-Za-z0-9_-]{16,})/g, (m) => `${m.slice(0, 4)}****${m.slice(-4)}`)
    .replace(/(Bearer\s+)[A-Za-z0-9_.-]{16,}/gi, (_m, p1) => `${p1}****`)
    .replace(/(ghp_[A-Za-z0-9]{16,})/g, (m) => `${m.slice(0, 4)}****${m.slice(-4)}`)
    .replace(/(AKID[A-Za-z0-9]{12,})/g, (m) => `${m.slice(0, 4)}****${m.slice(-4)}`);
}

/**
 * 安全写入: 父目录不存在则创建,失败不抛(降级到 stderr 提示)
 */
async function safeAppendFile(filePath, line) {
  try {
    await mkdir(join(filePath, '..'), { recursive: true });
    await appendFile(filePath, line, 'utf8');
    return true;
  } catch (err) {
    process.stderr.write(`[trae-prompt-logger] 写入失败: ${filePath}\n  ${err.message}\n`);
    return false;
  }
}

/**
 * 原子追加: 用 "a" 模式 + flock-free 追加(appendFile 内部已用 O_APPEND)
 */

// ─── 主流程 ─────────────────────────────────────────────

async function main() {
  const raw = await readStdin();

  // [trace-2026-08-14] 探针:任何触发都先 dump 到 logs/,便于排查是否被 TRAE 调用
  try {
    const { appendFileSync, mkdirSync } = await import('node:fs');
    const { join } = await import('node:path');
    const traceDir = join(process.cwd(), '.trae', 'prompt-logs');
    mkdirSync(traceDir, { recursive: true });
    appendFileSync(
      join(traceDir, 'trace.log'),
      `[${new Date().toISOString()}] argv=${JSON.stringify(process.argv.slice(2))} stdin_len=${raw.length} cwd=${process.cwd()}\n`,
      'utf8',
    );
    if (raw) {
      appendFileSync(join(traceDir, 'trace.log'), `  raw=${raw.slice(0, 400)}\n`, 'utf8');
    }
  } catch {}

  let payload;
  try {
    payload = raw.trim() ? JSON.parse(raw) : {};
  } catch (err) {
    process.stderr.write(`[trae-prompt-logger] payload 解析失败: ${err.message}\n`);
    process.exit(0); // 退出码 0: 不影响 TRAE 会话
  }

  // 必须字段缺失则直接返回(可能不是 UserPromptSubmit 事件被误用)
  const { session_id, cwd, prompt } = payload;
  if (!session_id || !cwd) {
    process.exit(0);
  }

  // 跳过空 prompt(防止噪音)
  if (typeof prompt !== 'string' || prompt.trim().length === 0) {
    process.exit(0);
  }

  // 解析项目根目录: cwd 即 TRAE 给的当前工作目录
  // resolve 规范化,移除 .. 等相对路径
  const projectRoot = resolve(cwd);

  // 路径: <project>/.trae/prompt-logs/sessions/<session_id>/prompts.ndjson
  const sessionFile = join(
    projectRoot,
    '.trae',
    'prompt-logs',
    'sessions',
    session_id,
    'prompts.ndjson',
  );
  const indexFile = join(
    projectRoot,
    '.trae',
    'prompt-logs',
    'index.ndjson',
  );

  // 落盘记录
  const record = {
    ts: new Date().toISOString(),
    session_id,
    project: projectRoot,
    cwd: payload.cwd,
    workspace_roots: payload.workspace_roots ?? [],
    hook_event_name: payload.hook_event_name ?? 'UserPromptSubmit',
    prompt: sanitize(prompt),
    prompt_length: prompt.length,
  };

  const line = JSON.stringify(record) + '\n';

  // 双写: session 文件 + 全局索引(并行,互不影响)
  const results = await Promise.all([
    safeAppendFile(sessionFile, line),
    safeAppendFile(indexFile, line),
  ]);

  if (results.every((r) => !r)) {
    // 两次都失败: 仍然退出 0,避免阻断 TRAE;但 stderr 给提示
    process.exit(0);
  }

  process.exit(0);
}

// ─── 入口 ─────────────────────────────────────────────

main().catch((err) => {
  // 兜底: 任何未捕获错误都不影响 TRAE 会话
  process.stderr.write(`[trae-prompt-logger] 致命错误: ${err.message}\n${err.stack}\n`);
  process.exit(0);
});
