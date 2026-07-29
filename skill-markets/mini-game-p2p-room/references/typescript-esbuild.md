# TypeScript + esbuild 构建踩坑

> SKILL.md §10 详细实现。来自 gomoku JS→TS 迁移，3 小时 debug 的完整记录。

---

## 10.1 核心陷阱：esbuild IIFE + 同名 var 遮蔽

**现象**：源码中有 `window.Gomoku = Gomoku`，构建产物中也有，但浏览器中 `window.Gomoku === undefined`。

**构建产物**（esbuild `format: 'iife'`）：
```js
"use strict";
var Gomoku = (() => {
  // ...全部游戏代码...
  var Gomoku = { init, createRoom, joinRoom, /* ... */ };
  window.Gomoku = Gomoku;    // 你以为这行生效了？
})();
```

**根因**：外部 `var Gomoku` 和 IIFE 内部 `var Gomoku` **同名**。在动态创建的 `<script>` 标签中，`window.Gomoku = Gomoku`（赋值表达式）作为 IIFE 最后一条语句时，`window.Gomoku` 被设置为内部变量值，但 `var Gomoku = (...)` 的外层赋值又将 `window.Gomoku` 覆盖为 `undefined`。

**Playwright 验证过程**（每一步逐步隔离）：
```js
// 测试1: 不用 IIFE → ✅ 正常
var Gomoku = {x:42};           // window.Gomoku = {x:42}

// 测试2: IIFE + return → ✅ 正常
var Gomoku = (() => { var inner = {x:42}; return inner; })();

// 测试3: IIFE + 同名 var + window 赋值 → ❌ 失败！
var Gomoku = (() => {
  var Gomoku = {x:42};
  window.Gomoku = Gomoku;      // IIFE 内 window.Gomoku = {x:42} ✅
})();                          // 但出来后 window.Gomoku = undefined ❌

// 测试4: 加显式 return → ✅ 正常
var Gomoku = (() => {
  var Gomoku = {x:42};
  window.Gomoku = Gomoku;
  return Gomoku;               // 显式 return 打破了遮蔽
})();
```

**解决方案**：
```ts
// ✅ 正确：直接在 IIFE 内部用对象字面量赋值
// 不定义 var/const Gomoku 变量，不依赖 IIFE 返回值
if (typeof window !== 'undefined') {
  (window as any).Gomoku = { init, createRoom, joinRoom, /* ... */ };
}
```

## 10.2 陷阱二：esbuild globalName 给出 CJS wrapper

```js
// build.mjs 中设置 globalName: 'Gomoku' + format: 'iife'
// 源码中 export default Gomoku
// 产物：
var Gomoku = (() => {
  // ...
  return __toCommonJS(main_exports);
})();
// window.Gomoku = { default: { init, createRoom, ... }, Gomoku: { ... } }
// Gomoku.init → undefined！因为 init 在 Gomoku.default.init
```

**结论**：不要用 `globalName` + `export default` 组合。手动 `window.X = {...}` 最可靠。

## 10.3 正确的 esbuild 构建配置

```js
// build.mjs
import * as esbuild from 'esbuild';

const common = {
  bundle: true,
  format: 'iife',
  target: 'es2020',
  minify: false,
  sourcemap: true,
  // ❌ 不设 globalName — 由源码中手动 window.X = {...} 处理
};

await esbuild.build({ ...common, entryPoints: ['src/main.ts'], outfile: 'dist/main.js' });
await esbuild.build({ ...common, entryPoints: ['src/room.ts'], outfile: 'dist/room.js' });
await esbuild.build({ ...common, entryPoints: ['src/sound.ts'], outfile: 'dist/sound.js' });
await esbuild.build({ ...common, entryPoints: ['src/game_input.ts'], outfile: 'dist/input.js' });
```

```html
<!-- index.html: 加载顺序 = 依赖顺序 -->
<script src="dist/sound.js"></script>
<script src="dist/room.js"></script>
<script src="dist/input.js"></script>
<script src="dist/main.js"></script>
```

## 10.4 调试方法论：Playwright 浏览器内隔离测试

当 `window.Global === undefined` 无法用静态分析定位时：

```
1. Playwright navigate 到页面
2. playwright_evaluate 创建动态 <script> 标签，注入最小复现用例
3. playwright_console_logs 查看 console.log 输出
4. 逐变量名、逐语法结构隔离 → 锁定精确触发条件
5. 确认根因后改源码 → 重新构建 → 再次 playwright_evaluate 验证
```

**关键原则**：浏览器的实际行为 > 你对 JS 语法的直觉。同名 `var` 在 IIFE 中的遮蔽语义在静态 `<script>` 和动态 `<script>` 中表现不同。
