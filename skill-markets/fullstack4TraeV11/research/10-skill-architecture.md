# 高内聚专家架构

> V11 升级核心：从 V10 的分散架构升级为高内聚专家 skill 架构。

---

## 架构总览

```mermaid
mindmap
  root((高内聚架构))
    核心原则
      stage自包含
      插拔式组件
      编排器轻量化
    目录结构
      SKILL.md骨架
      references细节
      anti-patterns反例
      templates模板
      workflows流程
      scripts脚本
    依赖声明
      requires硬依赖
      optional软依赖
      stage_config配置
```

---

## V10 vs V11 架构对比

```mermaid
graph TB
    subgraph V10架构
        A1[agents/] --> A2[分散的agent定义]
        A3[references/] --> A4[共享参考]
        A5[templates/] --> A6[共享模板]
        
        A2 --> A7[问题: 修改需改多处]
        A4 --> A8[问题: 跨文件查找]
        A6 --> A9[问题: 模板与agent分离]
    end
    
    subgraph V11架构
        B1[skills/01-intake/] --> B2[自包含]
        B3[skills/02-plan/] --> B4[自包含]
        B5[... ] --> B6[自包含]
        
        B2 --> B7[优势: 独立升级]
        B4 --> B8[优势: 零影响其他]
        B6 --> B9[优势: 插拔式替换]
    end
    
    style A7 fill:#f66
    style A8 fill:#f66
    style A9 fill:#f66
    
    style B7 fill:#9f9
    style B8 fill:#9f9
    style B9 fill:#9f9
```

---

## Stage Skill 自包含结构

```mermaid
graph TB
    subgraph Stage_Skill[skills/{NN}-{name}/]
        A[SKILL.md<br/>阶段入口]
        B[README.md<br/>阶段元信息]
        C[scripts/<br/>确定性脚本]
        D[workflows/<br/>阶段内工作流]
        E[templates/<br/>产物模板]
        F[references/<br/>方法论细节]
        G[anti-patterns/<br/>反例库]
    end
    
    A --> A1[铁律 ≤10条]
    A --> A2[边界定义]
    A --> A3[委派触发词]
    A --> A4[depends_on声明]
    
    B --> B1[stage说明]
    B --> B2[依赖声明]
    B --> B3[产出清单]
    
    style A fill:#9cf
```

---

## 编排器职责

```mermaid
graph TB
    subgraph 编排器[SKILL.md编排器]
        A[路由]
        B[门禁]
        C[状态卡同步]
    end
    
    A --> A1[解析stage_config]
    A --> A2[加载对应stage skill]
    
    B --> B1[调用门禁脚本]
    B --> B2[验证门禁结果]
    
    C --> C1[更新current_stage]
    C --> C2[同步产物清单]
    
    style A fill:#f9f
    style B fill:#f9f
    style C fill:#f9f
```

**编排器不做**:
- ❌ 不执行具体任务
- ❌ 不直接编辑代码
- ❌ 不替换 stage skill 决策

---

## 13 个 Stage Skills

```mermaid
graph TB
    subgraph 规划阶段
        S1[01-intake<br/>意图识别]
        S2[02-plan<br/>三路探索]
        S3[03-test-plan<br/>测试映射]
        S4[04-spec<br/>规格编写]
        S5[05-prototype<br/>双源验证]
    end
    
    subgraph 契约阶段
        S6[06-contract<br/>契约定义]
        S7[07-implement<br/>TDD实现]
        S8[08-real-verify<br/>启动验证]
    end
    
    subgraph 验收阶段
        S9[09-review<br/>四维验收]
        S10[10-rot-scan<br/>腐化扫描]
        S11[11-accept<br/>归档沉淀]
    end
    
    subgraph 支线
        S12[12-bug-fix<br/>Bug修复]
        S13[13-project-health<br/>健康检查]
    end
    
    S1 --> S2 --> S3 --> S4 --> S5
    S5 --> S6 --> S7 --> S8
    S8 --> S9 --> S10 --> S11
    
    S1 -.-> S12
    S1 -.-> S13
```

---

## 依赖声明机制

### YAML Frontmatter

```yaml
---
name: skill-name
description: 一句话 + 触发条件
requires:
  skills: [dependency-name]    # 硬依赖：必须先加载
  optional: [optional-name]     # 软依赖：建议但不强制
stage_config:
  intake:
    route: "skills/01-intake/SKILL.md"
    skills: []
    stages: []
  plan:
    route: "skills/02-plan/SKILL.md"
    skills: [gitnexus4Trae]
    stages: [-1/intake]
---
```

### 依赖加载流程

```mermaid
flowchart TB
    A[加载SKILL.md] --> B[解析frontmatter]
    B --> C{requires.skills?}
    C -->|是| D[检查依赖是否已加载]
    C -->|否| E[直接加载stage skill]
    
    D --> F{已加载?}
    F -->|是| E
    F -->|否| G[递归加载依赖]
    G --> E
    
    E --> H{requires.optional?}
    H -->|是| I[尝试加载可选依赖]
    H -->|否| J[完成]
    I --> J
    
    style G fill:#f9f
```

---

## 配置化依赖覆盖

```mermaid
flowchart TB
    A[3层优先级] --> B[1. 项目级覆盖]
    A --> C[2. 编排器stage_config]
    A --> D[3. stage skill depends_on]
    
    B --> E[最高优先级]
    C --> F[中等优先级]
    D --> G[最低优先级]
    
    E --> H{项目级有配置?}
    H -->|是| I[使用项目级]
    H -->|否| F
    
    style B fill:#f66
    style I fill:#f66
```

---

## Stage Skill 示例

### 01-intake/SKILL.md 结构

```mermaid
graph TB
    subgraph 01-intake
        A[YAML Frontmatter]
        B[铁律 10条]
        C[边界定义]
        D[委派触发词]
        E[depends_on声明]
        F[工作流指针]
        G[反例指针]
    end
    
    A --> A1[name: 01-intake]
    A --> A2[description]
    A --> A3[requires]
    
    B --> B1[Article I]
    B --> B2[Article IV]
    B --> B3[Article V]
    B --> B4[...]
    
    C --> C1[输入: 用户意图]
    C --> C2[输出: 状态卡 + 路由]
    
    D --> D1["新需求"]
    D --> D2["Bug反馈"]
    D --> D3["咨询"]
    
    style A fill:#9cf
```

---

## 插拔式升级流程

```mermaid
sequenceDiagram
    participant Dev as 开发者
    participant Git as Git仓库
    participant IDE as Trae IDE
    participant Skill as Skill系统
    
    Dev->>Git: 修改单个stage skill
    Git->>Dev: 提交变更
    Dev->>IDE: 重启IDE
    IDE->>Skill: 重新加载SKILL.md
    Skill->>Skill: 解析frontmatter
    Skill->>Skill: 加载依赖
    Skill->>Dev: 升级完成
    
    Note over Skill: 其他stage skill不受影响
```

---

## 高内聚设计原则

```mermaid
graph TB
    A[高内聚原则] --> B[单一职责]
    A --> C[自包含]
    A --> D[零外部依赖]
    A --> E[可独立测试]
    
    B --> B1[一个stage做一件事]
    B --> B2[不跨stage操作]
    
    C --> C1[所有资源在本目录]
    C --> C2[引用而非内联]
    
    D --> D1[引用其他skill名]
    D --> D2[不跨目录读取]
    
    E --> E1[可单独验证]
    E --> E2[可单独升级]
    
    style B fill:#9f9
    style C fill:#9f9
    style D fill:#9f9
    style E fill:#9f9
```

---

## 目录结构完整版

```
fullstack4TraeV11/
├── SKILL.md                # 总编排器
├── references/             # 9个公共references
│   ├── constitution.md
│   ├── common-iron-rules.md
│   ├── common-anti-patterns.md
│   ├── stage-interaction-protocol.md
│   ├── state-card-protocol.md
│   ├── dependency-config.md
│   ├── document-layer.md
│   ├── report-growth.md
│   └── ask-question-anti-patterns.md
├── templates/              # 项目级模板
│   ├── project-agents-example.md
│   ├── project-rules-example/
│   └── state-card.md
├── scripts/                # 14个公共scripts
│   ├── stage-gate.py
│   └── state-card-validator.py
└── skills/                 # 13个stage skill
    ├── 01-intake/
    │   ├── SKILL.md
    │   ├── README.md
    │   ├── scripts/
    │   ├── workflows/
    │   ├── templates/
    │   ├── references/
    │   └── anti-patterns/
    ├── 02-plan/
    ├── ...
    └── 13-project-health/
```

---

## 关联文档

- [SKILL.md](../SKILL.md)
- [依赖配置](../references/dependency-config.md)
- [阶段交互协议](../references/stage-interaction-protocol.md)