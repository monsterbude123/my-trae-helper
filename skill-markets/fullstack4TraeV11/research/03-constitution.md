# V11 宪法 — 16 条铁律

> 不可协商的质量底线。冲突判定顺序：Constitution > Spec > Contract > Code > 个人判断。

---

## 宪法总览

```mermaid
mindmap
  root((16条宪法))
    质量底线
      I. TDD强制
      II. 满分硬门禁
      III. 零残留迁移
    委派纪律
      IV. 委派纪律
      V. GitNexus First
      VI. Ponytail First
    真相源
      VII. 文档优先
      VIII. 归档不可变
    即时同步
      IX. TDD即时
      X. 异会话验证
      XI. 视觉真实验证
    腐化防护
      XII. 文档诚实
      XIII. 骨架是债
      XIV. rot-detector必跑
    反虚假交付
      XV. 障碍诚实汇报
      XVI. 禁抽象理由
```

---

## 宪法层次结构

```mermaid
graph TB
    subgraph 质量底线[一、质量底线 3条]
        A1[I. TDD强制]
        A2[II. 满分硬门禁]
        A3[III. 零残留迁移]
    end
    
    subgraph 委派纪律[二、委派纪律 3条]
        A4[IV. 委派纪律]
        A5[V. GitNexus First]
        A6[VI. Ponytail First]
    end
    
    subgraph 真相源[三、真相源 2条]
        A7[VII. 文档优先]
        A8[VIII. 归档不可变]
    end
    
    subgraph 即时同步[四、即时同步 3条]
        A9[IX. TDD即时]
        A10[X. 异会话验证]
        A11[XI. 视觉真实验证]
    end
    
    subgraph 腐化防护[五、腐化防护 3条]
        A12[XII. 文档诚实]
        A13[XIII. 骨架是债]
        A14[XIV. rot-detector必跑]
    end
    
    subgraph 反虚假交付[六、反虚假交付 2条]
        A15[XV. 障碍诚实汇报]
        A16[XVI. 禁抽象理由]
    end
```

---

## 永不可降级清单

```mermaid
graph TB
    A[16条宪法] --> B{可降级?}
    B -->|否| C[永不可降级 9条]
    B -->|是| D[可降级 7条]
    
    C --> E[I. TDD强制]
    C --> F[II. 满分硬门禁]
    C --> G[IV. 委派纪律]
    C --> H[V. GitNexus First]
    C --> I[VIII. 归档不可变]
    C --> J[IX. TDD即时]
    C --> K[XIV. rot-detector必跑]
    C --> L[XV. 障碍诚实]
    C --> M[XVI. 禁抽象理由]
    
    style C fill:#f66
    style E fill:#f66
    style F fill:#f66
    style G fill:#f66
    style H fill:#f66
    style I fill:#f66
    style J fill:#f66
    style K fill:#f66
    style L fill:#f66
    style M fill:#f66
```

---

## 一、质量底线 3 条

### Article I. TDD 强制

```mermaid
flowchart TB
    A[新功能/Bug修复] --> B[先写失败测试]
    B --> C{测试FAIL?}
    C -->|否| D[重写测试]
    D --> B
    C -->|是| E[写实现]
    E --> F{测试GREEN?}
    F -->|否| E
    F -->|是| G[REFACTOR]
    
    style B fill:#f66
    style C fill:#f66
```

**铁律**: 无失败测试不写实现。

**违反后果**: 🛑 退回 Phase 3 重新跑 RED→GREEN。

---

### Article II. 满分硬门禁

```mermaid
graph TB
    A[4维评分] --> B[维度1: 代码层]
    A --> C[维度2: API层]
    A --> D[维度3: UI/UX层]
    A --> E[维度4: 模块边际]
    
    B --> F{任一维度0分?}
    C --> F
    D --> F
    E --> F
    
    F -->|是| G[🛑 REJECT]
    F -->|否| H{全部满分?}
    H -->|是| I[✅ PASS]
    H -->|否| G
    
    style G fill:#f66
    style I fill:#9f9
```

**铁律**: 4 维度验收任一非满分 = 🛑 REJECT。

**评分算法**: 通过维度 / 适用维度 × 5.0

---

### Article III. 零残留迁移

```mermaid
graph LR
    A[迁移/重构] --> B{残留文件?}
    B -->|.bak/.old| C[🛑 REJECT]
    B -->|无| D[✅ PASS]
    
    style C fill:#f66
```

**铁律**: 无 `.bak` / `.old` 后缀文件。

---

## 二、委派纪律 3 条

### Article IV. 委派纪律

```mermaid
graph TB
    subgraph 主上下文职责
        A1[协调]
        A2[验收]
        A3[状态卡更新]
        A4[路由决策]
    end
    
    subgraph 子代理职责
        B1[执行]
        B2[4字段回报]
        B3[门禁遵守]
    end
    
    A1 --> B1
    B1 --> A2
    A2 --> A3
    
    style A1 fill:#9cf
    style B1 fill:#9f9
```

**铁律**: 主上下文不直行代码，只做协调。

**违反后果**: 主上下文 Edit/Write 代码 = 🛑 委派违规。

---

### Article V. GitNexus First

```mermaid
flowchart TB
    A[改Symbol前] --> B{GitNexus可用?}
    B -->|是| C[impact调用]
    B -->|否| D[npx gitnexus analyze]
    D --> C
    
    C --> E[查看上游/下游]
    E --> F[评估影响面]
    F --> G[继续修改]
    
    style B fill:#f9f
```

**铁律**: 影响面评估用工具不用 grep。

**违反后果**: GitNexus 可用却用 grep = 🛑 委派违规。

---

### Article VI. Ponytail First

```mermaid
graph LR
    A[代码检查] --> B{单文件 ≤ 800行?}
    B -->|否| C[拆分]
    B -->|是| D{函数 ≤ 50行?}
    D -->|否| E[拆分]
    D -->|是| F{魔法数字?}
    F -->|是| G[提取常量]
    F -->|否| H{L0/L1硬编码?}
    H -->|是| I[外置config]
    H -->|否| J[✅ PASS]
    
    style J fill:#9f9
```

**铁律**: 最简实现优先。

---

## 三、真相源 2 条

### Article VII. 文档与代码冲突以文档为准

```mermaid
flowchart TB
    A[发现漂移] --> B{类型}
    B -->|代码实现错误| C[改代码]
    B -->|文档描述过时| D[改文档]
    
    C --> E[先改spec]
    D --> F[验证spec真实]
    
    E --> G[再改代码]
    F --> G
    
    G --> H[✅ 真相源对齐]
    
    style E fill:#f9f
```

**铁律**: Spec 是真相源，代码为规格服务。

---

### Article VIII. 归档不可变

```mermaid
graph TB
    A[archive/文件] --> B{尝试修改?}
    B -->|是| C[🛑 REJECT]
    B -->|否| D[✅ 保持不变]
    
    C --> E[应新建change]
    E --> F[从归档复制起点]
    
    style C fill:#f66
```

**铁律**: `archive/` 下文件禁止修改。

---

## 四、即时同步 3 条

### Article IX. TDD 即时

```mermaid
sequenceDiagram
    participant Dev as 开发者
    participant Test as 测试
    participant Code as 代码
    
    Dev->>Test: 改实现
    Test->>Test: 同步改测试
    Dev->>Code: 删组件
    Test->>Test: 同步删测试
    Test->>Test: orphan-detector验证
```

**铁律**: 改实现/删组件 → 立即同步改测试/删测试。

---

### Article X. 异会话验证

```mermaid
flowchart TB
    A[子代理返回] --> B{3层独立验证}
    
    B --> C[Layer1: 存在性]
    B --> D[Layer2: 准确性]
    B --> E[Layer3: 产物存在]
    
    C --> C1[LS验证路径]
    D --> D1[Run验证pass_count]
    E --> E1[Glob验证产物]
    
    C1 --> F{全部通过?}
    D1 --> F
    E1 --> F
    
    F -->|是| G[接受报告]
    F -->|否| H[质疑+退回]
    
    style B fill:#f9f
```

**铁律**: 自评 = self_attested，主上下文必二次抽检。

---

### Article XI. 视觉真实验证

```mermaid
flowchart TB
    A[截图证据] --> B[PNG magic验证]
    B --> C{前8字节正确?}
    C -->|否| D[🛑 无效PNG]
    C -->|是| E[文件大小检查]
    E --> F{≥ 5000 bytes?}
    F -->|否| G[⚠️ 疑似空白]
    F -->|是| H[亮度检查]
    H --> I{30-240范围?}
    I -->|否| J[⚠️ 异常亮度]
    I -->|是| K[✅ 视觉验证通过]
    
    style D fill:#f66
    style G fill:#f96
    style J fill:#f96
    style K fill:#9f9
```

**铁律**: 视觉证据必须 PIL 解码 + 直方图 + 关键区域采样。

---

## 五、腐化防护 3 条

### Article XII. 文档诚实

```mermaid
graph LR
    A[state-card/INDEX] --> B{INV真实存在?}
    B -->|是| C[spec.md落地]
    B -->|否| D[🛕 虚标]
    
    C --> E[✅ 文档诚实]
    D --> F[proactive-scan检测]
    
    style D fill:#f66
```

**铁律**: state-card/INDEX 声称的 INV 必在 spec.md 落地。

---

### Article XIII. 骨架是债

```mermaid
graph TB
    A[仅定义无实现] --> B{已过2周?}
    B -->|是| C[冻结或归档]
    B -->|否| D[推进实现]
    
    C --> E[stub-pileup扫描]
    E --> F[✅ 债务可见]
    
    style C fill:#f9f
```

**铁律**: 仅定义无实现 = 隐性技术债。

---

### Article XIV. rot-detector 必跑

```mermaid
graph TB
    A[Phase 4.5] --> B[8项扫描]
    
    B --> C1[视觉验证假阳性]
    B --> C2[归档修改]
    B --> C3[自评自签]
    B --> C4[孤儿测试]
    B --> C5[构建残留]
    B --> C6[自我吹嘘]
    B --> C7[状态卡陈旧]
    B --> C8[骨架堆积]
    
    C1 --> D{任一FAIL?}
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    C6 --> D
    C7 --> D
    C8 --> D
    
    D -->|是| E[🛑 REJECT]
    D -->|否| F[✅ PASS]
    
    style E fill:#f66
    style F fill:#9f9
```

**铁律**: Phase 4.5 Proactive Rot Scan 不可跳过。

---

## 六、反虚假交付 2 条

### Article XV. 障碍诚实汇报

```mermaid
graph TB
    A[遇到障碍] --> B[5字段阻塞报告]
    
    B --> C[type: 类型]
    B --> D[description: 描述]
    B --> E[solution: 方案]
    B --> F[duration: 耗时]
    B --> G[attempts: 尝试次数]
    
    C --> H[立即输出]
    D --> H
    E --> H
    F --> H
    G --> H
    
    style B fill:#f66
```

**铁律**: 遇到障碍立即输出 5 字段阻塞报告。

---

### Article XVI. 禁止编造抽象理由

```mermaid
graph TB
    A[被质疑] --> B{理由类型}
    
    B -->|抽象理由| C[🛕 禁止]
    B -->|具体修正| D[✅ 允许]
    
    C --> C1[理解偏差]
    C --> C2[流程裁剪]
    C --> C3[心理障碍]
    C --> C4[概念漂移]
    C --> C5[上下文丢失]
    C --> C6[权衡取舍]
    
    D --> D1[我错了]
    D --> D2[具体未执行规则]
    D --> D3[可执行补救]
    
    style C fill:#f66
```

**铁律**: 被质疑禁止用"理解偏差"等不可证伪理由。

---

## 宪法与阶段映射

```mermaid
graph TB
    subgraph Stage_-1
        A1[I, IV, V, XV, XVI]
    end
    
    subgraph Stage_0
        A2[I, IV, V, VI, VII]
    end
    
    subgraph Stage_0.5
        A3[I, II, IX]
    end
    
    subgraph Stage_1
        A4[I, VII, XII]
    end
    
    subgraph Stage_1.5
        A5[I, VII, XI]
    end
    
    subgraph Stage_2
        A6[I, VII, VIII, IX]
    end
    
    subgraph Stage_3
        A7[I, IV, V, VI, VII, IX]
    end
    
    subgraph Stage_3.5
        A8[II, X, XI, XV]
    end
    
    subgraph Stage_4
        A9[I, II, IV, X, XI, XII, XV, XVI]
    end
    
    subgraph Stage_4.5
        A10[XII, XIII, XIV]
    end
    
    subgraph Stage_5
        A11[VIII, XII, XIII]
    end
    
    subgraph Stage_6
        A12[I, V, IX, XV, XVI]
    end
    
    subgraph Stage_7
        A13[I, II, IV, X, XII, XV, XVI]
    end
```

---

## 宪法冲突判定

```mermaid
flowchart TB
    A[冲突发生] --> B{判定顺序}
    
    B --> C[1. Constitution]
    B --> D[2. Spec]
    B --> E[3. Contract]
    B --> F[4. Code]
    B --> G[5. 个人判断]
    
    C --> C1{宪法有规定?}
    C1 -->|是| H[宪法优先]
    C1 -->|否| D
    
    D --> D1{Spec有规定?}
    D1 -->|是| I[Spec优先]
    D1 -->|否| E
    
    E --> E1{Contract有规定?}
    E1 -->|是| J[Contract优先]
    E1 -->|否| F
    
    F --> F1{Code有规定?}
    F1 -->|是| K[Code次之]
    F1 -->|否| G
    
    style C fill:#f66
    style H fill:#f66
```

---

## 关联文档

- [宪法详细版](../references/constitution.md)
- [公共铁律](../references/common-iron-rules.md)
- [公共反例](../references/common-anti-patterns.md)