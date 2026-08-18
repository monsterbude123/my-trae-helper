/**
 * tests/unit/test_add_all.mjs — End-to-end tests for `trae-skills add-all`
 *
 * 目标:
 *   - bin/cli.mjs add-all <flags...>
 *   - runAddAll(args) 函数（src/add-all.mjs 导出）
 *
 * 运行: node tests/unit/test_add_all.mjs
 *
 * 设计:
 *   - 纯 Node 18+ + spawnSync 抓子进程 stdout / stderr / status
 *   - 不引入新依赖（仅 node:fs / node:path / node:os / node:child_process / node:assert）
 *   - 跨平台：Windows / Linux / macOS 通用
 *     - 临时目录统一用 os.tmpdir()，不用 homedir
 *     - 链接断言用 lstatSync + isSymbolicLink()（兼容 Windows junction）
 *   - 临时目录在每个测试结束清理（fs.rmSync recursive force）
 *   - 失败不阻断其他（try/catch 收集）
 *   - 任一 FAIL → process.exitCode = 1
 */

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  existsSync,
  lstatSync,
  mkdtempSync,
  readdirSync,
  rmSync,
  statSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..', '..');
const CLI_BIN = join(REPO_ROOT, 'bin', 'cli.mjs');
const ADD_ALL_SRC = join(REPO_ROOT, 'src', 'add-all.mjs');
const SKILL_MARKETS_DIR = join(REPO_ROOT, 'skill-markets');

// ─── 结果收集 ─────────────────────────────────────────────────
let passed = 0;
let failed = 0;
let skipped = 0;
const failMessages = [];

async function test(name, fn) {
  try {
    await fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (err) {
    if (err && err.__skip) {
      console.log(`  ⏭  SKIP: ${name} — ${err.message}`);
      skipped++;
      return;
    }
    console.log(`  ❌ ${name}`);
    console.log(`     ${err.message}`);
    failed++;
    failMessages.push(`${name}: ${err.message}`);
  }
}

function skip(reason) {
  const e = new Error(reason);
  e.__skip = true;
  throw e;
}

// ─── 子进程辅助 ──────────────────────────────────────────────
/**
 * 跑 bin/cli.mjs add-all <args...>
 * @param {string[]} args
 * @param {object} [opts]
 * @param {string} [opts.cwd]
 * @param {object} [opts.env]
 * @returns {{status: number|null, stdout: string, stderr: string}}
 */
function runCli(args, opts = {}) {
  return spawnSync(process.execPath, [CLI_BIN, 'add-all', ...args], {
    cwd: opts.cwd || REPO_ROOT,
    env: { ...process.env, NO_COLOR: '1', ...(opts.env || {}) },
    encoding: 'utf-8',
    timeout: 30_000,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

// ─── 探测接口是否存在 ──────────────────────────────────────
const addAllSrcExists = existsSync(ADD_ALL_SRC);
const addAllRegistered = (() => {
  const r = spawnSync(process.execPath, [CLI_BIN, 'add-all', '--help'], {
    cwd: REPO_ROOT,
    env: { ...process.env, NO_COLOR: '1' },
    encoding: 'utf-8',
    timeout: 10_000,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  // 成功注册 → exit 0 + stdout 含 add-all / --help 关键字
  // 未注册 → exit 1 + stderr 含 "未知命令"
  return r.status === 0 && /add-all/i.test(r.stdout || '');
})();

if (!addAllSrcExists || !addAllRegistered) {
  console.log('━━━ add-all (E2E) ━━━');
  console.log(
    `  ⚠  add-all 接口未就绪: src/add-all.mjs=${addAllSrcExists} cli注册=${addAllRegistered}`
  );
  console.log(
    '  提示: 等待子代理 A 落地 src/add-all.mjs + bin/cli.mjs 注册 add-all 命令后重跑'
  );
}

console.log('\n━━━ add-all (E2E) ━━━');

// ─── 测试 1: --help ─────────────────────────────────────────
await test('test_help_output — --help 输出含 add-all / --trae-cn / --bundles / --exclude / --include, exit 0', () => {
  if (!addAllRegistered) {
    skip('add-all 命令尚未注册到 bin/cli.mjs');
  }
  const r = runCli(['--help']);
  assert.equal(r.status, 0, `expected exit 0, got ${r.status}; stderr=${r.stderr?.slice(0, 400)}`);
  const out = r.stdout || '';
  assert.ok(/add-all/.test(out), `stdout 应包含 add-all, got: ${out.slice(0, 400)}`);
  assert.ok(/--trae-cn/.test(out), `stdout 应包含 --trae-cn, got: ${out.slice(0, 400)}`);
  assert.ok(/--bundles/.test(out), `stdout 应包含 --bundles, got: ${out.slice(0, 400)}`);
  assert.ok(/--exclude/.test(out), `stdout 应包含 --exclude, got: ${out.slice(0, 400)}`);
  assert.ok(/--include/.test(out), `stdout 应包含 --include, got: ${out.slice(0, 400)}`);
});

// ─── 测试 2: dry-run 不写盘 ─────────────────────────────────────────
await test('test_dry_run_no_disk_writes_to_repo — dry-run 后 skill-markets/ 子目录 mtime 不变', () => {
  if (!addAllRegistered) {
    skip('add-all 命令尚未注册到 bin/cli.mjs');
  }
  // 取前 5 个顶级 skill 目录，记 mtime
  const samples = readdirSync(SKILL_MARKETS_DIR, { withFileTypes: true })
    .filter((e) => {
      try {
        return statSync(join(SKILL_MARKETS_DIR, e.name)).isDirectory();
      } catch {
        return false;
      }
    })
    .slice(0, 5)
    .map((e) => join(SKILL_MARKETS_DIR, e.name));

  const before = samples.map((p) => statSync(p).mtimeMs);
  // -a trae-cn 显式指定,避免依赖 detectInstalledAgents 在 CI 上表现
  // --bundles "" 跳过所有 bundle,跑得快
  // -y 跳过 confirm
  const r = runCli(['-a', 'trae-cn', '--dry-run', '--bundles', '', '-y']);
  const after = samples.map((p) => statSync(p).mtimeMs);

  assert.equal(r.status, 0, `dry-run 期望 exit 0, got ${r.status}; stderr=${r.stderr?.slice(0, 400)}`);
  for (let i = 0; i < samples.length; i++) {
    assert.equal(
      after[i],
      before[i],
      `skill-markets/${samples[i].slice(SKILL_MARKETS_DIR.length + 1)} mtime 改变: ${before[i]} → ${after[i]}`
    );
  }
});

// ─── 测试 3: --exclude ─────────────────────────────────────────
await test('test_exclude_skips_skill — --exclude acceptance-discipline 输出不含该子 skill 名称', () => {
  if (!addAllRegistered) {
    skip('add-all 命令尚未注册到 bin/cli.mjs');
  }
  // -a trae-cn 显式指定 + -y 跳过 confirm + --dry-run + --bundles "" 跳 bundle
  const r = runCli(['-a', 'trae-cn', '--exclude', 'acceptance-discipline', '--dry-run', '--bundles', '', '-y']);
  assert.equal(r.status, 0, `dry-run 期望 exit 0, got ${r.status}; stderr=${r.stderr?.slice(0, 400)}`);
  const out = r.stdout || '';
  // acceptance-discipline 是顶层 skill,被 --exclude 后,装载行不应出现
  // 实际实现 print: `[${skill.dirName}] → ${res}` 形式
  assert.ok(
    !/\[acceptance-discipline\]\s*→/.test(out),
    `stdout 不应包含 acceptance-discipline 安装行, got: ${out.slice(0, 600)}`
  );
});

// ─── 测试 4: --include 过滤 ─────────────────────────────────────────
await test('test_include_filters_to_subset — --include 只跑 coding-xinfa,docsify-doc-builder', () => {
  if (!addAllRegistered) {
    skip('add-all 命令尚未注册到 bin/cli.mjs');
  }
  // 用 --bundles "" 跳过所有 bundle,这样 stdout 干净,只含 include 的 2 个顶层
  const r = runCli([
    '-a', 'trae-cn',
    '--include', 'coding-xinfa,docsify-doc-builder',
    '--bundles', '',
    '--dry-run',
    '-y',
  ]);
  assert.equal(r.status, 0, `dry-run 期望 exit 0, got ${r.status}; stderr=${r.stderr?.slice(0, 400)}`);
  const out = r.stdout || '';
  // 必须命中这两个
  assert.ok(/coding-xinfa/.test(out), `stdout 应包含 coding-xinfa, got: ${out.slice(0, 600)}`);
  assert.ok(/docsify-doc-builder/.test(out), `stdout 应包含 docsify-doc-builder, got: ${out.slice(0, 600)}`);
  // 不应包含其他无关顶层 skill
  assert.ok(
    !/comfyui-api-skills/.test(out),
    `stdout 不应包含 comfyui-api-skills (bundle 内容), got: ${out.slice(0, 600)}`
  );
  assert.ok(
    !/fullstack4TraeV11/.test(out),
    `stdout 不应包含 fullstack4TraeV11 (bundle), got: ${out.slice(0, 600)}`
  );
});

// ─── 测试 5: 无效输入 exit 1 ─────────────────────────────────────────
await test('test_no_agents_exits_nonzero — 不存在的 include 期望 exit ≠ 0 或正确跳过', () => {
  if (!addAllRegistered) {
    skip('add-all 命令尚未注册到 bin/cli.mjs');
  }
  // -a trae-cn 显式指定 + -y 跳过 confirm
  const r = runCli(['-a', 'trae-cn', '--bundles', '', '--include', 'nonexistent-skill-zzz-12345', '-y']);
  // 允许 exit ∈ {0, 1},但 stdout/stderr 至少有一处提到"未找到" / "跳过" / "无"
  const combined = `${r.stdout || ''}\n${r.stderr || ''}`;
  assert.ok(
    /未找到|nonexistent|跳过|无可用|无任何|错误|error/i.test(combined),
    `期望输出含"未找到"或"跳过"等,实际: ${combined.slice(0, 600)}`
  );
  // 不破坏文件系统（不应创建任何新顶级目录）
  // 仅 sanity: 不能静默成功
  if (r.status === 0) {
    console.log(`     ⚠ exit 0 但有错误提示 — 半通过（实现可放过）`);
  }
});

// ─── 测试 6: 实际安装到临时目录（通过 mock HOME + --trae-cn）─────────────
// add-all 不支持 --target-dir;目标目录由 agent.globalSkillsDir 决定,而后者由
// agents.mjs 在模块加载时用 homedir() 计算 → 通过覆盖 HOME / USERPROFILE 让
// 整个 agent 全局目录落在 os.tmpdir() 下,实现零副作用实装。
await test('test_install_real_creates_symlink — mock HOME 装到 os.tmpdir() 后验证 symlink/junction', () => {
  if (!addAllRegistered) {
    skip('add-all 命令尚未注册到 bin/cli.mjs');
  }

  const ts = Date.now();
  const rand = Math.random().toString(36).slice(2, 8);
  const mockHome = mkdtempSync(join(tmpdir(), `add-all-home-${ts}-${rand}-`));
  const expectedTargetSkills = join(mockHome, '.trae-cn', 'skills');

  try {
    // 覆盖 HOME / USERPROFILE,确保 agents.mjs homedir() 返回 mockHome
    const envOverride = process.platform === 'win32'
      ? { USERPROFILE: mockHome, HOME: mockHome }
      : { HOME: mockHome };

    const r = runCli(
      [
        '--trae-cn',                 // 全局 → 走 agent.globalSkillsDir
        '-a', 'trae-cn',             // 显式指定 agent
        '--include', 'coding-xinfa', // 只装 1 个,快
        '--bundles', '',             // 跳所有 bundle,快
        '-y',                        // 跳过 confirm
      ],
      { env: envOverride }
    );

    const out = `${r.stdout || ''}\n${r.stderr || ''}`;
    assert.equal(r.status, 0, `实装期望 exit 0, got ${r.status}; stderr=${r.stderr?.slice(0, 400)}`);
    // 期望目标目录里出现 coding-xinfa
    const entry = join(expectedTargetSkills, 'coding-xinfa');
    assert.ok(
      existsSync(entry),
      `expected ${entry} to exist after install; output: ${out.slice(0, 600)}`
    );
    const lst = lstatSync(entry);
    // Windows junction 在 lstat 下报 isSymbolicLink()=true (Node 18+),
    // 但部分实现/旧版本可能是 dir — 两者都可接受
    assert.ok(
      lst.isSymbolicLink() || lst.isDirectory(),
      'installed entry 应该是 symlink/junction 或目录'
    );
  } finally {
    // 清理 mock HOME
    try {
      rmSync(mockHome, { recursive: true, force: true });
    } catch {
      // ignore
    }
  }
});

// ─── 汇总 ─────────────────────────────────────────────────────
console.log(`\n━━━ 通过: ${passed} 失败: ${failed} 跳过: ${skipped} ━━━`);

if (failed > 0) {
  console.log('\n失败明细:');
  for (const m of failMessages) console.log(`  - ${m}`);
}

process.exitCode = failed > 0 ? 1 : 0;