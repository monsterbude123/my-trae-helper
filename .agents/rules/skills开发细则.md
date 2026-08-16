---
description: skills开发细则需要注意的事项
alwaysApply: true
enabled: true
updatedAt: 2026-08-14
provider:
---

# skills开发细则需要注意的事项
- MUST: 新增技能先把todo写到skill的todos/task.md todos/checklist.md文件里(防止事情做一半),skill对应的功能开发完，门禁进行检查全部agent复核之后再删除todo。
- MUST: 有需要配置环境的，把skill专属的环境变量示例写到 skills目录下的.env.example。
- MUST: 运行测试的时候，使用脚本自动去项目的根目录加载.env。
# 反例
- MUST NOT: 有需要配置环境的，把skill没有专属的.env.example。
- MUST NOT: 运行测试的时候，没有使用脚本自动去项目的根目录加载.env。
- MUST NOT: skills 的脚本或者md里面有具体的key的硬编码，导致泄露信息。
