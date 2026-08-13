'use strict';

const { greet } = require('./utils/greet');

const PORT = process.env.PORT || 3000;

function main() {
  const message = greet('World');
  console.log(message);
  console.log(`Listening on port ${PORT}`);
}

if (require.main === module) {
  main();
}

module.exports = { main };