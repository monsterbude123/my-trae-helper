# Phase 0 启动协议

> 参照 Claude-Code-Game-Studios `/start` + `/setup-engine` + godogen `publish.sh --engine` 模式。

## 协议流程

```
Phase 0 激活:
    │
    ├── 场景 A: 用户已指定引擎
    │     ├── 验证引擎在路由表中存在（§3 引擎替换方案）
    │     ├── 不存在 → 告知可用引擎列表 → 用户选择 or 回退场景 B
    │     ├── 存在 → 记录引擎类型（写入 project-state）
    │     └── 进入 Phase 1
    │
    ├── 场景 B: 用户未指定引擎
    │     ├── 加载 engine-decision-guide.md
    │     ├── 引导对话: Q1 类型 → Q2 平台 → Q3 技术偏好
    │     ├── 综合推荐 → 用户确认
    │     └── 记录 → 进入 Phase 1
    │
    └── 场景 C: 用户拒绝选择（"随便""你定"）
          ├── VN 默认 → WebGAL，告知用户原因
          ├── 非 VN → 告知"需选定引擎"，再次请求
          └── 记录 → 进入 Phase 1
```

## 引擎验证规则

- 引擎在路由表中 → 可用（即使标记"待建"，告知用户状态）
- 引擎不在路由表中 → 不可用，展示可用列表
- 标记为 "(ext)" → 外部技能，需检查是否已安装
- 标记为 "(待建)" → 告知用户该引擎尚未接入，是否换引擎 or 等待

## 记录格式

Phase 0 结束时记录：

```
引擎: [engine-name]
类型: [vn / 2d / 3d]
平台: [web / desktop / mobile / all]
脚本技能: [skill-name]
构建技能: [skill-name]
```

示例：

```
引擎: WebGAL
类型: vn
平台: web
脚本技能: webgal-scripting
构建技能: webgal-engine-build
```
