# gas-guide.md

> 来源：CC Studio unreal-specialist
> 关联：unreal-scripting SKILL.md §GAS 系统深入

## GAS 是什么

Gameplay Ability System（GAS）是 UE 官方提供的技能框架，用于构建 RPG/FPS/MOBA 等需要复杂技能逻辑的游戏。它处理技能激活、属性修改、Buff/Debuff、冷却、消耗、网络复制等全部流程。

---

## 核心组件

| 组件 | 职责 | 挂载位置 |
|------|------|---------|
| **UAbilitySystemComponent (ASC)** | 技能管理器：Grant/Activate/Remove 技能 | PlayerState 或 Character |
| **UAttributeSet** | 属性容器：HP/MP/攻击力等数值 | ASC 所在 Actor |
| **UGameplayAbility** | 单个技能实现 | ASC 管理 |
| **UGameplayEffect** | 属性修改效果（即时/持续/无限） | 由技能 Apply |
| **UGameplayCue** | 视觉/音频反馈（粒子特效、音效） | GameplayCueManager |

---

## 创建步骤

### Step 1：ASC 挂载

```cpp
// PlayerState 中（多人游戏推荐）
UCLASS()
class AMyPlayerState : public APlayerState
{
    GENERATED_BODY()

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;
};
```

```cpp
// 单机 / 简单项目可直接挂 Character
AMyCharacter::AMyCharacter()
{
    AbilitySystemComponent = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("ASC"));
}
```

### Step 2：创建 AttributeSet

```cpp
UCLASS()
class UCombatAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Health)
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UCombatAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_MaxHealth)
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UCombatAttributeSet, MaxHealth)

    UFUNCTION()
    void OnRep_Health(const FGameplayAttributeData& OldHealth);
};
```

### Step 3：实现 GameplayAbility

```cpp
void UGA_Attack::ActivateAbility(...)
{
    // 1. 检查成本/冷却
    if (!CommitAbility(Handle, ActorInfo, ActivationInfo))
    {
        EndAbility(Handle, ActorInfo, ActivationInfo, true, false);
        return;
    }

    // 2. 播放动画（PlayMontageAndWait — WaitTargetData — ApplyEffect）
    UAbilityTask_PlayMontageAndWait* Task = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(
        this, TEXT("Attack"), AttackMontage);
    Task->OnCompleted.AddDynamic(this, &UGA_Attack::OnMontageCompleted);
    Task->ReadyForActivation();
}
```

### Step 4：Apply GameplayEffect

```cpp
// 造成伤害
FGameplayEffectSpecHandle SpecHandle = AbilitySystemComponent->MakeOutgoingSpec(
    DamageEffectClass, 1.0f, AbilitySystemComponent->MakeEffectContext());
SpecHandle.Data.Get()->SetSetByCallerMagnitude(
    FGameplayTag::RequestGameplayTag("Data.Damage"), AttackPower);
AbilitySystemComponent->ApplyGameplayEffectSpecToTarget(
    *SpecHandle.Data.Get(), TargetASC);
```

---

## GameplayTags 权限控制

```cpp
UPROPERTY(EditDefaultsOnly, Category = "Ability")
FGameplayTag ActivationTag;      // Ability.InputTag.Primary

UPROPERTY(EditDefaultsOnly, Category = "Ability")
FGameplayTagContainer BlockedBy; // State.Stunned / State.Dead

// 激活前检查：ASC->HasMatchingGameplayTag(BlockedBy) → 阻止
```

---

## 完整攻击技能示例

```
1. TryActivateAbilityByTag(Ability.InputTag.Attack)
2.   ├── CanActivate? (Cost / Cooldown / NOT BlockedBy)
3.   ├── CommitAbility (消耗资源 / 进入冷却)
4.   ├── PlayMontageAndWait (播放攻击动画)
5.   ├── WaitTargetData (等待命中检测窗口)
6.   ├── MakeOutgoingSpec (构造伤害 Effect)
7.   ├── ApplyGameplayEffectSpecToTarget (对目标施加)
8.   └── EndAbility
```

---

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| ASC 挂谁？ | 多人需在 PlayerState | 单机挂 Character，多人挂 PlayerState |
| Client Prediction 错误 | 属性没有 ReplicatedUsing | 加 ReplicatedUsing + OnRep 回调 |
| GameplayEffect 不触发 | 缺少 GameplayEffect 的 Application Requirement | 检查 Effect 的 Policy 和 Tag Requirements |
| 技能无法激活 | BlockedBy Tags 匹配或 Cost 不足 | 调试 ASC->CanActivateAbility() |
| GE 数值不生效 | AttributeSet 未注册到 ASC | ASC->GetOrCreateAttributeSubobject() |
