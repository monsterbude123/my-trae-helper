# babylon-scaffold.md

> 来源：godogen babylon/scaffold.md（吸收自 babylon-scaffold-v1，2026-06 提取）
> 关联：babylon-scripting/SKILL.md §项目骨架
> 目的：提供 Babylon.js 7+ + Vite 6+ + TS strict mode 的最小可运行项目骨架。

## §1 package.json

最小依赖清单：核心引擎 + GUI + 加载器 + 类型。

```json
{
  "name": "babylon-game",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "preview": "vite preview --port 4173",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@babylonjs/core": "^7.40.0",
    "@babylonjs/gui": "^7.40.0",
    "@babylonjs/loaders": "^7.40.0",
    "@babylonjs/materials": "^7.40.0"
  },
  "devDependencies": {
    "@types/node": "^20.12.0",
    "typescript": "^5.4.0",
    "vite": "^6.0.0"
  }
}
```

> 说明：`@babylonjs/inspector` 单独装，避免污染生产包。

## §2 tsconfig.json

strict mode + noImplicitAny + ESNext module resolution。

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true,
    "types": ["node", "vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.tsx"],
  "exclude": ["node_modules", "dist"]
}
```

## §3 vite.config.ts

Vite 配置：HMR + 静态资源 + 别名。

```ts
import { defineConfig } from "vite";
import { resolve } from "node:path";

export default defineConfig({
  root: ".",
  publicDir: "public",
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
      "@scenes": resolve(__dirname, "src/scenes"),
      "@characters": resolve(__dirname, "src/characters"),
    },
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    strictPort: true,
  },
  build: {
    target: "es2022",
    outDir: "dist",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          babylon: ["@babylonjs/core"],
          gui: ["@babylonjs/gui"],
        },
      },
    },
  },
  optimizeDeps: {
    include: ["@babylonjs/core", "@babylonjs/gui", "@babylonjs/loaders"],
  },
});
```

## §4 index.html 入口

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Babylon Game</title>
    <style>html,body,#app{margin:0;width:100%;height:100%;overflow:hidden;background:#000}</style>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

## §5 完整骨架速查

| 文件 | 行数参考 | 必需 |
|------|---------|------|
| package.json | 25 | ✅ |
| tsconfig.json | 25 | ✅ |
| vite.config.ts | 30 | ✅ |
| index.html | 12 | ✅ |
| src/main.ts | 10 | ✅ |

> 安装：`npm install` → `npm run dev` → 浏览器访问 `http://localhost:5173`
