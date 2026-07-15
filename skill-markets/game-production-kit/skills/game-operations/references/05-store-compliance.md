# 商店发布与合规

> 来源：各平台开发者文档
> 关联：game-operations SKILL.md §骨架流程.1（上线检查清单）

各平台商店发布要求 + 年龄分级体系。引擎无关。

## §1 Steamworks

| 项目 | 规格 |
|------|------|
| SteamPipe CLI | 构建脚本上传 build 到 Steam |
| 商店页素材 | 头图 460×215 / 主图 616×353 / 背景 1438×810 |
| 截图 | ≥5 张，1280×720+ |
| 预告片 | 推荐 1080p，≤2 分钟 |
| 描述 | 简短描述（≤300 字）+ 详细描述 |
| 标签 | 3-5 个类型标签 |
| 成就 | ISteamUserStats API → SetAchievement |
| 排行榜 | ISteamUserStats API → FindLeaderboard → UploadLeaderboardScore |
| 云存档 | Steam Auto-Cloud 配置 |
| 反作弊 | VAC / EAC / BattlEye 集成声明 |

**SteamPipe 基本流程**：

```bash
# 上传 build
steamcmd +login {user} +run_app_build {vdf_path} +quit
```

**审核周期**：商店页 ~2-5 天 / 版本更新 ~1-3 天

## §2 Epic Games Store

| 要求 | 说明 |
|------|------|
| 跨平台联机 | 如支持联机，需实现跨平台（EGS 强制要求） |
| EOS 集成 | 可选，提供成就/统计/会话管理 |
| 商店页素材 | 与 Steam 类似，另有 EGS 专用尺寸 |
| 年龄分级 | IARC 自评（§6） |

## §3 App Store

| 项目 | 说明 |
|------|------|
| 截图 | 6.7" / 6.5" / 5.5" / 12.9" iPad（多尺寸） |
| App Privacy 标签 | 数据收集类型声明（强制） |
| TestFlight | 内测分发（≤10,000 测试员） |
| IAP | StoreKit → 所有内购商品 |
| 审核被拒 TOP5 | 崩溃 / 占位符内容 / 不完整 / 隐私标签造假 / 缺少功能 |

**审核周期**：首次 ~2-7 天 / 更新 ~1-2 天

## §4 Google Play

| 项目 | 说明 |
|------|------|
| 格式 | Android App Bundle (AAB) |
| 目标 API | 必须 target 最近 1 年内 API 级别 |
| 数据安全表单 | 数据收集/加密/分享声明 |
| 隐私政策 | 必须可访问 URL |
| 分级问卷 | IARC 自评 |
| 签名 | Play App Signing 或自管理密钥 |

**审核周期**：~2-7 天

## §5 itch.io

| 项目 | 工具 |
|------|------|
| 上传 | `butler push {dir} {user}/{game}:{channel}` |
| 定价 | 免费 / 任意定价 / 固定价格 |
| 多文件 | 多 channel 分发（如 `win`/`mac`/`linux`） |

```bash
# butler 命令行示例
butler push build/win username/game:windows
butler push build/mac username/game:mac
```

## §6 年龄分级

| 体系 | 区域 | 流程 |
|------|------|------|
| **ESRB** | 北美 | 填写问卷 → 等待评级 → 标签展示 |
| **PEGI** | 欧洲 | 自评或 IARC → 标签展示 |
| **IARC** | 国际（通用） | 在线问卷 → 自动生成多体系分级 |
| **CERO** | 日本 | 提交审核 → 获取评级 |
| **GRAC** | 韩国 | 提交审核 → 获取评级 |

**IARC 是 Steam / EGS / Google Play / 任天堂等平台通用方案**，一次问卷生成 ESRB + PEGI + USK + ACB + ClassInd 等多个分级。

| 平台 | 分级方式 |
|------|---------|
| Steam | IARC 自评 |
| EGS | IARC 自评 |
| App Store | 苹果自有分级 |
| Google Play | IARC 自评 |
| itch.io | 开发者自行声明 |
