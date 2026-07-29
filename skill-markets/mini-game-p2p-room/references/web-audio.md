# Web Audio 音效系统

> SKILL.md §7 详细实现。纯合成，无外部音频文件。

---

```js
const SoundFX = (() => {
  let ctx = null;
  function getCtx() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();  // 🛑 浏览器自动暂停恢复
    return ctx;
  }
  // 模式一：Oscillator 合成（点击/回合/加入/胜利/失败）
  function playClick() {
    const osc = c.createOscillator();            // 振荡器
    const gain = c.createGain();                 // 音量包络
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, t);         // 频率曲线
    osc.frequency.exponentialRampToValueAtTime(440, t + 0.08);
    gain.gain.setValueAtTime(0.15, t);             // 音量曲线
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.1);
    osc.connect(gain).connect(c.destination);      // 连接链
    osc.start(t); osc.stop(t + 0.1);
  }
  // 模式二：BufferSource 噪声（爆炸）
  function playExplosion() {
    const buffer = c.createBuffer(1, bufferSize, c.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++)
      data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 3);  // 衰减噪声
    noise.connect(noiseGain).connect(c.destination); noise.start(t);
  }
  // 解锁：首次用户交互触发
  function unlock() { getCtx(); }
  return { unlock, click: playClick, explosion: playExplosion, /* ... */ };
})();
// init() 中: document.addEventListener('click', unlock, { once: true });
```
