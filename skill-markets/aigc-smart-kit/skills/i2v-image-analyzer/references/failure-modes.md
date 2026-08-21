# 图理解失败的 7 类坑 + 修复

> vision 模型看图时常踩的坑。每个坑给根因 + 修复策略。

## §1 vision 误识别主体(把背景当主体)

**现象**:vision 把"主体旁的路人"或"背景里的猫"识别成主主体。

**根因**:vision 默认按"画面中心 + 最大物体"判主体,但构图里主体可能在边缘。

**修复**:
```
1. vision prompt 显式说:"先找构图中心 / 三分线焦点上的主体,忽略边缘 / 模糊元素"
2. 检查 subject.position 字段,如果不是构图焦点 → 重新指定
3. 让 vision 列出 top-3 候选主体 + 主体概率
```

## §2 风格词过度细化

**现象**:vision 输出 `cinematic, photographic, hyper-realistic, photorealistic, ultra-detailed, 8K, RAW photo, ...` 一长串风格词,导致 prompt 风格饱和。

**根因**:vision 倾向堆叠风格词"以防不够准",但 prompt 风格词过载会让模型混乱。

**修复**:
```
强制约束风格词 ≤ 4 个:
  style: 主风格 1 个
  art_style: 子风格 1 个(选填)
  lighting: 1 个
  color_grade: 1 个(选填)

超出词表的形容词剔除(不写入 schema)
```

## §3 时间 / 天气过度推测

**现象**:vision 对"outdoor + 暖光"自动判断为"golden hour",但实际是"正午 + 暖滤镜"。

**根因**:vision 倾向给具体时间,但经常猜错。

**修复**:
```
scene.time_of_day 必填,但要求 vision 给出 confidence:
  - high: 有明确证据(时钟 / 太阳位置)
  - medium: 推测(暖光 → 黄金时刻)
  - low: 无法判断 → 留空或写 "unknown"

下游包装 prompt 时:
  - confidence = high → 直接用
  - confidence = low → 不写入 prompt,留 vision 不确定的空间
```

## §4 漏掉图中的文字 / Logo

**现象**:vision 不识别图里的招牌 / 海报 / 字幕,导致后续视频生成时这些文字糊掉。

**根因**:vision OCR 能力参差,有时只识别大文字不识别小文字。

**修复**:
```
1. vision prompt 强制: "列出图中所有可见文字 + 位置 + 大小(verbatim)"
2. constraints.text_in_image 字段必填,即便空数组
3. 下游包装时,如果有 text_in_image:
   - H3: 写 `rises verbatim: "..."` + 位置
   - Seedance: 写 explicit reference + verbatim
```

## §5 推荐运镜违反画面构图

**现象**:vision 看到 wide shot 风景图,推荐 `extreme close-up`,结果生成出来人物比例全错。

**根因**:vision 不懂运镜构图匹配,只看"哪里能动"。

**修复**:
```
推荐运镜 MUST 满足构图适配:
  wide / extreme-wide → push in / dolly in / arc
  medium / close-up   → pull back / dolly out / pan
  product shot        → static / locked-off
  dynamic element     → tracking shot / handheld

schema 加校验:cinematography.framing 与 dynamic.recommended_camera_motion 不冲突
```

## §6 关键词与 vision 冲突未解决

**现象**:用户说"镜头推近",但 vision 看到的是 wide shot,推荐 pull back;最终输出模糊两个方向。

**根因**:§3 关键词合并协议未严格执行。

**修复**:
```
强制优先级:
  1. user_overrides > vision 默认
  2. 冲突时显式写 user_overrides.merged_into 字段
  3. schema 校验:cinematography.recommended_motion 与 user_overrides 字段一致
```

## §7 analyzer 输出后忘了给改造钩子

**现象**:Agent 生成 H3 prompt 后直接交给用户,没有提示"还能怎么改 / 还能生成其他平台"。

**根因**:Hook 协议在 §5.2,但 Agent 容易忘。

**修复**:
```
i2v-h3-prompt 输出后 MUST 追加 §5.2 改造提示块:
  ┌─────────────────────────────────┐
  │ 【已生成】MiniMax H3 / 三段式     │
  │ 📌 你可以这样改造:                │
  │   • "改 Seedance 2.5 版本"        │
  │   • "要更短的 5s"                │
  │   • "加对白"                     │
  │   • "改成 Hailuo 02 方括号运镜"   │
  │   • "加参考素材做 R2V"           │
  │   • "加 BGM"                    │
  └─────────────────────────────────┘
```

## §8 速查表

| 现象 | 关键修复 |
|------|---------|
| vision 误识别主体 | 构图焦点优先 + top-3 候选 |
| 风格词过载 | 风格词 ≤4 + 词表收敛 |
| 时间推测错 | confidence 字段 + low 则不写 |
| 漏文字 | 强制 OCR + constraints.text_in_image |
| 运镜构图冲突 | framing × motion 适配表 |
| 关键词冲突 | user_overrides > vision 默认 |
| 忘改造钩子 | 输出后 MUST 追加 §5.2 块 |
| vision API 调用失败 | 见 §10(env 缺失 / 网络 / 模型拒绝 / 非 JSON 输出) |

## §9 来源

- 蒸馏自 [docs/research/2026-08-19-i2v-prompt-skills.md](../../../docs/research/2026-08-19-i2v-prompt-skills.md)
- 跨平台实战:
  - [Kling 3.0 I2V prompt 实战](https://kling3.app/blog/how-to-use-kling-3-0-image-to-video)
  - [Veo 3.1 prompt guide](https://www.veo3gen.app/blog/veo-31-image-to-video-prompts-that-actually-animate-not-just-wiggle-a-beginner-g)

## §10 vision API 调用失败(实现层兜底)

> `scripts/i2v_vision_call.py` 已经做了 3 层降级,但调用方仍需知道每类失败的诊断 + 修复。
> 失败 → CLI exit code = 2,`analyzer_status="partial: <原因>"`。

### §10.1 env 缺失(最常见)

**现象**:
```
[FATAL] 未找到 API Key。请设置以下任一环境变量:
  - MINIMAX_API_KEY(国内 api.minimaxi.com)
  - MINIMAX_GLOBAL_API_KEY(国际 api.minimax.io)
  - 或在项目根目录 .env 配置
```

**根因**:`MINIMAX_API_KEY` / `MINIMAX_GLOBAL_API_KEY` 没设,`.env` 也没找到。

**修复**:
```
# 1) 项目根目录 .env(推荐,脚本自动加载)
echo 'MINIMAX_API_KEY=eyJ-your-key' >> .env

# 2) 或 shell 直传(不进 git)
export MINIMAX_API_KEY=eyJ-your-key

# 3) 验证加载
python -c "import os; print(os.environ.get('MINIMAX_API_KEY', '<missing>')[:8])"
```

**.env 路径**:
- `cwd/.env`(项目根)
- 脚本向上 4 层内的 `.env`
- 已加载的 shell env 优先于 `.env`(不会被覆盖)

### §10.2 网络异常(代理 / 防火墙 / DNS)

**现象**:
```
[WARNING] 网络异常(第 1 次):HTTPSConnectionPool ... — 1.5s 后重试
[WARNING] 网络异常(第 2 次):... — 2.2s 后重试
[WARNING] 网络异常(第 3 次):... — 3.4s 后重试
RuntimeError: 重试 3 次后仍失败:...
```

**根因**:VPN / 代理 / 公司防火墙拦截 `api.minimaxi.com`。

**修复**:
```
# 1) 检查能否直连
curl -I https://api.minimaxi.com/v1/text/chatcompletion_v2

# 2) 配置代理(走 env,不动脚本)
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890

# 3) 自定义 base URL(测试环境)
export MINIMAX_BASE_URL=https://your-proxy.example.com/v1

# 4) 调大超时(默认 60s)
export MINIMAX_TIMEOUT=180
```

### §10.3 鉴权失败(401 / 403)

**现象**:
```
PermissionError: [401] 鉴权失败 — 检查 API Key 是否有效。body=...
```

**根因**:Key 无效 / 过期 / 区域错配(CN Key 走 GLOBAL 端点)。

**修复**:
```
1. 登录 minimax 开放平台 → 重新签发 Key
2. 区分区域:
   MINIMAX_API_KEY        → api.minimaxi.com(国内)
   MINIMAX_GLOBAL_API_KEY → api.minimax.io(国际)
3. 脚本会自动按 Key 选 region,无需手动设 MINIMAX_BASE_URL
4. 检查 Key 是否含空格 / 换行 / 引号
```

### §10.4 限流(429)

**现象**:`PermissionError: [429] 触发限流 — 等待 1.5s 后重试`(脚本**不重试** 429,直接抛)

**根因**:并发过高 / Key 被临时限流。

**修复**:
```
1. 降低并发:concurrent.futures.ThreadPoolExecutor(max_workers=2)
2. 加退避:调用方 sleep(2 ** attempt) 后重试整轮
3. 升级套餐 / 多 Key 轮询
```

### §10.5 模型拒绝 / 5xx(脚本自动重试 3 次)

**现象**:`RuntimeError: [500] 服务端错误 — body=...`(3 次后抛)

**根因**:vision 模型服务端故障。

**修复**:
```
1. 等待 1~2 分钟再试(临时性故障)
2. 切换模型:--model MiniMax-M2.7(M3 故障时降级)
3. 检查图片大小:base64 后 > 20MB → 缩图 / 转 JPEG 降质量
4. 检查格式:GIF 仅取首帧;PDF 不支持
```

### §10.6 模型输出非 JSON

**现象**:`WARNING: 模型输出非 JSON,降级 partial schema。raw[:200]=...`

**根因**:
- 模型没遵循 system prompt 的"仅输出 JSON"约束。
- 模型输出了 markdown 包裹但 `_extract_json` 没匹配上(罕见嵌套语法错)。

**修复**:
```
1. 脚本已尝试 3 种解析策略:
   - 整体即 JSON
   - ```json ... ``` 包裹
   - 首个 { 到末尾 } 兜底
   → 都不匹配才降级
2. 升级模型:M3 < M2.7 时 M2.7 偶尔遗漏,M3 较稳
3. 降温度(已 0.4):改脚本 SYSTEM_PROMPT 加"禁止 markdown"
4. 强制 json_object response_format:
   → 当前端点不支持,留待 API 升级
```

### §10.7 降级 partial schema 怎么用

vision 完全失败时,`analyzer_status` 字段告知原因,字段缺失部分填 `"unknown"` 或空数组。

```
# 下游 i2v-h3-prompt 收到 partial schema 时的处理:
report = json.loads(open("image-report.json").read())
if report.get("analyzer_status", "ok") != "ok":
    LOG.warning("analyzer 降级:%s,prompt 用 conservative fallback", report["analyzer_status"])
    # 跳过 vision 贡献的字段,只输出 user_keywords 部分
```

参考 [image-schema.md §8](image-schema.md) 最小骨架。**`unknown` 字段不写入 prompt**,留 vision 不确定的留白。