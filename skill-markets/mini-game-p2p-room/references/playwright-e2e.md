# P2P 游戏的 Playwright E2E 测试模式

> SKILL.md §11 详细实现。无测试 = 人工 debug 3h+ 的血泪教训。

---

## 11.1 为什么 P2P 游戏必须 E2E

P2P 房间对战有独特的测试难点，**单元测试覆盖不了**：

```
❌ 单元测试无法覆盖的场景：
  - Host 刷新后 localStorage → 重建 Peer → 等待 Client 重连的完整闭环
  - 两个浏览器 Tab 之间的 PeerJS DataConnection 消息收发
  - esbuild 构建产物中 window.Global 是否真正可用（不是源码，是产物）
  - ICE 服务器连通性（虽然是外部因素，但连接超时的 fallback 可测）
  - localStorage 序列化/反序列化的完整游戏状态恢复
```

## 11.2 最小 E2E 检查清单（每个 P2P 游戏必须通过）

```yaml
# {game}-e2e.yaml — 放在游戏目录下
scenarios:
  - id: smoke-build
    desc: "构建产物加载后 window 命名空间可用"
    steps:
      - build: pnpm build
      - navigate: dist/index.html
      - assert: window.Gomoku !== undefined
      - assert: typeof window.Gomoku.init === 'function'
      - assert: typeof window.Gomoku.createRoom === 'function'
    caught_bugs: ["esbuild IIFE window.Gomoku === undefined"]

  - id: host-create-room
    desc: "Host 创建房间，Peer 正常启动"
    steps:
      - navigate: dist/index.html (tab1)
      - click: #btn-create-room
      - assert: 房间码可见（4-6 位数字）
      - assert: PeerJS connection status === 'connected'

  - id: client-join-room
    desc: "Client 输入房间码加入"
    steps:
      - navigate: dist/index.html (tab2)
      - fill: #room-code-input with tab1 的房间码
      - click: #btn-join-room
      - assert: tab1 显示"对手加入"
      - assert: tab2 显示"加入成功"

  - id: host-refresh-reconnect
    desc: "Host 刷新后棋盘恢复 + Client 自动重连"
    steps:
      - 先完成 host-create-room + client-join-room
      - 再下几步棋（确保 board 非空）
      - tab1.reload()  # Host 刷新
      - assert: tab1 棋盘恢复（非空棋盘）
      - assert: tab1 显示"等待对手重连"
      - wait: tab2 自动重连（最多 22s）
      - assert: tab1 显示对手已重连
      - assert: tab1 + tab2 棋盘一致
    caught_bugs:
      - "Host 刷新调用 joinRoom 连接自己"
      - "reconnect_state 缺 board/currentTurn/moveCount"
      - "onPeerRejoin 未清除 joinTimer 导致 Host 误踢人"

  - id: game-full-flow
    desc: "完整对局：创建→加入→落子→胜负→重开"
    steps:
      - 完成 host-create-room + client-join-room
      - 交替落子直到一方五连
      - assert: 胜利弹窗显示正确玩家
      - click: 再来一局
      - assert: 棋盘清空，双方就绪
```

## 11.3 Playwright 双 Tab 测试模式

```ts
// test/{game}-e2e.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Gomoku P2P', () => {
  test('Host 刷新后棋盘恢复', async ({ browser }) => {
    // 两个独立 context（模拟两个独立浏览器）
    const hostCtx = await browser.newContext();
    const clientCtx = await browser.newContext();
    const hostPage = await hostCtx.newPage();
    const clientPage = await clientCtx.newPage();

    // 1. 加载页面
    await hostPage.goto('http://localhost:3000/gomoku/dist/');
    await clientPage.goto('http://localhost:3000/gomoku/dist/');

    // 2. Host 创建房间
    await hostPage.click('#btn-create-room');
    const roomCode = await hostPage.textContent('#room-code');
    expect(roomCode).toMatch(/\d{4,6}/);

    // 3. Client 加入
    await clientPage.fill('#room-code-input', roomCode!);
    await clientPage.click('#btn-join-room');
    await expect(clientPage.locator('#status')).toContainText('加入成功');

    // 4. 下几步棋
    await hostPage.click('.cell[data-row="7"][data-col="7"]'); // 黑
    await clientPage.click('.cell[data-row="7"][data-col="8"]'); // 白
    await hostPage.click('.cell[data-row="8"][data-col="7"]'); // 黑

    // 5. Host 刷新
    await hostPage.reload();
    await hostPage.waitForLoadState('networkidle');

    // 🔑 核心断言：window.Gomoku 可用
    const hasGomoku = await hostPage.evaluate(() => typeof window.Gomoku !== 'undefined');
    expect(hasGomoku).toBe(true);

    // 🔑 核心断言：棋盘恢复（三颗子）
    const stoneCount = await hostPage.evaluate(() => {
      const cells = document.querySelectorAll('.cell .stone');
      return cells.length;
    });
    expect(stoneCount).toBe(3);

    // 6. Client 重连
    await expect(hostPage.locator('#status')).toContainText('对手已重连', { timeout: 30000 });

    // 7. 棋盘一致性
    const hostBoard = await hostPage.evaluate(() => {
      return (window as any).Gomoku.getBoard();
    });
    const clientBoard = await clientPage.evaluate(() => {
      return (window as any).Gomoku.getBoard();
    });
    expect(hostBoard).toEqual(clientBoard);
  });
});
```

## 11.4 构建产物 smoke test（最便宜的 E2E，必须最先写）

```ts
test('构建产物 window 命名空间可用', async ({ page }) => {
  await page.goto('http://localhost:3000/gomoku/dist/');

  // 每个入口文件的 window 挂载点
  const namespaces = ['Gomoku', 'GomokuRoom', 'GomokuSound', 'GomokuInput'];
  for (const ns of namespaces) {
    const exists = await page.evaluate((name) => {
      return typeof (window as any)[name] !== 'undefined';
    }, ns);
    expect(exists, `${ns} should exist on window`).toBe(true);
  }

  // Gomoku 主入口的所有公共方法
  const methods = ['init', 'createRoom', 'joinRoom', 'getBoard', 'resetGame'];
  for (const m of methods) {
    const isFunc = await page.evaluate((method) => {
      return typeof (window as any).Gomoku?.[method] === 'function';
    }, m);
    expect(isFunc, `Gomoku.${m} should be a function`).toBe(true);
  }
});
```

**这个测试 3 秒跑完，能拦住 §10.1 的 3 小时 debug。**

## 11.5 TDD 在 P2P 游戏中的实践顺序

```
1. smoke-build test     → 🔴 RED（先写测试，确认构建产物 window 挂载正确）
2. 写 build 配置        → 🟢 GREEN（esbuild 构建，手动 window.X = {...}）
3. host-reconnect test  → 🔴 RED（Host 刷新后棋盘恢复）
4. 写 rejoinRoom 逻辑   → 🟢 GREEN（isHost 分支 + reconnect_state 完整字段）
5. client-reconnect test → 🔴 RED（Client 自动重连）
6. 写 onPeerRejoin 逻辑 → 🟢 GREEN
7. full-flow test       → 🔴 RED（完整对局）
8. 完整实现             → 🟢 GREEN
```

## 11.6 反模式：伪测试（比没测试更危险）

| 伪测试表现 | 为什么危险 |
|-----------|-----------|
| "浏览器里手动点了创建房间，能进" | 没测刷新/重连/状态恢复 |
| "构建不报错 = 产物正确" | esbuild 不报错但 `window.Gomoku === undefined` |
| "代码看着没问题" | 同名 var IIFE 遮蔽——看着没问题，浏览器里就是 undefined |
| "改了一行不用测" | `reconnect_state` 只加了 board 字段，但忘了改序列化位置 |

**铁律：P2P 游戏提 PR 前，至少跑通 smoke-build + host-refresh-reconnect 两个 E2E。**

## 11.7 Playwright 配置（`playwright.config.ts`）

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './test',
  timeout: 60000,           // P2P 重连可能较慢
  expect: { timeout: 15000 },
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
  },
  webServer: {
    command: 'pnpm serve',  // 或 npx serve . -p 3000
    port: 3000,
    reuseExistingServer: true,
  },
});
```
