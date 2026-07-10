# 30-testing / 测试分区运行器（Test Partition Runner）

> **定位**：测试阶段卡住时的工程化解决方案。
>
> **何时加载**：全局测试挂起 / 失败 / 用户报告测试阻塞问题时。

---

## 一、核心原则

```
WHEN GLOBAL TEST HANGS → PARTITION BY DIRECTORY → IDENTIFY BAD TESTS → FIX OR SKIP
全局测试卡住时 → 按目录分区测试 → 识别问题测试 → 修复或跳过
```

**不要盲目重试整套测试**，浪费时间且无法定位问题。

---

## 二、常见测试阻塞模式

| 模式 | 症状 | 根因 |
|------|------|------|
| 网络超时 | 测试卡在 API 调用 | 测试中发起真实网络请求（mock 缺失） |
| 无限重试 | 测试卡在重试日志中 | mock 没应用到重试函数 |
| 资源锁 | 测试卡在文件/数据库访问 | native 模块未编译 |
| 循环等待 | 测试永不完成 | 异步生成器未正确消费 |

---

## 三、四阶段工作流

### Phase 1: 定位阻塞点

```bash
# 全局测试加超时
npm test -- --reporter=verbose 2>&1 | head -200

# 如果挂起，记下最后一行输出
# 那就是你的阻塞点
```

### Phase 2: 分区测试

**按目录跑，不要一次跑全部**：

```bash
# 先跑核心模块（最重要）
npm test -- src/lib/sqlite-queue --reporter=verbose
npm test -- src/lib/langgraph --reporter=verbose

# 再跑依赖模块
npm test -- src/lib/ai-services --reporter=verbose

# 最后跑 API 路由
npm test -- src/app/api --reporter=verbose
```

### Phase 3: 识别坏测试

**坏测试的信号**：

1. **Mock 未正确应用**
   - 测试调用了真实 API
   - `vi.mock()` 路径与 import 路径不匹配
   - Mock 函数签名与真实函数不匹配

2. **异步生成器未消费**
   - `chat()` 返回 `AsyncGenerator`，不是 `Promise`
   - 不能用 `.rejects.toThrow()` 测生成器
   - 必须用 `for await...of` 或 `try/catch`

3. **ReadableStream mock 错误**
   - `ReadableStream.from([string])` 不工作
   - 需要 `ReadableStream<Uint8Array>` + `TextEncoder`

4. **Native 模块未编译**
   - `better-sqlite3` 需要 `npm rebuild`
   - `prisma` 需要 `npx prisma generate`

### Phase 4: 修复或跳过

**修复优先级**：

| 情况 | 行动 |
|------|------|
| 测试针对核心功能 | 必须修复 |
| 测试针对已废弃/未使用代码 | 跳过或删除 |
| 测试揭示真实 Bug | 记录 Bug 并修复测试 |

---

## 四、常见修复模板

### Fix 1: Mock 重试函数（而非基础函数）

```typescript
/ BEFORE: 只 mock fetchWithProxy
vi.mock('@/lib/serverUtils', () => ({ fetchWithProxy: vi.fn() }));

/ AFTER: mock fetchWithRetry（实际调用方）
vi.mock('@/lib/concurrency-limiter', () => ({
  fetchWithRetry: vi.fn(),
}));
```

### Fix 2: 异步生成器测试

```typescript
/ BEFORE: 错误 — 生成器不是 Promise
await expect(adapter.chat([...])).rejects.toThrow('429');

/ AFTER: 正确 — 消费生成器
let error: Error | null = null;
try {
  for await (const _ of adapter.chat([...])) {
    / 消费生成器
  }
} catch (e) {
  error = e as Error;
}
expect(error).toBeTruthy();
expect(error?.message).toContain('429');
```

### Fix 3: ReadableStream mock

```typescript
/ BEFORE: 错误 — string 不是 ArrayBuffer
ReadableStream.from([sseBody]);

/ AFTER: 正确 — Uint8Array 流
function createMockStreamBody(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  let index = 0;
  return new ReadableStream<Uint8Array>({
    pull(controller) {
      if (index < chunks.length) {
        controller.enqueue(encoder.encode(chunks[index]));
        index++;
      } else {
        controller.close();
      }
    }
  });
}
```

### Fix 4: Native 模块重建

```bash
npm rebuild better-sqlite3
npx prisma generate
```

---

## 五、决策树

```
全局测试挂起？
├── 是 → 记下最后一行输出
│   ├── 网络请求？→ 检查 mock 路径
│   ├── 重试循环？→ mock 重试函数，不是基础 fetch
│   ├── 文件锁？→ 重建 native 模块
│   └── 未知 → 按目录分区测试
│
└── 否 → 跑分区测试
    ├── 核心模块通过？→ 继续依赖模块
    ├── 核心模块失败？→ 先修核心测试
    └── 全通过？→ 跑全局测试验证
```

---

## 六、坏测试报告模板

```markdown
## 🚨 Bad Test Identified

**文件**: `path/to/test.ts`
**问题类型**: [Mock 未应用 | 异步生成器 | Stream mock | Native 模块]
**影响**: 阻塞全部测试
**建议**: [修复 | 跳过 | 删除]

**根因**:
[解释为什么测试写错了]

**修复**:
[展示修复后的代码]
```

---

## 七、与其他阶段的协作

| 阶段 | 协作方式 |
|------|---------|
| `20-development/tdd-workflow` | 写新测试时避免坏模式 |
| `50-debugging/debugging` | 测试失败原因不明时进入调试 |
| `40-acceptance/verification-loop` | 修完坏测试后跑完整验证 |

---

## 八、检查清单

- [ ] 从最后一行输出定位阻塞点？
- [ ] 按目录跑分区测试？
- [ ] 识别出坏测试的具体问题？
- [ ] 修复或跳过坏测试？
- [ ] 记录根因供未来参考？
- [ ] 跑全局测试验证修复？
