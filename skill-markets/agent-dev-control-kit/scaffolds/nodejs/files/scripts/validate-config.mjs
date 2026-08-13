#!/usr/bin/env node
// validate-config.mjs — sanity-check the gate/guard configs.

import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const ROOT = process.cwd();

function check(label, condition) {
  console.log(`${condition ? '✅' : '❌'} ${label}`);
  return condition;
}

function main() {
  let ok = true;

  ok &= check('package.json exists', existsSync(resolve(ROOT, 'package.json')));
  ok &= check('gates/gate-config.json exists', existsSync(resolve(ROOT, 'gates/gate-config.json')));
  ok &= check('guards/guard-config.json exists', existsSync(resolve(ROOT, 'guards/guard-config.json')));

  try {
    const gate = JSON.parse(readFileSync(resolve(ROOT, 'gates/gate-config.json'), 'utf8'));
    ok &= check('gate-config has L1', !!gate.levels?.L1);
    ok &= check('gate-config has L2', !!gate.levels?.L2);
  } catch (e) {
    console.error(`❌ gate-config.json invalid JSON: ${e.message}`);
    ok = false;
  }

  try {
    const guard = JSON.parse(readFileSync(resolve(ROOT, 'guards/guard-config.json'), 'utf8'));
    ok &= check(`guard-config has ${guard.guards?.length ?? 0} guard(s)`, (guard.guards?.length ?? 0) > 0);
  } catch (e) {
    console.error(`❌ guard-config.json invalid JSON: ${e.message}`);
    ok = false;
  }

  if (!ok) {
    console.error('Validation FAILED');
    process.exit(1);
  }
  console.log('Validation PASSED');
}

main();