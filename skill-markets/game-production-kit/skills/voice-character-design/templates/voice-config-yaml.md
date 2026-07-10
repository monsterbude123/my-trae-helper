# 批量角色 voice 配置 yaml 模板

> 适合一个项目多个角色。一次写完，脚本读这个文件生成 voices.json。

## 文件位置

`{project}/voice/voices.yaml`

## 完整模板

```yaml
# ============================================================================
# 角色音色配置 - 「项目名」
# 参照 voice-character-design skill 生成
# 创建日期: YYYY-MM-DD
# TTS 模型: Qwen3-TTS 1.7B VoiceDesign (Chinese)
# ============================================================================

project:
  name: 时空里等你
  tts_model: qwen3-tts-1.7b-voicedesign
  language: Chinese
  default_seed_strategy: per_character_fixed

# ============================================================================
# 全剧通用数值参数（单角色可覆盖）
# ============================================================================
defaults:
  temperature: 0.75
  top_p: 0.85
  repetition_penalty: 1.05
  max_new_tokens: 280

# ============================================================================
# 角色列表
# ============================================================================
characters:

  - id: qiu_suwan
    name_zh: 邱苏晚
    role: 主角恋人
    
    # 5 维声学特征
    axes:
      age: early 20s
      gender: female
      resonance: head + slight chest
      pace: slow with pauses
      pitch_trend: gentle rise on emotional phrases
    
    # 数值参数（覆盖全局）
    params:
      temperature: 0.75
      top_p: 0.85
      repetition_penalty: 1.05
      max_new_tokens: 280
      seed: 10042
    
    # Instruct（30-60 词英文）
    instruct: |
      A young Chinese female in her early 20s with a crystalline, gentle mid-range voice.
      Tender and slightly melancholic, with soft, measured pacing at a moderate tempo.
      Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases.
      There's a fragile, intimate quality to her delivery, as if every word is precious.
    
    # 情绪变体（可选）
    variants:
      calm:
        instruct: |
          A young Chinese female in her early 20s with a crystalline, gentle mid-range voice.
          Calm and tender, with soft measured pacing at a slower tempo.
          Speaks standard Mandarin with quiet warmth, gentle falling intonation.
          The delivery is reflective, like a memory being shared intimately.
        seed: 10042
      melancholy:
        instruct: |
          A young Chinese female in her early 20s with a crystalline, slightly fragile voice.
          Tender and melancholic, with slow hesitant pacing and longer pauses.
          Speaks standard Mandarin with breathy softness, and pitch slightly wavering.
          There's a sense of fading, as if her voice is slowly disappearing.
        seed: 10042
      hopeful:
        instruct: |
          A young Chinese female in her early 20s with a bright, crystalline mid-range voice.
          Hopeful and warm, with measured but rising pacing.
          Speaks standard Mandarin with rising intonation and gentle excitement.
          Her delivery is intimate and precious, as if every word matters deeply.
        seed: 10042

  - id: lin_zhiyi
    name_zh: 林之一
    role: 主角（第一人称，不出声）
    enabled: false  # 第一人称 VN，主角不出声（旁白替代）
    notes: |
      主角无对白——所有主角视角用 {旁白} 替代

  - id: cafe_boss
    name_zh: 咖啡馆老板
    role: 知情者 / 隐喻者
    
    axes:
      age: late 60s
      gender: male
      resonance: deep chest
      pace: slow deliberate
      pitch_trend: falling
    
    params:
      temperature: 0.7
      top_p: 0.85
      repetition_penalty: 1.05
      max_new_tokens: 320
      seed: 10044
    
    instruct: |
      An elderly Chinese male in his late 60s with a deep, gravelly baritone voice.
      Calm, knowing, and measured, with slow, deliberate pacing.
      Speaks standard Mandarin with an unhurried, philosophical quality.
      Each sentence carries the weight of experience, with rich overtones and a slight roughness that hints at decades of smoking and wisdom.

  - id: narrator
    name_zh: 旁白
    role: 全局旁白 / 主角内心独白
    
    axes:
      age: 30s
      gender: male
      resonance: mid
      pace: moderate
      pitch_trend: flat with subtle scene adaptation
    
    params:
      temperature: 0.7
      top_p: 0.85
      repetition_penalty: 1.05
      max_new_tokens: 320
      seed: 10045
    
    instruct: |
      A neutral Chinese male narrator in his 30s with a clear, professional voice.
      Calm, balanced, and atmospheric, with a moderate pace and subtle emotional coloring.
      Speaks standard Mandarin with the gravitas of a documentary narrator, neither too fast nor too slow.
      Tone adapts slightly to scene mood: mysterious for tense moments, warm for tender scenes.
    
    # 情绪变体
    variants:
      tense:
        instruct: |
          A neutral Chinese male narrator in his 30s with a clear, professional voice.
          Tense and mysterious, with a measured pace and slightly hushed delivery.
          Speaks standard Mandarin with restrained urgency, lower volume.
          The delivery suggests something is being revealed that should not be said aloud.
        seed: 10045
      tender:
        instruct: |
          A neutral Chinese male narrator in his 30s with a clear, professional voice.
          Warm and gentle, with a soft pace and tender emotional coloring.
          Speaks standard Mandarin with intimate warmth, as if speaking to a close friend.
          The delivery is hopeful but bittersweet, like remembering a beautiful past.
        seed: 10045

# ============================================================================
# 全局 BGM/角色协调检查
# ============================================================================
coordination:
  bgm_conflicts:
    - bgm: s_unease
      conflicts_with: [cafe_boss]
      reason: 老板深胸声与 BGM 低频冲突
      solution: 对白时 BGM 降到 30% 音量

  character_differentiation:
    - qiu_suwan vs cafe_boss:
        diff_axes: [age, gender, resonance, pitch_trend]
        overlap_axes: [pace]
        verdict: ✅ 区分明显
    - narrator vs qiu_suwan:
        diff_axes: [age, gender, emotion_baseline]
        overlap_axes: [resonance]
        verdict: ✅ 区分明显

# ============================================================================
# 注释
# ============================================================================
notes:
  - "所有角色 seed 跨场景固定，不漂移"
  - "变体共享 seed，确保音色稳定"
  - "主对话角色 10042-10044 间隔 1，方便记忆"
  - "第一幕到真结局用同一组 seed，玩家会潜意识感到'一直是同一个人'"
```
