---
name: i2v-image-analyzer
description: [DEPRECATED] 此 skill 已并入 video-input-analyzer。Use video-input-analyzer/ 替代。本文件保留仅作向后兼容。新调用会自动 redirect。
version: 0.9.0-deprecated
redirect_to: ../video-input-analyzer/
replaced_by: video-input-analyzer/v1.0
deprecated_at: 2026-08-20
---

# 本 skill 已弃用 — 详见 `../video-input-analyzer/`

> **⚠️ DEPRECATED since 2026-08-20**
>
> 本 skill `i2v-image-analyzer/v0.9` 已并入 [`../video-input-analyzer/v1.0`](../video-input-analyzer/SKILL.md)。
>
> ## 迁移指南
>
> | 老用法 | 新用法 |
> |--------|--------|
> | `Skill(name="i2v-image-analyzer")` | `Skill(name="video-input-analyzer")` |
> | `--image photo.jpg` | `--image photo.jpg`(向后兼容)+ `--input-mode auto` 自动判 i2v |
> | 输出 `image-report.json` v1.0 | 输出 `input-report.json` v2.0(包含 v1.0 字段) |
>
> ## 自动 redirect
>
> `scripts/i2v_vision_call.py` 仍接受 `--image` 单图参数,自动按 i2v 模式处理。
> 无需修改 CLI 调用,内部已升级为多模态。
>
> ## 何时仍可用本 skill
>
> - 老项目代码引用了 `i2v-image-analyzer` 的文件名 / import 名(改 import)
> - 老测试 / 老 fixtures(待主代理统一迁移)
>
> ## 完整功能
>
> 请见 [`../video-input-analyzer/SKILL.md`](../video-input-analyzer/SKILL.md)。
