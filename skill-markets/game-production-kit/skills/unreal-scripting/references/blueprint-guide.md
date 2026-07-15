# blueprint-guide.md

> 来源：CC Studio unreal-specialist
> 关联：unreal-scripting SKILL.md §Blueprint 使用原则

## Blueprint 类型

| 类型 | 用途 | 何时用 |
|------|------|--------|
| **Blueprint Class** | 继承 C++ 或纯 BP 的 Actor/Component/Widget | 需要实例化的游戏对象 |
| **Data-Only Blueprint** | 仅修改父类 UPROPERTY 默认值，无图表逻辑 | 创建角色/武器变体 |
| **Blueprint Macro** | 可复用的节点组，支持输入输出引脚 | 重复逻辑片段（< 10 节点） |
| **Blueprint Function Library** | 全局静态函数集合 | 工具函数，无状态 |

---

## ✅ 适合 Blueprint

### 事件响应链

```
OnInteract → PlaySound → ShowDialogue → PlayMontage → Delay → HideDialogue
```
事件驱动的线性流程，可视化编辑比 C++ 代码更直观。

### Timeline 动画

Timeline 节点天生适合 Blueprint——可视化时间轴 + 曲线编辑器，用于：
- 门/窗开关动画
- UI 淡入淡出
- 角色表情过渡

### 数据变体

Data-Only Blueprint 零代码创建变体：
```
BP_Enemy_Goblin (DataAsset: EnemyData_Goblin)
BP_Enemy_Orc    (DataAsset: EnemyData_Orc)
```

### UI 快速原型

UMG Widget 的事件绑定 + 视觉反馈在 BP 中快速迭代。

---

## ❌ 应转为 C++

| 场景 | 原因 | C++ 替代 |
|------|------|---------|
| 图形 > 20 节点 | 可读性崩溃，难以维护 | 封装为 UFUNCTION(BlueprintCallable) |
| 数学密集计算 | BP 纯计算节点开销大 | C++ 内联函数 |
| 网络复制逻辑 | BP 的 Replication 支持有限 | UPROPERTY(Replicated) + RPC |
| Tick 重逻辑 | BP Tick 每帧执行，开销累积 | C++ 中条件 Tick + SCOPE_CYCLE_COUNTER |
| for-each 大数组 | BP 循环每个元素都有节点开销 | C++ for-range 零开销 |

---

## C++ ↔ BP 桥接

### BlueprintCallable

```cpp
// C++ 实现，BP 可调用
UFUNCTION(BlueprintCallable, Category = "Dialogue")
void ShowDialogue(const FText& Text);
```

### BlueprintNativeEvent

```cpp
// C++ 有默认实现，BP 可重写
UFUNCTION(BlueprintNativeEvent, Category = "Dialogue")
void OnDialogueStarted();
// C++ 实现签名: void OnDialogueStarted_Implementation();
```

### BlueprintImplementableEvent

```cpp
// C++ 无实现，完全由 BP 提供
UFUNCTION(BlueprintImplementableEvent, Category = "Dialogue")
void OnDialogueFinished();
```

---

## 示例：对话显示逻辑（BP 端）

```
事件: ShowDialogue(Text, Portrait)
  │
  ├── Set Visibility: DialogueWidget → Visible
  ├── Set Text: RichTextBlock → Text
  ├── Set Brush: PortraitImage → Portrait
  ├── Timeline: 0.0→1.0 (0.5s) 绑定 Opacity
  │     ├── Track: DialogueWidget.Opacity
  │     └── Curve: 0→1 Ease In
  ├── Wait: Timeline Finished
  ├── 等待玩家输入 (InputAction Advance)
  └── Timeline: 1.0→0.0 (0.3s) → Hide
```

此流程约 12 节点，在阈值内，适合保持为 Blueprint。
