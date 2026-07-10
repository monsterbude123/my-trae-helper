# voice-acting-script-skill · 业务铁律

## 不可逾越的约束

### 1. 剧本格式必须严格匹配

剧本必须是 Markdown 文件，包含：
- `### **标题**` 格式的标题行
- `● 时长:约XmYs ● 人物以中国五大瑞兽为形象，...` 格式的元信息
- 5 列 Markdown 表格（时间线 / 描述 / 动作 / 台词 / 备注）

如不符合，必须先转换剧本格式，不能修改 parser。

### 2. 角色 ID 必须注册

`scripts/vaslib/parser/script_parser.py::CHARACTER_ID_MAP` 必须包含剧本中出现的所有角色。未注册的角色会被静默丢弃。

### 3. 批次时间上限 13 秒

`MAX_BATCH_SECONDS = TARGET_BATCH_SECONDS - BATCH_MARGIN_SECONDS = 15 - 2 = 13`

不能放宽到 15+，否则 TTS 引擎会因超时失败。

### 4. 多音字词典只在 POLYPHONE_DICT

不能动态添加、不能 LLM 推断。所有多音字必须人工预先登记。

### 5. 方言映射表是单一真相源

`scripts/vaslib/config/voices.py::DIALECT_MAPPINGS` 是方言→音色的唯一映射。
任何方言相关变更必须改这里，不要在 voice_assigner.py 中散落硬编码。

### 6. 合成服务地址默认不能改默认值

`http://127.0.0.1:50000` (CosyVoice) 和 `http://localhost:7860` (OmniVoice) 是社区默认部署地址。
本地开发可改，但 PR 中不能改默认值。

### 7. 输出目录可重入

`vas analyze` 可重复执行到同一 `-o` 目录，输出会被覆盖。这是设计如此。

## 业务边界

### 不做的事

- 不做剧本自动生成（不接 LLM）
- 不做音频后处理（拼接、混音、降噪交给 FFmpeg / 外部工具）
- 不做视频合成（仅交付音频 + 时间轴 JSON）
- 不做音色训练（仅使用预训练音色）
- 不做实时 TTS（仅离线批处理）

### 做的事

- 解析固定格式的中文剧本
- 角色属性 → 三引擎音色配置
- 13 秒批次切分 + 倾斜修正
- 三引擎注音 JSON + Markdown 报告
- 调用本地 TTS 服务合成音频
- 生成时间轴 / 音色映射 / 引擎对比报告

## 性能 / 质量约束

- 单剧本处理时间 < 30s（不含 TTS 合成）
- 注音规则必须同时支持 JSON 机器消费和 Markdown 人类审核
- TTS 合成失败时，工程文件仍可生成（标记 error 字段）

## 不在范围内

- 跨语言剧本（仅中文）
- 非 Markdown 剧本格式（仅 Markdown 表格）
- 多人协作版本控制（无 Git 集成）
- Web UI（仅 CLI + Markdown 报告）
