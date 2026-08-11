---
title: 验收门禁 + 4 维评分 + 通过依据 3 类分层 + DOM 视觉证据
description: 满分硬门禁 + 证据链 + 视觉证据三层校验 + 通过依据分层
layer: fact
---

# 验收门禁 + 4 维评分 + 通过依据 3 类分层 + DOM 视觉证据 Mindmap

> V10.12 验收协议核心: **满分硬门禁（任何非满分 = �� REJECT）+ 视觉证据 3 层校验 + 通过依据 3 类分层**。

## 一、4 维验收硬门禁

```mermaid
mindmap
  root((4 维硬门禁<br/>任一非满分 = REJECT))
    维度 1 代码层 25%
      单元测试全绿
      Contract 测试全绿
      Lint 0 error
      覆盖率 ≥ 90%
      无 TODO/FIXME
      code-hygiene.py 通过
      理解确认 2 项验证
    维度 2 API 层 30%
      真实端点非 mock
      接口签名 100% 一致
      数据模型 100% 一致
      错误码 100% 一致
      事件 100% 一致
    维度 3 UI/UX 层 25%
      Phase A 视觉一致性
      Phase B 交互逻辑
      Phase C UI 细节
      6 项检查清单
    维度 4 模块边际 20%
      GitNexus impact
      下游无副作用
      文档同步
      扩展点标注
    硬门禁
      ✅ 4 维全满分 = PASS
      �� 任一非满分 = REJECT
      �� 禁止 N/A 计入分母
      �� 禁止灰色术语
```

## 二、4 维评分算法

```mermaid
graph LR
    Through[通过维度]
    Total[适用维度]
    Multiply[× 5.0]
    Result[总分]

    Through --> Divide[通过 / 适用]
    Total --> Divide
    Divide --> Multiply
    Multiply --> Result

    Result -->|≥ 4.0| Pass[✅ PASS]
    Result -->|任何维度 0 分| Reject[�� REJECT]
    Result -->|< 4.0| Reject

    classDef step fill:#95e1d3,color:#000
    classDef result fill:#4ecdc4,color:#fff
    classDef fail fill:#ff6b6b,color:#fff
    class Through,Total,Multiply,Divide step
    class Result,Pass result
    class Reject fail
```

## 三、产物证据链（强制）

```mermaid
flowchart TD
    Sub[子代理返回 Completion Report]
    Claim[声称 PASS]
    Evidence[附真实命令输出]
    Cmd[命令存在]
    Exit[退出码 0]
    Output[输出包含预期]

    Sub --> Claim
    Claim -->|强制附| Evidence
    Evidence --> Cmd
    Evidence --> Exit
    Evidence --> Output

    Cmd -->|是| S1[✅]
    Exit -->|是| S2[✅]
    Output -->|是| S3[✅]

    S1 --> Match{3 项全匹配?}
    S2 --> Match
    S3 --> Match

    Match -->|是| Pass[✅ 接受]
    Match -->|否| Reject[�� REJECT<br/>不允许 agent 自报]

    classDef step fill:#95e1d3,color:#000
    classDef pass fill:#4ecdc4,color:#fff
    classDef fail fill:#ff6b6b,color:#fff
    class Sub,Claim,Evidence,Cmd,Exit,Output,Match step
    class S1,S2,S3,Pass pass
    class Reject fail
```

## 四、通过依据 3 类分层（V10.8 NEW）

```mermaid
graph TB
    subgraph Backend[1 后端/编译类<br/>机器可验证]
        B1[tsc --noEmit 0 错误]
        B2[curl /api/v1/... 正确]
        B3[cargo build / test]
        B4[vitest / pytest 全绿]
    end

    subgraph UI[2 UI 渲染类<br/>用户可见 机器可验证]
        U1[Playwright 截图 ≥ 1 张/任务]
        U2[主上下文亲自 Read 抽检]
        U3[视觉验证协议 3 校验]
        U4[verify 描述 vs 实际像素]
    end

    subgraph User[3 用户视角类<br/>必须用户验收]
        Us1[用户亲眼看到效果]
        Us2[用户书面确认 通过]
        Us3[任一闭环用户签字]
    end

    Layer1[主上下文回复<br/>按 3 类分层]
    Layer1 --> Backend
    Layer1 --> UI
    Layer1 --> User

    Backend --> Result1[✅ 通过 / 未跑 / 略]
    UI --> Result2[⚠️ 未跑 / ✅ 通过]
    User --> Result3[⏳ 用户未验收 / 闭环未签字]

    Result1 -->|跑 + OK<br/>未跑 = 标| Check1
    Result2 -->|跑 + Read<br/>未跑 = 标| Check2
    Result3 -->|等用户签字| Check3

    Check1 -->|都 OK| Pass[声明完成]
    Check2 -->|都 OK| Pass
    Check3 -->|都 OK| Pass

    Check1 -->|任一缺| Cannot[❌ 不能声称完成]
    Check2 -->|任一缺| Cannot
    Check3 -->|任一缺| Cannot

    classDef back fill:#95e1d3,color:#000
    classDef ui fill:#ffd93d,color:#000
    classDef user fill:#6bcf7f,color:#000
    classDef pass fill:#4ecdc4,color:#fff
    classDef fail fill:#ff6b6b,color:#fff
    class Backend,B1,B2,B3,B4,Layer1,Result1,Check1 back
    class UI,U1,U2,U3,U4,Result2,Check2 ui
    class User,Us1,Us2,Us3,Result3,Check3 user
    class Pass pass
    class Cannot fail
```

## 五、视觉证据 3 层校验 + 活跃性

```mermaid
graph TB
    Visual[视觉证据<br/>docs/verifications/tauri/*.png]

    Visual --> L1[1 PNG magic number<br/>前 8 字节 == b'\x89PNG\r\n\x1a\n']
    Visual --> L2[2 文件大小 ≥ 5000 bytes]
    Visual --> L3[3 PIL 平均亮度 30-240]
    Visual --> L4[4 文件活跃性 ≤ 7 天]
    Visual --> L5[5 视觉证据目录<br/>docs/verifications/tauri/]

    L1 --> Result1{L1 OK?}
    L2 --> Result2{L2 OK?}
    L3 --> Result3{L3 OK?}
    L4 --> Result4{L4 OK?}
    L5 --> Result5{L5 OK?}

    Result1 -->|否| F1[�� REJECT]
    Result2 -->|否| F2[�� REJECT]
    Result3 -->|否| W1[⚠️ 仅警告]
    Result4 -->|否| F3[�� REJECT]
    Result5 -->|否| F4[�� REJECT]

    Result1 -->|是| P1[✅]
    Result2 -->|是| P2[✅]
    Result3 -->|是| P3[✅]
    Result4 -->|是| P4[✅]
    Result5 -->|是| P5[✅]

    P1 --> Total{全 OK?}
    P2 --> Total
    P3 --> Total
    P4 --> Total
    P5 --> Total

    Total -->|是| Pass[✅ 视觉验证通过]
    Total -->|否| Reject[�� REJECT]

    classDef layer fill:#95e1d3,color:#000
    classDef pass fill:#4ecdc4,color:#fff
    classDef fail fill:#ff6b6b,color:#fff
    classDef warn fill:#ffd93d,color:#000
    class Visual,L1,L2,L3,L4,L5,Result1,Result2,Result3,Result4,Result5,Total layer
    class P1,P2,P3,P4,P5,Pass pass
    class F1,F2,F3,F4,Reject fail
    class W1 warn
```

## 六、UI 细节遗漏检查清单（V10.8 NEW）

```mermaid
mindmap
  root((UI 细节检查清单<br/>6 项必跑))
    1 全局滚动条
      Firefox scrollbar-width
      Chrome ::-webkit-scrollbar
      Windows / macOS
    2 Focus ring
      Tab 键盘导航
      可见焦点指示器
      非 outline none
    3 reduced motion
      prefers-reduced-motion
      禁用 transition
      禁用 animation
    4 font-smoothing
      antialiased
      text-rendering
      一致性
    5 断点过渡
      sidebar 折叠
      panel toggle
      流畅无闪烁
    6 暗色主题
      所有区域背景色
      视觉区分
      非纯黑大平面
    检查方式
      启动应用
      逐项视验证
      每项截图
      任一 ❌ = uiux 不通过
```

## 七、Reviewer Completion Report 模板

```mermaid
graph TB
    Template[Reviewer Completion Report<br/>V10.12 强制]

    Template --> T1[agent: reviewer]
    Template --> T2[artifacts: 审查报告 + DOC SYNC]
    Template --> T3[code_dimension: PASS/FAIL]
    Template --> T4[api_dimension: PASS/FAIL/N/A]
    Template --> T5[uiux_dimension: PASS/FAIL/N/A]
    Template --> T6[boundary_dimension: PASS/FAIL/N/A]
    Template --> T7[functional_verification: PASS/FAIL]
    Template --> T8[product_evidence: 4 维 + 命令 + 输出]
    Template --> T9[total_score: X.X/5.0]
    Template --> T10[status: ✓ / ��]

    classDef tpl fill:#95e1d3,color:#000
    class T1,T2,T3,T4,T5,T6,T7,T8,T9,T10 tpl
```

## 八、关键引用

- 验收门禁: [acceptance-gates-v10.md](../references/acceptance-gates-v10.md)
- 通过依据 3 类分层: [acceptance-gates-v10.md §通过依据 3 类分层](../references/acceptance-gates-v10.md)
- UI 细节检查清单: [acceptance-gates-v10.md §UI 细节遗漏检查清单](../references/acceptance-gates-v10.md)
- 视觉证据 3 层校验: [reset-and-verify-protocol.md §V10.3.9 视觉证据门禁](../references/reset-and-verify-protocol.md)
-