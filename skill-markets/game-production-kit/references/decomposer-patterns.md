# 任务分解模式 (Decomposer)

> 吸收自 godogen decomposer.md。分析游戏、识别实现风险、定义验证标准。输出 PLAN.md。

## 核心逻辑

把完整游戏设计分解为 **Risk Tasks**（需隔离实现）和 **Main Build**（常规开发）。

## 风险分类（需隔离）

以下任务因"失败不可预测"且"与其他系统混合时错误模糊"需要隔离实现：

- 程序化生成（地形/关卡/迷宫）
- 程序化动画（IK/物理驱动）
- 精灵/角色动画（多帧+状态机）
- 复杂载具物理
- 自定义着色器
- 运行时几何生成
- 动态导航（运行时 NavMesh）
- 复杂摄像机系统（多目标追踪/平滑过渡）

## 隔离策略

```
1. 每个 Risk Task 单独一个 feature branch
2. 验证标准必须 probe 动态过渡（如 idle→walk, walk→attack）
3. 不依赖静态截图匹配 reference.png
4. 与 Main Build 的集成点提前定义（输入/输出接口）
```

## PLAN.md 输出格式

```markdown
## Risk Tasks

### {Task Name}
- **Why isolated**: {不可预测性原因}
- **Approach**: {隔离实现策略}
- **Input**: {需要的外部数据/素材}
- **Output**: {产出物 + 集成接口}
- **Verify**: {验证标准，含动态过渡检查}

---

## Main Build

### {Feature Group}
- **Assets needed**: {素材清单}
- **Verify**:
  - 通用: {通用验证}
  - 游戏特定: {游戏特定验证}
  - Reference 一致性: {与 visual-target reference.png 对比}
  - Proof bundle: {screenshots/result/{N}/}
```

## 验证标准设计原则

```
❌ 静态截图对比 reference.png  → 只适合场景构图
✅ 动态过渡 probe              → idle→walk 无跳帧, walk→attack 连贯
✅ 边界条件覆盖                → 两个角色同时在屏幕上
✅ 输入验证                    → 触摸/点击/键盘 都能触发对话
```
