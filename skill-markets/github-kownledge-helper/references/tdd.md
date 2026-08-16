# TDD 模板（vitest）

> 本项目 src-cli/ 的脚本开发走 TDD。本文件沉淀红绿循环、测试组织、vitest 配置的最小模板。

## 核心约定

1. **测试在 `src-cli/test/`**，与 `src/` 并列，匹配模式 `*.test.ts`。
2. **TDD 三步**：先写测试（红）→ 跑测试确认红 → 写实现（绿）→ 跑测试确认绿 → 重构。**禁止**先写实现后补测试。
3. **测试先行于脚本**：用户说"写一个 X 脚本"→ 先写 X 的测试 → 再写 X。
4. **临时脚本禁止**：所有 .ts / .ps1 脚本必须有对应测试文件。无测试 = 不交付。
5. **e2e 用真实 tmp 目录 + 真 git**：不 mock git（mock 会掩盖真实 bug）。tmp 用 `mkdtempSync(tmpdir() + 'prefix-')`，每个 test 自己清理。

## vitest 配置（已就位）

- 依赖：`vitest@4.x` 在 devDependencies。
- `vitest.config.ts`：`root: 'src-cli'`、`include: ['test/**/*.test.ts']`、Node 环境。
- `tsconfig.json#include` 加 `test/**/*.ts`，跑 typecheck 时也覆盖测试。
- `package.json#scripts`：
  ```json
  "test": "vitest run",
  "test:watch": "vitest"
  ```

## 测试类型与典型用法

### 1. 纯函数单测（parseRepoInput / summarizeFreshness）

- 不用 fs / git / process.chdir。
- 每个 case 直接 `it('...', () => expect(fn(input)).toEqual(output))`。
- 边界：空 / 非法 / 极端值。

### 2. 集成测（buildEntryFromRepo）

- 用 `mkdtempSync` 建 tmp dir + 真 git init + 真 commit + 真 clone URL（`https://github.com/...` 或 `file://` 协议）。
- 验证副作用（fs 状态）。
- afterEach：`rmSync` + chdir 离开。

### 3. e2e（addRepo）

- 真实 bare remote fixture（用 `git init --bare` + `symbolic-ref HEAD refs/heads/<branch>`，避免 "remote HEAD refers to nonexistent ref"）。
- process.chdir(tmpRoot) → getProjectRoot 自动定位。
- 验证：clone 后 .git 存在、docs 镜像存在、manifest 已追加。
- afterEach：chdir 离开 + `rmSync({ maxRetries: 10, retryDelay: 200 })` 抗 Windows EBUSY。

### 4. 涉及外部命令的（verifyDocs / runBuildIndex）

- 接受可配置 `cwd` 参数（默认 process.cwd()），测试不污染真项目根。
- 真实 spawn 子进程 + 解析 stdout，**不** mock 子进程（mock 会让"命令改了路径"类问题逃过测试）。

## 路径解析的测试隔离模式

> src-cli 的 `paths.ts` 用 `import.meta.url` 推算项目根（永远是真项目根），与测试期望"在 tmp 跑"冲突。
> 解决：`getProjectRoot(cwd: string = process.cwd())` 从 cwd 向上找 `manifest.json` 找最近的根。

测试中 `process.chdir(tmpRoot)`，所有 lib 函数读 cwd → getProjectRoot 找到 tmpRoot。所有受影响的函数（readManifest / writeManifest / runSyncDocs / addRepo / runVerifyDocs）都接 `cwd` 参数。

## 进度

- 5 个测试套件 / 25 个用例 / 7.4s。
- 套件分布：
  - `parseRepoInput.test.ts`：11 例（输入解析，纯函数）
  - `buildEntryFromRepo.test.ts`：3 例（git fixture + 集成）
  - `manifestAppend.test.ts`：3 例（manifest CRUD）
  - `verifyDocs.test.ts`：5 例（解析 + 汇总）
  - `add.e2e.test.ts`：3 例（端到端）

## 反模式

- ❌ 先写 `scripts/foo.ts` 再补 `test/foo.test.ts`（违反 TDD，常见于赶进度）
- ❌ 测试用 `vi.mock` 替换 fs / git（逃逸真实 bug）
- ❌ 测试不清理 tmp → 磁盘爆炸
- ❌ e2e 跑在真项目根 → 污染 manifest
- ❌ vitest 配置 `globals: true`（污染全局命名空间，与 ts strict 冲突）
- ❌ typecheck 时不覆盖 test/（TS 错漏到运行时才发现）

## 跑测试

```bash
pnpm test           # CI 模式（vitest run）
pnpm test:watch     # 开发模式（vitest）
pnpm typecheck      # 单独跑 tsc -p src-cli --noEmit
```

## 与项目规则的对应

- `project-rules.md` §9.5 技能演进：每完成一个大型任务必须升级 skill。本模板本身就是一次"沉淀"。
- `AGENT.md` §9.2 大型任务判定：TDD 实现新 CLI 是大型任务。
- 缺失-CLI 走开发的工作流：见 [workflows.md §9](./workflows.md#9-缺失-cli-走开发的工作流2026-08-13-新增)。
