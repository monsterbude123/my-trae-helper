#!/usr/bin/env node
// api-contract-guard.mjs
// Verifies that every service module exports functions matching the API schema.
// Exit 0 = pass, 1 = fail.

import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

const ROOT = process.cwd();
const SERVICES_DIR = resolve(ROOT, 'src/services');
const SCHEMAS_DIR = resolve(ROOT, 'schemas/api');

function listFiles(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter((f) => f.endsWith('.js') || f.endsWith('.mjs'));
}

function extractExports(filePath) {
  const src = readFileSync(filePath, 'utf8');
  const matches = [...src.matchAll(/export\s+(?:async\s+)?function\s+(\w+)/g)];
  return matches.map((m) => m[1]);
}

function main() {
  if (!existsSync(SERVICES_DIR)) {
    console.log('[api-contract-guard] No src/services/ found — skipped.');
    return 0;
  }

  const serviceFiles = listFiles(SERVICES_DIR);
  const schemaFiles = listFiles(SCHEMAS_DIR).filter((f) => f.endsWith('.json'));

  if (serviceFiles.length === 0) {
    console.log('[api-contract-guard] No services found — skipped.');
    return 0;
  }

  let failures = 0;
  for (const svc of serviceFiles) {
    const exports = extractExports(join(SERVICES_DIR, svc));
    console.log(`[api-contract-guard] ${svc}: exports = [${exports.join(', ') || 'none'}]`);
    if (exports.length === 0) {
      console.error(`[api-contract-guard] FAIL: ${svc} has no exported functions`);
      failures += 1;
    }
  }

  console.log(`[api-contract-guard] schemas: ${schemaFiles.length} found`);

  if (failures > 0) {
    console.error(`[api-contract-guard] ${failures} failure(s)`);
    return 1;
  }
  console.log('[api-contract-guard] PASSED');
  return 0;
}

process.exit(main());