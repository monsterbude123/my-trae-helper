# §12 AI Agent 验收协议

> 本节定义 AI agent 在执行验收任务时的行为规范。所有 agent（包括主 agent 与子 agent）必须遵守。

---

## 触发词与自动加载

当用户输入包含以下关键词时，AI agent 应自动加载本 skill 并按协议执行：

| 触发场景 | 关键词 |
|---------|-------|
| 写测试 | "写测试" / "加测试" / "补测试" / "新增测试" |
| 测试异常 | "测试失败" / "测试超时" / "测试卡" / "测试报错" / "mock 不生效" / "测试慢" |
| 测试阻塞 | "测试卡住" / "测试阻塞" / "测试挂起" / "测试不过" / "分区测试" / "坏测试" |
| E2E 验收 | "跑 E2E" / "全量" / "回归" / "CI" / "发版" / "XX 有问题" / "帮我看看" / "修一下" |
| 性能验收 | "性能压测" / "P99" / "压测" / "性能基线" |
| 安全验收 | "安全扫描" / "依赖扫描" / "鉴权矩阵" / "CVE" |
| 门禁 | "PR check" / "门禁" / "release gate" / "验收" / "上线前" |

---

## 模式选择决策树

```
用户输入
  │
  ├─ "跑一下 E2E" / "全量" / "回归" / "CI" / "发版"
  │   → Workflow A（批量验收）
  │
  ├─ "XX 页面有问题" / "帮我看看" / "为什么" / "修一下"
  │   → Workflow B（即时诊断）
  │
  ├─ "测试卡住" / "测试挂起" / 全量测试不结束
  │   → 阻塞应急：分区定位
  │
  ├─ "写测试" / "加测试" / "补测试"
  │   → 单测 + 集成模板
  │
  ├─ "mock 不生效" / "测试报错"
  │   → Mock 检查清单 + 案例库
  │
  ├─ "性能压测" / "P99 飙升"
  │   → 性能验收
  │
  ├─ "安全扫描" / "CVE"
  │   → 安全验收
  │
  ├─ "上线前" / "发版前" / "门禁"
  │   → 验收门禁 + L3 Release Gate
  │
  └─ 不确定
      → 问用户："你需要的是？（A）单测/集成测试编写 （B）E2E 验收 （C）测试阻塞排查 （D）性能/安全验收 （E）发版门禁检查"
```

---

## AI 行为契约（通用）

```
✅ MUST DO
- 加载本 skill 后，明确告诉用户当前选用哪种模式
- 每个关键决策点说明依据（引用具体章节 / 检查项）
- 修复后必须验证（截图 + 日志 + 操作）
- 输出根因时引用具体日志行 / 代码行号
- 识别到 Bad Test 按案例库模板记录
- 度量指标异常时主动告警

❌ MUST NOT DO
- 只截图不拉日志就下结论
- 跳过日志检查直接猜根因
- 修复后不验证就声称完成
- 盲目重试整个测试套件
- 已知有问题还跑全量 E2E
- 把失败测试标 xfail 凑数
- 用 --no-verify 强推
- 只说"模块有问题"而没有根因
- 只看后端不看前端（或反过来）
- 忽略 WARNING 日志
```

---

## 多 Agent 协作时的 RACI

当多个 agent 并行开发时，验收责任必须清晰：

| 任务 | Responsible（执行）| Accountable（决策）| Consulted（咨询）| Informed（知会）|
|------|------------------|-------------------|-----------------|----------------|
| 单测编写 | 子 agent A | 模块 Owner | Tech Lead | - |
| 集成测试 | 子 agent B | 模块 Owner | DB Owner | - |
| E2E Workflow A | 主 agent | Tech Lead | 模块 Owner | QA |
| E2E Workflow B | 主 agent | 模块 Owner | - | - |
| 性能验收 | 性能 agent | 性能 Owner | Tech Lead | QA |
| 安全验收 | 安全 agent | 安全 Owner | Tech Lead | QA |
| 发版门禁 | 主 agent | Tech Lead | 所有 Owner | 全员 |

**铁律**：每个验收任务必须有且只有一个 Accountable。多个 agent 协作时，主 agent 是发版门禁的 Accountable。

---

## 子 Agent 委派规范

主 agent 委派验收任务给子 agent 时，必须在 prompt 中包含：

```
[Task ID]: <唯一 ID>
[Skill]: acceptance-discipline（必读）
[任务]: <具体描述>
[模式]: Workflow A / Workflow B / 单测编写 / 阻塞排查 / ...
[输入]: <文件路径 / 模块名 / 复现步骤>
[输出格式]: <诊断报告 / 修复 diff / 度量数据>
[完成标志]: <明确的标准，引用 §X.Y>
[禁止行为]: <引用 §12.3>
[worklog]: 必读 /home/z/my-project/worklog.md，完成后追加记录
```

---

## 产出格式规范

### 诊断报告（Workflow A）

必须包含：截图证据 + 后端日志 + 网络请求 + 控制台 + 根因 + 修复建议。
详细格式见 [e2e-audit-agent.md](../agents/e2e-audit-agent.md)。

### 即时诊断结论（Workflow B）

```
根因: {api/代码位置} → {错误类型}
证据: 
  - 截图: {path}（{现象}）
  - 前端日志: {console.error 行}
  - 网络请求: {method} {url} → {status}
  - 后端日志: {timestamp} {level} {file}:{line} {message}
修复: {文件:行号 具体改动}
验证: 重新执行 {操作} → 截图 {path} → 前后端无 ERROR ✅
```

### Bad Test 报告

见 [blockage-resolver-agent.md](../agents/blockage-resolver-agent.md) 的 Bad Test 反馈模板。

---

## 协议的演进

- 本协议随团队实践持续演进，每次重要更新必须在 worklog 记录
- 协议变更需 Tech Lead 签字
- 子 agent 反馈协议不适用时，主 agent 必须评估并修订
