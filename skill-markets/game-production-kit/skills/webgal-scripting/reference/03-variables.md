# 三、变量系统详解

## 3.1 变量类型

支持三种值类型：
- **数字**：`15`、`5e3`、`-5.5`
- **布尔值**：`true` / `false`
- **字符串**：无法识别为数字或布尔值的均转换为字符串

## 3.2 变量运算

支持基本四则运算：`+` `-` `*` `/`

```webgal
setVar:score=10;
setVar:score=score+5;
setVar:score=score*2;
```

`=` 是赋值，`==` 是相等比较（不可混用）。

## 3.3 局部变量 vs 全局变量

| 类型 | 作用域 | 命令 |
|:---|:---|:---|
| 普通变量 | 当前场景（存档/读档保存恢复） | `setVar:变量名=值;` |
| 长效变量 | 整个游戏（除非用户清空数据） | `setVar:变量名=值 -global;` |

## 3.4 随机数

```webgal
setVar:a=random();           0-1 浮点数
setVar:a=random(5,10);       5-10 整数
setVar:a=random(5,10,true);  5-10 浮点数
```

## 3.5 内置变量域

- `$stage`：运行时内置变量（可在编辑器 state 选项卡查看）
- `$userData`：存档内置变量（可在 indexedDB 查看）
- 配置变量直接通过变量名访问：`(Game_name)`

内置变量访问示例（`>=4.5.4`）：

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

## 3.6 变量插值

```webgal
setVar:name=WebGAL;
WebGAL:欢迎使用 {name}！;
{name}:我也最喜欢 WebGAL 了！;  角色名也可用插值
```
