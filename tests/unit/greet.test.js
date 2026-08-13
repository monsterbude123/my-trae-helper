'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { greet } = require('../../src/utils/greet');

test('greet returns greeting for valid name', () => {
  assert.equal(greet('Alice'), 'Hello, Alice!');
});

test('greet throws on empty name', () => {
  assert.throws(() => greet(''), TypeError);
});

test('greet throws on non-string name', () => {
  assert.throws(() => greet(123), TypeError);
});