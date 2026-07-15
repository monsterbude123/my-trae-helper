# Unity Input System 使用指南

> 来源：CC Studio unity-specialist
> 关联：unity-scripting SKILL.md §详细参考

Input System 是 Unity 的官方替换，替代旧 `Input` 类，支持跨平台输入抽象和运行时重绑定。

## .inputactions 文件结构

在 Project 窗口 `Create → Input Actions` 生成 `.inputactions` 文件。三层架构：

```
GameInput.inputactions
├── Gameplay (Action Map)
│   ├── Move (Action) → WASD / Left Stick
│   ├── Confirm (Action) → Enter / Button South
│   ├── Cancel (Action) → Escape / Button East
│   └── Skip (Action) → Space / Button North
├── UI (Action Map)
│   ├── Navigate
│   ├── Submit
│   └── Cancel
└── Dialog (Action Map)
    └── Advance (Action) → Mouse Left / Touch Tap
```

**Action Maps** = 上下文分组（Gameplay 时不触发 UI 输入）  
**Actions** = 具体输入动作  
**Bindings** = 按键/设备绑定（一个 Action 可多个 Binding）

## C# 代码生成

在 `.inputactions` 的 Inspector 勾选 `Generate C# Class` → 生成强类型包装：

```csharp
private GameInput input;

void Awake()
{
    input = new GameInput();
    input.Gameplay.Confirm.performed += OnConfirm;
    input.Gameplay.Move.performed  += OnMove;
    input.Gameplay.Move.canceled   += OnMoveStop;
}

void OnEnable()  => input.Enable();
void OnDisable() => input.Disable();

private void OnMove(InputAction.CallbackContext ctx)
{
    Vector2 dir = ctx.ReadValue<Vector2>();
    // 角色移动
}

private void OnMoveStop(InputAction.CallbackContext ctx)
{
    // dir = Vector2.zero，停止移动
}
```

## PlayerInput 组件

挂 `PlayerInput` 组件到 GameObject，可选两种通知模式：

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `Invoke Unity Events` | Inspector 拖拽绑定回调 | 快速原型、简单项目 |
| `Invoke C Sharp Events` | 代码订阅 `onActionTriggered` | 生产项目、灵活控制 |
| `Send Messages` | 反射调用 `OnMove()` 等方法 | 不推荐 |

```csharp
// C Sharp Events 模式
var playerInput = GetComponent<PlayerInput>();
playerInput.onActionTriggered += ctx =>
{
    if (ctx.action.name == "Confirm")
        DialogueManager.Instance.OnConfirm();
};
```

## 设备支持

Input System 自动检测设备，无需写平台判断：

- **Keyboard/Mouse**: `W/A/S/D`, `Enter`, `Escape`, `Left Button`
- **Gamepad**: `Left Stick`, `Button South/North/East/West`
- **Touchscreen**: `Primary Touch`
- **Pen/XR**: 同框架支持

多个 Binding 绑定同一 Action，自动适配当前设备。

## 示例：角色移动 + 确认/取消

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private float speed = 5f;
    private GameInput input;
    private Vector2 moveInput;

    void Awake() => input = new GameInput();

    void OnEnable()
    {
        input.Enable();
        input.Gameplay.Move.performed  += ctx => moveInput = ctx.ReadValue<Vector2>();
        input.Gameplay.Move.canceled   += ctx => moveInput = Vector2.zero;
        input.Gameplay.Confirm.performed += ctx => OnInteract();
        input.Gameplay.Cancel.performed  += ctx => OnCancel();
    }

    void OnDisable() => input.Disable();

    void Update() => transform.Translate(moveInput * speed * Time.deltaTime);

    void OnInteract() => Debug.Log("交互！");
    void OnCancel()   => Debug.Log("取消！");
}
```

> 运行时重绑定 API → Unity 官方文档 `InputActionRebindingExtensions`。
