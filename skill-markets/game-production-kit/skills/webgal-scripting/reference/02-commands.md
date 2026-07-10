# 二、命令参考完全列表

## 2.1 对话 `say`

任何无法被识别为命令的行，都会被尝试作为对话命令执行。

**简化语法**：
```webgal
角色名:对话内容;
:旁白内容;  （冒号前留空=旁白）
```

**`say` 命令语法**：
```webgal
say:对话内容 -speaker=角色名;
```

**多行文字**：用 `|` 分割多行。

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `-speaker` | 字符串 | 说话者名称。未填则沿用上一次 |
| `-notend` | 布尔 | 显示完文字后立刻执行下一条命令 |
| `-concat` | 布尔 | 不清空对话框已有文字，新文字接续在后面 |
| `-clear` | 布尔 | 清除说话者（旁白专用） |
| `-vocal` | 字符串 | 配音文件路径（简化写法：直接 `-hello.wav`） |
| `-fontSize` | 字符串 | `small` / `medium` / `large` / `default` |
| `-left` | 布尔 | 驱动左侧立绘张嘴说话 |
| `-right` | 布尔 | 驱动右侧立绘张嘴说话 |
| `-center` | 布尔 | 驱动中间立绘张嘴说话 |
| `-figureId` | 字符串 | 驱动指定 id 立绘张嘴说话 |

**变量插值**：用 `{}` 语法嵌入变量。
```webgal
setVar:name=WebGAL;
{name}:欢迎使用 {engine}！;
```

**注音语法**：`[要注音的词](注音)`

**文本拓展语法**：`[文本](style=color:#66327C\; style-alltext=font-style:italic\;font-size:80%\; ruby=注音)`

## 2.2 对话插入演出（`-notend` / `-concat` 组合）

```webgal
WebGAL:测试语句插演出！马上切换立绘...... -notend;
changeFigure:k1.png -next;
切换立绘！马上切换表情...... -notend -concat;
changeFigure:k2.png -next;
切换表情！ -concat;
```

## 2.3 全屏文字 `intro`

```webgal
intro:第一行文字|第二行文字|第三行文字;
```

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `-fontSize` | 字符串 | — | `small` / `medium` / `large` |
| `-fontColor` | 字符串 | `rgba(0,0,0,1)` | 字体颜色 |
| `-backgroundColor` | 字符串 | `rgba(0,0,0,1)` | 背景颜色 |
| `-backgroundImage` | 字符串 | — | 背景图像路径 |
| `-animation` | 字符串 | `fadeIn` | `fadeIn` / `slideIn` / `typingEffect` / `pixelateEffect` / `revealAnimation` |
| `-delayTime` | 数字(ms) | 1500 | 每行文字显示延迟 |
| `-hold` | 布尔 | false | true 时等待玩家点击才继续 |
| `-userForward` | 布尔 | false | true 时手动点击才显示下一行 |

## 2.4 获取用户输入 `getUserInput`

```webgal
getUserInput:变量名 -title=提示文本 -buttonText=确认;
```

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `-title` | 字符串 | 输入框标题 |
| `-buttonText` | 字符串 | 确认按钮文本 |
| `-defaultValue` | 字符串 | 默认值 |
| `-rule` | 字符串 | 正则校验规则 |
| `-ruleFlag` | 字符串 | 正则标识（如 `g`、`i`） |
| `-ruleText` | 字符串 | 校验失败提示（`$0` 可获取用户输入） |
| `-ruleButtonText` | 字符串 | 校验失败弹窗按钮文本，默认为 `OK` |

## 2.5 切换背景 `changeBg`

```webgal
changeBg:bg.png;          入场/替换背景
changeBg:none;            退场（空字符串同理）
changeBg:bg.png -next;    立刻执行下一条
```

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `-transform` | JSON 字符串 | — | 设置变换效果（仅入场/替换时生效） |
| `-enter` | 字符串 | — | 自定义入场动画名称 |
| `-exit` | 字符串 | — | 自定义退场动画名称 |
| `-duration` | 数字(ms) | 1500 | 作用于默认入场动画 |
| `-enterDuration` | 数字(ms) | 取 duration | 入场动画时长 |
| `-exitDuration` | 数字(ms) | 1500 | 退场动画时长 |
| `-ease` | 字符串 | `easeInOut` | 缓动类型 |
| `-unlockname` | 字符串 | — | CG 鉴赏收录名称 |
| `-series` | 字符串 | — | CG 鉴赏系列名 |

## 2.6 切换立绘 `changeFigure`

立绘入场、替换立绘、立绘退场、设置立绘参数的四合一命令。

```webgal
changeFigure:1/open_eyes.png;                   图片立绘入场
changeFigure:character_a/model.json;             Live2D 立绘入场
changeFigure:character_x/model.json?type=spine;  Spine 立绘入场
changeFigure:none;                               退场（空字符串同理）
```

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `-left` | 布尔 | false | 放置左侧，默认 id=`fig-left` |
| `-right` | 布尔 | false | 放置右侧，默认 id=`fig-right` |
| `-id` | 字符串 | 自动 | 未填时：-left→fig-left, -right→fig-right, 否则→fig-center |
| `-transform` | JSON 字符串 | — | 设置变换效果（仅入场/替换时生效，与 `-enter` 互斥） |
| `-enter` | 字符串 | — | 自定义入场动画 |
| `-exit` | 字符串 | — | 自定义退场动画 |
| `-duration` | 数字(ms) | 300 | 作用于默认入场动画 |
| `-enterDuration` | 数字(ms) | 取 duration | 入场动画时长 |
| `-exitDuration` | 数字(ms) | 450 | 退场动画时长 |
| `-ease` | 字符串 | `easeInOut` | 缓动类型 |
| `-zIndex` | 整数 | 0 | 层级，越大越靠上 |
| `-blendMode` | 字符串 | `normal` | 混合模式（仅入场/替换时生效） |
| `-clear` / `-none` | 布尔 | false | 将语句内容替换为空字符串 |
| `-mouthOpen` | 字符串 | — | 张嘴差分图片路径 |
| `-mouthHalfOpen` | 字符串 | — | 半张嘴差分图片路径 |
| `-mouthClose` | 字符串 | — | 闭嘴差分图片路径 |
| `-eyesOpen` | 字符串 | — | 睁眼差分图片路径 |
| `-eyesClose` | 字符串 | — | 闭眼差分图片路径 |
| `-motion` | 字符串 | — | Live2D/Spine 动作名称 |
| `-expression` | 字符串 | — | Live2D 表情名称 |
| `-skin` | 字符串 | — | Spine 皮肤名称 |
| `-bounds` | number[4] | — | Live2D 显示区域扩展 `左,上,右,下` |
| `-blink` | JSON 字符串 | — | Live2D 眨眼参数 |
| `-focus` | JSON 字符串 | — | Live2D 注视参数 |

立绘路径与 `id` 保持不变时，不会触发出退场动画，直接将新参数应用到目标立绘。

## 2.7 设置变换 `setTransform`

为在场舞台对象设置**单段**动画/变换。

```webgal
setTransform:{"position":{"x":-500},"brightness":0.5} -target=aaa -duration=500;
```

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `-target` | 字符串 | 目标：`fig-center`/`fig-left`/`fig-right`/自由立绘id/`bg-main`/`stage-main` |
| `-duration` | 数字(ms) | 动画持续时间 |
| `-ease` | 字符串 | 缓动类型，默认 `easeInOut` |
| `-writeDefault` | 布尔 | true 时未赋值的属性写入默认值 |
| `-keep` | 布尔 | 转为跨语句动画，需配合 `-next` 使用 |

## 2.8 设置动画 `setAnimation`

调用预定义的动画文件，驱动目标执行**多段**动画。

```webgal
setAnimation:shake -target=aaa;
```

预置动画名：`enter`、`exit`、`shake`、`enter-from-bottom`、`enter-from-left`、`enter-from-right`、`move-front-and-back`、`blur`、`oldFilm`、`dotFilm`、`reflectionFilm`、`glitchFilm`、`rgbFilm`、`godrayFilm`、`removeFilm`、`shockwaveIn`、`shockwaveOut`

参数同 `setTransform`（无 `-duration`、`-ease`）。

## 2.9 设置临时动画 `setTempAnimation`

直接在脚本中定义多段动画，无需动画文件。

```webgal
setTempAnimation:[{"duration":0},{"position":{"x":500},"duration":500},{"rotation":0.3,"duration":300}] -target=aaa;
```

语句内容格式为动画片段的 JSON 数组 `[{},{},...]`。第一个片段 duration 通常设为 0（起始状态）。参数同 `setAnimation`。

## 2.10 设置复杂动画 `setComplexAnimation`

```webgal
setComplexAnimation:universalSoftIn -target=aaa -duration=1000;
```

内置：`universalSoftIn`（透明度淡入）、`universalSoftOff`（透明度淡出）。

## 2.11 设置进出场效果 `setTransition`

覆盖默认的渐变进出场效果：

```webgal
setTransition: -target=fig-center -enter=enter-from-bottom -exit=exit;
```

**注意**：必须在 `changeFigure`/`changeBg` **之后立即连续执行**才能覆盖进场动画。出场动画在对象退场时生效。

## 2.12 背景音乐 `bgm`

播放/切换/停止 BGM 及设置参数的四合一命令。

```webgal
bgm:01.wav;               播放
bgm:02.wav;               切换
bgm:none;                 停止（空字符串同理）
bgm:morning.wav -enter=1500;  淡入播放
bgm:none -enter=3000;      淡出停止
```

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `-volume` | 数字 | 100 | 音量百分比，0-100 |
| `-enter` | 数字(ms) | 0 | 淡入时间 |
| `-unlockname` | 字符串 | — | BGM 鉴赏收录名称 |
| `-series` | 字符串 | — | BGM 鉴赏系列名 |

同一首 BGM 路径不变时，调整参数不会打断播放。

## 2.13 音效 `playEffect`

播放/替换/停止音效的三合一命令。

```webgal
playEffect:rain.wav;             播放
playEffect:rain.wav -id=rain;    循环播放（设 id 自动循环）
playEffect:none -id=rain;        停止指定 id 音效
playEffect:none;                 停止无 id 音效
```

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `-id` | 字符串 | — | 设 id 后音效循环播放；不同 id 和无 id 的音效可叠加 |
| `-volume` | 数字 | 100 | 音量百分比 |

## 2.14 播放视频 `playVideo`

```webgal
playVideo:video.mp4;
playVideo:video.mp4 -skipOff;  不允许跳过
```

## 2.15 分支选择 `choose`

```webgal
choose:选项文本1:跳转目标1|选项文本2:跳转目标2;
```

跳转目标可以是**场景文件**路径或本场景的**标签名**。

**条件展示与启用**：
```webgal
choose:(hasTicket==true)->出示门票:ticket|(doorPower>0)[doorPower>1]->强行开门:force|回家:home;
```

- `(条件)`：控制选项是否**显示**
- `[条件]`：控制选项是否**可点击**
- `->`：分隔条件前缀和选项内容

选择无效的选项（跳转目标不存在）时，引擎继续执行当前场景后续命令。

## 2.16 标签 `label`

```webgal
label:myLabel;
```

每个标签在同一场景文件中只能定义**一次**。`choose` 和 `jumpLabel` 从文件开头往下搜索，跳转到第一个匹配的标签位置。

## 2.17 跳转标签 `jumpLabel`

```webgal
jumpLabel:targetLabel;
jumpLabel:targetLabel -when=score>1;  条件跳转
```

## 2.18 切换场景 `changeScene`

```webgal
changeScene:chapter_01/part_02.txt;
```

成功执行后，**当前场景的后续命令不会被执行**。注意：舞台（立绘、背景）不会被自动清除。

## 2.19 调用场景 `callScene`

```webgal
callScene:chapter_01/shop.txt;
```

临时加载新场景，新场景结束后**回到原场景继续执行**。

## 2.20 设置变量 `setVar`

```webgal
setVar:变量名=值;
setVar:score=10;              数字
setVar:flag=true;             布尔
setVar:name=人物名称;         字符串
setVar:score=score+1;         运算
setVar:a=random();            0-1 随机浮点数
setVar:a=random(5,10);        5-10 随机整数
setVar:a=random(5,10,true);   5-10 随机浮点数
```

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `-global` | 布尔 | true 时设置长效（全局）变量，整个游戏生效，除非用户清除全部数据 |

支持运算符：`+` `-` `*` `/`。`=` 是赋值，`==` 是相等比较。

## 2.21 变量插值

```webgal
setVar:name=WebGAL;
WebGAL:欢迎使用 {name}！;
{name}:我也最喜欢 WebGAL 了！;  角色名也可用插值
```

## 2.22 内置变量访问（`>=4.5.4`）

```webgal
setVar:a=($stage.bgm.volume);     运行时内置变量
setVar:lang=($userData.optionData.language);  存档内置变量
WebGAL:当前 BGM 音量为{$stage.bgm.volume};
```

可修改的配置变量：`Title_img`、`Title_bgm`、`Game_name`、`Game_key`。

```webgal
setVar:Game_name=新标题 -global;  修改配置变量需加 -global
```

也可在 `config.txt` 中自定义配置变量（如 `version:1;`），在脚本中通过 `(变量名)` 读取，使用 `-global` 修改。

## 2.23 显示变量 `showVars`

```webgal
showVars;
```

在对话框中显示所有本地变量与全局变量的值（调试用）。

## 2.24 文本框控制 `setTextbox`

```webgal
setTextbox:hide;   隐藏对话框
setTextbox:on;     恢复显示（hide 以外的任意值均可）
```

此外，使用 **`:;`**（空对话）也可以关闭对话框，下一句对话自动恢复显示。

## 2.25 小头像 `miniAvatar`

```webgal
miniAvatar:character_a/avatar.png;  显示
miniAvatar:none;                    隐藏
```

## 2.26 舞台特效 `pixiInit` / `pixiPerform`

```webgal
pixiInit;                  初始化（也可用于清除所有特效）
pixiPerform:rain;          下雨
pixiPerform:snow;          下雪
pixiPerform:heavySnow;     大雪
pixiPerform:cherryBlossoms; 樱花
```

不重新 `pixiInit` 可直接叠加多种特效。

## 2.27 电影模式 `filmMode`

```webgal
filmMode:on;    开启
filmMode:none;  关闭
```

## 2.28 结束游戏 `end`

```webgal
end;
```

结束当前场景并返回标题页。

## 2.29 等待 `wait`

```webgal
wait:5000;  等待 5 秒（单位：毫秒）
```

## 2.30 解锁 CG `unlockCg`

```webgal
unlockCg:chapter_03/date.png -name=第一次约会 -series=角色B;
```

## 2.31 解锁 BGM `unlockBgm`

```webgal
unlockBgm:s_Title.mp3 -name=Smiling-Swinging!!! -series=系列名;
```

## 2.32 UI 样式切换 `applyStyle`

```webgal
applyStyle:原样式名->新样式名;
applyStyle:Choose_item->Choose_item_Red,TextBox_main->TextBox_main_Black;  多个替换
```

无论替换多少次，始终保持原样式名在 `->` 左侧。

## 2.33 播放语音 `playVocal`

播放角色配音文件（TTS 生成），必须紧跟对应的对话行之后：

```webgal
邱苏晚:你跳过的每一个瞬间，都变成了我的一部分。;
playVocal:v_mist_meet_0001_qiusuwan.flac;
```

| 参数 | 类型 | 说明 |
|:---|:---|:---|
| `-volume` | 数字 | 音量百分比，0-100 |

**避坑**：
- playVocal 必须在对话行**之后**（不是之前），否则先朗读后显示文字
- playVocal **不要加进 if/choose 判定内**——跳跃时语音不会自动播放
- 文件放 `vocal/` 目录（不是 `bgm/`）

## 2.34 Steam 成就 `callSteam`

```webgal
callSteam: -achievementId=ACH_WIN_ONE_GAME;
```

仅 Electron / Steam 构建环境有效。需在 `config.txt` 配置 `Steam_AppID`。
