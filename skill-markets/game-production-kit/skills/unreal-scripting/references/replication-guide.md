# replication-guide.md

> 来源：CC Studio unreal-specialist
> 关联：unreal-scripting SKILL.md §网络复制

## 网络模式

| 模式 | 说明 | 用途 |
|------|------|------|
| **Standalone** | 无网络，单进程 | 单机游戏、本地测试 |
| **Server** | 专用服务器（无渲染） | 生产环境多人游戏 |
| **Client** | 连接服务器的客户端 | 玩家端 |
| **Listen Server** | 一个客户端同时是服务器 | 小型合作 / P2P |

选择：大型多人 → Dedicated Server；小型合作 → Listen Server。

---

## Replication 基础

### 开启复制

```cpp
// Character 默认开启
AMyCharacter::AMyCharacter()
{
    bReplicates = true;
}
```

### 标记属性

```cpp
UPROPERTY(Replicated)
float CurrentHP;

UPROPERTY(ReplicatedUsing = OnRep_PlayerName)
FString PlayerName;

UFUNCTION()
void OnRep_PlayerName();
```

### 注册生命周期

```cpp
void AMyCharacter::GetLifetimeReplicatedProps(
    TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(AMyCharacter, CurrentHP);
    DOREPLIFETIME_CONDITION(AMyCharacter, PlayerName, COND_InitialOnly);
}
```

常用条件：COND_InitialOnly（仅初始同步）、COND_OwnerOnly（仅拥有者）、COND_SkipOwner。

---

## RPC（Remote Procedure Call）

| 类型 | 调用方 | 执行方 | 用途 |
|------|--------|--------|------|
| **Server** | Client | Server | 请求服操作：攻击、拾取 |
| **Client** | Server | Owning Client | 推送反馈：命中确认、UI 提示 |
| **NetMulticast** | Server | 所有 Client | 广播事件：爆炸、全局公告 |

```cpp
// Server RPC — 客户端发起，服务器执行
UFUNCTION(Server, Reliable)
void Server_DoAttack(AActor* Target);

// 实现文件
void AMyCharacter::Server_DoAttack_Implementation(AActor* Target)
{
    // 验证调用者合法性
    // 执行攻击逻辑（Server Authoritative）
}

// Client RPC — 服务器推送到拥有者客户端
UFUNCTION(Client, Reliable)
void Client_OnDamageReceived(float Damage, AActor* Attacker);
```

### Reliability

| 类型 | 保证 | 适用 |
|------|------|------|
| **Reliable** | 一定到达，有序 | 伤害、拾取、状态变更 |
| **Unreliable** | 可能丢失 | 位置同步、视觉反馈 |

大多数 Gameplay RPC 应使用 Reliable。

---

## Client Prediction

Movement Component 自带 Client Prediction：客户端先移动 → 服务器校验 → 不匹配时回退。

```cpp
// Character Movement 预测（UE 内置）
// 无需手动实现，UCharacterMovementComponent 已处理
// 前提：bReplicates = true
```

自定义预测需实现：
1. 客户端立即执行（模拟）
2. 发送 Server RPC
3. 服务器验证并执行
4. 不匹配时 Corretion（客户端回退）

---

## 网络相关性

```cpp
// Net Cull Distance — 超出距离不复制
UPROPERTY(EditDefaultsOnly, Category = "Replication")
float NetCullDistanceSquared = 225000000.0f; // 15000 units

// Always Relevant — 始终复制（慎用）
bAlwaysRelevant = false; // 默认，让距离裁剪生效

// 自定义相关性
virtual bool IsNetRelevantFor(
    const AActor* RealViewer,
    const AActor* ViewTarget,
    const FVector& SrcLocation) const override;
```

---

## 示例：角色位置同步

```
服务器端（Server Authoritative）:
  1. Character Movement Component 在 Server 执行移动
  2. 自动复制 Location/Rotation/Velocity 到客户端
  3. 客户端收到后插值到目标位置（SimulatedProxy）

客户端:
  1. 本地输入 → 本地 Movement Component 立即移动（预测）
  2. 发送 Move RPC 到服务器
  3. 服务器校验 → 不匹配时发送 Correction

代码层面：
  - UCharacterMovementComponent::bReplicates = true（默认）
  - 无需额外代码，UE 内置网络移动
```

### 自定义网络移动要点

```
[Server] 拥有 Actor Authoritative 状态
   ├── Movement 计算（Tick）
   ├── Replicated: Location, Rotation
   └── 必要时 NetMulticast RPC 播放动画

[Client] AutonomousProxy → 本地预测
[Client] SimulatedProxy → 服务器复制的插值位置
```

---

## 调试

```cpp
// 控制台命令
net.RepGraph.LogAll 1           // 查看复制图
stat net                        // 网络统计
p.NetShowCorrections 1          // 可视化位置修正
```
