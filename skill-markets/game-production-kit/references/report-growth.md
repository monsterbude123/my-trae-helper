# Report Growth — 异常处理与技能生长

> 来源：fullstack4TraeV8 report-growth 模式，适配游戏制作流水线
> report 是 Game Production Kit 的 Try-Catch 机制

---

## 异常分层（L1-L4）

### L1: 资产/文件异常

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| 图片生成失败（ComfyUI） | retry 2 次 → 降级占位素材 | [L1] 素材生成失败: {asset_name}, 引擎: ComfyUI, 已降级 |
| TTS 合成超时 | retry 1 次 → 跳过该对话行 | [L1] TTS 超时: {voice_line}, 已跳过 |
| 音频/视频格式不兼容 | 转码 → 失败则标记 | [L1] 格式不兼容: {file}, 目标格式: {fmt} |
| 场景脚本引用断裂 | 标记 missing 引用 → 不进 Phase 4 | [L1] 引用断裂: scene_{id} refs {missing_asset} |

### L2: Phase 执行异常

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| engine-build 失败 | retry with clean → 仍失败阻塞 | [L2] 构建失败: {engine}, 错误: {build_log \|\| extract} |
| 场景脚本解析错误 | 标记错误行 → 回退 Phase 3 | [L2] 脚本解析错误: {file}#{line} |
| asset-manifest 版本冲突 | 询问用户 → 选择版本 | [L2] 版本冲突: {asset} v{old} vs v{new} |

### L3: 游戏逻辑异常

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| 分支覆盖不足 | 标记 CONCERNS → 不进发布 | [L3] 分支覆盖: {implemented}/{total} |
| 存档兼容性测试失败 | 阻塞 Phase 6 | [L3] 存档不兼容: v{N-1} 存档无法在 v{N} 读取 |
| 性能基准不达标 | 标记 → 建议优化 | [L3] 性能: {fps} < 目标 {target_fps} |
| Hotfix 回归 | 修复引入新 Bug | 写 hotfix 记录 + 关联 report；report 中标注 trigger: hotfix-{id} |

### L4: 平台/环境异常

| 异常 | 行为 | report 记录 |
|------|------|-----------|
| GitNexus 索引过期 | 自动 `npx gitnexus analyze` | [L4] GitNexus 已更新 |
| 引擎工具链缺失 | report + 安装指引 | [L4] {engine} SDK 缺失 |
| 打包签名失败 | report + 阻塞 | [L4] 签名失败: {platform} |

---

## 异常处理原则

```
1. NEVER SILENT FAIL  — 异常必须有可见输出（控制台 + report 文件）
2. RETRY TWICE, STOP  — 最多重试 2 次（游戏资产生成慢，避免无限等待）
3. FAIL FAST, REPORT  — 不可恢复 → 立即生成 report + 阻塞流水线
4. NEVER GUESS        — 素材缺失用占位符，不编造内容
5. STATE CARD TRUTH   — 状态卡 .project-state-card.md 同步记录异常
```

> **retry 次数统一**: 资产类 retry 2 次，代码类 retry 1 次。asset-pipeline 的 3 次是个别超时场景，由子技能自行处理。

---

## 编号与路径规则

报告路径: {game_key}/reports/report-{phase}{seq}.md
  - {phase}: phase 编号（0-7），占 1 位
  - {seq}: 该 phase 内的序号（01-99），占 2 位

示例:
  reports/report-201.md → Phase 2 第 1 个报告
  reports/report-402.md → Phase 4 第 2 个报告
  reports/report-701.md → Phase 7 第 1 个报告

原则: 全局唯一编号，不会跨 phase 冲突。

---

## report 文件格式

```markdown
# report-{0X}.md
**时间**: YYYY-MM-DD HH:MM
**Game Key**: {game_key}
**异常等级**: L1 / L2 / L3 / L4
**Phase**: {0-7}

## 触发场景
{素材生成失败 / 构建失败 / 逻辑异常 / 平台错误}

## 问题描述
{发生了什么}

## 根因分析
{为什么会发生}

## 降级方案（如有）
{占位素材 / 跳过该行 / 转码替代}

## 用户处理
- [ ] 待处理 / [x] 已处理 / [-] 不适用
```

---

## 技能生长协议

> L1-L4 异常解决后，评估是否需要写入技能以预防同类问题。

```
报告产出后:
  ├── L1/L2 解决后 → 问 Agent："此异常模式是否应固化到 skill？"
  │     ├── 是 → 追加到对应 skill 的 references/（如 asset-generation-patterns.md）
  │     └── 否 → 仅留 report
  │
  ├── L3 解决后 → 必须写入 quality-gate 检查项
  │
  └── L4 解决后 → 必须写入对应 engine-scripting 的 quirks 文档
```

---

## 与 cockpit 联动

- 每个 report 产出时，在 `.project-state-card.md` 阻塞项区追加一条
- report 标记为"已处理"后，从阻塞项区移除
- 新会话重入时，检查 cockpit 阻塞项 → 加载未处理的 report
