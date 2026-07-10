# voice-acting-skill · References

> 深度参考文档索引。

## 必读（首次使用）

| 文档 | 说明 |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 整体架构、模块依赖、数据流 |
| [CONSTRAINTS.md](CONSTRAINTS.md) | 业务铁律、不可逾越的约束 |
| [DECISIONS.md](DECISIONS.md) | 关键设计决策（ADRs） |

## 模块参考

| 文档 | 对应模块 |
|---|---|
| [modules/script-parser.md](modules/script-parser.md) | `vaslib.parser.script_parser` |
| [modules/voice-assigner.md](modules/voice-assigner.md) | `vaslib.analyzer.voice_assigner` |
| [modules/batch-manager.md](modules/batch-manager.md) | `vaslib.batcher.batch_manager` |
| [modules/annotation-generator.md](modules/annotation-generator.md) | `vaslib.annotator.annotation_generator` |

## 引用关系

```
SKILL.md (编排器)
  ↓ 路由
skills/*/SKILL.md (子技能)
  ↓ 引用
references/ARCHITECTURE.md (架构)
references/CONSTRAINTS.md (约束)
references/modules/*.md (模块细节)
references/DECISIONS.md (历史决策)
```

## 不在 references/ 中的内容

- 代码实现细节 → 直接读 `scripts/vaslib/` 源码
- 使用方法 → 读顶层 `SKILL.md` 或各子技能 `SKILL.md`
- 配置文件 → `scripts/vaslib/config/voices.py` 或 `assets/configs/`
