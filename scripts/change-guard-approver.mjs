#!/usr/bin/env node
/**
 * change-guard-approver.mjs — guard/gate 保护 + 身份审批守卫
 *
 * 解决的问题:
 *   任何 agent 都能直接修改 .husky/pre-commit / scripts/skill-*-guard.py / workflow
 *   等关键守卫脚本,造成"agent 改守卫自绕过"
 *
 * 设计: 4 Tier 保护 + 角色审批 + CI 决议
 *   Tier 1: 自由修改
 *   Tier 2: 需同角色审批 (peer-review)
 *   Tier 3: 需 release-manager / project-owner 审批
 *   Tier 4: 禁止修改 (任何身份,即使 owner — 由 git hook 物理阻断)
 *
 * 接入点:
 *   - .husky/pre-commit: --check (预检,不阻断) → 写 pending 文件
 *   - .husky/pre-push:   --gate (阻断,要求 pending 已批准)
 *   - CI (skill-market-gate.yml L3): --resolve (CI 读 pending 决议)
 *
 * CLI:
 *   node change-guard-approver.mjs check --changed <files...> [--tier STRICT]
 *   node change-guard-approver.mjs gate  --branch <branch> --user <name>
 *   node change-guard-approver.mjs resolve --branch <branch> --user <name> --role <role> --decision approve|reject
 *   node change-guard-approver.mjs status [--branch <branch>]
 *
 * 关联:
 *   - .trae/identity/skill-roles.yaml
 *   - .trae/identity/protected-paths.yaml
 *   - .trae/approvals/<branch>/<commit>.pending.json
 *   - AGENTS.md §1 铁律 / §2 三层控制
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, statSync, readdirSync } from 'node:fs';
import { join, resolve, basename } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import yaml from 'yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = resolve(__filename, '..');
const REPO_ROOT = resolve(__dirname, '..');

const ROLES_PATH = join(REPO_ROOT, '.trae/identity/skill-roles.yaml');
const PROTECTED_PATHS_PATH = join(REPO_ROOT, '.trae/identity/protected-paths.yaml');
const APPROVALS_DIR = join(REPO_ROOT, '.trae/approvals');

// ─── 工具 ─────────────────────────────────────────────

function loadYaml(path) {
  if (!existsSync(path)) return null;
  return yaml.parse(readFileSync(path, 'utf-8'));
}

function loadRoles() {
  const cfg = loadYaml(ROLES_PATH);
  if (!cfg) throw new Error(`身份清单不存在: ${ROLES_PATH}`);
  return cfg;
}

function loadProtectedPaths() {
  const cfg = loadYaml(PROTECTED_PATHS_PATH);
  if (!cfg) throw new Error(`保护路径清单不存在: ${PROTECTED_PATHS_PATH}`);
  return cfg.protected_paths || [];
}

/** 把 glob 转正则 (仅支持 *, **, ?) */
function globToRegex(glob) {
  let re = '';
  for (let i = 0; i < glob.length; i++) {
    const c = glob[i];
    if (c === '*') {
      if (glob[i + 1] === '*') {
        re += '.*';
        i++;
        if (glob[i + 1] === '/') i++;
      } else {
        re += '[^/]*';
      }
    } else if (c === '?') {
      re += '[^/]';
    } else if (/\./.test(c)) {
      re += '\\' + c;
    } else {
      re += c;
    }
  }
  return new RegExp('^' + re + '$');
}

/** 查找一个路径的保护策略 — 首个命中即生效 */
function findPathPolicy(filePath, policies) {
  const normalized = filePath.replace(/\\/g, '/').replace(/^\.\//, '');
  for (const policy of policies) {
    const re = globToRegex(policy.pattern);
    if (re.test(normalized)) return policy;
  }
  return null;
}

/** 解析当前 git user */
function gitUser() {
  try {
    const name = execFileSync('git', ['config', 'user.name'], { encoding: 'utf-8' }).trim();
    const email = execFileSync('git', ['config', 'user.email'], { encoding: 'utf-8' }).trim();
    return `${name} <${email}>`;
  } catch {
    return process.env.USER || 'unknown';
  }
}

/** 解析用户角色 */
function resolveRole(user, rolesCfg) {
  for (const mapping of rolesCfg.users || []) {
    if (mapping.user === user) return mapping.role;
  }
  // glob 匹配 (e.g. "*.trae-ide.local")
  for (const mapping of rolesCfg.users || []) {
    if (mapping.user.includes('*')) {
      const re = new RegExp('^' + mapping.user.replace(/\*/g, '.*') + '$');
      if (re.test(user)) return mapping.role;
    }
  }
  return rolesCfg.fallback_role || 'contributor';
}

/** role 等级映射 */
const ROLE_RANK = { contributor: 1, 'qa-lead': 2, 'release-manager': 3, 'project-owner': 4 };

function roleRank(role) {
  return ROLE_RANK[role] || 0;
}

function canApproveTier(role, tier) {
  const cfg = loadRoles();
  const def = (cfg.identities?.roles || []).find((r) => r.id === role);
  return def?.can_approve_tiers?.includes(tier) || false;
}

function canEditTier(role, tier) {
  const cfg = loadRoles();
  const def = (cfg.identities?.roles || []).find((r) => r.id === role);
  return def?.can_edit_tiers?.includes(tier) || false;
}

// ─── pending 审批文件 ─────────────────────────────

function getPendingFile(branch, commit) {
  return join(APPROVALS_DIR, branch, `${commit}.pending.json`);
}

function getResolvedFile(branch, commit) {
  return join(APPROVALS_DIR, branch, `${commit}.resolved.json`);
}

function writePending(branch, commit, payload) {
  const dir = join(APPROVALS_DIR, branch);
  mkdirSync(dir, { recursive: true });
  const path = getPendingFile(branch, commit);
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf-8');
  return path;
}

function readPending(branch, commit) {
  const path = getPendingFile(branch, commit);
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, 'utf-8'));
}

function readResolved(branch, commit) {
  const path = getResolvedFile(branch, commit);
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, 'utf-8'));
}

// ─── 子命令: check (pre-commit 预检) ─────────────

function cmdCheck(args) {
  const idx = args.indexOf('--changed');
  if (idx === -1) {
    console.error('用法: change-guard-approver.mjs check --changed <file1> <file2> ...');
    process.exit(5);
  }
  const files = args.slice(idx + 1).filter((a) => !a.startsWith('--'));
  const strict = args.includes('--tier') && args[args.indexOf('--tier') + 1] === 'STRICT';

  const policies = loadProtectedPaths();
  const user = gitUser();
  const role = resolveRole(user, loadRoles());
  const currentBranch = currentGitBranch();
  const commit = currentGitCommit();

  const issues = [];
  for (const f of files) {
    const policy = findPathPolicy(f, policies);
    if (!policy) continue; // 不在保护清单 → 自由

    if (policy.tier === 4) {
      issues.push({
        severity: 'BLOCK',
        code: 'PRF-004',
        file: f,
        policy,
        message: `Tier 4 禁止修改: ${f} (${policy.reason})`,
        fix: '该路径不可被任何身份修改。如确需修改,先修改 .trae/identity/protected-paths.yaml 自身。',
      });
      continue;
    }

    // Tier 1: 自由
    if (policy.tier === 1) continue;

    // Tier 2/3: 任何角色都能"提交变更",但必须由 required_role 审批
    // (允许 contributor 提交,这样他们的 commit 不被阻断;真正的审批在 push 阶段)
    issues.push({
      severity: 'INFO',
      code: `PRF-OK${policy.tier}`,
      file: f,
      policy,
      message: `Tier ${policy.tier} 变更已记录 (你=${role}, 需 ${policy.required_role} 审批)`,
    });
  }

  // 把所有 INFO 写成 pending (一次性, 覆盖写)
  const infoIssues = issues.filter((i) => i.severity === 'INFO');
  if (infoIssues.length > 0 && !strict) {
    const pendingPayload = {
      schema: 1,
      branch: currentBranch,
      commit,
      author: user,
      author_role: role,
      created_at: new Date().toISOString(),
      files: infoIssues.map((i) => ({
        path: i.file,
        tier: i.policy.tier,
        required_role: i.policy.required_role,
        reason: i.policy.reason,
      })),
      status: 'pending',
    };
    const path = writePending(currentBranch, commit, pendingPayload);
    console.log(`📝 写入 pending 审批: ${path}`);
    console.log(`   ${infoIssues.length} 个 Tier 2/3 变更需 ${[...new Set(infoIssues.map((i) => i.policy.required_role))].join('/')} 审批`);
  }

  // 输出
  for (const i of issues) {
    const icon = i.severity === 'BLOCK' ? '🛑' : i.severity === 'INFO' ? '✅' : 'ℹ';
    console.log(`${icon} [${i.code}] ${i.message}`);
  }

  if (issues.some((i) => i.severity === 'BLOCK')) {
    console.error(`\n❌ change-guard-approver BLOCK: ${issues.filter((i) => i.severity === 'BLOCK').length} 项不允许的修改`);
    process.exit(4);
  }
  // 即使 issues 全是 INFO,也允许 commit (审批在 push 阶段做)
  process.exit(0);
}

// ─── 子命令: gate (pre-push 阻断) ─────────────────

function cmdGate(args) {
  const branch = argValue(args, '--branch') || currentGitBranch();
  const user = argValue(args, '--user') || gitUser();
  const commit = currentGitCommit();

  const policies = loadProtectedPaths();
  const pending = readPending(branch, commit);
  const resolved = readResolved(branch, commit);

  // 取 commit 涉及的所有变更文件
  const changed = changedFiles(commit);
  const issues = [];

  for (const f of changed) {
    const policy = findPathPolicy(f, policies);
    if (!policy) continue;
    if (policy.tier === 1) continue;

    if (policy.tier === 4) {
      issues.push({
        severity: 'BLOCK', code: 'PRF-004', file: f,
        message: `Tier 4 路径仍被修改: ${f}`,
      });
      continue;
    }

    if (policy.tier === 2 || policy.tier === 3) {
      if (pending && pending.files.some((pf) => pf.path === f)) {
        // 有 pending → 检查 resolved
        if (!resolved) {
          issues.push({
            severity: 'BLOCK', code: 'PRF-GATE', file: f,
            message: `Tier ${policy.tier} 修改 ${f} 还未审批 (pending 但无 resolved)`,
            fix: '由 release-manager / project-owner 运行 resolve --decision approve',
          });
        } else if (resolved.decision === 'reject') {
          issues.push({
            severity: 'BLOCK', code: 'PRF-REJECTED', file: f,
            message: `Tier ${policy.tier} 修改 ${f} 被 ${resolved.reviewer} 拒绝: ${resolved.comment || '(无理由)'}`,
            fix: 'git reset HEAD~1 后重新 commit,或重新申请审批',
          });
        } else if (resolved.decision === 'approve') {
          // 检查审批人角色是否够高
          if (resolved.reviewer_role && !canApproveTier(resolved.reviewer_role, policy.tier)) {
            issues.push({
              severity: 'BLOCK', code: 'PRF-LOWROLE', file: f,
              message: `审批人 ${resolved.reviewer} (${resolved.reviewer_role}) 无权批准 Tier ${policy.tier}`,
              fix: '由更高角色重新审批',
            });
          } else {
            issues.push({
              severity: 'INFO', code: 'PRF-OK', file: f,
              message: `Tier ${policy.tier} 修改 ${f} 已由 ${resolved.reviewer} (${resolved.reviewer_role}) 审批通过`,
            });
          }
        }
      } else if (resolved && resolved.files?.some((rf) => rf.path === f)) {
        // 没有 pending 但有 resolved(可能跨 commit) — 跳过
        continue;
      } else {
        issues.push({
          severity: 'BLOCK', code: 'PRF-NOPEND', file: f,
          message: `Tier ${policy.tier} 修改 ${f} 无 pending 记录,无法推送`,
          fix: '回滚此 commit,或由 Tier 4 不可逆路径通过 GitHub PR 流程审批',
        });
      }
    }
  }

  for (const i of issues) {
    const icon = i.severity === 'BLOCK' ? '🛑' : '✅';
    console.log(`${icon} [${i.code}] ${i.message}`);
  }
  if (issues.some((i) => i.severity === 'BLOCK')) {
    console.error(`\n❌ push gate BLOCK: ${issues.filter((i) => i.severity === 'BLOCK').length} 项`);
    process.exit(4);
  }
  process.exit(0);
}

// ─── 子命令: resolve (人工审批) ──────────────────

function cmdResolve(args) {
  const branch = argValue(args, '--branch') || currentGitBranch();
  const user = argValue(args, '--user') || gitUser();
  const role = argValue(args, '--role') || resolveRole(user, loadRoles());
  const decision = argValue(args, '--decision');
  const comment = argValue(args, '--comment') || '';

  if (!['approve', 'reject'].includes(decision)) {
    console.error('用法: change-guard-approver.mjs resolve --decision approve|reject [--comment "理由"]');
    process.exit(5);
  }

  const commit = currentGitCommit();
  const pending = readPending(branch, commit);
  if (!pending) {
    console.error(`❌ 无 pending 记录: ${branch} / ${commit}`);
    process.exit(1);
  }

  // 校验: Tier 4 任何角色都不可批
  if (pending.files.some((f) => f.tier === 4) && decision === 'approve') {
    console.error(`❌ Tier 4 不可被任何身份 approve (包括 project-owner)`);
    process.exit(4);
  }

  // 校验: 审批人角色必须能批所有 pending 文件的最高 tier
  const maxTier = Math.max(...pending.files.map((f) => f.tier || 1));
  if (decision === 'approve' && !canApproveTier(role, maxTier)) {
    console.error(`❌ 你的角色 ${role} 不能 approve Tier ${maxTier} (需要: ${pending.files.find((f) => f.tier === maxTier)?.required_role})`);
    process.exit(4);
  }

  // 写 resolved
  const dir = join(APPROVALS_DIR, branch);
  mkdirSync(dir, { recursive: true });
  const resolvedPath = getResolvedFile(branch, commit);
  const resolvedPayload = {
    schema: 1,
    branch,
    commit,
    reviewer: user,
    reviewer_role: role,
    decision,
    comment,
    approved_at: new Date().toISOString(),
    approved_files: pending.files.map((f) => ({ path: f.path, tier: f.tier })),
  };
  writeFileSync(resolvedPath, JSON.stringify(resolvedPayload, null, 2) + '\n', 'utf-8');
  console.log(`✅ 决议已记录: ${resolvedPath}`);
  console.log(`   决策: ${decision}  by  ${user} (${role})`);
  if (comment) console.log(`   理由: ${comment}`);
  process.exit(0);
}

// ─── 子命令: status (查看当前分支 pending) ──────────

function cmdStatus(args) {
  const branch = argValue(args, '--branch') || currentGitBranch();
  const commit = currentGitCommit();
  const pending = readPending(branch, commit);
  const resolved = readResolved(branch, commit);

  console.log(`📋 分支: ${branch}`);
  console.log(`   Commit: ${commit}`);

  if (!pending && !resolved) {
    console.log('   ✅ 无 pending / resolved 记录 (该 commit 无 Tier 2+ 变更)');
    return;
  }
  if (pending) {
    console.log(`\n   ⏳ Pending (${pending.created_at}):`);
    console.log(`      作者: ${pending.author} (${pending.author_role})`);
    console.log(`      文件: ${pending.files.length} 个`);
    for (const f of pending.files) {
      console.log(`        - ${f.path}  [Tier ${f.tier}]  需 ${f.required_role}`);
    }
  }
  if (resolved) {
    const icon = resolved.decision === 'approve' ? '✅' : '❌';
    console.log(`\n   ${icon} Resolved (${resolved.approved_at}):`);
    console.log(`      审批人: ${resolved.reviewer} (${resolved.reviewer_role})`);
    console.log(`      决策: ${resolved.decision}`);
    if (resolved.comment) console.log(`      理由: ${resolved.comment}`);
  }
}

// ─── git 工具 ─────────────────────────────────────

function currentGitBranch() {
  try {
    return execFileSync('git', ['rev-parse', '--abbrev-ref', 'HEAD'], { encoding: 'utf-8' }).trim();
  } catch {
    return 'unknown';
  }
}

function currentGitCommit() {
  try {
    return execFileSync('git', ['rev-parse', '--short', 'HEAD'], { encoding: 'utf-8' }).trim();
  } catch {
    return 'unknown';
  }
}

function changedFiles(commit) {
  try {
    // 比较 HEAD~1 到 HEAD 的变更文件(不关心 staged,只关心已 commit)
    const out = execFileSync('git', ['diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'], { encoding: 'utf-8' });
    return out.split('\n').filter(Boolean);
  } catch {
    return [];
  }
}

function argValue(args, flag) {
  const i = args.indexOf(flag);
  return i === -1 ? null : args[i + 1];
}

// ─── 入口 ─────────────────────────────────────────

function main() {
  const [, , sub, ...rest] = process.argv;
  const handlers = {
    check: cmdCheck,
    gate: cmdGate,
    resolve: cmdResolve,
    status: cmdStatus,
  };
  const handler = handlers[sub];
  if (!handler) {
    console.error(`用法: change-guard-approver.mjs <${Object.keys(handlers).join('|')}> [options]`);
    process.exit(5);
  }
  handler(rest);
}

main();
