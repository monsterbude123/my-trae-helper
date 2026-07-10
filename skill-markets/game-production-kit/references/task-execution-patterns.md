# 任务执行模式 (Task Execution)

> 吸收自 godogen task-execution.md。标准实现循环 + 导入素材检查。

## 默认实现循环

> 先 Risk Slice 后 Main Build。每个任务前必须读上下文文件。

```
1. 读 STRUCTURE.md + 当前模块 -> 了解上下文
2. 导入素材 -> 确认文件在正确位置
3. 生成/更新场景构建器 -> 按 Build Order 运行
4. 写运行时脚本
5. 编译 -> 修复编译错误
6. 运行时验证
7. 读日志（不只是退出码）
8. 更新状态文件
9. 重复直到停止条件达成
```

## 引擎特定循环

### Godot

```
1. 读 STRUCTURE.md + project.godot + 相关 .csproj/.gd 文件
2. godot --headless --import
3. 生成 scene builder -> 按 Build Order 运行
4. 写 .gd / .cs 脚本
5. dotnet build     # C# 项目
6. 修复编译错误
7. godot --headless --quit    # 验证启动
8. 运行时烟雾测试
9. 读日志 + 更新 STRUCTURE.md
```

### Bevy

```
1. 读 STRUCTURE.md + Cargo.toml + 相关 .rs 文件
2. 素材放 assets/ 下
3. 写 ECS systems
4. cargo fmt -> cargo check
5. 修复编译错误
6. cargo run (桌面) 或 xvfb-run (无头)
7. 读日志 + 更新 STRUCTURE.md
```

### Babylon.js

```
1. 读 STRUCTURE.md + package.json + 相关 .ts 文件
2. 素材放 public/ 下
3. 写 TypeScript 场景脚本
4. npm run dev Vite HMR -> 检查浏览器
5. Playwright screenshot -> 验证
6. 更新 STRUCTURE.md
```

### WebGAL

```
1. 读 story-design.md + asset-manifest.md + 已有 .txt 文件
2. 写场景脚本 (.txt)
3. 放入素材到场景目录
4. npm run dev 本地预览
5. 验证对话逻辑
```

## 导入素材检查三要素

```
1. 文件在素材目录下 (assets/ / public/ / figure/ 等)
2. 运行时路径与实际文件路径一致
3. 已运行导入命令 (godot --headless --import / cargo check / npm run dev)
```

## 停止条件

每个任务完成后检查以下条件：

```
- 编译通过 (无 error，允许已知 warning)
- 引擎无启动错误
- 素材已正确导入
- 运行时验证完成 (烟雾测试)
- proof bundle 存在 (screenshots/result/{N}/)
- STRUCTURE.md 已更新
```

> 所有条件满足 → 该任务标记为 DONE → 进入下一个任务
