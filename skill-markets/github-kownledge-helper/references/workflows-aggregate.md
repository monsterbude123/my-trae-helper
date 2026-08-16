# 工作流：聚合目录处理（§5）

> 从 [workflows.md](./workflows.md) 拆出，避免主文件超 200 行。
> 单文件 ≤ 200 行。

## 5. 聚合目录处理（2026-08-13 新增）

当用户按主题分组（ai-app / ai-prompt / ai-skills-sets 等），**每个子项目都可能是独立 git 仓库**。

### 识别阶段

```
LS 顶层 → 看到聚合目录名
递归扫描 .git → 揭示子项目真实身份（LS 默认不显示隐藏 .git）
用 Get-ChildItem -Recurse -Force + Test-Path .git 找到全部 git 仓库
```

### 决策矩阵

| 场景 | 处理 |
|------|------|
| 子项目是独立 git 仓库 | 全部纳入 manifest，path 保留聚合层级 |
| 子项目无 .git（非 git 目录） | 提示用户，可能需手动 clone 或保留为本地资源 |
| 同 full_name 重复 | 去重，按 path 区分或删除重复 |

### manifest schema 扩展

聚合场景下加 `group` 字段（schema 1.1）：

```json
{
  "name": "Pixelle-Video",
  "owner": "AIDC-AI",
  "full_name": "AIDC-AI/Pixelle-Video",
  "group": "ai-app",                          // ← 新增
  "path": "repos/ai-app/AIDC-AI__Pixelle-Video",
  "docs_path": "docs/ai-app/AIDC-AI__Pixelle-Video"
}
```

### docs/ 结构

聚合场景下 docs/ 保留聚合层级（与 repos/ 对应），便于按主题浏览。
跨仓检索走 doc-map-manager 忽略路径层级，全局 --lookup 命中所有。