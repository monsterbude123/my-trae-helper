# 四、条件判断详解

## 4.1 通用参数 `-when`

任何命令均可使用 `-when=条件表达式` 来控制是否执行：

```webgal
changeScene:1.txt -when=a>1;
jumpLabel:next -when=score>=10;
```

## 4.2 比较运算符

| 运算符 | 说明 |
|:---|:---|
| `>` | 大于 |
| `<` | 小于 |
| `>=` | 大于等于 |
| `<=` | 小于等于 |
| `==` | 等于 |
| `!=` | 不等于 |
| `==true` | 布尔为真 |
| `==false` | 布尔为假 |
| `&&` | 逻辑与 |
| `||` | 逻辑或 |

**注意**：`=` 是赋值符号，不可用于条件判断。

## 4.3 条件跳转

```webgal
setVar:score=2;
jumpLabel:scoreHigh -when=score>1;
角色A:分数不足时会看到这里。;
jumpLabel:scoreEnd;
;
label:scoreHigh;
角色A:分数大于 1，跳转成功。;
;
label:scoreEnd;
```

## 4.4 `choose` 条件语法

- `(条件表达式)`：控制选项是否**显示**
- `[条件表达式]`：控制选项是否**可点击**

```webgal
choose:(hasTicket==true)->出示门票:ticket|(doorPower>0)[doorPower>1]->强行开门:force|回家:home;
```

## 4.5 级联 `if` 写法

WebGAL 支持多行 `if` 级联（无需 else 分支），从上到下依次求值：

```webgal
if:clueCount>=4 && choseRepair==true:callScene:ending_true.txt;
if:clueCount>=4:callScene:ending_normal.txt;
if:clueCount<4:callScene:ending_bad.txt;
```

这种写法是 WebGAL 的标准模式，等价于 if-else if-else 链。
