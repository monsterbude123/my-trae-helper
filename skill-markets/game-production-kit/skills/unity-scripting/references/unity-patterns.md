# Unity 核心脚本模式

> 来源：CC Studio unity-specialist
> 关联：unity-scripting SKILL.md §核心脚本模式索引

## §1 角色数据 ScriptableObject

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "CharacterData", menuName = "VN/Character Data")]
public class CharacterData : ScriptableObject
{
    public string characterId;
    public string displayName;

    [TextArea(2, 5)]
    public string want;       // 驱动目标
    [TextArea(2, 5)]
    public string fear;       // 核心恐惧

    public int hp = 100;
    public int attackPower = 10;
    public Sprite[] portraits; // 面孔：默认/喜/怒/哀/惊
}
```

**使用**: 在 Project 窗口右键 `Create → VN → Character Data`，填写数据后拖入 MonoBehaviour 的 `CharacterData` 字段。数据与逻辑分离，无需硬编码。

## §2 对话系统（UniTask 异步）

```csharp
using Cysharp.Threading.Tasks;
using TMPro;
using UnityEngine;

public class DialogueManager : MonoBehaviour
{
    public static DialogueManager Instance { get; private set; }

    [SerializeField] private TMP_Text dialogueText;
    [SerializeField] private float charsPerSecond = 40f;

    void Awake() => Instance = this;

    public async UniTask ShowDialogue(CharacterData character, string text)
    {
        dialogueText.text = "";
        string speaker = character != null ? character.displayName : "???";
        string fullText = $"<b>{speaker}</b>: {text}";

        for (int i = 0; i < fullText.Length; i++)
        {
            dialogueText.text += fullText[i];
            await UniTask.Delay((int)(1000f / charsPerSecond));
        }
        // 等待玩家确认
        await UniTask.WaitUntil(() => Input.GetMouseButtonDown(0));
    }
}
```

**模式**: Singleton + await 驱动 → 链式对话流 (`await ShowDialogue(alice, "你好"); await ShowDialogue(bob, "你好");`)。

## §3 新 Input System

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class InputHandler : MonoBehaviour
{
    private GameInput inputActions;

    void Awake()
    {
        inputActions = new GameInput();
        inputActions.Gameplay.Confirm.performed += OnConfirm;
        inputActions.Gameplay.Cancel.performed  += OnCancel;
    }

    void OnEnable()  => inputActions.Enable();
    void OnDisable() => inputActions.Disable();

    private void OnConfirm(InputAction.CallbackContext ctx)
        => Debug.Log("确认键按下");

    private void OnCancel(InputAction.CallbackContext ctx)
        => Debug.Log("取消键按下");
}
```

> 完整配置见 `references/input-system-guide.md`。

## §4 Addressables 异步加载

```csharp
using UnityEngine;
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;

public class AssetLoader : MonoBehaviour
{
    public async UniTask<Sprite> LoadPortrait(string key)
    {
        var handle = Addressables.LoadAssetAsync<Sprite>(key);
        await handle.Task;
        if (handle.Status == AsyncOperationStatus.Succeeded)
            return handle.Result;
        Debug.LogError($"加载失败: {key}");
        return null;
    }

    void OnDestroy()
    {
        // Release 由各持有方负责，避免全局 Release
    }
}
```

**要点**: 用 `UniTask` await handle，非协程。Release 在生命期结束时调用，避免内存泄漏。

> 完整 Addressables 指南见 `references/addressables-guide.md`。
