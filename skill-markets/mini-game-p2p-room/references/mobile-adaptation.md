# 移动端适配要点

> SKILL.md §8 详细实现。

---

```css
html, body {
  background: #0a0a1a;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
  -webkit-tap-highlight-color: transparent;           /* 禁止触摸高亮 */
  min-height: 100dvh;                                  /* 移动端安全区域 */
}
/* 触屏按钮必须可点 */
.cell { aspect-ratio: 1/1; min-width: 28px; }
.btn:active { transform: scale(0.96); }                /* 按压反馈 */
/* input 限制输入 + 实时过滤 */
input[inputmode="numeric"] { /* JS: e.target.value = e.target.value.replace(/\D/g,'').slice(0,4); */ }
```

关键点：
- `<meta viewport-fit=cover, user-scalable=no>`
- `100dvh` 安全区域适配
- `tap-highlight-color: transparent`
- `input inputmode="numeric"` + JS 过滤
