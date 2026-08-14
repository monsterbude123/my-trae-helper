---
name: mini-game-p2p-room
description: 网页小游戏 P2P 房间对战完整构建模式 — PeerJS 房主-客户端协议 + 游戏状态机 + CSS 精灵图 + Web Audio 音效 + 移动端适配 + TypeScript/esbuild 构建经验 + Playwright E2E 测试模式。当用户需要在 web-mini-game 项目中创建多人房间对战游戏、使用 PeerJS 实现 P2P 联机、刷新重连、esbuild IIFE window 赋值、编写 E2E 测试、或遇到精灵图偏移/连接超时/AudioContext 锁等问题时主动加载。触发词：房间对战、P2P 联机、PeerJS、多人游戏、数字炸弹、五子棋、精灵图头像、AudioContext、ICE 服务器、连接超时、刷新重连、esbuild IIFE、window undefined、TypeScript 迁移、E2E 测试、Playwright 双 Tab、P2P 测试。
intent: 网页小游戏 P2P 房间对战完整构建模式 — PeerJS 房主-客户端协议 + 游戏状态机 + CSS 精灵图 ...
category: other
audience: [designer]
---
# P2P 房间对战小游戏 — 构建模式

> 基于 `number-bomb-room` + `gomoku` 两次从零实战的完整经验。

---

## §0 P2P 连接必修 6 条

| # | 规则 | 违反后果 |
|---|------|---------|
| 1 | `hostConn.on('open')` 内 **必须** `clearTimeout(joinTimer)` | 手机端连接成功后仍被超时断开 |
| 2 | `hostConn.on('error')` **必须**处理 | 连接静默失败，无用户提示 |
| 3 | `hostConn.on('close')` **必须** `clearTimeout(joinTimer)` | 断开后仍显示"连接超时" |
| 4 | `createRoom` 重试递归传 `retries` | ID 冲突后静默失败 |
| 5 | PeerJS **必须** `debug: 2` | 问题无法排查 |
| 6 | `peer.on('disconnected')` → `peer.reconnect()` | 玩家掉线 |

> 完整 Host/Client 创建模式、ICE 配置、消息协议、刷新重连 → [references/p2p-protocol.md](references/p2p-protocol.md)

---

## §1 架构决策树

```
开始新游戏
├── 多人实时互动？ → PeerJS (WebRTC P2P)
├── 持久化状态？ → localStorage (名称/偏好) + PeerJS (对局状态)
└── 房间发现？ → 4 位数字房间码（本模式）
```

Host-Authority 模式：Host 是游戏逻辑唯一执行者，Client 只发送操作请求。

---

## §2 文件结构

```
{game-name}/
├── index.html          # HTML + CSS 全内联
├── src/main.ts         # 核心逻辑: PeerJS + 状态机 + 游戏规则
├── src/room.ts         # PeerJS 连接管理
├── src/game_input.ts   # DOM 事件绑定
├── src/sound.ts        # Web Audio 音效
└── dist/               # esbuild 构建产物
```

分离原则：`main` = 纯逻辑；`room` = 连接管理；`input` = 事件；`sound` = 音效工厂。

---

## §3 构建 Checklist

```
P2P 连接（§0 必修 6 条）：
[ ] hostConn.on('open') 内 clearTimeout(joinTimer)   → #1
[ ] hostConn.on('error') 处理                         → #2
[ ] hostConn.on('close') 内 clearTimeout(joinTimer)   → #3
[ ] createRoom ID 冲突递归传 retries                   → #4
[ ] PeerJS debug: 2                                   → #5
[ ] peer.on('disconnected') → peer.reconnect()         → #6
[ ] ICE 3×STUN + 3×TURN 配置完整

刷新重连：
[ ] rejoinRoom 区分 isHost/Client 分支
[ ] reconnect_state 包含 board/currentTurn/moveCount/lastMove
[ ] Host → createRoomWithCode, Client → joinRoom
[ ] onPeerRejoin 中 clearTimeout(joinTimer)

构建（TypeScript + esbuild）：
[ ] ❌ 不用 globalName + export default 组合
[ ] ✅ 手动 window.X = {...} 在 IIFE 内部
[ ] 加载顺序: sound → room → input → main

E2E 最低要求：
[ ] smoke-build: window 命名空间 + 方法可用
[ ] host-refresh-reconnect: 棋盘恢复 + Client 重连
```

---

## §4 参考索引

需要具体代码模式时，按需加载：

| 场景 | 参考文件 |
|------|---------|
| Host/Client 创建模式、ICE、消息协议、刷新重连 | [p2p-protocol.md](references/p2p-protocol.md) |
| 模块模式 + 状态机 + CSS Grid 棋盘 | [game-logic.md](references/game-logic.md) |
| CSS 精灵图头像 + 纯 CSS 替代方案 | [css-sprites.md](references/css-sprites.md) |
| CSS 径向渐变光晕 + 网格纹理 + 浮动粒子 | [css-backgrounds.md](references/css-backgrounds.md) |
| Web Audio Oscillator/BufferSource 音效 | [web-audio.md](references/web-audio.md) |
| 100dvh、tap-highlight、input 过滤 | [mobile-adaptation.md](references/mobile-adaptation.md) |
| esbuild IIFE var 遮蔽、globalName 陷阱 | [typescript-esbuild.md](references/typescript-esbuild.md) |
| 双 Tab E2E、smoke test、TDD 顺序 | [playwright-e2e.md](references/playwright-e2e.md) |

---

## §5 铁律

```
1. P2P 游戏提 PR 前，至少跑通 smoke-build + host-refresh-reconnect
2. 构建产物必须 E2E 验证 window 挂载（esbuild 不报错 ≠ 产物正确）
3. Host 刷新 = createRoomWithCode，不是 joinRoom
4. reconnect_state 必须完整序列化游戏状态，不只 UI 状态
```
