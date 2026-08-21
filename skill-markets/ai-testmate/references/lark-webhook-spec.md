# lark-webhook-spec — 飞书消息推送规范

## §1 消息卡片格式(interactive card)

reporter 通过 lark MCP 推送测试报告,卡片结构:

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "🤖 ai-testmate 测试报告 <timestamp>"
      },
      "template": "blue"   // 全绿=green,部分失败=orange,全失败=red
    },
    "elements": [
      {
        "tag": "div",
        "fields": [
          {"tag": "text", "text": "**总用例**\n<total>"},
          {"tag": "text", "text": "**通过**\n<passed> ✅"},
          {"tag": "text", "text": "**失败**\n<failed> ❌"},
          {"tag": "text", "text": "**错误率**\n<error_rate>"}
        ]
      },
      {
        "tag": "hr"
      },
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**失败用例 Top 5**:\n<list with bug_link>"
        }
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {"tag": "plain_text", "content": "查看完整报告"},
            "type": "primary",
            "url": "<workspace>/reports/<ts>/report.html"
          }
        ]
      },
      {
        "tag": "note",
        "elements": [
          {"tag": "plain_text", "content": "@<REPORT_PUSH_USERS>"}
        ]
      }
    ]
  }
}
```

## §2 调用范式(lark MCP)

```python
# lark MCP 命令(由 reporter 调用)
lark_im_message send \
  --chat_id "$LARK_WEBHOOK_CHAT_ID" \
  --msg_type interactive \
  --content "$(cat card.json)"
```

> ⚠️ 必须走 lark MCP,不允许直连 webhook URL(AP-4)

## §3 @ 人格式

- `REPORT_PUSH_USERS=ou_aaa,ou_bbb`(open_id 列表,逗号分隔)
- 卡片底部 `note.elements` 拼接 `<at user_id="ou_aaa"></at>`

## §4 失败降级

```
lark MCP 调用失败(超时/鉴权/网络):
  → 降级到 logs/webhook-failed.jsonl 记录卡片 JSON + 时间戳 + 错误信息
  → 不静默丢
  → reporter 输出: [WARN] webhook failed, fallback to logs/
```

## §5 模板按结果选色

| 通过率 | 模板色 |
|:------:|--------|
| 100%   | green |
| ≥80%   | blue  |
| ≥50%   | orange |
| <50%   | red   |

## §6 反例(AP-4)

- ❌ reporter 直连 webhook URL(`https://open.feishu.cn/open-apis/bot/v2/hook/...`)
- ❌ 把 webhook URL 写进 `.env.example`
- ❌ 推送失败静默吞错