# 五、场景管理详解

## 5.1 场景文件

- 入口：`scene/start.txt`（必须存在，不可重命名）
- 场景文件命名：英文，用 `/` 分割子目录
- 场景切换后，当前场景后续语句不再执行

## 5.2 `changeScene` vs `callScene`

| 命令 | 行为 | 返回 |
|:---|:---|:---|
| `changeScene:文件.txt;` | 切换场景 | 不返回 |
| `callScene:文件.txt;` | 调用场景（子场景） | 子场景结束后返回原场景 |

两者都不会自动清除舞台（立绘、背景），需要手动清理。

## 5.3 标签系统

- `label:标签名;` 定义跳转目标
- `jumpLabel:标签名;` 跳转到标签
- `choose:选项:标签名|...;` 分支选择跳转到标签

每个标签在同一场景文件中只能定义**一次**。不同场景文件允许多个同名标签。`choose`/`jumpLabel` 从上往下搜索，跳转到**第一个**匹配。

**分支末尾务必使用 `jumpLabel` 跳出**，否则会线性执行到下一个分支：

```webgal
choose:分支1:label_1|分支2:label_2;
;
label:label_1;
角色A:这是分支1;
jumpLabel:end;
;
label:label_2;
角色A:这是分支2;
jumpLabel:end;
;
label:end;
角色A:分支结束;
```

## 5.4 场景清理范式

切换场景前建议显式清理舞台状态：

```webgal
changeFigure:none -left;
changeFigure:none -right;
changeFigure:none;
changeBg:none;
:;
changeScene:next.txt;
```
