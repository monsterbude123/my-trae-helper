# 七、音频系统详解

## 7.1 BGM

```webgal
bgm:music.mp3;                    播放
bgm:other.mp3;                    切换
bgm:none -enter=3000;             淡出停止
bgm:music.mp3 -volume=50;         设置音量（同路径不打断）
bgm:music.mp3 -enter=3000;        淡入播放
```

## 7.2 语音（vocal）

```webgal
角色名:对话 -voice.wav;            简化写法
角色名:对话 -vocal=voice.wav;      完整写法
角色名:对话 -vocal=voice.wav -volume=50;
```

## 7.3 效果音

```webgal
playEffect:effect.wav;            播放一次
playEffect:effect.wav -id=loop1;  循环播放
playEffect:none -id=loop1;        停止循环
playEffect:effect.wav -volume=60;
```

## 7.4 音频鉴赏

```webgal
unlockBgm:music.mp3 -name=曲名 -series=系列名;
```
