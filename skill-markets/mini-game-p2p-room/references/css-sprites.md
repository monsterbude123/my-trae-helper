# CSS 精灵图头像系统

> SKILL.md §5 详细实现。

---

## 5.1 精灵图模式

```css
.avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: url('assets/avatars-sprite.png') no-repeat;
  background-size: 144px 144px;          /* display_size × grid_cols */
  background-position: center;           /* 🛑 必须！否则头像歪 */
  flex-shrink: 0;
  border: 2px solid rgba(233, 69, 96, 0.35);
  image-rendering: crisp-edges;          /* 像素风精灵图 */
}
.avi-N { background-position: -(col*36px) -(row*36px); }
```

## 5.2 纯 CSS 头像（无图片替代方案）

```css
.avatar { 
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 800; color: #fff;
}
.av-0 { background: linear-gradient(135deg, #e94560, #c23152); }
.av-1 { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.av-2 { background: linear-gradient(135deg, #22c55e, #15803d); }
.av-3 { background: linear-gradient(135deg, #f0c040, #d97706); }
```

## 5.3 修复经验

| 症状 | 根因 | 修复 |
|------|------|------|
| 头像歪/偏移 | `.avatar` 缺基类 `background-position: center`，浏览器默认 origin `0 0` | 基类加 `center`，per-avi 覆盖偏移 |
| 头像模糊 | `image-rendering` 未指定或用了 `auto` | 像素风用 `crisp-edges` |
| 圆形白边 | `border-radius: 50%` 覆盖了精灵图背景边缘 | 调大 `background-size` 或给 `padding: 1px` |
