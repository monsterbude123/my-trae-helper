# Python 懒人开发指南

> Python 社区也有过度工程倾向。本指南聚焦 Python 特有的简化机会。
>
> 读取本文件的时机：当你写 Python 代码时，对照检查是否有更 Pythonic 的写法。

---

## 1. 数据结构惯用法

### dict 操作

```python
# ❌ 检查 key 再取值
if 'key' in d:
    value = d['key']
else:
    value = 'default'

# ✅ .get 一行搞定
value = d.get('key', 'default')

# ❌ 设置不存在的值
if 'key' not in d:
    d['key'] = []
d['key'].append(value)

# ✅ setdefault 一行
d.setdefault('key', []).append(value)

# ❌ dict 合并
merged = d1.copy()
merged.update(d2)

# ✅ Python 3.9+
merged = d1 | d2
```

### list 推导 vs for 循环

```python
# ❌ for 循环构建 list
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x ** 2)

# ✅ 列表推导
squares = [x ** 2 for x in range(10) if x % 2 == 0]

# ✅ dict 推导
name_map = {u.id: u.name for u in users}

# ✅ set 推导
unique = {u.email for u in users}
```

### 解构 (unpacking)

```python
# ❌ 临时变量交换
tmp = a
a = b
b = tmp

# ✅
a, b = b, a

# ❌ 逐个取值
first = items[0]
second = items[1]
rest = items[2:]

# ✅
first, second, *rest = items

# ❌ 函数返回多值用 dict 或 tuple[0]
def get_user(): return {'name': 'Tom', 'age': 20}
user = get_user()
name = user['name']

# ✅ namedtuple / dataclass / 多值返回
from collections import namedtuple
UserInfo = namedtuple('UserInfo', ['name', 'age'])
def get_user(): return UserInfo('Tom', 20)
user = get_user()
name = user.name
```

---

## 2. pathlib 替代 os.path

```python
# ❌ os.path 系列
import os
dir_path = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(dir_path, '..', 'data', 'config.json')
with open(data_file) as f:
    content = f.read()

# ✅ pathlib
from pathlib import Path
data_file = Path(__file__).resolve().parent.parent / 'data' / 'config.json'
content = data_file.read_text()

# pathlib 常用操作
Path.home()                          # 用户目录
Path.cwd()                           # 当前工作目录
p.parent                             # 父目录
p.name                               # 文件名
p.suffix                             # 扩展名 .json
p.stem                               # 不带扩展名的文件名
p.exists()                           # 是否存在
p.is_file() / p.is_dir()             # 类型判断
p.read_text(encoding='utf-8')        # 读取文本
p.write_text(data, encoding='utf-8') # 写入文本
p.read_bytes()                       # 读取二进制
p.glob('**/*.py')                    # 递归 glob
p.mkdir(parents=True, exist_ok=True) # 递归建目录
```

---

## 3. dataclass 替代手写类

```python
# ❌ 手写 __init__ / __repr__ / __eq__
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point(x={self.x}, y={self.y})'

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

# ✅ dataclass 一行装饰器搞定
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# 命名元组（不可变 + 更轻量）
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
```

---

## 4. 上下文管理器简化资源管理

```python
# ❌ 手动 close
f = open('file.txt')
try:
    content = f.read()
finally:
    f.close()

# ✅ with 语句
with open('file.txt') as f:
    content = f.read()

# 自定义上下文管理器（比写 __enter__/__exit__ 更简单的方式）
from contextlib import contextmanager

@contextmanager
def temp_chdir(path):
    """临时切换工作目录"""
    import os
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)
```

---

## 5. 简化函数设计

### 一个函数只做一件事，但不要拆太碎

```python
# ❌ 过度拆分——一个简单逻辑拆成 5 个单行函数
def get_name(user):
    return user['name']

def capitalize(s):
    return s.capitalize()

def greet(name):
    return f'Hello, {name}!'

def greet_user(user):
    return greet(capitalize(get_name(user)))

# ✅ 一个函数刚好够
def greet_user(user):
    name = user['name'].capitalize()
    return f'Hello, {name}!'
```

### 用参数默认值替代工厂

```python
# ❌ 工厂函数每个参数一种变体
def create_http_client(): ...
def create_http_client_with_timeout(timeout): ...
def create_http_client_with_retry(timeout, retries): ...

# ✅ 默认参数
def create_http_client(timeout=30, retries=3): ...
```

---

## 6. 装饰器简化横切关注点

```python
# 缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_query(user_id: int) -> dict:
    # 结果自动缓存
    return db.query(...)

# 计时
import time

def timed(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f'{func.__name__}: {time.time() - start:.3f}s')
        return result
    return wrapper

# 重试
def retry(times=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == times - 1:
                        raise
                    print(f'重试 {i + 1}/{times}: {e}')
        return wrapper
    return decorator
```

---

## 7. 并发简化

```python
# ❌ 手写线程管理
import threading
threads = []
for url in urls:
    t = threading.Thread(target=download, args=(url,))
    t.start()
    threads.append(t)
for t in threads:
    t.join()

# ✅ 线程池
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download, urls))

# ✅ 异步
import asyncio
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

---

## 8. 常见的可删除依赖

| pip 包 | 为什么可以删 | 用这个替代 |
|--------|-------------|-----------|
| `pytz` | 时区处理 | `zoneinfo`（Python 3.9+ 内置）|
| `python-dotenv` | 加载 .env | 手写 10 行解析或 `os.environ.get()` |
| `requests`（简单场景） | HTTP GET | `urllib.request` 或 `httpx`（异步） |
| `pandas`（仅读写 CSV） | 重量级依赖 | `csv` 模块 |
| `attrs` | 比 dataclass 功能多 | `dataclass`（3.7+ 内置，够用） |
| `loguru` | 比 logging 好看 | `logging`（内置，已经够用） |
| `sh` | 调 shell 命令 | `subprocess.run()` |
| `click`（简单场景）| 命令行参数 | `argparse`（内置） |
| `pydantic`（简单场景）| 数据验证 | `dataclass` + 手动验证 |
| `jsonschema`（简单验证）| JSON Schema 验证 | 手动检查必需字段 |
| `cachetools` | 缓存 | `functools.lru_cache` / `functools.cache` |
| `pathlib2` | pathlib 的 backport | 直接用 `pathlib`（Python 3.4+ 内置） |
| `pipenv` / `poetry`（简单项目）| 包管理 | `pip` + `requirements.txt` |
| `black` / `isort`（如果没团队规范）| 格式化 | IDE 自带格式化 |

---

## 9. Python 项目启动检查清单

在 `pip install` 之前先确认：

- [ ] 真的需要一个新包？标准库已经读过了？
- [ ] Python 版本 >= 3.9？很多新功能已经内置了
- [ ] 这个包的功能其实只有一两个函数？手写是不是更简单？
- [ ] `zoneinfo`、`dataclass`、`pathlib`、`tomllib` 这些内置替代品确认过？
- [ ] 这个包的依赖树多大？（`pip show <pkg>` 看看）
- [ ] 团队已经有的依赖中，有没有功能重叠的？

---

## 10. Pythonic 速查口诀

```
取 dict 值用 .get() 而不是先 in 再 []
迭代用 for item in items 而不是 range(len())
字符串拼接用 f-string 而不是 % 或 .format()
文件操作用 with 而不是 手写 try/finally
路径操作优先 pathlib 而不是 os.path
需要简单类用 dataclass 而不是手写 __init__
检查是否为空用 if items: 而不是 if len(items) > 0:
```
