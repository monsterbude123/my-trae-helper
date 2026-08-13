'use strict';

/**
 * Greet a user by name.
 * @param {string} name
 * @returns {string}
 */
function greet(name) {
  if (!name || typeof name !== 'string') {
    throw new TypeError('name must be a non-empty string');
  }
  return `Hello, ${name}!`;
}

module.exports = { greet };