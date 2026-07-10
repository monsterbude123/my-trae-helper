# 平台原生能力大全

> 这里是"能不写代码就不写代码"的武器库。遇到需求时先查这张表，找到原生方案就不用写一行代码。
>
> 读取本文件的时机：当你准备引入一个新依赖，或者想确认某个功能是否有标准库/平台原生方案时。

---

## 浏览器原生 HTML 元素

这些元素在现代浏览器中全部可用，零 JS 即可实现交互。

| 需求 | 原生方案 | 为什么不用自己写 |
|------|----------|------------------|
| 日期选择器 | `<input type="date">` | 自带日历 UI，`min`/`max` 约束范围 |
| 时间选择器 | `<input type="time">` | 原生时间滚轮 |
| 日期时间选择 | `<input type="datetime-local">` | 日期+时间合并选择 |
| 月份选择 | `<input type="month">` | 年月选择 |
| 周选择 | `<input type="week">` | 周选择器 |
| 颜色选择器 | `<input type="color">` | 系统原生取色器，零行代码 |
| 弹窗/对话框 | `<dialog>` 元素 | 自带 `showModal()`、`close()`、`::backdrop`，无需 z-index 层叠 |
| 折叠/展开 | `<details>` + `<summary>` | 零 JS 手风琴，支持 `open` 属性控制默认状态 |
| 自动完成 | `<input list="id">` + `<datalist>` | 输入建议下拉，比自写 autocomplete 更可靠 |
| 范围滑块 | `<input type="range">` | 自带拖拽，`min`/`max`/`step` 控制 |
| 数字输入 | `<input type="number">` | 自带上下箭头，`min`/`max`/`step` |
| 进度条 | `<progress value="70" max="100">` | 确定进度和不确定进度（省略 value） |
| 度量仪 | `<meter value="0.6">` | 带 `low`/`high`/`optimum` 阈值自动着色 |
| 文件选择 | `<input type="file">` | 自带文件浏览对话框，`accept` 过滤类型，`multiple` 多选 |
| 搜索框 | `<input type="search">` | 自带清除按钮（WebKit） |
| 电话输入 | `<input type="tel">` | 手机上弹出数字键盘 |
| 图片按钮 | `<input type="image">` | 图片提交按钮，自带坐标信息 |
| 输出元素 | `<output>` | 表单计算结果展示，与表单关联 |
| 图片地图 | `<map>` + `<area>` | 无需 JS 的图片热点区域 |
| 选项分组 | `<optgroup>` | 下拉框分组，与 `<select>` 配合 |
| 表单验证 | `required`, `pattern`, `minlength`, `maxlength`, `min`, `max`, `type="email"`, `type="url"` | 零 JS 前端验证，`:invalid` / `:valid` 伪类配合样式 |

### HTML 元素的 JS 交互能力

| 功能 | 原生 API |
|------|----------|
| 获取表单数据 | `new FormData(formElement)` 直接拿到所有字段 |
| 表单校验 | `formElement.checkValidity()` + `formElement.reportValidity()` |
| 自定义验证消息 | `input.setCustomValidity("提示")` |
| 约束验证 API | `input.validity.tooShort` / `tooLong` / `valueMissing` / `typeMismatch` 等 |

---

## 现代 CSS 能力（无需预处理器）

| 需求 | 原生 CSS 方案 | 替代的预处理器功能 |
|------|-------------|-------------------|
| 变量/主题 | `--var: value;` + `var(--var, fallback)` | Less/Sass 变量 |
| 嵌套规则 | `&` 嵌套（CSS Nesting 规范） | Sass 嵌套 |
| 响应式字号 | `clamp(1rem, 2vw, 2rem)` | JS 计算 + resize 监听 |
| 容器查询 | `@container (min-width: 300px)` | JS 测量父容器宽度 |
| 网格布局 | `display: grid` | 手写 Flexbox 嵌套 |
| 子网格 | `grid-template-rows: subgrid` | 嵌套 Grid 手动对齐 |
| 粘性定位 | `position: sticky` | JS `scroll` 事件监听 |
| 平滑滚动 | `scroll-behavior: smooth` | JS `scrollTo({ behavior })` |
| 暗色模式 | `@media (prefers-color-scheme: dark)` | JS 检测系统主题 |
| 减少动画 | `@media (prefers-reduced-motion: reduce)` | JS 检测无障碍设置 |
| 滚动吸附 | `scroll-snap-type` + `scroll-snap-align` | JS 轮播库 |
| 视口单位 | `dvh` / `svh` / `lvh`（动态/小/大视口高度）| JS `innerHeight` 计算 |
| 宽高比 | `aspect-ratio: 16/9` | `padding-top` hack |
| 文本截断 | `text-overflow: ellipsis` + `overflow: hidden` + `white-space: nowrap` | JS 截断 |
| 多行截断 | `-webkit-line-clamp: 3` | JS 行数计算 |
| 滤镜 | `filter: blur() brightness() contrast() grayscale() sepia()` | Canvas 处理 |
| 背景滤镜 | `backdrop-filter: blur(10px)` | JS + Canvas 模糊 |
| 混合模式 | `mix-blend-mode` / `background-blend-mode` | Canvas 合成 |
| 遮罩 | `mask-image` / `clip-path` | JS / Canvas |
| 逻辑属性 | `margin-inline` / `padding-block` 替代 `left`/`right`（国际化友好）| 手动区分 RTL |
| 选择器 | `:has()`, `:is()`, `:where()`, `:not()` | JS 查询遍历 |
| 内容可见性 | `content-visibility: auto` | 虚拟滚动库 |
| 层叠上下文 | `@layer` | 选择器优先级管理 hack |

---

## 浏览器 JavaScript API（零依赖）

### 数据操作

| 需求 | 原生 API | 被你替代的 npm 包 |
|------|----------|-------------------|
| 深拷贝 | `structuredClone(obj)` | `lodash.cloneDeep` (~17KB) |
| 浅合并 | `{...a, ...b}` 或 `Object.assign(a, b)` | `lodash.merge` (简单场景) |
| 数组去重 | `[...new Set(arr)]` | `lodash.uniq` |
| 数组扁平化 | `arr.flat(depth)` / `arr.flatMap(fn)` | `lodash.flattenDeep` |
| 对象取值 | `obj?.a?.b?.c`（可选链） | `lodash.get` |
| 默认值 | `val ?? defaultVal`（空值合并） | `lodash.defaultTo` |
| 从数组取最后 | `arr.at(-1)` | `lodash.last` |
| 分组聚合 | `Object.groupBy(arr, fn)` / `Map.groupBy()` | `lodash.groupBy` |
| Promise 超时 | `Promise.race([promise, timeout])` 或 `AbortSignal.timeout()` | `p-timeout` |
| 同时设置多个属性 | `Object.assign(el.style, {...})` | 逐个赋值 |

### 日期和时间

| 需求 | 原生 API | 被你替代的包 |
|------|----------|-------------|
| 日期格式化 | `date.toLocaleDateString('zh-CN', {...})` | `moment.js` (~70KB) |
| 时间格式化 | `date.toLocaleTimeString('zh-CN', {...})` | `moment.js` |
| 相对时间 | `new Intl.RelativeTimeFormat('zh-CN').format(-3, 'day')` → "3天前" | `moment.fromNow()` |
| 数字格式化 | `new Intl.NumberFormat('zh-CN').format(12345)` → "12,345" | `numeral.js` |
| 货币格式化 | `new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' }).format(99)` | 手写 ¥99 |
| 复数规则 | `new Intl.PluralRules('zh-CN').select(n)` | `i18n` 包 |
| 时长计算 | `date2 - date1` 得到毫秒差，手动换算 | `ms` 包 |
| 日期比较 | `date1 > date2` 直接比较 | `date-fns.isAfter` |

### 字符串和编码

| 需求 | 原生 API | 被你替代的包 |
|------|----------|-------------|
| UUID 生成 | `crypto.randomUUID()` | `uuid` 包 |
| Base64 编码 | `btoa(str)` / `atob(str)` | `js-base64` |
| Base64 URL 安全 | 自己处理 `+ → -`、`/ → _`（5 行） | `base64url` |
| 字符串填充 | `str.padStart(n, '0')` / `str.padEnd(n, ' ')` | `left-pad` |
| URL 编码 | `encodeURIComponent()` / `decodeURIComponent()` | `querystring` |
| HTML 转义 | 用 `textContent` 赋值自动转义：`div.textContent = untrusted` | `escape-html` |
| 模板字符串 | `` `Hello ${name}` `` | `handlebars` / `ejs`（简单场景） |
| 大小写转换 | `str.toLowerCase()` / `toUpperCase()` | - |
| 去除空白 | `str.trim()` / `trimStart()` / `trimEnd()` | - |
| 包含判断 | `str.includes(sub)` / `startsWith()` / `endsWith()` | 手写 indexOf |
| 模糊搜索 | `str.includes(query.toLowerCase())`（大部分场景够了） | `fuse.js` |
| 截断+省略号 | `str.slice(0, n) + (str.length > n ? '...' : '')` | `truncate` 包 |

### DOM 和网络

| 需求 | 原生 API | 被你替代的包 |
|------|----------|-------------|
| URL 参数 | `new URL(url).searchParams.get('key')` | `qs` 包 |
| 设置 URL 参数 | `url.searchParams.set('key', 'val')` | 字符串拼接 |
| Clipboard | `navigator.clipboard.writeText(text)` | `clipboard.js` |
| Fetch + 超时 | `fetch(url, { signal: AbortSignal.timeout(5000) })` | `axios` |
| Fetch 中断 | `new AbortController()` + `controller.abort()` | `axios.CancelToken` |
| Form 提交 | `new FormData(formEl)` + `fetch()` | `jQuery.ajax` |
| 本地存储 | `localStorage` / `sessionStorage` | `store.js` |
| IndexedDB | 原生 `indexedDB` API 太啰嗦 → 这次用 `localStorage` 简化（ponytail: 索引查询场景再升级 IndexedDB） | `idb` 包 |
| Event 发射器 | `new EventTarget()` + `dispatchEvent(new CustomEvent(...))` | `mitt` / `eventemitter3` |
| DOM 就绪 | `document.readyState === 'loading'` 检查，或用 `defer` 属性 | `DOMContentLoaded` 中 |
| 元素可见性 | `new IntersectionObserver()` | 手写 scroll 监听 |
| 元素尺寸变化 | `new ResizeObserver()` | `resize` 监听 + 计算 |
| Mutation 监听 | `new MutationObserver()` | 手动轮询 |

### 加密和随机

| 需求 | 原生 API | 被你替代的包 |
|------|----------|-------------|
| 随机数 | `Math.random()`（非安全场景）| - |
| 安全随机 | `crypto.getRandomValues(new Uint32Array(1))[0]` | `randombytes` |
| 随机颜色 | `#${Math.random().toString(16).slice(2, 8).padEnd(6, '0')}` | `randomcolor` |
| 哈希（SHA-256） | `crypto.subtle.digest('SHA-256', data)` | `hash.js` |
| HMAC | `crypto.subtle.sign('HMAC', key, data)` | `crypto-js` |

### Canvas 和媒体

| 需求 | 原生 API | 被你替代的包 |
|------|----------|-------------|
| Canvas 导出 | `canvas.toDataURL('image/png')` / `canvas.toBlob()` | `html2canvas`（反过来用） |
| 视频截图 | `ctx.drawImage(videoEl, 0, 0)` 直接绘制 video 帧 | 视频处理库 |
| 图片压缩 | `canvas.toBlob(callback, 'image/jpeg', quality)` | `compressor.js` |
| 条形码读取 | 使用 BarcodeDetector API（Chrome）或这轮先跳过 | `quagga.js` |
| 语音识别 | `webkitSpeechRecognition`（有限支持）或这次不实现 | 语音识别 SDK |

---

## Node.js 标准库（Node 18+）

### 文件系统

| 需求 | 原生方案 | 被你替代的 npm 包 |
|------|----------|-------------------|
| 递归创建目录 | `fs.mkdirSync(path, { recursive: true })` | `mkdirp` |
| 递归删除目录 | `fs.rmSync(path, { recursive: true, force: true })` | `rimraf` |
| 读取文本文件 | `fs.readFileSync(path, 'utf-8')` | `fs-extra.readFile` |
| 写入文本文件 | `fs.writeFileSync(path, data, 'utf-8')` | `fs-extra.writeFile` |
| 复制文件 | `fs.cpSync(src, dest, { recursive: true })` | `fs-extra.copy` |
| 移动文件 | `fs.renameSync(oldPath, newPath)`（同分区）/ `fs.cpSync` + `fs.rmSync`（跨分区） | `fs-extra.move` |
| 检查路径存在 | `fs.existsSync(path)` | `fs-extra.exists` |
| 文件监听 | `fs.watch(filename, callback)` | `chokidar` |
| 遍历目录 | `fs.readdirSync(dir, { recursive: true })` | `glob` 包 |
| 文件 glob | `fs.readdirSync(dir, { recursive: true }).filter(name => name.endsWith('.js'))` （简单模式够用） | `tiny-glob` |
| 临时文件 | `fs.mkdtempSync()` + `node:os.tmpdir()` | `tmp` |

### 网络和 HTTP

| 需求 | 原生方案 | 被你替代的 npm 包 |
|------|----------|-------------------|
| HTTP GET | `fetch(url)`（内置，Node 18+） | `node-fetch` / `axios` / `got` |
| HTTP POST | `fetch(url, { method: 'POST', body: JSON.stringify(data) })` | `axios.post()` |
| HTTP 超时 | `fetch(url, { signal: AbortSignal.timeout(5000) })` | axios 超时配置 |
| WebSocket 服务端 | 内置 `WebSocket` (Node 22+) 或 `node:http` + `upgrade` | `ws` |
| URL 解析 | `new URL(url)` / `new URLSearchParams(params)` | `url-parse` |
| DNS 解析 | `dns.promises.resolve(hostname)` | - |
| HTTP Server | `node:http.createServer()`（简单场景） | `express`（简单 API） |

### 加密和安全

| 需求 | 原生方案 | 被你替代的 npm 包 |
|------|----------|-------------------|
| UUID | `crypto.randomUUID()` | `uuid` |
| 随机字节 | `crypto.randomBytes(n)` | `randombytes` |
| 密码哈希 | `crypto.scryptSync(password, salt, 64)` | `bcrypt` |
| 哈希（SHA-256） | `crypto.createHash('sha256').update(data).digest('hex')` | `hash.js` |
| HMAC | `crypto.createHmac('sha256', secret).update(data).digest('hex')` | `crypto-js` |
| 加密/解密 | `crypto.createCipheriv()` / `createDecipheriv()` | `aes-js` |
| JWT 生成 | 自己拼：base64url(header) + "." + base64url(payload) + "." + HMAC签名 | `jsonwebtoken` |

### 进程和环境

| 需求 | 原生方案 | 被你替代的 npm 包 |
|------|----------|-------------------|
| 环境变量 | `process.env.VAR \|\| 'default'` | `dotenv`（加上 `node --env-file=.env` Node 20.6+） |
| 命令行参数 | `util.parseArgs({ options: {...} })` (Node 18.3+) | `commander` / `yargs` |
| 退出进程 | `process.exit(code)` | - |
| 当前目录 | `process.cwd()` / `import.meta.dirname` (Node 21+) | - |
| 平台检测 | `process.platform` (`'win32'` / `'darwin'` / `'linux'`) | `os.platform()` |
| 获取用户 HOME | `os.homedir()` | - |
| 内存使用 | `process.memoryUsage()` | - |
| CPU 使用 | `os.cpus()` / `process.cpuUsage()` | - |

### 路径和流

| 需求 | 原生方案 | 被你替代的 npm 包 |
|------|----------|-------------------|
| 路径拼接 | `path.join('a', 'b', 'c')` | 字符串拼接（跨平台问题） |
| 获取文件名 | `path.basename(p)` / `path.extname(p)` | 手写正则 |
| 路径解析 | `path.resolve('.')` / `path.dirname(p)` | - |
| 路径规范化 | `path.normalize(p)` | - |
| 流式管道 | `stream.pipeline(readable, transform, writable, cb)` | `through2` |
| 逐行读取 | `readline.createInterface({ input: readableStream })` | `line-by-line` |
| 事件发射器 | `import { EventEmitter } from 'node:events'` | `mitt` / `eventemitter3` |

### 测试

| 需求 | 原生方案 | 被你替代的 npm 包 |
|------|----------|-------------------|
| 测试运行器 | `node:test` + `node --test` (Node 18+) | `mocha` + `jest` |
| 断言 | `node:assert` / `node:assert/strict` | `chai` |
| 模拟时间 | `node:test` 的 `mock.timers` (Node 20+) | `sinon.useFakeTimers` |
| 覆盖率 | `node --test --experimental-test-coverage` (Node 22+) | `c8` / `nyc` |

---

## Python 标准库（Python 3.9+）

### 文件系统和路径

| 需求 | 原生方案 | 被你替代的 pip 包 |
|------|----------|-------------------|
| 路径操作 | `from pathlib import Path` 替代所有 `os.path` | `pathlib2`（已经内置） |
| 递归创建目录 | `Path('a/b/c').mkdir(parents=True, exist_ok=True)` | 手写 `os.makedirs` |
| 遍历目录 | `Path('.').glob('**/*.py')` / `rglob('*.py')` | `glob2` |
| 读取文本 | `Path('file.txt').read_text(encoding='utf-8')` | `open().read()` |
| 写入文本 | `Path('file.txt').write_text(data, encoding='utf-8')` | `open().write()` |
| 临时文件 | `import tempfile` / `tempfile.NamedTemporaryFile()` | 手动管理 |
| 临时目录 | `tempfile.TemporaryDirectory()` | 手动清理 |
| 文件原子写入 | `tempfile.NamedTemporaryFile(delete=False, dir=parent)` + `os.replace(tmp, target)` | `atomicwrites` |
| 环境变量 | `os.environ.get('KEY', 'default')` | `python-dotenv` |

### 数据结构

| 需求 | 原生方案 | 被你替代的 pip 包 |
|------|----------|-------------------|
| 数据类 | `@dataclass` 替代手写 `__init__` / `__repr__` / `__eq__` | `attrs` |
| 枚举 | `from enum import Enum, auto` | 手写常量 |
| LRU 缓存 | `@functools.lru_cache(maxsize=128)` | `cachetools` |
| 计数器 | `from collections import Counter` | 手写 dict 计数 |
| 默认字典 | `from collections import defaultdict` | `dict.setdefault` |
| 有序字典 | 普通 `dict` 就是有序的（Python 3.7+） | `OrderedDict` |
| 双端队列 | `from collections import deque` | 手写环形缓冲区 |
| 命名元组 | `from collections import namedtuple` | 手写小类 |
| 堆队列 | `import heapq` | 手写堆实现 |

### 日期和时间

| 需求 | 原生方案 | 被你替代的 pip 包 |
|------|----------|-------------------|
| 时区处理 | `from zoneinfo import ZoneInfo` (3.9+) | `pytz` |
| 日期格式化 | `dt.strftime('%Y-%m-%d %H:%M:%S')` | `dateutil` |
| 日期解析 | `datetime.fromisoformat('2024-01-01T12:00:00')` (3.7+) | `dateutil.parser` |
| 时间间隔 | `datetime.timedelta(days=3)` | 手写秒计算 |
| 时间戳 | `datetime.now().timestamp()` | 手写转换 |

### 并发和进程

| 需求 | 原生方案 | 被你替代的 pip 包 |
|------|----------|-------------------|
| 线程池 | `from concurrent.futures import ThreadPoolExecutor` | 手写线程管理 |
| 进程池 | `from concurrent.futures import ProcessPoolExecutor` | `multiprocessing` 封装 |
| 子进程 | `subprocess.run(['cmd', 'arg'], capture_output=True, text=True)` | `sh` 包 |
| 异步 HTTP | `import urllib.request`（简单 GET）| `requests`（简单场景） |
| 异步超时 | `asyncio.wait_for(coro, timeout=10)` | 手写超时管理 |

### 配置和序列化

| 需求 | 原生方案 | 被你替代的 pip 包 |
|------|----------|-------------------|
| JSON | `import json` | `orjson` / `ujson`（简单场景） |
| TOML | `import tomllib` (3.11+) | `toml` |
| INI 配置 | `from configparser import ConfigParser` | 手写解析 |
| CSV | `import csv` | `pandas`（只做 CSV 读写时） |
| 日志 | `import logging` | `loguru`（简单场景） |
| 正则 | `import re` | - |
| 命令行参数 | `import argparse` | `click`（简单场景） |
| 随机数 | `import random` / `secrets`（安全场景）| - |

---

## 数据库（用 SQL 替代 ORM 黑盒）

当 ORM 的"方便"变成"调试地狱"时，原生 SQL 更简单：

| 需求 | 原生 SQL 方案 | 说明 |
|------|-------------|------|
| 唯一约束 | `UNIQUE (email)` | 数据库保证唯一性，不是应用层检查 |
| 外键约束 | `FOREIGN KEY (user_id) REFERENCES users(id)` | 数据库保证引用完整性 |
| 检查约束 | `CHECK (age > 0 AND age < 150)` | 数据库层面验证 |
| 默认值 | `DEFAULT now()` / `DEFAULT false` | 让数据库管理，应用层不关心 |
| 级联删除 | `ON DELETE CASCADE` | 数据库自动清理关联数据 |
| 部分索引 | `CREATE UNIQUE INDEX ON orders (user_id) WHERE status = 'active'` | 只为活跃订单建索引 |
| 表达式索引 | `CREATE INDEX ON users (lower(email))` | 大小写不敏感唯一索引 |
| 窗口函数 | `ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)` | 部门内薪资排名，无需应用层循环 |
| 排名 | `RANK()` / `DENSE_RANK()` / `NTILE(n)` | 标准排名函数 |
| 前后行访问 | `LAG(value, 1) OVER (ORDER BY date)` / `LEAD()` | 环比计算，无需自连接 |
| 运行总计 | `SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING)` | 累计求和 |
| 递归查询 | `WITH RECURSIVE cte AS (...)` | 树状结构、组织架构查询 |
| JSON 存储 | `jsonb` 类型（PostgreSQL）+ `->` / `->>` / `@>` / `?` 操作符 | 半结构化数据存 JSONB，不单独建表 |
| JSON 索引 | `CREATE INDEX ON table USING gin (data jsonb_path_ops)` | JSONB 字段也能建索引 |
| UPSERT (PG) | `INSERT ... ON CONFLICT (id) DO UPDATE SET ...` | 插入或更新一行搞定 |
| UPSERT (SQLite) | `INSERT ... ON CONFLICT DO UPDATE SET ...` | 同 PG，SQLite 3.24+ |
| UPSERT (MySQL) | `INSERT ... ON DUPLICATE KEY UPDATE ...` | MySQL 方言 |
| 全文搜索 (PG) | `to_tsvector()` + `to_tsquery()` + `@@` | 内置 FTS，无需 ElasticSearch |
| 全文搜索 (SQLite) | FTS5 扩展：`CREATE VIRTUAL TABLE ... USING fts5(...)` | SQLite 内置全文搜索 |
| 数组类型 (PG) | `TEXT[]` / `INTEGER[]` + `ANY()` / `@>` / `&&` | 简单多值不需要关联表 |
| 枚举类型 (PG) | `CREATE TYPE status AS ENUM (...)` | 数据库层面约束枚举值 |
| 生成列 | `GENERATED ALWAYS AS (...) STORED` | 计算列，数据库自动维护 |
