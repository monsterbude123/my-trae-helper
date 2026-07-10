# 九、config.txt 配置项参考

文件位置：`game/config.txt`（或游戏根目录）。

## 9.1 配置项列表

| 配置项 | 描述 | 示例 |
|:---|:---|:---|
| `Game_name` | 游戏名称 | `Game_name:WebGAL;` |
| `Game_key` | 游戏识别码（6-10 字符，不重复） | `Game_key:0f33fdGr;` |
| `Title_img` | 标题图片（放 `background/`） | `Title_img:Title.png;` |
| `Title_bgm` | 标题背景音乐（放 `bgm/`） | `Title_bgm:夏影.mp3;` |
| `Game_Logo` | 游戏 Logo（可用 `\|` 分割多个） | `Game_Logo:logo1.png\|logo2.png;` |
| `Enable_Appreciation` | 启用鉴赏（CG/BGM） | `Enable_Appreciation:true;` |
| `Default_Language` | 默认语言 | `'zh_CN'`/`'zh_TW'`/`'en'`/`'ja'`/`'fr'`/`'de'` |
| `Show_panic` | 紧急回避功能 | `Show_panic:true;` |
| `Legacy_Expression_Blend_Mode` | Live2D 旧表情混合模式 | `Legacy_Expression_Blend_Mode:true;` |
| `Max_line` | 文本框最大显示行数 | `Max_line:3;` |
| `Line_height` | 文本框行高（em） | `Line_height:2.2;` |
| `Steam_AppID` | Steam 应用 ID | `Steam_AppID:480;` |
| 自定义变量 | 如 `version:1;` | 可在脚本中通过 `(version)` 访问 |

## 9.2 语言切换

```webgal
setVar:lang=($userData.optionData.language);
changeScene:start_zh.txt -when=lang==0;
changeScene:start_en.txt -when=lang==1;
changeScene:start_ja.txt -when=lang==2;
```
