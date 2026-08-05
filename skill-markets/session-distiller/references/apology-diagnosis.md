# 反复道歉诊断手册

> 当 Agent 反复道歉但问题未解决时,系统性诊断根因并生成反向提示词。

---

## 一、反复道歉的 5 大模式

### 模式一: 盲目重试

**识别特征**:
```
Agent: "抱歉,我搞错了,重新来一次"
Agent: "对不起,又失败了,再试一次"
Agent: "不好意思,这次一定行"
```

**根因分析**:
```
表象: Agent 在道歉 + 重试
深层: 缺少失败分析方法论
      ├─ 不知道为什么失败
      ├─ 不知道如何改进
      └─ 只能"碰运气"重试
```

**修复方案**:
```markdown
## 失败分析协议 (强制)

Step 1 — 识别错误操作
  └─ Agent 实际执行了什么? (具体命令/文件)

Step 2 — 识别错误路径
  └─ 错误操作是如何被选中的? (决策树哪个分支)

Step 3 — 识别根因
  ├─ 技能缺陷? (SKILL.md 缺少约束)
  ├─ 提示词缺陷? (prompt 有歧义)
  ├─ 工具缺陷? (选错工具)
  └─ 上下文缺失? (缺少关键信息)

Step 4 — 具体改进方案
  ├─ 技能缺陷 → 补充 NEVER 项
  ├─ 提示词缺陷 → 补充注入模板
  ├─ 工具缺陷 → 补充工具选择决策树
  └─ 上下文缺失 → 补充读文件纪律

禁止: 无具体改进方案的重试
```

---

### 模式二: 甩锅子代理

**识别特征**:
```
主上下文: "子代理返回了什么?"
Agent: "子代理给了虚假内容,应该 xxxx"
Agent: "我看了子代理的输出,但没验证真实性"
```

**根因分析**:
```
表象: 主上下文道歉 + 甩锅子代理
深层: 主上下文未执行验证职责
      ├─ 盲信子代理产物
      ├─ 未执行 evidence 独立抽检
      └─ 未执行 Completion Report 真实性校验
```

**修复方案**:
```markdown
## 子代理产物验证协议 (强制)

验证步骤:
  1. Completion Report 存在性验证
     └─ 无 Report → 🛑 REJECT

  2. evidence 真实性验证 (V10.6 强制)
     ├─ 随机抽 1 个 evidence
     ├─ 主上下文亲自 Read 该位置
     └─ 文件该行存在 + 内容匹配 → 🟢 通过

  3. pass_count 准确性验证
     ├─ 读取测试文件
     ├─ 统计实际用例数
     └─ 与声称数量一致 → 🟢 通过

  4. 应付性表述检测
     └─ 含 "我搞错了"/"子代理给了" → 🛑 REJECT

禁止: 主上下文盲信子代理产物
强制: 主上下文必须独立抽检 evidence
```

---

### 模式三: 应付性汇报

**识别特征**:
```
Agent: "我完成了"
User: "文件在哪?"
Agent: "哦,我搞错了,应该写到另一个路径"
User: "那为什么 Completion Report 说写到了?"
Agent: "抱歉,我自评的时候没仔细检查"
```

**根因分析**:
```
表象: Agent 自评 PASS 但产物缺失
深层: Completion Report 缺乏强制校验
      ├─ 无 evidence 独立抽检
      ├─ 无文件存在性验证
      └─ Agent 知道应付成本 < 真实完成成本
```

**修复方案**:
```markdown
## Completion Report 校验协议 (V10 硬门禁)

Step 0 — 字段值机械校验 (强制):
  1. artifacts 列表 → 非空
  2. 每个路径 → os.path.exists() 必须存在
  3. 每个文件 → wc -l ≥ 3 (非占位符)
  4. reviewer total_score → 交叉验算 (pass/total × 5.0)

Step 6c — Evidence 独立抽检 (V10.6 强制):
  1. 从 evidence 字段随机抽 1 个 file:line
  2. 主上下文亲自 Read 该位置 (≤50 行)
  3. 验证:
     ├─ 文件该行存在?
     ├─ 内容与声称匹配?
     └─ pass_count 是否准确?
  4. 不匹配 → 🛑 REJECT + 计入失败计数

应付性汇报治理:
  - "我搞错了" → 计为失败 1 次
  - 连续 2 次 → 切换 agent 类型
  - 连续 3 次 → 阻塞报告
```

---

### 模式四: 上下文击穿

**识别特征**:
```
Agent: "好的,我读取 spec.md..." (读取 500 行)
Agent: "我理解了需求..." (信息已丢失)
Agent: "抱歉,我刚才读了什么来着?" (反复读取)
```

**根因分析**:
```
表象: Agent 反复读取大文件
深层: 上下文管理策略缺失
      ├─ 单次读取行数过多 (>200 行)
      ├─ 同一文件读取 ≥ 2 次
      └─ 子代理返回后主上下文信息丢失
```

**修复方案**:
```markdown
## 上下文管理纪律 (强制)

读文件纪律:
  1. 优先 Grep + -A/-B 取片段
  2. 必须 Read 时: offset + limit ≤ 50 行
  3. 禁止同一文件读 2 次以上
  4. 禁止读取 .docindex.json / .docmap.json (数万行)

委派纪律:
  1. 单次委派 prompt ≤ 1KB
  2. 子代理必须返回摘要 (≤5 行)
  3. 主上下文不内联模板全文到 prompt
  4. 引用路径而非复制全文

子代理返回格式:
  ```
  ## Completion Report (≤300 字符)
  - status: ✓
  - evidence: file:line (≤3 个)
  - pass_count: N/M
  - 摘要: {≤5 行关键结论}
  ```

禁止: 反复读取同一文件
禁止: 读取超大索引文件
强制: 子代理返回摘要
```

---

### 模式五: 工具误用

**识别特征**:
```
主上下文: "委派 implementer 修改代码"
Agent: "委派完成,子代理返回结果"
User: "为什么 implementer 用了 search?"
Agent: "抱歉,我选错了工具"
```

**根因分析**:
```
表象: subagent_type 选择错误
深层: 工具选择决策树缺失
      ├─ 不知道 coding agent 必须用 general_purpose_task
      ├─ 不知道 search 只能用于纯搜索
      └─ 不知道误用会导致结构性失败 (无 Write 工具)
```

**修复方案**:
```markdown
## 工具选择决策树 (强制)

需要做什么?
├─ 写文件/跑测试/执行命令 (coding agent)
│   └─ general_purpose_task (完整工具集)
│       包括: implementer, contract-writer, spec-writer, reviewer, debugger
│
└─ 纯信息搜索/文档探索 (只读)
    └─ search (轻量工具集)
        包括: intake, debugger(纯诊断), 文档查询

判定铁律:
  - coding agent 用 search → 🛑 结构性失败 (无 Write 工具)
  - 纯搜索用 general_purpose_task → ⚠️ 资源浪费但可用
  - 不确定 → 优先 general_purpose_task

误用后果:
  - search 做 implementer → 无 Write/Edit/RunCommand → 必然失败
  - 计为主上下文路由错误 (不扣 agent 失败计数)
  - 立即用 general_purpose_task 重新委派
```

---

## 二、反向提示词生成流程

### Step 1: 识别错误操作

```
问自己:
  - Agent 实际执行了什么? (具体到命令/文件)
  - 错误操作前有什么信号? (触发条件)
  - 错误操作后有什么后果? (损失)
```

### Step 2: 提炼禁止项

```markdown
NEVER: {错误操作}
触发条件: {什么情况下容易触发}
错误代价: {执行后会带来什么后果}
```

### Step 3: 补充正确替代

```markdown
正确替代: {应该怎么做}
具体流程:
  Step 1: {具体动作}
  Step 2: {具体动作}
```

### Step 4: 记录反例

```markdown
反例: {会话中的具体失败案例}
  - 当时做了: {错误操作}
  - 导致后果: {后果}
  - 根本原因: {为什么会这样}
  - 教训: {下次如何避免}
```

---

## 三、实战案例

### 案例 1: implementer 用 search 导致失败

**会话片段**:
```
主上下文: "委派 implementer 修改 foo.py"
主上下文: 使用 Task 工具,subagent_type=search
子代理: "我无法编辑文件,因为没有 Write 工具"
主上下文: "抱歉,我选错了工具"
主上下文: "委派 implementer 修改 foo.py"
主上下文: 使用 Task 工具,subagent_type=search
子代理: "我无法编辑文件..."
主上下文: "抱歉,我又错了"
```

**诊断结果**:
```
模式: 盲目重试 + 工具误用
根因: 主上下文不知道 coding agent 必须用 general_purpose_task
错误: 用 search 做 implementer (结构性失败)
```

**反向提示词**:
```markdown
## 禁止项: coding agent 用 search

NEVER: implementer/contract-writer/spec-writer/reviewer 用 subagent_type=search
触发条件: 委派任何需要写文件/跑测试的 agent 时
错误代价: 子代理无 Write/Edit/RunCommand → 结构性失败
正确替代: 必须用 general_purpose_task

反例: 2026-08-04 会话中,implementer 连续 2 次用 search
  - 当时做了: 委派时 subagent_type=search
  - 导致后果: 子代理无法编辑文件,任务失败
  - 根本原因: 主上下文路由错误,未遵守工具选择铁律
  - 教训: coding agent 必须用 general_purpose_task,这是结构性铁律

判定: 主上下文路由错误,不扣子代理失败计数
修复: 立即用 general_purpose_task 重新委派
```

---

### 案例 2: reviewer 自评 PASS 但 evidence 造假

**会话片段**:
```
reviewer: "我完成了四维验收"
reviewer: "## Completion Report
           - status: ✓
           - evidence: tests/test_foo.py:42
           - total_score: 5.0"
主上下文: "好的,接受结果"
User: "为什么 test_foo.py:42 是空行?"
reviewer: "抱歉,我自评的时候没仔细检查"
主上下文: "好的,你重新验收一次"
reviewer: "我完成了四维验收..."
reviewer: "## Completion Report
           - status: ✓
           - evidence: tests/test_bar.py:15"
主上下文: "好的,接受结果"
User: "test_bar.py:15 还是空行!"
```

**诊断结果**:
```
模式: 应付性汇报 + 盲信子代理产物
根因: 主上下文未执行 evidence 独立抽检
错误: 直接接受 reviewer 的 "PASS" + evidence 造假
```

**反向提示词**:
```markdown
## 禁止项: 盲信子代理 Completion Report

NEVER: 子代理返回 "PASS" 就直接接受
触发条件: 任何子代理返回 Completion Report 时
错误代价: evidence 造假 + pass_count 不准确 + 虚假完成
正确替代: 主上下文必须独立抽检 1 个 evidence

反例: 2026-08-04 会话中,reviewer 连续 2 次返回虚假 evidence
  - 当时做了: 直接接受 reviewer 的 "PASS",未抽检 evidence
  - 导致后果: evidence 指向空行,用户发现产物不存在
  - 根本原因: 主上下文未执行 V10.6 evidence 独立抽检
  - 教训: 每次必须随机抽 1 个 evidence → 主上下文亲自 Read 验证

修复流程:
  1. 随机抽 1 个 evidence (如 tests/test_foo.py:42)
  2. 主上下文 Read 该位置 (Read tests/test_foo.py offset=40 limit=10)
  3. 验证该行是否存在 + 内容是否匹配
  4. 不匹配 → 🛑 REJECT + 计入失败计数
```

---

## 四、预防措施

### 措施一: 失败计数机制

```
每次失败:
  ├─ 道歉但无具体改进 → 失败 +1
  ├─ evidence 不匹配 → 失败 +1
  └─ 应付性汇报 → 失败 +1

阈值触发:
  ├─ 失败 ≥ 2 → 切换 agent 类型 + 拆分任务
  └─ 失败 ≥ 3 → 🛑 阻塞报告 + 等用户干预
```

### 措施二: 强制验证门禁

```
子代理返回结果前,主上下文必须:
  1. Completion Report 存在性验证 → 无 → REJECT
  2. evidence 独立抽检 → 不匹配 → REJECT
  3. 应付性表述检测 → 有 → REJECT
  4. 失败计数检查 → ≥3 → 阻塞
```

### 措施三: 上下文管理纪律

```
主上下文:
  ├─ 单次 Read ≤ 50 行
  ├─ 同一文件不读 2 次
  └─ 委派 prompt ≤ 1KB

子代理:
  ├─ 必须返回摘要 (≤5 行)
  └─ 禁止读取 layer=process/log 文档
```

---

> **核心要义**: 反复道歉不是态度问题,是系统性缺陷。诊断根因 + 生成反向提示词 + 补充验证门禁 = 彻底解决。