'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { main } = require('../../src/index');

test('main runs without error', () => {
  assert.doesNotThrow(() => main());
});