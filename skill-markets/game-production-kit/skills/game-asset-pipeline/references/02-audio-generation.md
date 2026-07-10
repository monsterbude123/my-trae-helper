# 音频生成（BGM + SFX + AMB + FX）

> 引擎无关。音频素材生成管线。

## 声场四层架构

音频是分层的声场体验，不是平面的：

| 层 | 类型 | 音量比例 | 示例 |
|----|------|---------|------|
| L1 | BGM（主调） | 100% | 主题曲、场景基调 |
| L2 | SFX（动作） | 60-80% | 脚步声、开门声、键盘声 |
| L3 | AMB（环境） | 40-60% | 雨声、城市背景、咖啡馆嘈杂 |
| L4 | FX（情感） | 30-50% | 回忆闪回、梦境切换、现实拉回 |

**原则**：每层独立生成、独立控制音量。L2-L4 不可省略（常见错误：只做 BGM 不做 SFX/AMB/FX）。

## 使用 workflow 模板

使用 `bgm_generate.json`，只修改 3 个字段：

| 修改项 | 节点 | 字段 |
|--------|------|------|
| 音频描述 | node 68 | `inputs.value` |
| 输出前缀 | node 19 | `inputs.filename_prefix` |
| 时长 | node 74 | `inputs.value`（秒，浮点数） |

**类别切换**（node 69 CustomCombo）：
- `Music` (index=0)：60-120s 场景 BGM
- `Instrument` (index=1)：30-60s 纯乐器过场
- `SFX` (index=2)：5-15s 音效
- `One-shot` (index=3)：3-8s 短击音

**清单要求**：
- 每个场景 1 首 BGM + 标题画面 1 首
- 关键音效（开门、电话、脚步声等，3-15s）
- 不全做 120s 长音乐

## Stable Audio 3 避坑

| 问题 | 根因 | 修复 |
|------|------|------|
| 多个音频听起来一样 | prompt 共享太多"low/sub-bass/dark"关键词 | 每个 prompt 用具体名词/材质/动词，40-60+ tokens |
| 提示词未生效 | `PrimitiveStringMultiline` 字段名写错（用 `text` 而非 `value`） | 节点 68 用 `value` 注入 |
| 内容完全重复 | `KSampler.seed` 固定 | 每条注入独立 seed（`int(time.time()*1000) + i*7919`） |
| One-shot 不清晰 | Stable Audio 3 对"single event"描述不擅长 | 用具体物件材质描述（如"rain-soaked pavement"替代"footsteps"） |

> **注意**：MD5 不同不代表内容不同——Stable Audio 对同一 prompt 也会有微小波动。**必须做 RMS/peak 验证**确保内容实际不同。
