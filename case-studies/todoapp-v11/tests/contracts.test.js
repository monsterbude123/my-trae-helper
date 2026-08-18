/**
 * V11 契约测试 — 验证 contracts/api-contracts.md 真实生效
 * 不依赖 server 启动,用 supertest-style 模拟 fetch 不行,所以直接 spawn server 子进程
 */
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

const SERVER = path.join(__dirname, '..', 'src', 'server.js');
const PORT = 3100; // 与生产端口 3000 隔离

let proc;
let pass = 0, fail = 0;

function log(test, ok, detail = '') {
  if (ok) { pass++; console.log(`  ✓ ${test} ${detail}`); }
  else { fail++; console.log(`  ✗ ${test} ${detail}`); }
}

function req(method, urlPath, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const r = http.request({
      hostname: 'localhost',
      port: PORT,
      path: urlPath,
      method,
      headers: data ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } : {},
    }, (res) => {
      let buf = '';
      res.on('data', (c) => buf += c);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: buf ? JSON.parse(buf) : null });
        } catch (e) { resolve({ status: res.statusCode, body: buf }); }
      });
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

async function main() {
  console.log('--- V11 todoApp 契约测试 (Stage 3.5 verify) ---');
  proc = spawn('node', [SERVER], { env: { ...process.env, PORT: String(PORT) } });
  proc.stderr.on('data', (d) => process.stderr.write(d));

  // 等服务启动
  await new Promise((r) => setTimeout(r, 800));

  // 1. /health 探针
  let r = await req('GET', '/health');
  log('GET /health 200', r.status === 200 && r.body.status === 'ok', `(status=${r.status}, body=${JSON.stringify(r.body)})`);

  // 2. POST /api/todos 正常
  r = await req('POST', '/api/todos', { title: '写 V11 报告' });
  log('POST /api/todos 创建 todo', r.status === 201 && r.body.todo.id === 1, `(id=${r.body?.todo?.id})`);
  const todoId = r.body.todo.id;

  // 3. POST /api/todos 缺 title → 400
  r = await req('POST', '/api/todos', {});
  log('POST /api/todos 缺 title 返回 400', r.status === 400 && /title/.test(r.body.error), `(status=${r.status})`);

  // 4. GET /api/todos 列表含 todoId
  r = await req('GET', '/api/todos');
  log('GET /api/todos 列表非空', r.status === 200 && r.body.todos.some((t) => t.id === todoId), `(count=${r.body.todos.length})`);

  // 5. PATCH /api/todos/:id 切换 done
  r = await req('PATCH', `/api/todos/${todoId}`, { done: true });
  log('PATCH /api/todos/:id done=true', r.status === 200 && r.body.todo.done === true, `(done=${r.body.todo.done})`);

  // 6. PATCH 不存在 id → 404
  r = await req('PATCH', '/api/todos/999', { done: true });
  log('PATCH 不存在 id 返回 404', r.status === 404, `(status=${r.status})`);

  // 7. DELETE /api/todos/:id
  r = await req('DELETE', `/api/todos/${todoId}`);
  log('DELETE /api/todos/:id', r.status === 200 && r.body.deleted === todoId, `(deleted=${r.body.deleted})`);

  // 8. GET /health 后 todo 计数 = 0
  r = await req('GET', '/health');
  log('GET /health 后 todos=0', r.body.todos === 0, `(todos=${r.body.todos})`);

  console.log(`\n=== ${pass} pass / ${fail} fail ===`);
  proc.kill();
  process.exit(fail > 0 ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  if (proc) proc.kill();
  process.exit(1);
});