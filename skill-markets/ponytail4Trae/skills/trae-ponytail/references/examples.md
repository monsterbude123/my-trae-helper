# 简化示例大全

> 每个例子都是"过度工程 vs 最简实现"的对比。左边是大多数人会写的版本，右边是懒惰高级工程师的版本。
>
> 读取本文件的时机：当你准备引入一个新依赖，或者感觉某段代码太复杂时。

---

## 前端篇

### 1. 防抖

| | 过度工程 | 最简实现 |
|---|---|---|
| 方案 | `npm install lodash.debounce`（4.7KB）| 5 行手写 |
| 引入 | `import debounce from 'lodash/debounce'` | 无 |

```javascript
// ✅ 5 行，覆盖 90% 场景
function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(fn, delay, ...args); };
}

// ponytail: 手写 debounce，需要 leading/trailing/maxWait 选项时换 lodash.debounce
```

---

### 2. 节流

```javascript
// ✅ 7 行
function throttle(fn, interval) {
  let lastTime = 0;
  return (...args) => {
    const now = Date.now();
    if (now - lastTime >= interval) { lastTime = now; fn(...args); }
  };
}
```

---

### 3. 深拷贝

| | 过度工程 | 最简实现 |
|---|---|---|
| 方案 | `npm install lodash`（~70KB）| 1 行原生 API |
| 引入 | `import cloneDeep from 'lodash/cloneDeep'` | 无 |

```javascript
// ✅ 1 行
const copy = structuredClone(obj);

// 注意事项：structuredClone 不支持函数、Symbol、DOM 节点
// 这些场景才需要 lodash.cloneDeep
```

---

### 4. 浅合并

```javascript
// ❌ import merge from 'lodash/merge'
// ✅
const merged = { ...defaults, ...overrides };
```

---

### 5. 数组去重

```javascript
// ❌ import uniq from 'lodash/uniq'
// ✅
const unique = [...new Set(arr)];
```

---

### 6. Email 格式验证

| | 过度工程 | 最简实现 |
|---|---|---|
| 方案 | `npm install validator`（~80KB）| 3 行正则 |
| 大小 | 80KB | ~100 bytes |

```javascript
// ✅ 3 行
const isEmail = (s) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
// ponytail: 仅格式验证，如需验证邮箱真实性，改为发送验证邮件
```

---

### 7. UUID

| | 过度工程 | 最简实现 |
|---|---|---|
| 方案 | `npm install uuid` | 1 行原生 API |
| 大小 | ~3KB | 0 |

```javascript
// ✅ 1 行
const id = crypto.randomUUID();
```

---

### 8. URL 参数解析

| | 过度工程 | 最简实现 |
|---|---|---|
| 方案 | `npm install qs`（~10KB）| 0 行，原生 API |

```javascript
// ❌ import qs from 'qs';  const params = qs.parse(location.search);
// ✅ 0 行新代码，直接使用原生 API
const params = new URLSearchParams(location.search);
params.get('page');   // "1"
params.get('sort');   // "desc"
params.has('debug');  // true/false
```

---

### 9. 日期格式化

| | 过度工程 | 最简实现 |
|---|---|---|
| 方案 | `npm install dayjs`（~7KB）或 `moment`（~70KB）| 0 行原生 Intl API |

```javascript
// ❌ import dayjs from 'dayjs';  dayjs(date).format('YYYY-MM-DD');
// ✅
const date = new Date();

// 简单格式化
date.toISOString().split('T')[0];                    // "2026-06-22"

// 中文日期
date.toLocaleDateString('zh-CN');                     // "2026/6/22"

// 自定义格式
new Intl.DateTimeFormat('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit'
}).format(date);                                      // "2026/06/22"

// 相对时间
new Intl.RelativeTimeFormat('zh-CN').format(-3, 'day'); // "3天前"
new Intl.RelativeTimeFormat('zh-CN').format(1, 'hour'); // "1小时后"
```

---

### 10. 数字格式化

```javascript
// ❌ import numeral from 'numeral';  numeral(12345).format('0,0');
// ✅
new Intl.NumberFormat('zh-CN').format(12345);  // "12,345"

// 货币
new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' }).format(99.9);  // "¥99.90"

// 百分比
new Intl.NumberFormat('zh-CN', { style: 'percent' }).format(0.123);  // "12%"

// 保留两位小数
(3.14159).toFixed(2);  // "3.14"
```

---

### 11. 深比较（简单场景）

```javascript
// ❌ import isEqual from 'lodash/isEqual'
// ✅ JSON 序列化比较（适用于纯数据对象，无函数/Date/undefined）
function shallowEqual(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}
// ponytail: JSON 序列化比较，需要处理函数/Date/循环引用时换 lodash.isEqual
```

---

### 12. 随机颜色

```javascript
// ❌ npm install randomcolor (~10KB)
// ✅ 1 行
function randomColor() {
  return '#' + Math.floor(Math.random() * 0xFFFFFF).toString(16).padStart(6, '0');
}
```

---

### 13. Clipboard 读写

```javascript
// ❌ npm install clipboard.js (~4KB)
// ✅ 0 行
// 写入
await navigator.clipboard.writeText('要复制的文本');

// 读取
const text = await navigator.clipboard.readText();
```

---

## 后端篇

### 14. 环境变量加载

| | 过度工程 | 最简实现 |
|---|---|---|
| Node | `npm install dotenv` → `require('dotenv').config()` | `node --env-file=.env app.js`（Node 20.6+）|
| Python | `pip install python-dotenv` → `load_dotenv()` | 10 行手写解析 |

```javascript
// ✅ Node 20.6+
// 启动命令: node --env-file=.env app.js
// 代码中直接 process.env.DATABASE_URL

// ✅ 手写 .env 解析（10 行）
const fs = require('fs');
const env = Object.fromEntries(
  fs.readFileSync('.env', 'utf-8').split('\n')
    .filter(line => line.trim() && !line.startsWith('#'))
    .map(line => line.split('=').map(s => s.trim()))
);
Object.assign(process.env, env);
```

---

### 15. 递归创建/删除目录

```javascript
// ❌ npm install mkdirp + rimraf
// Node 14+ 直接内置
const fs = require('fs');

// 递归创建
fs.mkdirSync('a/b/c', { recursive: true });

// 递归删除
fs.rmSync('old/dir', { recursive: true, force: true });
```

---

### 16. HTTP 请求

| | 过度工程 | 最简实现 |
|---|---|---|
| 方案 | `npm install axios` | 内置 `fetch()`（Node 18+）|

```javascript
// ❌ import axios from 'axios';  const res = await axios.get(url);
// ✅
const res = await fetch('https://api.example.com/data');
const data = await res.json();

// 带超时
const data = await fetch(url, { signal: AbortSignal.timeout(5000) })
  .then(r => r.json());

// POST JSON
const res = await fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
});
```

---

### 17. 命令行参数

```javascript
// ❌ npm install commander / yargs
// ✅ Node 18.3+ 内置
import { parseArgs } from 'node:util';

const { values } = parseArgs({
  options: {
    port: { type: 'string', default: '3000' },
    debug: { type: 'boolean', default: false },
  },
});

console.log(values.port, values.debug);
// 运行: node app.js --port 8080 --debug
```

---

### 18. 密码哈希

```javascript
// ❌ npm install bcrypt（需要编译原生模块，安装常出问题）
// ✅ Node 内置
const crypto = require('crypto');

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  const [salt, hash] = stored.split(':');
  const computed = crypto.scryptSync(password, salt, 64).toString('hex');
  return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(computed));
}
// ponytail: scrypt 替代 bcrypt，需要 Argon2 算法时换 @noble/hashes
```

---

### 19. Python 数据类

```python
# ❌
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age!r})"

    def __eq__(self, other):
        if not isinstance(other, User): return False
        return self.name == other.name and self.email == other.email and self.age == other.age

# ✅
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int
# 自动生成 __init__、__repr__、__eq__
```

---

### 20. Python 路径操作

```python
# ❌
import os
path = os.path.join(os.path.dirname(__file__), 'data', 'config.json')
with open(path) as f: data = f.read()

# ✅
from pathlib import Path
path = Path(__file__).parent / 'data' / 'config.json'
data = path.read_text()
```

---

### 21. 简单 HTTP Server（开发用途）

```bash
# ❌ npm install http-server 并配置
# ✅ 一行
python -m http.server 8000
# 或
npx serve .     # 如果项目中已有 serve（npx 会自动下载临时使用）
```

```python
# ❌ 写一个 Flask/FastAPI 来提供静态文件
# ✅ 一行
python -m http.server 8000 --directory ./dist
```

---

### 22. 图片压缩（构建脚本）

```bash
# ❌ npm install imagemin + 多个插件（经常安装失败）
# ✅ 用系统工具
# Linux/Mac
find . -name '*.png' -exec pngquant --ext .png --force {} \;
# Windows: 用 sharp-cli（一个纯 JS 依赖，不需要原生编译）
npx sharp-cli --input ./input.png --output ./output.png --quality 80
```

---

### 23. SQL vs ORM

```python
# ❌ ORM 无法调试的 N+1 问题
users = session.query(User).all()
for user in users:
    orders = user.orders  # 每个 user 触发一次查询！

# ✅ SQL 一次性查完
users_with_orders = db.execute("""
    SELECT u.*, o.id as order_id, o.total
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
""").fetchall()

# ❌ ORM 复杂的聚合
session.query(
    Order.status,
    func.count(Order.id),
    func.sum(Order.total)
).group_by(Order.status).all()

# ✅ SQL 更清晰
db.execute("""
    SELECT status, COUNT(*), SUM(total)
    FROM orders
    GROUP BY status
""").fetchall()
```

---

## 总结对照表

| 需求 | 过度工程 | 最简方案 | 节省 |
|------|----------|----------|------|
| 防抖 | `lodash.debounce` (4.7KB) | 5 行手写 | 一个依赖 |
| 深拷贝 | `lodash.cloneDeep` (17KB) | `structuredClone()` | 一个依赖 |
| UUID | `uuid` 包 | `crypto.randomUUID()` | 一个依赖 |
| 日期格式化 | `moment.js` (70KB) | `Intl.DateTimeFormat` | 一个重量级依赖 |
| Email 验证 | `validator.js` (80KB) | 3 行正则 | 一个依赖 |
| URL 参数 | `qs` (10KB) | `URLSearchParams` | 一个依赖 |
| 环境变量 | `dotenv` | `--env-file` 或 10 行 | 一个依赖 |
| HTTP 请求 | `axios` | `fetch()` (Node 18+) | 一个依赖 |
| 目录操作 | `mkdirp` + `rimraf` | `fs.mkdirSync/rmSync` | 两个依赖 |
| 命令行参数 | `commander` | `util.parseArgs()` | 一个依赖 |
| 密码哈希 | `bcrypt`（需编译） | `crypto.scryptSync` | 一个编译痛苦 |
| HTTP Server | `http-server` | `python -m http.server` | 按需使用 |
| 数据类 | 手写 `__init__`/`__repr__`/`__eq__` | `@dataclass` | 30 行 → 5 行 |
| 路径操作 | `os.path` | `pathlib.Path` | 更少 bug |
