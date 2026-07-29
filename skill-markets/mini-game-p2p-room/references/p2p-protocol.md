# P2P 协议完整模式

> §0 必修 6 条 + §3 协议详解。SKILL.md 引用本文件获取完整代码模式。

---

## §0 P2P 连接必修 6 条（手机端不超时的底线）

> 来自 number-bomb-room（正常工作）与 gomoku（手机端超时）的对比分析。

| # | 规则 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | `hostConn.on('open')` 内 **必须** `clearTimeout(joinTimer)` | 手机端 ICE 协商可能 >12s，DataChannel open ≠ joined 已收到。超时检查 `phase` 可能为 `idle` | 手机端连接成功后被超时断开 |
| 2 | `hostConn.on('error')` **必须**处理 | DataChannel 打开阶段可能失败（NAT/防火墙） | 连接静默失败，无用户提示 |
| 3 | `hostConn.on('close')` **必须** `clearTimeout(joinTimer)` | 连接断开应取消等待 | 断开后仍显示"连接超时" |
| 4 | `createRoom` 重试逻辑 **必须**递归传 `retries` | 直接访问外层变量可能为 `undefined` | ID 冲突后静默失败 |
| 5 | PeerJS **必须** `debug: 2` | 无日志 = 无法定位 ICE/TURN 连接阶段 | 问题无法排查 |
| 6 | `peer.on('disconnected')` 必须 `peer.reconnect()` | 信令服务器可能短暂断开 | 玩家掉线 |

### 标准 Host 创建模式

```js
function doCreatePeer(roomCode, retries = 3) {
  if (peer) peer.destroy();                               // 清理旧实例
  peer = new Peer(roomCode, { config: ICE, debug: 2 });    // MUST debug: 2

  peer.on('open', (id) => { /* 房间就绪 */ });
  peer.on('error', (e) => {
    if (e.type === 'unavailable-id' && retries > 0) {     // 递归重试
      doCreatePeer(newCode, retries - 1);                  // retries 显式传递
    } else { resetToIdle(); }
  });
  peer.on('disconnected', () => peer.reconnect());
  peer.on('connection', (conn) => {
    conns.push(conn);
    conn.on('data', handleMsg);
    conn.on('close', () => { /* 清理玩家 + 空房间定时 */ });
  });
}
```

### 标准 Client 加入模式

```js
function joinRoom(code) {
  peer = new Peer({ config: ICE, debug: 2 });             // 匿名 peer
  peer.on('open', () => {
    hostConn = peer.connect(code, { reliable: true });
    hostConn.on('open', () => {
      clearTimeout(joinTimer);                             // 🛑 必修#1：立即清除
      joinTimer = null;
      hostConn.send({ type: 'join', name, avatar });
    });
    hostConn.on('data', handleMsg);
    hostConn.on('close', () => { clearTimeout(joinTimer); reset(); });  // 🛑 必修#3
    hostConn.on('error', () => { clearTimeout(joinTimer); reset(); });  // 🛑 必修#2
    // 计时器放最后（所有 handler 注册完毕再启动）
    joinTimer = setTimeout(() => { reset(); }, 12000);
  });
  peer.on('error', (e) => { clearTimeout(joinTimer); reset(); });
  peer.on('disconnected', () => peer.reconnect());         // 🛑 必修#6
}
```

---

## §3 P2P 协议模式

### 3.1 ICE 服务器配置

```js
const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },    // 3 个 STUN 冗余
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
    { urls: 'turn:openrelay.metered.ca:80',      // TURN 作为 fallback（NAT 穿透）
      username: 'openrelayproject', credential: 'openrelayproject' },
    { urls: 'turn:openrelay.metered.ca:443',      // TCP 备用
      username: 'openrelayproject', credential: 'openrelayproject' },
    { urls: 'turn:openrelay.metered.ca:443?transport=tcp',
      username: 'openrelayproject', credential: 'openrelayproject' },
  ]
};
```

### 3.4 消息协议

```
消息类型（Host ↔ Client）：
  join        Client→Host   加入房间（name, avatar）
  joined      Host→Client   确认加入（yourId, hostAvatar, hostName, color）
  playerList  Host→Client   玩家列表更新
  state       Host→Client   游戏完整状态同步
  click       Client→Host   玩家操作请求
  move        Host→Client   落子（row, col, color, currentTurn）/ Client→Host
  result      Host→Client   单步结果
  turn        Host→Client   回合切换
  gameOver    Host→Client   游戏结束（winner, totalMoves）
  restart     Host→Client   重新开始
  requestRestart  Client→Host  请求重新开始
  error       Host→Client   错误消息
```

**关键**：Host 是游戏逻辑的唯一执行者（Server Authority），Client 只发送操作请求。

### 3.5 重连与清理

```js
peer.on('disconnected', () => peer.reconnect());  // 信令断开自动重连
// 空房间 120 秒后自动关闭（Host 侧）
emptyTimer = setTimeout(() => { if (phase === 'room') reset(); }, 120000);
// Client 断开 → 从玩家列表移除 → broadcast 更新
```

### 3.6 Host 刷新重连完整模式

> 来源：gomoku Host 刷新后无法重连，报 "Failed to execute 'connect' on 'RTCPeerConnection'"。

#### 根因

**Host 刷新后 `rejoinRoom` 对所有情况都调用 `joinRoom()`**。但 Host 的 PeerJS ID 就是房间码本身，调用 `joinRoom` 相当于尝试连接自己 → 必然失败。

```
❌ 错误路径: Host 刷新 → rejoinRoom → joinRoom(roomCode) → peer.connect(roomCode) → 连接自己 → 失败
✅ 正确路径: Host 刷新 → rejoinRoom → createRoomWithCode(roomCode) → 用原房间码重建 Peer → 等待 Client 重连
```

#### 正确的重连分支逻辑

```js
function rejoinRoom(state) {
  if (state.isHost) {
    // 🔑 Host: 重新创建房间（不复用旧 Peer 实例，刷新后不存在）
    RoomManager.createRoomWithCode(state.roomCode, () => {
      toast('房间已恢复，等待对手重连...');
    });

    // 恢复游戏状态（棋盘、当前回合等）
    board = state.board || emptyBoard();
    currentTurn = state.currentTurn || 'black';
    moveCount = state.moveCount || 0;
    lastMove = state.lastMove || null;

    // 如果对局进行中，重建棋盘 UI
    if (state.phase === 'playing') {
      buildBoard();
      for (let r = 0; r < BOARD; r++)
        for (let c = 0; c < BOARD; c++)
          if (board[r][c]) renderStone(r, c, board[r][c]);
      updateTurnUI();
      showScreen('screen-game');
    }

    // 给对手 60s 重连窗口（比 Client 的 22s 长，因为 Host 先启动）
    joinTimer = setTimeout(() => {
      toast('对手未重连，返回大厅');
      resetIdle();
      localStorage.removeItem('gomoku_reconnect_state');
    }, 60000);

  } else {
    // Client: 加入已存在的房间（不变）
    RoomManager.joinRoom(state.roomCode, () => {
      RoomManager.send({ type: 'rejoin', name, avatar, color });
      toast('重连成功');
    });
  }
}
```

#### reconnect_state 必须序列化的字段

```js
// ❌ 只保存了 UI 状态，缺棋盘数据 → Host 刷新后棋盘是空的
localStorage.setItem('reconnect_state', JSON.stringify({
  roomCode, isHost, playerName, myColor, phase
}));

// ✅ 必须包含完整游戏状态
localStorage.setItem('reconnect_state', JSON.stringify({
  roomCode, isHost,
  playerName, myColor, myAvatar,
  oppName, oppAvatar,
  phase,                        // idle | room | playing | over
  board,                        // 二维数组，棋盘落子状态
  currentTurn,                  // 'black' | 'white'
  moveCount,                    // 已落子数
  lastMove,                     // { row, col }
  savedAt: Date.now()           // 过期判断用
}));
```

#### onPeerRejoin 收尾

```js
onPeerRejoin: (data, conn) => {
  // Host 收到 Client 重连 → 清除超时 + 清理 reconnect 标记
  clearTimeout(joinTimer);
  joinTimer = null;
  localStorage.removeItem('gomoku_reconnect_state');
  // ... 恢复玩家信息、广播状态
};
```

#### 改造清单

| 改造项 | 说明 |
|--------|------|
| `RoomManager` 导出 `createRoomWithCode` | 允许 Host 用指定房间码重建 Peer |
| `rejoinRoom` 区分 `isHost` 分支 | Host → createRoomWithCode, Client → joinRoom |
| `reconnect_state` 增加 `board/currentTurn/moveCount/lastMove` | 棋盘完整恢复 |
| `onPeerRejoin` 中 `clearTimeout(joinTimer)` | 防止 Host 侧 60s 超时误杀 |
