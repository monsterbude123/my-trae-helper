# 游戏逻辑模式

> SKILL.md §4 详细实现。模块模式 + 状态机 + Host-Authority + CSS Grid 棋盘。

---

## 4.1 模块模式 + 状态机

```js
const Game = (() => {
  let phase = 'idle';  // idle | room(lobby) | playing | over
  let isHost = false;
  let players = [];

  function init() { /* 绑定 DOM + localStorage */ }
  // Host 逻辑: createRoom, startGame, handleClick, broadcast
  // Client 逻辑: joinRoom, sendHost, handleClientMessage
  // 共享: updatePlayerList, buildGrid, showModal, toast

  return { init, createRoom, joinRoom, restart };
})();
// game_input.js: document.addEventListener('DOMContentLoaded', () => Game.init());
```

## 4.2 游戏状态同步模式

```
Host-Authority 模式：
  Client 操作 → sendHost(msg) → Host 校验 + 执行 → broadcast 结果
  
Host 持有 gameState 真相：
  - placeStone(row, col, color)
  - checkWin → phase = 'over'
  - 每次操作后 broadcast 最新 state
  - Client 接收 state 后纯渲染
```

## 4.3 动态 CSS Grid 棋盘

```js
function buildBoard() {
  boardEl.innerHTML = '';
  const frag = document.createDocumentFragment();     // 一次性插入，避免重绘
  for (let r = 0; r < SIZE; r++)
    for (let c = 0; c < SIZE; c++) {
      const cell = document.createElement('div');
      cell.className = 'cell'; cell.dataset.row = r; cell.dataset.col = c;
      frag.appendChild(cell);
    }
  boardEl.appendChild(frag);
}
```
