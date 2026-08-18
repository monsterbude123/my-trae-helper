/**
 * todoApp — Express 后端(内存存储,无 DB)
 * 端口 3000,符合 V11 commit-minimum-check.py /health 探针
 */
const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;

// 内存存储(todo = {id, title, done, created_at})
let todos = [];
let nextId = 1;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// 健康检查(V11 gate.base_url 探针)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'todoapp-v11', todos: todos.length });
});

// 列出全部 todos
app.get('/api/todos', (req, res) => {
  res.json({ todos });
});

// 创建 todo
app.post('/api/todos', (req, res) => {
  const { title } = req.body || {};
  if (!title || typeof title !== 'string' || title.trim() === '') {
    return res.status(400).json({ error: 'title 不能为空' });
  }
  const todo = {
    id: nextId++,
    title: title.trim(),
    done: false,
    created_at: new Date().toISOString(),
  };
  todos.push(todo);
  res.status(201).json({ todo });
});

// 切换 done 状态
app.patch('/api/todos/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const todo = todos.find((t) => t.id === id);
  if (!todo) return res.status(404).json({ error: 'todo 不存在' });
  if (typeof req.body.done === 'boolean') todo.done = req.body.done;
  res.json({ todo });
});

// 删除 todo
app.delete('/api/todos/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const idx = todos.findIndex((t) => t.id === id);
  if (idx === -1) return res.status(404).json({ error: 'todo 不存在' });
  todos.splice(idx, 1);
  res.json({ deleted: id });
});

// 错误兜底
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'internal error' });
});

app.listen(PORT, () => {
  console.log(`todoApp listening on http://localhost:${PORT}`);
});