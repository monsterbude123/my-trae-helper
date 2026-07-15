# 上线检查清单

> 来源：CC Studio release-checklist + launch-checklist
> 关联：game-operations SKILL.md §骨架流程.1

任何项目上线前必须逐项通过。未通过 → 阻断发布。

## §1 技术上线

| # | 检查项 | 判定 |
|---|--------|------|
| 1 | Release 构建通过（无 warning） | PASS/FAIL |
| 2 | CDN 部署完成、静态资源可访问 | PASS/FAIL |
| 3 | SSL 证书有效（HTTPS 强制） | PASS/FAIL |
| 4 | 域名 DNS 解析正确 | PASS/FAIL |
| 5 | 后端 API 健康检查 200 | PASS/FAIL |
| 6 | 数据库迁移已执行且无错误 | PASS/FAIL |
| 7 | 日志系统就绪、监控告警已配置 | PASS/FAIL |
| 8 | 备份策略已启用（每日自动备份） | PASS/FAIL |
| 9 | 负载测试通过（目标并发数） | PASS/FAIL |
| 10 | 回滚方案已就绪（上一版本 build tag 可用） | PASS/FAIL |

## §2 商店上线

| 平台 | 必需项 |
|------|--------|
| **Steam** | 商店页（≥5 截图 + 预告片 + 描述 + 标签）\| SteamPipe 配置 \| 成就图标 \| 云存档配置 |
| **Epic Games Store** | 产品页 \| 年龄分级 \| EOS 配置（如需要）\| 跨平台联机声明 |
| **itch.io** | 项目页 \| 截图 \| 定价 \| 分类标签 \| butler 配置 |
| **App Store** | App 信息 \| 截图（多尺寸）\| 隐私标签 \| 内购 IAP 列表 \| 审核备注 |
| **Google Play** | 商品详情 \| 截图 \| 分级问卷 \| 数据安全表单 \| AAB 签名 |
| **TapTap** | 游戏页 \| 截图/视频 \| 预约/下载配置 \| 版号（中国大陆） |

## §3 内容完整性

| # | 检查项 | 参照 |
|---|--------|------|
| 1 | 与 asset-manifest.md 交叉比对 → 全部素材存在 | Phase 2 |
| 2 | 关键路径 E2E 通过（启动→菜单→游玩→结算） | Phase 5 |
| 3 | 首次游玩体验（FTUE）无阻断 | 手动测试 |
| 4 | 所有成就/奖杯可正常解锁 | 平台 SDK |
| 5 | 游戏内购买/道具发放正常 | 后端联调 |
| 6 | 加载画面/启动 Logo 完整 | 品牌规范 |

## §4 法律合规

| # | 检查项 | 适用地区 |
|---|--------|---------|
| 1 | Age Rating 完成（ESRB / PEGI / IARC） | 全球 |
| 2 | Privacy Policy 已发布且可访问 | 全球 |
| 3 | EULA / Terms of Service 已内嵌 | 全球 |
| 4 | GDPR 合规（Cookie 同意 + 数据删除请求通道） | EU |
| 5 | COPPA 合规（13 岁以下数据保护） | US |
| 6 | 中国大陆版号（ISBN） | CN |
| 7 | 内购退款政策已声明 | 全球 |
| 8 | 第三方 SDK 清单已整理（隐私政策中列出） | 全球 |
| 9 | 版权声明 + 开放源代码许可声明 | 全球 |
