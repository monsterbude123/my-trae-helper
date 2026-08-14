#!/usr/bin/env node
/**
 * trae-prompt-logger.install.mjs — JSON helper for trae-prompt-logger installer
 *
 * 由 .ps1 调用,负责:
 *   1. 读 ~/.trae-cn/hooks.json(处理 BOM、损坏等异常)
 *   2. 合并 UserPromptSubmit Hook 组(移除旧 trae-prompt-logger,添加新)
 *   3. 写回(无 BOM、UTF-8、正确数组结构)
 *
 * CLI:
 *   node trae-prompt-logger.install.mjs --op install|uninstall \
 *        --file <hooks.json> --script <logger.mjs> --marker <mark>
 *
 * 输出:
 *   - 成功: 在 stdout 输出结果描述(JSON 状态摘要)
 *   - 失败: 在 stderr 输出错误,exit 1
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

// ─── CLI 解析 ─────────────────────────────────────────

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const val = argv[i + 1];
      args[key] = val;
      i++;
    }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
const OP = args.op;
const FILE = args.file;
const SCRIPT = args.script;
const MARKER = args.marker;

if (!OP || !FILE || !SCRIPT || !MARKER) {
  process.stderr.write('用法: node trae-prompt-logger.install.mjs --op install|uninstall --file <path> --script <path> --marker <str>\n');
  process.exit(2);
}

// ─── 工具 ─────────────────────────────────────────────

/** 去掉 UTF-8 BOM */
function stripBom(s) {
  if (s.charCodeAt(0) === 0xfeff) return s.slice(1);
  return s;
}

/** 读取 hooks.json,容错处理 */
async function readHooks() {
  let raw;
  try {
    raw = await readFile(FILE, 'utf8');
  } catch (err) {
    if (err.code === 'ENOENT') {
      return { version: 1, hooks: {} };
    }
    throw err;
  }

  const cleaned = stripBom(raw).trim();
  if (!cleaned) {
    return { version: 1, hooks: {} };
  }

  try {
    const parsed = JSON.parse(cleaned);
    // 兜底: version 缺失 / hooks 缺失
    return {
      version: typeof parsed.version === 'number' ? parsed.version : 1,
      hooks: parsed.hooks && typeof parsed.hooks === 'object' ? parsed.hooks : {},
    };
  } catch (err) {
    process.stderr.write(`⚠️ hooks.json 解析失败,按空配置处理(原文件已备份): ${err.message}\n`);
    return { version: 1, hooks: {} };
  }
}

/** 写回 hooks.json(无 BOM、UTF-8) */
async function writeHooks(config) {
  await mkdir(dirname(FILE), { recursive: true });
  const json = JSON.stringify(config, null, 2);
  await writeFile(FILE, json, 'utf8');
}

/** 判断一个 Hook 组是否是我们的(用 marker 识别) */
function isOurHookGroup(group) {
  if (!group || !Array.isArray(group.hooks)) return false;
  for (const h of group.hooks) {
    if (typeof h.command === 'string' && h.command.includes(MARKER)) {
      return true;
    }
  }
  return false;
}

/** 构造一个新的 Hook 组 */
function makeLoggerHookGroup(scriptPath) {
  return {
    matcher: null,
    hooks: [
      {
        type: 'command',
        command: `node "${scriptPath}"`,
        timeout: 10,
      },
    ],
  };
}

/** 规范化一个事件值,确保是数组,过滤掉我们的旧钩子 */
function normalizeEventValue(val) {
  if (val == null) return [];
  if (Array.isArray(val)) return val.filter((g) => !isOurHookGroup(g));
  // 旧版本可能写入对象/字符串,统一为数组
  return [];
}

// ─── 主流程 ─────────────────────────────────────────────

const config = await readHooks();
const events = config.hooks;

if (OP === 'uninstall') {
  if (Array.isArray(events.UserPromptSubmit)) {
    events.UserPromptPrompt = undefined; // 防误写
    events.UserPromptSubmit = events.UserPromptSubmit.filter((g) => !isOurHookGroup(g));
    if (events.UserPromptSubmit.length === 0) delete events.UserPromptSubmit;
  }
  await writeHooks(config);
  console.log('🗑️ 卸载完成');
  process.exit(0);
}

if (OP === 'install') {
  // 1. 规范化 UserPromptSubmit(过滤我们的旧条目,确保是数组)
  const existing = Array.isArray(events.UserPromptSubmit)
    ? events.UserPromptSubmit.filter((g) => !isOurHookGroup(g))
    : [];

  // 2. 追加新钩子
  existing.push(makeLoggerHookGroup(SCRIPT));

  // 3. 写回
  events.UserPromptSubmit = existing;

  await writeHooks(config);
  console.log(`📝 已注册,UserPromptSubmit 数组长度 = ${existing.length}`);
  process.exit(0);
}

process.stderr.write(`未知操作: ${OP}\n`);
process.exit(2);
