# 脚本使用时机

> 14 个公共脚本 + 各 stage 内部脚本。脚本失败 = 🛑 REJECT。

---

## 脚本总览

```mermaid
mindmap
  root((脚本体系))
    公共脚本
      stage-gate.py
      state-card-validator.py
      code-hygiene.py
      orphan-detector.py
      dist-hash-check.py
      visual-content-check.py
      acceptance-audit.py
      proactive-scan.py
      self-diagnose.py
      spec-purge.py
      spec-knowledge-extract.py
      reason-classifier.py
      setup-feature.py
      change-status.py
    Stage内部脚本
      contract-gate.py
      各stage自定义
```

---

## 公共脚本清单

```mermaid
graph TB
    subgraph 阶段门禁
        A[stage-gate.py<br/>V11阶段门禁]
        B[state-card-validator.py<br/>状态卡验证]
    end
    
    subgraph 代码质量
        C[code-hygiene.py<br/>代码卫生]
        D[orphan-detector.py<br/>孤儿测试]
    end
    
    subgraph 验证工具
        E[dist-hash-check.py<br/>Bundle一致性]
        F[visual-content-check.py<br/>视觉内容校验]
    end
    
    subgraph 验收审计
        G[acceptance-audit.py<br/>4维验收审计]
    end
    
    subgraph 腐化扫描
        H[proactive-scan.py<br/>5项腐化扫描]
        I[self-diagnose.py<br/>Meta自我诊断]
    end
    
    subgraph 归档工具
        J[spec-purge.py<br/>Spec清除归档]
        K[spec-knowledge-extract.py<br/>知识沉淀]
    end
    
    subgraph 辅助工具
        L[reason-classifier.py<br/>抽象理由分类]
        M[setup-feature.py<br/>创建change骨架]
        N[change-status.py<br/>读取change状态]
    end
```

---

## 脚本使用时机表

```mermaid
graph TB
    subgraph 所有Stage
        A[stage-gate.py<br/>Stage切换前]
        B[state-card-validator.py<br/>状态卡更新后]
        C[reason-classifier.py<br/>被质疑时]
    end
    
    subgraph Stage_0
        D[setup-feature.py<br/>创建change]
        E[change-status.py<br/>读取状态]
    end
    
    subgraph Stage_3_4_4.5
        F[code-hygiene.py<br/>Stage 3完成]
        G[orphan-detector.py<br/>Stage 4/4.5]
    end
    
    subgraph Stage_3.5_4
        H[dist-hash-check.py<br/>Stage 3.5]
        I[visual-content-check.py<br/>Stage 4]
    end
    
    subgraph Stage_4
        J[acceptance-audit.py<br/>4维验收]
    end
    
    subgraph Stage_4.5
        K[proactive-scan.py<br/>腐化扫描]
        L[self-diagnose.py<br/>自我诊断]
    end
    
    subgraph Stage_5
        M[spec-purge.py<br/>归档前]
        N[spec-knowledge-extract.py<br/>知识沉淀]
    end
```

---

## 脚本调用规则

```mermaid
flowchart TB
    A[脚本调用] --> B[主上下文亲自调用]
    B --> C{脚本输出}
    
    C -->|PASS| D[继续]
    C -->|FAIL| E[🛕 REJECT]
    C -->|N/A| F[状态卡标注理由]
    
    E --> G[走Article XV阻塞报告]
    
    style B fill:#f9f
    style E fill:#f66
```

**核心规则**:
- 主上下文亲自调用（不委派给子代理）
- 脚本输出必须真实保存
- 脚本失败 = 🛕 REJECT
- 脚本 N/A 必须标注理由

---

## stage-gate.py

```mermaid
flowchart TB
    A[stage-gate.py] --> B[加载stage_config]
    B --> C[检查当前stage]
    
    C --> D[验证门禁条件]
    D --> E{门禁通过?}
    
    E -->|是| F[输出: PASS]
    E -->|否| G[输出: FAIL + 原因]
    
    F --> H[允许进入下一Stage]
    G --> I[🛕 阻断]
    
    style F fill:#9f9
    style G fill:#f66
```

**使用时机**: 所有 stage 切换前

---

## state-card-validator.py

```mermaid
flowchart TB
    A[state-card-validator.py] --> B[加载状态卡]
    B --> C[执行Rule 1-5]
    
    C --> D[Rule 1: artifacts存在]
    C --> E[Rule 2: gate真实跑过]
    C --> F[Rule 3: blocked逻辑正确]
    C --> G[Rule 4: 时间戳完整]
    C --> H[Rule 5: stage合法]
    
    D --> I{全部通过?}
    E --> I
    F --> I
    G --> I
    H --> I
    
    I -->|是| J[输出: PASS]
    I -->|否| K[输出: FAIL + 不一致清单]
    
    style J fill:#9f9
    style K fill:#f66
```

**使用时机**: 所有 stage 状态卡更新后

---

## code-hygiene.py

```mermaid
flowchart TB
    A[code-hygiene.py] --> B[扫描代码]
    
    B --> C[检查: 单文件 ≤ 800行]
    B --> D[检查: 函数 ≤ 50行]
    B --> E[检查: 无魔法数字]
    B --> F[检查: 无TODO/FIXME]
    B --> G[检查: L0/L1值外置]
    
    C --> H{全部通过?}
    D --> H
    E --> H
    F --> H
    G --> H
    
    H -->|是| I[输出: PASS]
    H -->|否| J[输出: FAIL + 违规项]
    
    style I fill:#9f9
    style J fill:#f66
```

**使用时机**: Stage 3 Implement 完成

---

## orphan-detector.py

```mermaid
flowchart TB
    A[orphan-detector.py] --> B[扫描测试文件]
    B --> C[检查被测组件是否存在]
    
    C --> D{存在孤儿测试?}
    D -->|是| E[输出: FAIL + 孤儿列表]
    D -->|否| F[输出: PASS]
    
    E --> G[删除孤儿测试]
    G --> H[重新运行]
    
    style F fill:#9f9
    style E fill:#f66
```

**使用时机**: Stage 4 Review / Stage 4.5 Rot Scan

---

## visual-content-check.py

```mermaid
flowchart TB
    A[visual-content-check.py] --> B[加载截图]
    
    B --> C[PNG magic验证]
    B --> D[文件大小 ≥ 5000 bytes]
    B --> E[亮度检查 30-240]
    B --> F[文件活跃性 ≤ 7天]
    
    C --> G{全部通过?}
    D --> G
    E --> G
    F --> G
    
    G -->|是| H[输出: PASS]
    G -->|否| I[输出: FAIL + 异常项]
    
    style H fill:#9f9
    style I fill:#f66
```

**使用时机**: Stage 4 Review（视觉验证）

---

## proactive-scan.py

```mermaid
flowchart TB
    A[proactive-scan.py] --> B[8项扫描]
    
    B --> B1[1. 视觉验证假阳性]
    B --> B2[2. 归档修改]
    B --> B3[3. 自评自签]
    B --> B4[4. 孤儿测试]
    B --> B5[5. 构建残留]
    B --> B6[6. 自我吹嘘]
    B --> B7[7. 状态卡陈旧]
    B --> B8[8. 骨架堆积]
    
    B1 --> C{任一FAIL?}
    B2 --> C
    B3 --> C
    B4 --> C
    B5 --> C
    B6 --> C
    B7 --> C
    B8 --> C
    
    C -->|是| D[输出: FAIL + 修复列表]
    C -->|否| E[输出: PASS]
    
    style E fill:#9f9
    style D fill:#f66
```

**使用时机**: Stage 4.5 Rot Scan

---

## reason-classifier.py

```mermaid
flowchart TB
    A[reason-classifier.py] --> B[输入理由文本]
    B --> C[分类检测]
    
    C --> D{类型}
    D -->|抽象理由| E[6类检测]
    D -->|具体修正| F[PASS]
    
    E --> E1[理解偏差]
    E --> E2[流程裁剪]
    E --> E3[心理障碍]
    E --> E4[概念漂移]
    E --> E5[上下文丢失]
    E --> E6[权衡取舍]
    
    E1 --> G[输出: ABSTRACT_REASON]
    E2 --> G
    E3 --> G
    E4 --> G
    E5 --> G
    E6 --> G
    
    style G fill:#f66
    style F fill:#9f9
```

**使用时机**: 所有 stage（被质疑时）

---

## 脚本失败处理

```mermaid
sequenceDiagram
    participant Script as 脚本
    participant Agent as 主上下文
    participant Card as 状态卡
    participant User as 用户
    
    Script->>Agent: FAIL输出
    Agent->>Agent: 分析失败原因
    Agent->>Card: 更新health=🔴
    Agent->>Card: 更新blocked_by
    
    Agent->>User: 5字段阻塞报告
    
    alt 可自动修复
        User->>Agent: 自动修复
        Agent->>Script: 重新运行
    else 需用户决策
        User->>Agent: 用户决策
    end
```

---

## 脚本输出格式

### PASS 格式

```json
{
  "status": "PASS",
  "script": "stage-gate.py",
  "stage": "3/implement",
  "checks": {
    "tdd_green": true,
    "drift_check": true,
    "code_hygiene": true
  },
  "timestamp": "2026-08-11T14:30:00"
}
```

### FAIL 格式

```json
{
  "status": "FAIL",
  "script": "code-hygiene.py",
  "violations": [
    {
      "file": "src/services.rs",
      "line": 150,
      "rule": "function_too_long",
      "message": "Function `handle_request` exceeds 50 lines (78 lines)"
    }
  ],
  "timestamp": "2026-08-11T14:30:00"
}
```

---

## 关联文档

- [脚本目录](../scripts/README.md)
- [宪法 Article X](../references/constitution.md)
- [Hook生命周期](07-hook-lifecycle.md)