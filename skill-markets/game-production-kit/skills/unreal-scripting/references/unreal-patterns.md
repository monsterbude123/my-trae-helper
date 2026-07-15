# unreal-patterns.md

> 来源：CC Studio unreal-specialist
> 关联：unreal-scripting SKILL.md §核心模式索引

## §1 角色数据资产（UPrimaryDataAsset）

UPrimaryDataAsset 是 UE 的数据驱动核心，用于定义角色静态属性，方便设计师在编辑器中直接编辑。

```cpp
UCLASS(BlueprintType)
class UCharacterData : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, Category = "Identity")
    FText CharacterName;

    UPROPERTY(EditDefaultsOnly, Category = "Identity")
    FText Want;   // 角色内在动机

    UPROPERTY(EditDefaultsOnly, Category = "Identity")
    FText Fear;   // 角色深层恐惧

    UPROPERTY(EditDefaultsOnly, Category = "Stats")
    float MaxHP = 100.0f;

    UPROPERTY(EditDefaultsOnly, Category = "Stats")
    float AttackPower = 10.0f;

    UPROPERTY(EditDefaultsOnly, Category = "Abilities")
    TArray<TSubclassOf<UGameplayAbility>> AbilityList;

    UPROPERTY(EditDefaultsOnly, Category = "Visuals")
    TObjectPtr<UTexture2D> FacePortrait;
};
```

在 Blueprint 中右键 → Miscellaneous → Data Asset → 选 CharacterData 类即可创建实例。

## §2 Gameplay Tags 状态标识

FGameplayTag 是层级标签系统，用于标记角色状态、技能属性、对话分支条件。

```cpp
// 标签容器 — 挂载在 Actor/Component 上
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tags")
FGameplayTagContainer ActiveStateTags;

// 条件判断
bool bIsHostile = ActiveStateTags.HasTag(
    FGameplayTag::RequestGameplayTag("State.Hostile"));

// 逻辑运算：HasAny / HasAll / HasAnyExact
bool bCanTalk = ActiveStateTags.HasAll(
    FGameplayTagContainer::CreateFromArray({
        FGameplayTag::RequestGameplayTag("State.Alive"),
        FGameplayTag::RequestGameplayTag("State.Calm")
    }));
```

层级命名约定：`Category.SubCategory.Value`，如 `State.Emotion.Angry`、`Ability.Type.Melee`。

## §3 对话系统（Dialogue Component）

Dialogue Component 封装对话显示逻辑，挂载在任意 AActor 上，通过 BP Callable 函数供 Blueprint 调用。

```cpp
UCLASS(ClassGroup = "Dialogue", meta = (BlueprintSpawnableComponent))
class UDialogueComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Dialogue")
    void ShowDialogue(
        const FText& SpeakerName,
        const FText& DialogueText,
        UTexture2D* Portrait = nullptr);

    UFUNCTION(BlueprintCallable, Category = "Dialogue")
    void HideDialogue();

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnDialogueFinished);
    UPROPERTY(BlueprintAssignable)
    FOnDialogueFinished OnDialogueFinished;
};
```

使用方式：在角色 Blueprint 中 Add Component → DialogueComponent，通过 Event Graph 调用 ShowDialogue/HideDialogue。

## §4 GAS 技能系统

Gameplay Ability System 是 UE 官方技能框架，核心类：

- **UGameplayAbility** — 单个技能的 C++/BP 实现
- **UAbilitySystemComponent** — 技能管理器，挂载在 Owner Actor 上
- **UGameplayEffect** — 属性修改效果（伤害/治疗/Buff）

```cpp
UCLASS()
class UGA_MeleeAttack : public UGameplayAbility
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, Category = "Attack")
    FGameplayTag AttackTypeTag;

    UPROPERTY(EditDefaultsOnly, Category = "Attack")
    TSubclassOf<UGameplayEffect> DamageEffect;

    virtual void ActivateAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayAbilityActivationInfo ActivationInfo,
        const FGameplayEventData* TriggerEventData) override;
};
```

技能激活流程：GrantAbility → 检查 Cooldown/Cost → Activate → PlayMontageAndWait → ApplyEffect → EndAbility。

## §5 网络复制

UE 网络基础依赖三个核心机制：

```cpp
// 1. UPROPERTY 标记复制
UPROPERTY(Replicated)
float CurrentHP;

// 2. 注册生命周期
virtual void GetLifetimeReplicatedProps(
    TArray<FLifetimeProperty>& OutLifetimeProps) const override
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyCharacter, CurrentHP);
}

// 3. RPC
UFUNCTION(Server, Reliable)
void Server_DoAttack(AActor* Target);

UFUNCTION(Client, Reliable)
void Client_OnHitConfirmed(float Damage);
```

Server RPC 从客户端发起调用、在服务器执行；Client RPC 由服务器推送到客户端；NetMulticast 向所有客户端广播。

## §6 Blueprint ↔ C++ 决策

| 条件 | 选 Blueprint | 选 C++ |
|------|-------------|--------|
| 图形节点数 | ≤ 20 | > 20 |
| 数据类型 | 编辑器可配置变量 | 复杂结构体/算法 |
| 数学要求 | 简单加减 | 向量运算、插值、物理 |
| 网络 | 不涉及 | 复制、RPC、预测 |
| Tick | 无/简单 | 每帧执行的重逻辑 |
| 性能热点 | 事件驱动的一次性调用 | 频繁调用路径 |

桥接函数：

- **BlueprintNativeEvent** — C++ 有默认实现，BP 可选择重写
- **BlueprintImplementableEvent** — C++ 无实现，完全由 BP 提供

```cpp
UFUNCTION(BlueprintNativeEvent, Category = "Dialogue")
void OnDialogueStarted();
// C++ 实现: void AMyActor::OnDialogueStarted_Implementation() { ... }
```
