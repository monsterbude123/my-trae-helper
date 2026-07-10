# 反面模式大全

> 看到以下模式，立即警觉并拒绝。每个模式都给出了"过度工程版本"和"最简版本"的对比。
>
> 读取本文件的时机：当你看到一段代码感觉"过于复杂"时，对照此表确认它是否属于某种反面模式。

---

## 抽象类

### 1. 只有一个实现的接口/抽象类

**坏**：为了"以后可能有其他实现"而创建一个接口，但目前只有一个实现。

```typescript
// ❌ 过度工程
interface IUserRepository {
  findById(id: string): Promise<User>;
  save(user: User): Promise<void>;
}

class PostgresUserRepository implements IUserRepository {
  async findById(id: string): Promise<User> { /* ... */ }
  async save(user: User): Promise<void> { /* ... */ }
}

// 使用时还要 DI 注入
class UserService {
  constructor(private repo: IUserRepository) {}
}

// ✅ 最简实现
class UserRepository {
  async findById(id: string): Promise<User> { /* ... */ }
  async save(user: User): Promise<void> { /* ... */ }
}

// 使用时直接 new
const users = new UserRepository();
```

**何时升级**：当真的有第二个实现（如 Mock 测试、切换数据库）时再抽接口。

---

### 2. 只有一个产品的工厂模式

**坏**：工厂只有一个产品类型，工厂比产品还复杂。

```typescript
// ❌ 过度工程
interface Notification { send(msg: string): void; }

class EmailNotification implements Notification {
  send(msg: string) { /* 发邮件 */ }
}

class NotificationFactory {
  static create(type: 'email'): Notification {
    switch (type) {
      case 'email': return new EmailNotification();
      default: throw new Error('Unknown type');
    }
  }
}

// 使用
const notif = NotificationFactory.create('email');
notif.send('Hello');

// ✅ 最简实现
function sendEmail(msg: string) { /* 发邮件 */ }

// 使用
sendEmail('Hello');
```

**何时升级**：当真的有 3+ 种通知方式时才需要工厂或多态。

---

### 3. 只有一个策略的策略模式

```python
# ❌ 过度工程
class TaxStrategy(ABC):
    @abstractmethod
    def calculate(self, amount): ...

class ChinaTaxStrategy(TaxStrategy):
    def calculate(self, amount):
        return amount * 0.13

# 使用：DI 注入、配置切换...
strategy = ChinaTaxStrategy()
tax = strategy.calculate(100)

# ✅ 最简实现
def calculate_tax(amount):
    return amount * 0.13

tax = calculate_tax(100)
```

---

## 过度配置

### 4. 永远不改的配置文件

```javascript
// ❌ 过度工程 —— config.js
module.exports = {
  port: 3000,
  host: 'localhost',
  maxRetries: 3,
  timeout: 5000,
};

// ✅ 最简实现 —— 硬编码，需要时再抽
const PORT = 3000;
const HOST = 'localhost';
const MAX_RETRIES = 3;
const TIMEOUT = 5000;
```

**什么该用配置**：不同环境不同值的（如数据库连接串）、用户需要自定义的、加密密钥。其他都不需要。

---

### 5. 环境变量过度抽象

```javascript
// ❌ 为每个常量都建环境变量
const PORT = process.env.APP_PORT || 3000;
const HOST = process.env.APP_HOST || '0.0.0.0';
const LOG_LEVEL = process.env.APP_LOG_LEVEL || 'info';
const LOG_FORMAT = process.env.APP_LOG_FORMAT || 'json';
const CACHE_TTL = parseInt(process.env.APP_CACHE_TTL || '3600');
const CACHE_SIZE = parseInt(process.env.APP_CACHE_SIZE || '1000');
// ... 30 个环境变量

// ✅ 只有真正因环境而异的值才配环境变量
const DATABASE_URL = process.env.DATABASE_URL; // 必须配置
const PORT = process.env.PORT || 3000;         // 合理的默认值
// 其他的直接硬编码
```

---

## 文件碎片化

### 6. 整个文件只有一个导出

```typescript
// ❌ 三个文件，其中一个只有一行
// utils/formatDate.ts
export function formatDate(d: Date): string {
  return d.toISOString().split('T')[0];
}

// utils/formatMoney.ts
export function formatMoney(n: number): string {
  return `¥${n.toFixed(2)}`;
}

// utils/index.ts
export { formatDate } from './formatDate';
export { formatMoney } from './formatMoney';

// ✅ 一个文件搞定
// utils.ts
export function formatDate(d: Date): string {
  return d.toISOString().split('T')[0];
}

export function formatMoney(n: number): string {
  return `¥${n.toFixed(2)}`;
}
```

**记住**：800 行以内不拆分。re-export index.ts 是无意义的中间层。

---

### 7. 只有一个调用者的工具函数

```javascript
// ❌ 抽出只有一处使用的函数
function calculateFinalPrice(price, tax, discount) {
  const afterTax = price * (1 + tax);
  const afterDiscount = afterTax * (1 - discount);
  return Math.round(afterDiscount * 100) / 100;
}

function createOrder(product, quantity) {
  const finalPrice = calculateFinalPrice(product.price, 0.13, 0.1);
  // ... 其他逻辑
}

// ✅ 内联到调用处
function createOrder(product, quantity) {
  // 计算最终价格：含税 + 折扣
  const price = product.price;
  const afterTax = price * 1.13;
  const afterDiscount = afterTax * 0.9;
  const finalPrice = Math.round(afterDiscount * 100) / 100;
  // ... 其他逻辑
}
```

**但在以下情况可以抽**：逻辑被 3+ 处使用、逻辑不直观需要单独测试、逻辑超过 15 行影响可读性。

---

### 8. 过度拆分的组件

```tsx
// ❌ 五个文件实现一个表单
// components/UserForm/index.tsx
// components/UserForm/NameField.tsx
// components/UserForm/EmailField.tsx
// components/UserForm/SubmitButton.tsx
// components/UserForm/types.ts
// components/UserForm/validators.ts

// ✅ 一个文件
// components/UserForm.tsx (80 行)
function UserForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  function validate() { /* 10 行 */ }
  function handleSubmit(e) { /* 5 行 */ }

  return (
    <form onSubmit={handleSubmit}>
      <label>姓名 <input value={name} onChange={e => setName(e.target.value)} /></label>
      <label>邮箱 <input value={email} onChange={e => setEmail(e.target.value)} /></label>
      <button type="submit">提交</button>
    </form>
  );
}
```

---

## 过度设计

### 9. 为了"未来可能"的扩展点

```javascript
// ❌ 提前为"未来"设计的钩子
function processOrder(order, hooks = {}) {
  hooks.beforeProcess?.();
  const result = doProcess(order);
  hooks.afterProcess?.(result);
  hooks.onError = hooks.onError || console.error;
  return result;
}

// 目前只有一个调用者，从来不改 hooks

// ✅ 直接写
function processOrder(order) {
  return doProcess(order);
}
```

---

### 10. Template Method（模板方法模式）用继承替代组合

```python
# ❌ 为了复用 3 行代码搞了一套继承
class DataExporter(ABC):
    def export(self):
        data = self.fetch_data()
        formatted = self.format(data)
        self.write(formatted)

    @abstractmethod
    def fetch_data(self): ...
    @abstractmethod
    def format(self, data): ...
    @abstractmethod
    def write(self, formatted): ...

class CSVExporter(DataExporter):
    def fetch_data(self): return get_rows()
    def format(self, data): return to_csv(data)
    def write(self, s): Path('out.csv').write_text(s)

# ✅ 一个函数
def export_csv():
    rows = get_rows()
    csv = to_csv(rows)
    Path('out.csv').write_text(csv)
```

---

### 11. Builder 模式替代直接赋值

```typescript
// ❌ Builder 模式用于简单对象
class RequestBuilder {
  private url: string;
  private method: string = 'GET';
  private headers: Record<string, string> = {};

  setUrl(url: string) { this.url = url; return this; }
  setMethod(m: string) { this.method = m; return this; }
  setHeader(k: string, v: string) { this.headers[k] = v; return this; }
  build() {
    return { url: this.url, method: this.method, headers: this.headers };
  }
}

const req = new RequestBuilder()
  .setUrl('https://api.example.com')
  .setMethod('POST')
  .setHeader('Content-Type', 'application/json')
  .build();

// ✅ 直接写对象
const req = {
  url: 'https://api.example.com',
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
};
```

---

### 12. 装饰器模式替代函数组合

```javascript
// ❌ 装饰器模式包装日志
class Service {
  doWork() { /* ... */ }
}

class LoggingServiceDecorator {
  constructor(private service) {}
  doWork() {
    console.log('开始');
    const result = this.service.doWork();
    console.log('结束');
    return result;
  }
}

// ✅ 高阶函数（如果有多处需要）
function withLogging(fn) {
  return (...args) => {
    console.log('开始');
    const result = fn(...args);
    console.log('结束');
    return result;
  };
}

// 或者干脆只在需要的地方加两行
function doWork() {
  console.log('开始 doWork');
  const result = /* ... */;
  console.log('doWork 完成');
  return result;
}
```

---

## 控制流

### 13. 深层 if-else 嵌套

```javascript
// ❌ 箭头式代码
function getDiscount(user) {
  if (user) {
    if (user.isVip) {
      if (user.years > 5) {
        return 0.3;
      } else {
        return 0.2;
      }
    } else {
      if (user.isNew) {
        return 0.1;
      } else {
        return 0;
      }
    }
  } else {
    return 0;
  }
}

// ✅ 提前 return
function getDiscount(user) {
  if (!user) return 0;
  if (user.isVip && user.years > 5) return 0.3;
  if (user.isVip) return 0.2;
  if (user.isNew) return 0.1;
  return 0;
}
```

---

### 14. switch-case 过长可用查表

```javascript
// ❌ 冗长的 switch
function getStatusText(code) {
  switch (code) {
    case 0: return '待处理';
    case 1: return '处理中';
    case 2: return '已完成';
    case 3: return '已取消';
    case 4: return '已退款';
    default: return '未知';
  }
}

// ✅ 查表法
const STATUS_MAP = {
  0: '待处理',
  1: '处理中',
  2: '已完成',
  3: '已取消',
  4: '已退款',
};
function getStatusText(code) {
  return STATUS_MAP[code] ?? '未知';
}
```

---

## 类型体操

### 15. 类型声明过度嵌套

```typescript
// ❌ 类型层层继承
interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

interface NamedEntity extends BaseEntity {
  name: string;
}

interface UserEntity extends NamedEntity {
  email: string;
  role: UserRole;
}

// ✅ 扁平化
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  createdAt: Date;
  updatedAt: Date;
}
```

**记住**：类型声明的维护成本 ≠ 0。3 层继承以上就该摊平。

---

### 16. 泛型过度抽象

```typescript
// ❌ 泛型地狱
type ApiResponse<T, E = Error, M = Record<string, string>> = {
  data: T;
  error: E | null;
  meta: M;
  status: number;
};

// 大多数调用只用到 T
const res: ApiResponse<User, ApiError, PaginationMeta> = await fetchUsers();

// ✅ 直接用具体类型
interface UserListResponse {
  data: User[];
  error: string | null;
  total: number;
}

const res: UserListResponse = await fetchUsers();
```

---

## 其他常见反面模式

### 17. 引入"便利"库处理一两行原生就能做的事

```bash
# ❌ npm install left-pad (11 行代码的包，曾导致整个 npm 崩坏)
# ✅
const padded = str.padStart(10, '0');
```

### 18. 注释比代码还长

```javascript
// ❌
/**
 * 获取用户的全名
 * @param {object} user - 用户对象
 * @param {string} user.firstName - 用户的名
 * @param {string} user.lastName - 用户的姓
 * @returns {string} 用户的全名，格式为 "名 姓"
 * @example
 * getFullName({ firstName: '三', lastName: '张' })
 * // => '三 张'
 */
function getFullName(user) {
  return `${user.firstName} ${user.lastName}`;
}

// ✅ 代码即文档
function getFullName(user) {
  return `${user.firstName} ${user.lastName}`;
}
```

### 19. try-catch 包裹一切

```javascript
// ❌ 每层都 try-catch
async function handler(req, res) {
  try {
    const user = await getUser(req.params.id);
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}

// ✅ 只在最外层 catch（Express 中间件 / FastAPI exception handler）
async function handler(req, res) {
  const user = await getUser(req.params.id);
  res.json(user);
}
// 顶层框架的 error handler 统一处理
```

### 20. Promise 链过深

```javascript
// ❌ then 地狱
fetchUser(id)
  .then(user => fetchOrders(user.id)
    .then(orders => fetchDetails(orders[0].id)
      .then(details => ({ user, orders, details }))));

// ✅ async/await
const user = await fetchUser(id);
const orders = await fetchOrders(user.id);
const details = await fetchDetails(orders[0].id);
```
