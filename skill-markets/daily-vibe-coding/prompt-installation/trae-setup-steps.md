# TRAE Work 配置 daily-vibe-coding 定时任务 — 详细步骤

> TRAE Work **配置后无法修改运行模式/运行环境/存储位置**,所以首次配置务必一次设准。
> 三种创建方式都能用,推荐**方式 A**("在对话中创建")—— TRAE AI 解读后会自动引导你确认细节。

---

## 前置检查(1 分钟)

- [ ] TRAE Work 客户端已登录
- [ ] 已打开 work mode(左上角模式选择 = Work)
- [ ] 工作区打开到 `d:\workspace\my-trae-helper`
- [ ] 网络正常

---

## 方式 A:在对话中创建(推荐,2 分钟)

### 步骤

1. 打开 TRAE Work,进入**任意对话**(不必是新对话)
2. 复制 [`installation-prompt.md`](installation-prompt.md) 的**整段 prompt**
3. 粘贴到对话输入框,**回车发送**
4. TRAE AI 会解读并**确认以下细节**(必审):
   - 任务名 = `daily-vibe-coding`
   - 触发时间 = 每天 09:00 (Asia/Shanghai)
   - 运行模式 = **Work**
   - 运行环境 = **云端**(避免占本地电脑)
   - 输出位置 = `d:\workspace\my-trae-helper\logs\daily-vibe-coding\YYYY-MM-DD\`
5. 确认无误 → 点击"创建"
6. 创建成功 → 任务列表里看到 `daily-vibe-coding`,开关默认开启
7. 明日 09:00 自动跑(或点"运行一次"立即测试)

### 截图位(待补)

```
[截图: TRAE Work 对话框粘贴 prompt + AI 解读 + 确认]
```

---

## 方式 B:手动新建(5 分钟)

### 步骤

1. 左栏顶部 → **自动化** → 右上角 **手动新建**
2. 填写:
   - **任务名**: `daily-vibe-coding`
   - **触发时间**: 自定义 → `工作日早上 9:00` (TRAE Work 支持自然语言)
   - **任务内容**: 粘贴 [`installation-prompt.md`](installation-prompt.md) 的"任务内容"段(整个 PART 0 到 PART D + 关键约束)
   - **运行模式**: Work(只能选当前模式)
   - **运行环境**: 云端
   - **输出存储位置**: `d:\workspace\my-trae-helper\logs\daily-vibe-coding\`
3. **保存**

### 关键字段说明

| 字段 | 必填 | 推荐值 | 说明 |
|------|------|--------|------|
| 任务名 | ✓ | `daily-vibe-coding` | 显示在自动化列表里 |
| 触发时间 | ✓ | `每天 09:00` 或 `工作日 09:00` | 自然语言输入 |
| 任务内容 | ✓ | 复制 installation-prompt.md | 大段 prompt,TRAE 会自动运行 |
| 运行模式 | ✓ | Work | 默认当前模式,**不可改** |
| 运行环境 | ✓ | 云端 | 不占本地电脑,可后台跑 |
| 输出存储 | ✓ | `d:\workspace\my-trae-helper\logs\daily-vibe-coding\` | 任务运行后写到这里 |

---

## 方式 C:从模板创建(待补,需 TRAE Work 模板机制)

未来如果 TRAE Work 开放"任务模板"导出/导入,可把本任务保存为模板供团队复用。

---

## 验证任务已生效

任务创建后**立即点"运行一次"**(无次日等):

1. 左栏顶部 → **自动化** → 找到 `daily-vibe-coding`
2. 点卡片右侧 **"运行一次"** 按钮
3. 观察执行进度(右下角)
4. 完成后查看 `d:\workspace\my-trae-helper\logs\daily-vibe-coding\<今日日期>\`
5. 应包含 5 份 md:
   - `external-report.md`(调研)
   - `self-audit.md`(自检)
   - `upgrade-guid.md`(升级建议)
   - `SUGGESTIONS.md`(★核心审批入口★)
   - `INDEX.md`(本日目录索引)
   - `implementation-log.md`(空模板)

6. 打开 **SUGGESTIONS.md** 看 🟢/🟡/🔴/✋ 4 栏,这就是你的**今日决策面板**

---

## 调整与停止

| 操作 | 路径 | 说明 |
|------|------|------|
| 暂停任务 | 自动化列表 → 任务卡片右侧开关 → 关 | 保留配置,仅停跑 |
| 恢复任务 | 同上 → 开 | 次日 09:00 恢复 |
| 删除任务 | 卡片 → 右下角删除 | 配置丢失 |
| 修改触发时间 | TRAE Work 当前不支持(需删 + 新建) | 重新跑方式 A/B |
| 修改 prompt 内容 | **支持** → 任务卡片 → 编辑 → 改"任务内容"字段 | prompt 可改,运行模式/环境/位置不可改 |

---

## 失败兜底

| 现象 | 原因 | 修复 |
|------|------|------|
| 任务不自动跑 | 当前运行模式 ≠ 任务运行模式 | 切到 Work 模式 |
| 跑完后无产物 | 路径不在工作目录 | 检查 `d:\workspace\my-trae-helper` 是当前工作区 |
| 产出 5 份 md 缺 1 份 | agent 中途报错 | 查看 TRAE Work 执行历史 → 重跑 |
| SUGGESTIONS.md 全 🟢 | agent 偷懒,没自我分级 | 重新发 prompt 强调"必须分级" |
| agent 直接改了仓库 | 违反关键约束 #1 | 立刻回滚 + 改 prompt 强调"严禁修改" |

---

## 与 change-guard-approver 的关系

**两层保护**:

1. **TRAE Work 定时任务 prompt** 规定 agent 不改仓库(软约束,靠 prompt)
2. **change-guard-approver.mjs**(已在仓库部署):
   - 即使 agent 强行 commit 修改 .husky / scripts / src 等 Tier 3/4 路径,**pre-commit + pre-push 会物理阻断**
   - 强制要求 release-manager 角色审批

→ **双保险**: 即使 TRAE 定时任务失控,git hooks + 审批 gate 仍能兜底。