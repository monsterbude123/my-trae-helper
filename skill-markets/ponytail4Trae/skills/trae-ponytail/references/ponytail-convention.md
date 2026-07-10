# ponytail: 注释约定与自检规则

> 本节覆盖两个核心机制：如何标记有意的技术债，以及如何用最小代价给代码加自检。

---

## ponytail: 注释约定

当你**有意**做了一个简化决策时，用 `ponytail:` 注释记录。这不是普通 TODO，而是"我知道这里的取舍，这是有意的，以下是触发升级的条件"。

### 格式

```
// ponytail: <天花板描述>, <升级路径或触发条件>
```

### 为什么这么做

1. **可审计**：`grep -r "ponytail:" .` 一次找到所有有意的技术债
2. **有触发条件**：不是模糊的"以后优化"，而是"当 X 发生时"
3. **新成员友好**：后来者知道这是有意为之，不是疏忽
4. **防止以后再说变永远不说**

### 常见场景示例

#### 性能取舍

```javascript
// ponytail: 全局锁，如果吞吐量成为瓶颈，升级为按账户粒度加锁
const lock = new Mutex();

// ponytail: O(n²) 扫描，当数据量超过 10000 条时改为 Map 索引
items.forEach(a => {
  items.forEach(b => { if (a.id === b.parent) { ... } });
});

// ponytail: 轮询代替 WebSocket，当并发用户 >100 时切换为 SSE
setInterval(fetchUpdates, 5000);

// ponytail: 全量加载到内存，当文件超过 100MB 时改为流式处理
const data = JSON.parse(fs.readFileSync(path, 'utf-8'));
```

#### 简化实现

```javascript
// ponytail: 简单正则验证，如需验证邮箱真实性，改为发送验证邮件
const isEmail = (s) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);

// ponytail: localStorage 存储，需要跨设备同步时换 IndexedDB+后端
localStorage.setItem('prefs', JSON.stringify(prefs));

// ponytail: 仅英文排序，需要国际化时改用 Intl.Collator
items.sort((a, b) => a.name.localeCompare(b.name));

// ponytail: confirm() 弹窗，需要自定义 UI 时换 <dialog> 组件
if (!confirm('确定删除？')) return;
```

#### 依赖决策

```javascript
// ponytail: 手写 debounce 5 行代替 lodash.debounce(4.7KB)，需要 leading/trailing/maxWait 选项时换 lodash
function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(fn, delay, ...args); };
}

// ponytail: 手写 .env 解析代替 dotenv，需要变量展开/多行值时换 dotenv
const env = Object.fromEntries(
  fs.readFileSync('.env', 'utf-8').split('\n')
    .filter(l => l && !l.startsWith('#'))
    .map(l => l.split('=').map(s => s.trim()))
);
```

#### 语言特定

```python
# ponytail: re.split 分词，需要处理中文分词时换 jieba
words = re.split(r'\s+', text)

# ponytail: 内存缓存，需要持久化或分布式缓存时换 Redis
@functools.lru_cache(maxsize=256)
def get_user(user_id): ...

# ponytail: subprocess.run 调 git，需要复杂 git 操作时换 GitPython
result = subprocess.run(['git', 'log', '-1', '--format=%H'], capture_output=True, text=True)
```

```sql
-- ponytail: LIKE 搜索，数据量 >10 万行时启用 PostgreSQL FTS
SELECT * FROM articles WHERE title LIKE '%keyword%';

-- ponytail: 无索引查询，响应时间 >1s 时为 status 列加索引
SELECT * FROM orders WHERE status = 'pending';
```

### 债务盘点

定期运行以下命令盘点项目中所有 ponytail 标记：

```bash
# 列出所有有意的技术债
grep -rn "ponytail:" . --include="*.js" --include="*.ts" --include="*.py" --include="*.go" --include="*.rs" --include="*.sql"

# 按文件分组统计
grep -rc "ponytail:" . --include="*.js" --include="*.ts"
```

---

## 自检规则

非平凡逻辑必须留下**一个**可运行的检查。不是测试框架，不是测试文件——是最小的、可直接执行的自我证明。

### 核心原则

- **不需要测试框架**：无 mocha、jest、pytest、vitest
- **不需要 fixtures / setup / teardown**
- **只测核心逻辑路径**，不是穷举
- **一行函数不需要自检**
- **自检失败 = 代码就是坏的**

### 各语言自检模板

#### JavaScript / TypeScript

```javascript
// 方式 1：CommonJS 风格（Node）
function add(a, b) {
  return a + b;
}

if (require.main === module) {
  // 自检块
  console.assert(add(1, 2) === 3, 'add(1, 2) should be 3');
  console.assert(add(-1, 1) === 0, 'add(-1, 1) should be 0');
  console.log('✓ 自检通过');
}

// 方式 2：ESM 风格
import { fileURLToPath } from 'node:url';
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  console.assert(add(1, 2) === 3);
  console.log('✓ 自检通过');
}
```

#### Python

```python
def add(a, b):
    return a + b

if __name__ == "__main__":
    assert add(1, 2) == 3, "add(1, 2) should be 3"
    assert add(-1, 1) == 0, "add(-1, 1) should be 0"
    print("✓ 自检通过")
```

#### Shell

```bash
#!/usr/bin/env bash
add() {
    echo $(($1 + $2))
}

# 自检块
: <<'SELF_CHECK'
test "$(add 1 2)" = "3" || { echo "✗ add(1,2) failed"; exit 1; }
test "$(add -1 1)" = "0" || { echo "✗ add(-1,1) failed"; exit 1; }
echo "✓ 自检通过"
SELF_CHECK
```

#### Go

```go
package main

func add(a, b int) int {
    return a + b
}

// 运行自检: go run .
func main() {
    if add(1, 2) != 3 {
        panic("add(1, 2) should be 3")
    }
    if add(-1, 1) != 0 {
        panic("add(-1, 1) should be 0")
    }
    println("✓ 自检通过")
}
```

#### Rust

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    assert_eq!(add(1, 2), 3, "add(1, 2) should be 3");
    assert_eq!(add(-1, 1), 0, "add(-1, 1) should be 0");
    println!("✓ 自检通过");
}
```

### 什么需要自检，什么不需要

| 需要自检 | 不需要自检 |
|----------|-----------|
| 含分支逻辑的函数 | 纯属性赋值 |
| 数据转换/格式化 | 单行 wrapper |
| 算法实现 | getter/setter |
| 正则表达式 | 纯调用标准库的函数 |
| 状态机 | React 组件（用浏览器验证） |
| 校验函数 | CLI 入口（手动跑一次即可） |
| 排序/过滤逻辑 | 配置文件 |

### 自检的边界

自检不是单元测试。它只验证"代码能跑通核心路径"，不覆盖：
- 边缘情况（除非核心逻辑本身就处理边缘情况）
- 错误处理路径
- 性能基准
- 并发安全

它只是最小的"这段代码没坏"的证明。
