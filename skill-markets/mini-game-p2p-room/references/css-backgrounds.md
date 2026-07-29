# 生动背景设计（CSS Only）

> SKILL.md §6 详细实现。避免图片文件，纯 CSS 实现。

---

## 6.1 径向渐变光晕

```css
body::before {
  content: ''; position: fixed; inset: 0;
  background:
    radial-gradient(ellipse at 20% 30%, rgba(233,69,96,0.07) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(59,130,246,0.05) 0%, transparent 50%);
  pointer-events: none; z-index: 0;
}
```

## 6.2 网格纹理

```css
body::after {
  content: ''; position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none; z-index: 0;
}
```

## 6.3 浮动粒子动画

```css
.particle {
  position: fixed; border-radius: 50%;
  pointer-events: none; z-index: 0;
  animation: floatParticle linear infinite;
}
@keyframes floatParticle {
  0% { transform: translateY(100vh) scale(0.5); opacity: 0; }
  10% { opacity: 0.4; }
  90% { opacity: 0.4; }
  100% { transform: translateY(-10vh) scale(1); opacity: 0; }
}
```
