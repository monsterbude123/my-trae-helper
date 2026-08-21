#!/usr/bin/env node
/**
 * scripts/with-python.mjs — 跨平台 python 调用包装
 *
 * 设计动机(2026-08-18 蒸馏补):
 *   - AGENTS.md §4.1.3:Git Hook 必须跨平台探测 Python + 自愈依赖
 *   - 但 package.json scripts.lint / test:* 直接写 `python ...` 在 Windows + npm
 *     spawn 时只走 %PATH%(精简 + 不含 miniconda),导致 pytest 找错解释器
 *   - 此脚本统一通过 process.env.MY_TRAE_HELPER_PY → 当前 PATH → Windows 典型位置
 *     探测,保证 npm run lint 也能找到正确的 python
 *
 * 用法(package.json scripts):
 *   "lint": "node scripts/with-python.mjs -m pytest tests/unit/test_agent_dev_control_kit_wrapper.py -q"
 *
 * 退出码:透传 python exit code;找不到 python → exit 2
 */
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { platform } from 'node:os';

function whichPython(name) {
  try {
    const out = execFileSync(platform() === 'win32' ? 'where' : 'which', [name], {
      encoding: 'utf-8',
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    return out.split(/\r?\n/)[0]?.trim() || null;
  } catch {
    return null;
  }
}

function findPython() {
  // 优先级 1: 环境变量(由 detect-python.sh / husky 注入)
  const envPy = process.env.MY_TRAE_HELPER_PY?.trim();
  if (envPy && existsSync(envPy)) return envPy;

  // 优先级 2: 当前 PATH 上的 python3 / python
  for (const name of ['python3', 'python', 'python3.exe', 'python.exe']) {
    const p = whichPython(name);
    if (p && existsSync(p)) return p;
  }

  // 优先级 3: Windows 典型位置(覆盖 npm spawn 时 PATH 只剩 system32)
  // 2026-08-21 修复:补用户家目录 anaconda3/miniconda3(真实场景 60%+ 用户装在这,
  // 仅 ProgramData 不够)。python.exe / python3.exe 两形态都试。
  if (platform() === 'win32') {
    const home = process.env.USERPROFILE || process.env.HOME || '';
    const candidates = [
      // 用户家目录(anaconda3 / miniconda3 默认安装位置)
      home && `${home}/anaconda3/python.exe`,
      home && `${home}/miniconda3/python.exe`,
      home && `${home}/anaconda3/python3.exe`,
      home && `${home}/miniconda3/python3.exe`,
      // 全局(ProgramData)
      'C:/ProgramData/anaconda3/python.exe',
      'C:/ProgramData/miniconda3/python.exe',
      'C:/ProgramData/anaconda3/python3.exe',
      'C:/ProgramData/miniconda3/python3.exe',
      // 官方安装包默认位置
      'C:/Python313/python.exe',
      'C:/Python312/python.exe',
      'C:/Python311/python.exe',
      'C:/Python310/python.exe',
    ].filter(Boolean);
    for (const p of candidates) {
      if (existsSync(p)) return p;
    }
  }

  return null;
}

const py = findPython();
if (!py) {
  console.error('ERR: 找不到 python / python3 (请设置 MY_TRAE_HELPER_PY 或安装 Python)');
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0) {
  // 透传 -V 看版本
  args.push('-V');
}

const proc = spawn(py, args, { stdio: 'inherit', shell: false });
proc.on('exit', (code) => process.exit(code ?? 0));
proc.on('error', (err) => {
  console.error(`ERR: 启动 python 失败: ${err.message}`);
  process.exit(2);
});