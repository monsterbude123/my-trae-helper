---
name: webgal-engine-build
description: WebGAL 引擎构建与部署 — 将游戏脚本和素材打包为 WebGAL 可运行产物并部署到线上。包含截图/视频验证 proof bundle + 构建错误排查。触发词：WebGAL构建、WebGAL部署、webgal build、webgal deploy、游戏打包、游戏发布。
user-invocable: true
---

# WebGAL 引擎构建与部署

将游戏场景脚本和素材资源打包为 WebGAL 引擎可运行的 Web 产物，并部署上线。

> 前置条件：`game-quality-gate` 门禁已通过。

## 核心铁律

> 参照 godogen 视觉验证原则：**信任截图，不信任代码。** 代码编译通过不代表游戏能玩。

```
1. 构建后必须生成 proof bundle（关键场景截图 + 视频录像）
2. proof bundle 通过人工确认后才能部署
3. 构建失败 → 检查 quirks 常见坑 → 回退素材管线或脚本编写
```

## 构建流程

```
1. 素材导入验证 → 目录结构一致、PNG RGBA、txt 格式正确
2. 生成 config.txt（游戏标题、Game_key、封面图等）
3. 复制 WebGAL 引擎源码
4. 放入游戏资源（scene/、background/、figure/、bgm/、vocal/）
5. npm install + vite build
6. 产出 dist/
7. 截图验证 proof bundle → 人工确认
```

## 素材导入验证

> 参照 godogen 导入素材三要素检查。

构建前确认：
- 素材文件在正确目录（scene/、background/、figure/ 等）
- 运行时路径与实际文件路径一致（大小写敏感）
- PNG 为 RGBA 格式（figure/ 目录下）
- txt 场景脚本使用 UTF-8 编码

## config.txt 模板

```
Game_name:{游戏标题};
Game_key:{game_key};
Title_img:bg.webp;
Title_bgm:s_Title.mp3;
Game_Logo:bg.webp;
Enable_Appreciation:true;
Enable_Continue:true;
```

## 构建命令

```powershell
# 复制引擎
Copy-Item -Recurse docs/reference/WebGAL/packages/webgal _work/webgal-engine

# 放入资源
Copy-Item -Recurse {game_key}/config.txt _work/webgal-engine/public/game/
Copy-Item -Recurse {game_key}/scene/ _work/webgal-engine/public/game/scene/
Copy-Item -Recurse {game_key}/background/ _work/webgal-engine/public/game/background/
Copy-Item -Recurse {game_key}/figure/ _work/webgal-engine/public/game/figure/
Copy-Item -Recurse {game_key}/bgm/ _work/webgal-engine/public/game/bgm/

# 构建
cd _work/webgal-engine
npm install --legacy-peer-deps
npm install webgal-parser@4.6.1 --legacy-peer-deps
npx vite build --base=./
```

## Proof Bundle 验证

> 参照 godogen capture.md 确定性截图管线。

构建成功后，不是直接部署，而是先产生证据包：

```
screenshots/result/{build_tag}/
├── title.png          # 标题画面
├── scene_01.png       # 第一个场景
├── scene_02.png       # 有立绘的场景
├── scene_03.png       # 关键剧情节点
├── video.mp4          # 15s 从前到后的视频录像
└── proof.md           # 证据说明（哪些场景、哪些立绘、验证结论）
```

**视频要求**:
- 15s（最多 30s）展示游戏流程
- 覆盖：标题 → 至少 3 个场景 → 至少 1 个立绘切换
- 包含 BGM 和配音（如果已生成）

**人工确认点**:
```
proof bundle 已生成，建议人工核查：
1. 标题画面显示正确？
2. 第一场景立绘位置/大小正常？
3. 字幕与配音同步？
4. BGM 正常播放无静音？
```

确认通过后才进入部署步骤。

## 部署

> WebGAL 产物为标准静态站点（`dist/`），可部署到任意静态托管服务。

**部署方式**（按优先级）：

```
1. 静态站点托管: Netlify / Vercel / GitHub Pages / Cloudflare Pages
   → 上传 dist/ 目录即可

2. 自有服务器: Nginx + 反向代理
   → scp dist/ user@server:/var/www/{game-key}/

3. 子域名发布: 如有 publish CLI 工具
   → publish deploy {game-key} -d {domain} -w dist/
```

**部署前检查**:
- proof bundle 人工确认通过
- `dist/index.html` 存在并可访问
- 所有素材路径为相对路径（无绝对路径硬编码）
- `dist/` 总体积 < 50MB（首次加载性能）

## 常见构建错误（quirks）

> 参照 godogen quirks.md 坑收集模式。以下是从实际构建中积累的已知坑。

| 错误 | 原因 | 解决 |
|------|------|------|
| webgal-parser not found | parser 未安装 | `npm install webgal-parser@4.6.1 --legacy-peer-deps` |
| npm ERESOLVE | 依赖冲突 | 加 `--legacy-peer-deps` |
| 角色有白底 | figure/ PNG 不是 RGBA | 回素材管线 → 纯色背景重新生成 → BiRefNet 移除 |
| bin/vite.js 缺失 | node_modules 损坏 | 清掉 node_modules 后重新 install |
| 场景脚本不加载 | txt 编码非 UTF-8 | 转码为 UTF-8（勿用 ANSI/GBK） |
| 素材路径 404 | 路径大小写不匹配 | Web 环境大小写敏感，统一小写 |
| 配音无声音 | vocal/ 文件格式不支持 | 转为 OGG 或 MP3 |

> 新发现的坑写入 `quirks-webgal.md`（项目级），kit 维护者定期审查提升到本文件。

## 详细参考

- 引擎构建详解：`references/01-build.md`
- 部署上线详解：`references/02-deploy.md`
