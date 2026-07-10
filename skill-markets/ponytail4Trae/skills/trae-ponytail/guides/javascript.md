# JavaScript / TypeScript 懒人开发指南

> JS 生态是过度工程的重灾区。本指南聚焦 JS/TS 特有的陷阱和简化模式。
>
> 读取本文件的时机：当你写 JavaScript 或 TypeScript 代码时，对照检查是否有更简单的写法。

---

## 1. 变量和类型

### null vs undefined：不需要同时检查

```javascript
// ❌ 过度防御
if (value === null || value === undefined || value === '') { ... }

// ✅ 用 == null 同时检查 null 和 undefined
if (value == null) { ... }

// ✅ 或者用 ! 检查 falsy（但要小心 0 和 false）
if (!value) { ... }
```

### 默认值：用 ?? 而不是 ||

```javascript
// ❌ || 会把 0、''、false 也当作假值
const count = input || 10;  // input=0 时错误地取 10

// ✅ Nullish coalescing 只处理 null/undefined
const count = input ?? 10;  // input=0 时正确取 0
```

### TypeScript 类型推断：不要显式标注能推断的类型

```typescript
// ❌ 冗余的类型标注
const name: string = 'hello';
const items: number[] = [1, 2, 3];
const user: User = { id: '1', name: 'Tom', email: 'tom@example.com' };

// ✅ 类型可以被推断，省略标注
const name = 'hello';
const items = [1, 2, 3];
const user = { id: '1', name: 'Tom', email: 'tom@example.com' };
```

### TypeScript 类型体操：不要为了类型而类型

```typescript
// ❌ 不必要的泛型
function identity<T>(arg: T): T { return arg; }

// ❌ 不必要的类型别名
type StringOrNumber = string | number;
function process(value: StringOrNumber) { ... }
// 直接用 string | number

// ✅ 泛型只在真正需要类型间关系时使用
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  return keys.reduce((acc, k) => ({ ...acc, [k]: obj[k] }), {} as Pick<T, K>);
}
```

---

## 2. 数组操作惯用法

```javascript
// 遍历并转换 → map
const names = users.map(u => u.name);

// 过滤 → filter
const active = users.filter(u => u.status === 'active');

// 查找第一个 → find
const admin = users.find(u => u.role === 'admin');

// 检查是否存在 → some
const hasAdmin = users.some(u => u.role === 'admin');

// 全部满足 → every
const allActive = users.every(u => u.status === 'active');

// 累加/聚合 → reduce
const total = orders.reduce((sum, o) => sum + o.amount, 0);

// 分组 → Object.groupBy (ES2024)
const byRole = Object.groupBy(users, u => u.role);
```

### 避免的数组模式

```javascript
// ❌ for 循环做 map 的事
const names = [];
for (let i = 0; i < users.length; i++) {
  names.push(users[i].name);
}

// ✅
const names = users.map(u => u.name);

// ❌ filter + map 两个循环
const names = users.filter(u => u.active).map(u => u.name);

// ✅ flatMap 一次遍历
const names = users.flatMap(u => u.active ? u.name : []);

// ❌ forEach 做 reduce 的事
let total = 0;
orders.forEach(o => { total += o.amount; });

// ✅
const total = orders.reduce((sum, o) => sum + o.amount, 0);
```

---

## 3. 对象操作惯用法

```javascript
// 解构取字段
const { name, email } = user;

// 解构 + 重命名
const { name: userName, email: userEmail } = user;

// 解构 + 默认值
const { theme = 'light' } = settings;

// 展开合并
const updated = { ...user, name: 'New Name' };

// 排除字段
const { password, ...safe } = user;  // safe 不含 password

// 动态 key
const key = 'dynamicField';
const obj = { [key]: 'value' };

// 检查 key 存在
if (key in obj) { ... }
if (obj.hasOwnProperty(key)) { ... }

// Object.keys / values / entries
Object.keys(user);     // ['name', 'email']
Object.values(user);   // ['Tom', 'tom@example.com']
Object.entries(user);  // [['name', 'Tom'], ['email', 'tom@example.com']]
```

---

## 4. React 简化模式

### 不需要 useEffect 的场景

```tsx
// ❌ 用 useEffect 做能在渲染中做的事
function UserGreeting({ user }) {
  const [greeting, setGreeting] = useState('');
  useEffect(() => {
    setGreeting(`Hello, ${user.name}!`);
  }, [user]);
  return <div>{greeting}</div>;
}

// ✅ 直接在渲染中计算
function UserGreeting({ user }) {
  const greeting = `Hello, ${user.name}!`;
  return <div>{greeting}</div>;
}

// ✅ 如果计算昂贵，用 useMemo
function UserGreeting({ user }) {
  const greeting = useMemo(() => `Hello, ${user.name}!`, [user]);
  return <div>{greeting}</div>;
}
```

### 不需要 Redux / Zustand 的场景

```tsx
// ❌ 全局状态管理用于单个组件的状态
const store = create({ count: 0 });

// ✅ 简单的 useState 或 useReducer
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}

// ✅ 兄弟组件通信 → 状态提升到父组件
function Parent() {
  const [value, setValue] = useState('');
  return (
    <>
      <InputA value={value} onChange={setValue} />
      <DisplayB value={value} />
    </>
  );
}
```

### 不需要 useCallback

```tsx
// ❌ 无意义地包裹每一个 callback
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);

// ✅ 只在传给 memo 组件的 callback 才需要 useCallback
// 大多数情况下直接写就行
const handleClick = () => doSomething(id);
```

### 条件渲染简化

```tsx
// ❌ 复杂的三元
{status === 'loading' ? <Spinner /> : status === 'error' ? <Error /> : <Content />}

// ✅ 提前 return 或对象映射
function StatusView({ status }) {
  if (status === 'loading') return <Spinner />;
  if (status === 'error') return <Error />;
  return <Content />;
}

// ✅ 或者查表法
const STATUS_VIEWS = {
  loading: <Spinner />,
  error: <Error />,
  success: <Content />,
};
{STATUS_VIEWS[status]}
```

---

## 5. Vue 简化模式

### 不需要 Vuex / Pinia 的场景

```javascript
// ❌ 引入 Pinia 管理单个组件的状态
// ❌ 引入 Pinia 管理单页面共享的状态

// ✅ 简单场景：组件内 ref/reactive
const count = ref(0);

// ✅ 跨组件共享简单状态：composable
// composables/useSharedState.js
import { ref } from 'vue';
const shared = ref(0);
export function useSharedState() {
  return { shared };
}
```

### 不需要 computed 的场景

```javascript
// ❌ computed 只做简单取值
const name = computed(() => user.value.name);

// ✅ 直接取就行
const name = user.value.name;  // 或者模板中 {{ user.name }}
```

---

## 6. Node.js 简化模式

### Express 不需要过度中间件

```javascript
// ❌ 一个简单 API 引入 10 个中间件
const app = express();
app.use(cors());
app.use(helmet());
app.use(morgan('dev'));
app.use(compression());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(session({ ... }));
app.use(passport.initialize());
app.use(passport.session());

// ✅ 最简单的 API
const http = require('http');
const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok' }));
  }
});
server.listen(3000);
```

### 异步处理简化

```javascript
// ❌ Promise 链
fetchUser()
  .then(user => fetchOrders(user.id))
  .then(orders => processOrders(orders))
  .catch(err => handleError(err));

// ✅ async/await
try {
  const user = await fetchUser();
  const orders = await fetchOrders(user.id);
  await processOrders(orders);
} catch (err) {
  handleError(err);
}

// ✅ 不需要 try-catch 时更干净
const user = await fetchUser();
const orders = await fetchOrders(user.id);

// ✅ 并行请求
const [user, config] = await Promise.all([fetchUser(), fetchConfig()]);
```

---

## 7. 常见的可删除依赖

| npm 包 | 为什么可以删 | 用这个替代 |
|--------|-------------|-----------|
| `lodash` (全套) | 你只用 2-3 个函数 | 手写或原生 API |
| `moment` / `dayjs` | 70KB for 日期格式化 | `Intl.DateTimeFormat` |
| `axios` | 9KB for HTTP | `fetch()`（Node 18+）|
| `dotenv` | 单独安装 | `node --env-file=.env` (20.6+) |
| `uuid` | 3KB for UUID | `crypto.randomUUID()` |
| `classnames` | 600B for 类名拼接 | 手写 `${...}` 或 `[...].filter(Boolean).join(' ')` |
| `cross-env` | 跨平台 NODE_ENV | `set NODE_ENV=production &&` (Win) / `NODE_ENV=production` (Unix)，直接用脚本区分 |
| `rimraf` | 删目录 | `fs.rmSync(path, { recursive: true })` |
| `mkdirp` | 递归建目录 | `fs.mkdirSync(path, { recursive: true })` |
| `nodemon` | 文件变更重启 | `node --watch` (Node 18+) |
| `concurrently` | 并行运行脚本 | `npm-run-all` 或 `&` |
| `prettier` | 格式化 | 如果项目没强制统一格式，IDE 自带格式化就够了 |

---

## 8. JS/TS 项目启动检查清单

在 `npm install` 之前先确认：

- [ ] 真的需要一个新包？标准库和平台 API 已经读过了？
- [ ] 你只用这个包的一个函数？手写是不是更简单？
- [ ] 这个包有原生替代方案吗？（对照 platform-native.md）
- [ ] 这个包的大小值得吗？（bundlephobia.com）
- [ ] 这个包维护状态良好吗？（最后更新 > 1 年 = 危险信号）
- [ ] 团队已经有的依赖中，有没有功能重叠的？
