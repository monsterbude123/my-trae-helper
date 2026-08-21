# Changelog - V11 → V12

> V12 升主版本(2026-08-16 ADR ACCEPTED)。V11.8.6 累积落地后,V12 物理隔离思想从可选变强制默认。
> V11.8.7.1 起 **V11 扁平布局已彻底废弃**(`--layout` 仅 `v12-preview`),所有项目(含 V11 既有)必须 V12 物理布局。

---

## [V12.0.0.P5] - 2026-08-21

### 🔧 增量:产线预热脚本 + delegation SSoT + completion-self-check + 视觉证据

> **背景**:V12.0.0 主版本升级后,V11.8.7.P5 进一步收尾 4 项交付物,固化到 skill 内部脚本目录。
>
> **本批次新增**:
> - `references/delegation-headers-v11-SSOT.md` — delegation header 协议 SSoT(替代分散在多处 references)
> - `scripts/build-prod-warmup.ps1` + `scripts/build-prod-warmup.sh` — 产线环境预热脚本(Windows PowerShell + Linux/macOS Bash 双版本)
> - `scripts/completion-self-check.py` — 完成度自检脚本(支持 `--strict` 模式)
> - `scripts/screenshots/` — V11.8.7.P5 视觉证据归档(交付物完整度佐证)
>
> **配套治理**:与本仓库 cpcc V1.0 整合、add-all CLI 落地、project-rules-gate 整目录删除同步。

---

## [V12.0.0.P4] - 2026-08-19

(以下沿用既有 V12.0.0.P4 章节,本节未删)