#!/usr/bin/env node
// changed-file-impact-guard.mjs
// 改源码区必须同时改对应测试区（变更影响强制）。
// 数据源：CHANGED_FILES 环境变量（空格/逗号/换行分隔）或 `git diff --name-only --cached`。
// 配置：--config <path>（默认同目录 changed-file-impact-guard.yaml）
// Exit 0 = pass, 1 = fail, 0+WARN = yaml 包未安装（不阻塞）。

import { readFileSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

let parseYaml;
try {
  ({ parse: parseYaml } = await import('yaml'));
} catch {
  console.warn('[changed-file-impact-guard] WARN: yaml package not installed, skip (run `npm i yaml`).');
  process.exit(0);
}

function parseArgs(argv) {
  const out = { config: null, files: [] };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--config' && argv[i + 1]) {
      out.config = argv[i + 1];
      i += 1;
    } else {
      out.files.push(argv[i]);
    }
  }
  return out;
}

function normalizeFiles(raw) {
  return raw
    .flatMap((item) => String(item).split(/[\n,]/))
    .map((item) => item.trim())
    .filter(Boolean);
}

function readGitChangedFiles() {
  try {
    const out = execSync('git diff --name-only --cached', {
      cwd: process.cwd(),
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    return normalizeFiles([out]);
  } catch {
    return [];
  }
}

function toRegex(pattern) {
  return new RegExp(pattern);
}

function applyWhitelist(ruleId, file, whitelist) {
  const entry = whitelist.find((w) => w.rule === ruleId);
  if (!entry || !Array.isArray(entry.files)) return false;
  return entry.files.some((p) => file.startsWith(p) || toRegex(p).test(file));
}

function isRuleEnabled(rule, overrides) {
  if (rule.enabled === false) return false;
  const ov = (overrides || []).find((o) => o.id === rule.id);
  return !(ov && ov.action === 'disable');
}

function inspect(changedFiles, config) {
  const violations = [];
  const rules = (config.rules || []).filter((r) => isRuleEnabled(r, config.allowed_overrides));
  const whitelist = config.whitelist || [];

  for (const rule of rules) {
    const sourceRe = toRegex(rule.source);
    const testRes = (rule.tests || []).map(toRegex);
    const impacted = changedFiles.filter(
      (f) => sourceRe.test(f) && !applyWhitelist(rule.id, f, whitelist),
    );
    if (impacted.length === 0) continue;
    const hasMatch = changedFiles.some((f) => testRes.some((re) => re.test(f)));
    if (!hasMatch) {
      violations.push({ id: rule.id, message: rule.message, files: impacted });
    }
  }
  return violations;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const defaultConfig = resolve(dirname(fileURLToPath(import.meta.url)), 'changed-file-impact-guard.yaml');
  const configPath = args.config ? resolve(process.cwd(), args.config) : defaultConfig;

  let config;
  try {
    config = parseYaml(readFileSync(configPath, 'utf8')) || {};
  } catch (err) {
    console.warn(`[changed-file-impact-guard] WARN: cannot read config (${configPath}): ${err.message} — skip.`);
    return 0;
  }

  const fromArgs = normalizeFiles(args.files);
  const fromEnv = normalizeFiles([process.env.CHANGED_FILES || '']);
  const fromGit = readGitChangedFiles();
  const changed = fromArgs.length ? fromArgs : [...fromEnv, ...fromGit];

  if (changed.length === 0) {
    console.log('[changed-file-impact-guard] SKIP no changed files detected');
    return 0;
  }

  const violations = inspect(changed, config);
  if (violations.length > 0) {
    console.error('\n[changed-file-impact-guard] Missing matching test changes');
    for (const v of violations) {
      console.error(`  - [${v.id}] ${v.message}; files=${v.files.join(',')}`);
    }
    return 1;
  }

  console.log(`[changed-file-impact-guard] OK files=${changed.length}`);
  return 0;
}

process.exit(main());
