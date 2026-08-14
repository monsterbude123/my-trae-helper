# 记忆

> 将对后续协作有价值的偏好与规则保存为"记忆"。TRAE Work 支持**全局记忆**和**项目记忆**。

## 类型与存储

| 类型 | 生效范围 | 存储位置 |
|------|----------|----------|
| **全局记忆** | 当前用户本地的**所有项目** | macOS/Linux: `~/.trae-cn/memory/user_profile.md`<br>Windows: `%userprofile%/.trae-cn/memory/user_profile.md` |
| **项目记忆** | 当前用户本地的**当前项目** | macOS/Linux: `~/.trae-cn/memory/projects/{project_path}/project_memory.md`<br>Windows: `%userprofile%/.trae-cn/memory/projects/{project_path}/project_memory.md` |

> 记忆数据存储于本地，**无法跨电脑共享**。

## 不会被保存为记忆的信息

- 一次性或临时指令
- 模糊、不确定的偏好
- 敏感信息（密码、个人隐私）

> 以上信息除非用户明确指定保存。

## 启用记忆

**设置 → 规则与记忆 → 记忆** → 打开 **记忆** 开关。

## 手动管理

**设置 → 规则与记忆 → 记忆** → **全局** / **项目** 页签 → 点击用户记忆/项目记忆区域 → 系统打开文件夹并高亮 `user_profile.md` 或 `project_memory.md` → 直接编辑文件。

## 让 AI 主动管理

| 方式 | 示例 |
|------|------|
| **自动创建** | AI 自动识别有价值的偏好或规则并创建记忆 |
| **自动更新** | AI 识别偏好/规则变化时主动更新记忆 |
| **按要求创建** | "记住我偏好使用中文回答" → AI 写入对应记忆文件 |
| **按要求修改** | "以后叫我 David" → AI 更新对应记忆 |
| **按要求删除** | "删除关于我偏好的称呼的记忆" → AI 从记忆文件删除 |