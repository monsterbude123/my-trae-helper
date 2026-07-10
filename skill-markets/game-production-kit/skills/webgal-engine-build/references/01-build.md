# WebGAL 引擎构建

## config.txt 模板

```powershell
@"
Game_name:{游戏标题};
Game_key:{game_key};
Title_img:bg.webp;
Title_bgm:s_Title.mp3;
Game_Logo:bg.webp;
Enable_Appreciation:true;
Enable_Continue:true;
"@ | Out-File -Encoding utf8 {game_key}/config.txt
```

## 构建流程

```powershell
# 复制引擎
Copy-Item -Recurse docs/reference/WebGAL/packages/webgal _work/webgal-engine

# 放入游戏资源
Copy-Item -Recurse {game_key}/config.txt _work/webgal-engine/public/game/
Copy-Item -Recurse {game_key}/scene/ _work/webgal-engine/public/game/scene/
Copy-Item -Recurse {game_key}/background/ _work/webgal-engine/public/game/background/
Copy-Item -Recurse {game_key}/figure/ _work/webgal-engine/public/game/figure/
Copy-Item -Recurse {game_key}/bgm/ _work/webgal-engine/public/game/bgm/

# 安装并构建
cd _work/webgal-engine
npm install --legacy-peer-deps
npm install webgal-parser@4.6.1 --legacy-peer-deps
npx vite build --base=./
```

产物：`_work/webgal-engine/dist/`

## TTS 文件部署

TTS 文件必须复制到 3 个位置（WebGAL 静态资源规则）：

```
{game_key}/voice/                           # 源
_work/webgal-engine/public/game/voice/       # 构建输入
_work/webgal-engine/dist/game/voice/         # 构建输出（自动）
```

构建前必须 `vite build` 重新打包——vite 从 public/ 复制静态资源到 dist/。

## 常见构建错误

| 错误 | 解决 |
|------|------|
| webgal-parser not found | `npm install webgal-parser@4.6.1 --legacy-peer-deps`（必需依赖） |
| npm ERESOLVE | 加 `--legacy-peer-deps` |
| 角色有白底 | figure/ 下 PNG 不是 RGBA，回到素材管线重新抠图 |
| npm install 部分失败（`bin/vite.js` 缺失） | 清掉 `node_modules` 后重新 `npm install --legacy-peer-deps` |

## 脚本目录结构

```
{game_key}/scene/
├── start.txt          # 入口（必须存在）
├── {场景名}.txt       # 各场景脚本
├── ending_true.txt    # 真结局
├── ending_normal.txt  # 普通结局
└── ending_bad.txt     # 坏结局
```
