# Intent Classification Workflow — Stage -1 Intake

> Stage -1 Intake Step 1 必走。意图分类协议。

---

## 5 类意图

| 意图 | 触发词 | 路由 |
|------|--------|------|
| **feature** | "加个"/"实现"/"开发"/"实现功能" | Stage 0 Plan |
| **bugfix** | "修 bug"/"坏了"/"报错"/"异常" | Stage 6 Bug Fix |
| **enhance** | "优化"/"改进"/"重构" | Stage 0 Plan |
| **investigate** | "查一下"/"分析"/"为什么" | Stage 0 Plan (analysis) |
| **document** | "写文档"/"记录"/"更新 spec" | Stage 0 Plan (doc) |

---

## 分类算法

```python
def classify_intent(user_input: str) -> str:
    intent_keywords = {
        "feature": ["加", "实现", "开发", "创建", "做"],
        "bugfix": ["修", "坏", "报错", "异常", "失败"],
        "enhance": ["优化", "改进", "重构", "提升"],
        "investigate": ["查", "分析", "为什么", "怎么回事"],
        "document": ["文档", "记录", "更新", "写"],
    }

    scores = {intent: 0 for intent in intent_keywords}
    for intent, keywords in intent_keywords.items():
        for kw in keywords:
            if kw in user_input:
                scores[intent] += 1

    return max(scores, key=scores.get) if max(scores.values()) > 0 else "feature"
```

---

## 输出

```yaml
intent_class:
  primary: "feature"
  confidence: 0.85
  trigger_phrase: "加个用户认证"
  routing_target: "Stage 0 Plan"
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [stage-interaction-protocol.md](../../references/stage-interaction-protocol.md)