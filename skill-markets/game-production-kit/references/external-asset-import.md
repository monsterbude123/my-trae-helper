# 外部素材导入协议

> 触发: 用户提供第三方素材（itch.io 素材包/外包交付/自制素材/免费素材站）需要导入项目

## 导入流程

### Step 1: 分类扫描

将外部素材按目录结构分类:

素材源目录 → 映射到 {game_key}/assets/:
  sprites/    → assets/sprites/{category}/
  audio/bgm/  → assets/audio/bgm/
  audio/sfx/  → assets/audio/sfx/
  ui/         → assets/ui/
  fonts/      → assets/fonts/

### Step 2: 批量注册

运行导入脚本（自动扫描 + 写 asset-manifest 条目）:

```powershell
python scripts/import-external-assets.py {game_key} {external_dir}
```

### Step 3: 验证

脚本完成后自动输出:
  ✅ 已导入: 14 个 sprite, 3 个 BGM, 8 个 SFX
  ⚠️ 跳过: 2 个文件（格式不支持: .psd）
  ⏭️ 重复: 1 个文件（已存在于 assets/，跳过）

## asset-manifest 外部条目格式

外部导入的素材在 asset-manifest.md 中使用以下格式:

```yaml
# === 外部导入 ===
assets/sprite/character/npc_01.png:
  source: "external"
  source_detail: "itch.io — Pixel Fantasy UI Pack by CraftPix"
  license: "个人/商业使用许可"
  imported_at: "2026-07-09"
  status: "imported"
  category: "sprite"
  tags: [npc, pixel_art]
  notes: "162x192, 4帧动画精灵"

assets/audio/bgm/shop_theme.ogg:
  source: "external"
  source_detail: "外包 — 小美 (composer@example.com)"
  license: "买断，独家使用"
  imported_at: "2026-07-09"
  status: "imported"
  category: "bgm"
  tags: [shop, calm, loop]
  notes: "2:30 循环，BPM=90, C major"
```

## 与 AI 生成素材的区别

| 字段 | AI 生成 | 外部导入 |
|------|---------|---------|
| source | "story-design" | "external" |
| source_version | "v3" | 无 |
| generated_at | ✅ | ❌ (用 imported_at) |
| 生成参数 | ✅ (prompt/seed) | ❌ |
| status 状态 | pending→generated→approved | **imported** |
| cost | ✅ (API 调用费用) | ❌ (用 source_detail 记录实际成本) |
