#!/usr/bin/env node
/**
 * scripts/prepare-publish.mjs
 * 拷贝 skill-markets → .publish/skill-markets，清掉 .pyc / __pycache__ / .zip / .security-scan-passed
 * 拷贝 bin + src + LICENSE + README → .publish/
 * 发布时 bin 字段改成 .publish/bin/cli.mjs
 */
import { cpSync, rmSync, existsSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = process.cwd();
const PUBLISH = join(ROOT, '.publish');

function shouldSkip(name) {
  if (name === '__pycache__') return true;
  if (name.endsWith('.pyc')) return true;
  if (name.endsWith('.pyo')) return true;
  if (name.endsWith('.pyd')) return true;
  if (name.endsWith('.zip')) return true;
  if (name === '.security-scan-passed') return true;
  return false;
}

function cleanCopy(srcDir, dstDir) {
  if (!existsSync(srcDir)) return;
  if (existsSync(dstDir)) rmSync(dstDir, { recursive: true, force: true });
  mkdirSync(dstDir, { recursive: true });
  cpSync(srcDir, dstDir, {
    recursive: true,
    filter: (src) => {
      const base = src.split(/[\\/]/).pop();
      return !shouldSkip(base);
    },
  });
}

function copyFlat(srcPath, dstPath) {
  if (!existsSync(srcPath)) return;
  cpSync(srcPath, dstPath, { recursive: true });
}

// 1. 清理目标
if (existsSync(PUBLISH)) rmSync(PUBLISH, { recursive: true, force: true });
mkdirSync(PUBLISH, { recursive: true });

// 2. 拷贝
copyFlat(join(ROOT, 'bin'), join(PUBLISH, 'bin'));
copyFlat(join(ROOT, 'src'), join(PUBLISH, 'src'));
cleanCopy(join(ROOT, 'skill-markets'), join(PUBLISH, 'skill-markets'));
copyFlat(join(ROOT, 'LICENSE'), join(PUBLISH, 'LICENSE'));
copyFlat(join(ROOT, 'README.md'), join(PUBLISH, 'README.md'));
copyFlat(join(ROOT, 'package.json'), join(PUBLISH, 'package.json'));

// 3. 统计
function count(dir) {
  let files = 0;
  let size = 0;
  function walk(d) {
    for (const e of readdirSync(d, { withFileTypes: true })) {
      const p = join(d, e.name);
      const s = statSync(p);
      if (s.isDirectory()) walk(p);
      else {
        files += 1;
        size += s.size;
      }
    }
  }
  if (existsSync(dir)) walk(dir);
  return { files, size };
}

const src = count(join(ROOT, 'skill-markets'));
const dst = count(join(PUBLISH, 'skill-markets'));

console.log(`✓ prepared ${PUBLISH}`);
console.log(`  skill-markets: ${src.files} files / ${(src.size / 1024 / 1024).toFixed(2)} MB → ${dst.files} files / ${(dst.size / 1024 / 1024).toFixed(2)} MB`);
console.log(`  skipped: ${src.files - dst.files} files (pyc/zip/cache)`);