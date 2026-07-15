# UI Toolkit 运行时 UI 指南

> 来源：CC Studio unity-specialist
> 关联：unity-scripting SKILL.md §详细参考

UI Toolkit 是 Unity 推荐的运行时 UI 框架，基于 Web 范式（XML+CSS），替代 uGUI 和 IMGUI。

## 三框架对比

| 特性 | UI Toolkit | uGUI (Canvas) | IMGUI |
|------|-----------|--------------|-------|
| 范式 | UXML + USS | Prefab + Serialized | 纯代码 `OnGUI()` |
| 样式复用 | USS 样式表 | Prefab Variant | 无 |
| 数据绑定 | `BindingPath` 原生 | 需手写 | 无 |
| 性能 | GPU 合批 | Canvas Batch | CPU 重绘 |
| 编辑器/运行时 | 双模式共用 | 仅运行时 | 仅编辑器 |
| 推荐场景 | **生产项目运行时 UI** | 简单覆盖层 | 编辑器工具 |

## 三元组结构

```
DialogueUI.uxml    ← 布局（XML）
DialogueUI.uss     ← 样式（CSS-like）
DialogueUI.cs      ← 逻辑
```

**UXML**:
```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements">
    <ui:VisualElement name="dialogue-box" class="panel">
        <ui:Image name="portrait" />
        <ui:Label name="speaker-name" text="???" />
        <ui:Label name="dialogue-text" text="" />
        <ui:VisualElement name="choices">
            <ui:Button name="choice-0" text="选项A" />
            <ui:Button name="choice-1" text="选项B" />
        </ui:VisualElement>
    </ui:VisualElement>
</ui:UXML>
```

**USS**:
```css
.panel {
    position: absolute;
    bottom: 0;
    height: 200px;
    background-color: rgba(0,0,0,0.8);
}

#dialogue-text {
    font-size: 18px;
    color: white;
    -unity-font: url("project://database/Assets/Fonts/NotoSansSC SDF.asset");
}
```

## 运行时 UI 构建

挂 `UIDocument` 组件到 Canvas GameObject，指定 PanelSettings 和 VisualTreeAsset：

```csharp
using UnityEngine;
using UnityEngine.UIElements;

public class DialogueUI : MonoBehaviour
{
    private UIDocument doc;
    private Label dialogueText;
    private Image portrait;
    private VisualElement choices;

    void Awake()
    {
        doc = GetComponent<UIDocument>();
        var root = doc.rootVisualElement;
        dialogueText = root.Q<Label>("dialogue-text");
        portrait     = root.Q<Image>("portrait");
        choices      = root.Q<VisualElement>("choices");
    }

    public void ShowDialogue(string speaker, string text, Sprite face)
    {
        dialogueText.text = text;
        root.Q<Label>("speaker-name").text = speaker;
        portrait.sprite = face;
    }

    public void ShowChoices(string[] options, Action<int> onSelect)
    {
        choices.Clear();
        for (int i = 0; i < options.Length; i++)
        {
            int idx = i;
            var btn = new Button(() => onSelect(idx));
            btn.text = options[i];
            choices.Add(btn);
        }
    }
}
```

## 数据绑定

```xml
<ui:Label name="speaker" text="" binding-path="SpeakerName" />
<ui:Label name="dialogue" text="" binding-path="DialogueText" />
```

```csharp
// 使用 SerializedObject 自动同步
var data = new DialogueData { SpeakerName = "Alice", DialogueText = "你好" };
rootVisualElement.dataSource = data;
// 修改 data.SpeakerName → UI 自动更新
```

> 详细绑定模式见 `BindingSourceAsset` + `SerializedObject` 组合。

## TextMeshPro 集成

UI Toolkit 原生支持 TextMeshPro：

1. **字体**. 创建 `Font Asset`（SDF），放入 `Assets/Fonts/`
2. **USS 引用**. `-unity-font: url("project://database/Assets/Fonts/MyFont SDF.asset");`
3. **多语言**. 每个语言一个 Font Asset（含不同字符集），USS 切换字体 URL

```css
.LangZH { -unity-font: url("project://database/Assets/Fonts/NotoSansSC SDF.asset"); }
.LangJP { -unity-font: url("project://database/Assets/Fonts/NotoSansJP SDF.asset"); }
```

## 示例：对话 UI 完整流程

```
1. 创建 DialogueUI.uxml（布局） → 面板 + 头像 + 文本 + 选项
2. 创建 DialogueUI.uss（样式） → 背景色/字号/位置
3. 挂 UIDocument 组件，指定 PanelSettings + VisualTreeAsset
4. 写 DialogueUI.cs 脚本，Awake() 中 Q<> 查询元素
5. 调用 ShowDialogue() + ShowChoices() 控制显示
```

> 编辑器模式下 `Window → UI Toolkit → UI Builder` 可视化编辑 UXML/USS。
