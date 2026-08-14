---
name: test-partition-runner
status: deprecated
redirect_to: acceptance-discipline
description: [DEPRECATED → acceptance-discipline] 测试阻塞解决策略 - 分区测试+坏测试识别。当全局测试挂起/失败或用户报告测试阻塞问题时调用。支持逐步分区定位坏测试，而非盲目重试整个套件。
triggers: [测试卡住, 测试阻塞, 测试挂起, 测试失败, test blocking, test hang, test stuck, test failed, 测试不过, test timeout, 分区测试, partition test, 坏测试, bad test]
intent: [DEPRECATED → acceptance-discipline] 测试阻塞解决策略 - 分区测试+坏测试识别
category: gate
audience: [devops]
---
# Test Partition Runner

**Solve test blocking by partitioning, not guessing.**

## Core Principle

```
WHEN GLOBAL TEST HANGS → PARTITION BY DIRECTORY → IDENTIFY BAD TESTS → FIX OR SKIP
全局测试卡住时 → 按目录分区测试 → 识别问题测试 → 修复或跳过
```

## Problem Patterns

| Pattern | Symptom | Root Cause |
|---------|---------|------------|
| Network timeout | Test hangs at API call | Real network request in test (mock missing) |
| Infinite retry | Test hangs with retry logs | Mock not applied to retry function |
| Resource lock | Test hangs at file/DB access | Native module not compiled |
| Circular wait | Test never completes | Async generator not properly consumed |

## Workflow

### Phase 1: Identify Blocking Point

```bash
# Run global test with timeout
npm test -- --reporter=verbose 2>&1 | head -200

# If hangs, note the last output line
# That's your blocking point
```

### Phase 2: Partition Testing

**Run tests by directory, not all at once:**

```bash
# Core modules first (most important)
npm test -- src/lib/sqlite-queue --reporter=verbose
npm test -- src/lib/langgraph --reporter=verbose

# Then dependent modules
npm test -- src/lib/ai-services --reporter=verbose

# Finally API routes
npm test -- src/app/api --reporter=verbose
```

### Phase 3: Identify Bad Tests

**Signs of a bad test:**

1. **Mock not applied correctly**
   - Test calls real API
   - `vi.mock()` path doesn't match import path
   - Mock function signature doesn't match real function

2. **Async generator not consumed**
   - `chat()` returns `AsyncGenerator`, not `Promise`
   - Cannot use `.rejects.toThrow()` on generator
   - Must use `for await...of` or `try/catch`

3. **ReadableStream mock incorrect**
   - `ReadableStream.from([string])` doesn't work
   - Need `ReadableStream<Uint8Array>` with `TextEncoder`

4. **Native module not compiled**
   - `better-sqlite3` needs `npm rebuild`
   - `prisma` needs `npx prisma generate`

### Phase 4: Fix or Skip

**Fix priority:**

1. **Fix if**: Test is for core functionality
2. **Skip if**: Test is for deprecated/unused code
3. **Document if**: Test reveals real bug

## Common Fixes

### Fix 1: Mock Retry Function

```typescript
// BEFORE: Mock only fetchWithProxy
vi.mock('@/lib/serverUtils', () => ({ fetchWithProxy: vi.fn() }));

// AFTER: Mock fetchWithRetry (the actual caller)
vi.mock('@/lib/concurrency-limiter', () => ({
  fetchWithRetry: vi.fn(),
}));
```

### Fix 2: Async Generator Test

```typescript
// BEFORE: Wrong - generator is not a Promise
await expect(adapter.chat([...])).rejects.toThrow('429');

// AFTER: Correct - consume generator
let error: Error | null = null;
try {
  for await (const _ of adapter.chat([...])) {
    // consume generator
  }
} catch (e) {
  error = e as Error;
}
expect(error).toBeTruthy();
expect(error?.message).toContain('429');
```

### Fix 3: ReadableStream Mock

```typescript
// BEFORE: Wrong - string is not ArrayBuffer
ReadableStream.from([sseBody])

// AFTER: Correct - Uint8Array stream
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

### Fix 4: Native Module Rebuild

```bash
npm rebuild better-sqlite3
npx prisma generate
```

## Feedback Template

When identifying bad tests, report:

```markdown
## 🚨 Bad Test Identified

**File**: `path/to/test.ts`
**Issue**: [Mock not applied | Async generator | Stream mock | Native module]
**Impact**: Blocks all tests
**Suggestion**: [Fix | Skip | Delete]

**Root Cause**: 
[Explain why the test was written incorrectly]

**Fix**:
[Show the corrected code]
```

## Decision Tree

```
Global test hangs?
├── Yes → Note last output line
│   ├── Network request? → Check mock path
│   ├── Retry loop? → Mock retry function, not base fetch
│   ├── File lock? → Rebuild native modules
│   └── Unknown → Partition test by directory
│
└── No → Run partitioned tests
    ├── Core modules pass? → Continue to dependent modules
    ├── Core modules fail? → Fix core tests first
    └── All pass? → Run global test to verify
```

## Checklist

- [ ] Identified blocking point from last output?
- [ ] Ran partition tests by directory?
- [ ] Identified bad tests with specific issues?
- [ ] Fixed or skipped bad tests?
- [ ] Documented root cause for future reference?
- [ ] Ran global test to verify fix?

## Integration with Other Skills

| Skill | When to use |
|-------|-------------|
| `debugging` | When test fails with unclear error |
| `tdd-workflow` | When writing new tests to avoid bad patterns |
| `verification-loop` | After fixing tests, run full verification |
