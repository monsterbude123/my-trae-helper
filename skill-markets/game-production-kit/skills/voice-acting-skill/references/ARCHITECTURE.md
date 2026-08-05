# voice-acting-script-skill · 架构

## 1. 整体架构

配音剧本注音工具采用**管道式架构**（Pipeline Architecture），数据单向流动：

```
剧本 (Markdown)
   ↓
[parse_script]          # 解析
   ↓
[assign_voices]         # 角色 → 三引擎音色映射
   ↓
[create_batch_plan]     # 13 秒批次切分
   ↓
[generate_all]          # 三引擎注音生成
   ↓
[CosyVoice/OmniVoice]   # 合成
   ↓
[build_timeline/...]    # 工程文件
```

## 2. 模块依赖图

```
┌─────────────┐
│   parser/   │  script_parser.py
└──────┬──────┘
       │ ParsedScript
       ▼
┌─────────────┐
│  analyzer/  │  voice_assigner.py
└──────┬──────┘
       │ ScriptAnalysis
       ▼
┌─────────────┐
│  batcher/   │  batch_manager.py
└──────┬──────┘
       │ BatchPlan
       ▼
┌─────────────┐
│ annotator/  │  annotation_generator.py
└──────┬──────┘  + markdown_formatter.py
       │ QwenTts/CosyVoice/OmniVoice Annotation
       ▼
┌─────────────┐
│synthesizer/ │  cosyvoice_adapter.py
└─────────────┘  + omnivoice_adapter.py
                  + project_generator.py
```

## 3. 数据类型（pydantic models）

### 解析层

```python
ParsedScript
  ├── meta: ScriptMeta
  │     ├── title: str
  │     ├── characters: list[Character]
  │     └── total_duration_seconds: float
  └── scenes: list[Scene]
        ├── id, scene_number, time_range
        ├── location, time_of_day, description
        └── lines: list[Line]
              ├── type: dialogue|narration|action|emotion_hint
              ├── character_id, text, raw_text
              └── pause_before, pause_after
```

### 分析层

```python
ScriptAnalysis
  ├── meta: ScriptMeta
  ├── scenes: list[Scene]
  └── voice_assignments: list[VoiceAssignment]
        ├── character_id
        ├── qwen_tts: QwenTtsVoiceConfig
        ├── cosyvoice: CosyVoiceVoiceConfig
        └── omnivoice: OmniVoiceVoiceConfig
```

### 批次层

```python
BatchPlan
  ├── batches: list[Batch]
  │     ├── id, scene_id, lines
  │     ├── estimated_duration_seconds
  │     ├── target_duration_seconds
  │     └── tilt_correction: TiltCorrection | None
  ├── total_batches
  ├── average_lines_per_batch
  └── overflow_strategy
```

### 注音层（每引擎一个模型）

```python
QwenTtsAnnotation
CosyVoiceAnnotation
OmniVoiceAnnotation
```

### 合成层

```python
SynthesisResult / BatchSynthesisResult / ProjectTimeline
```

## 4. 数据流铁律

1. **单向流**：raw → parsed → analyzed → annotated → audio → project
2. **不可变**：每个阶段只读上一阶段输出，生成新对象
3. **可重入**：所有中间产物持久化为 JSON，可重新读取
4. **可跳过**：synthesize 可独立于 analyze 运行（直接读取 annotated/）

## 5. 设计原则

- **ponytail 思维**：能用代码确定性解决的事不上 LLM
- **标准库优先**：pydantic + click + httpx，不引入额外框架
- **零配置启动**：`pip install -e .` 即可使用 analyze
- **失败安全**：任一阶段失败不污染上游产物
- **可审核**：所有注音结果同时输出 JSON + Markdown 报告

## 6. 性能 / 限制

- 单剧本文本建议 < 10000 行（否则 batch_plan 解析变慢）
- CosyVoice 适配器使用 Gradio HTTP + SSE，单句约 1-3s
- OmniVoice 适配器使用 Gradio 客户端，合并输出比逐句快
- 批次大小硬上限 13 秒（带 2 秒安全 margin）

## 7. 部署

- **开发**：`pip install -e .`
- **运行**：`vas analyze 剧本.md -o output` + `vas synthesize -o output`
- **测试**：`python -m pytest scripts/tests/`
- **分发**：作为 Trae IDE 技能包，复制到 `~/.trae-cn/skills/`
