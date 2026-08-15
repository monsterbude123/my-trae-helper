---
name: fullstack-auto
description: 自动驾驶项目配置 — 一站式部署 fullstack + coding-xinfa + goal-mode + GitNexus + ponytail 的完整项目级配置模板。从 shuxia-project 实战验证中通用化提取,不是另一个技能包,而是项目初始化时可复制的 .trae/ 配置。
version: 1.0.0
---

# fullstack-auto — 自动驾驶项目配置

> 一站式部署 fullstack + coding-xinfa + goal-mode + GitNexus + ponytail 的完整项目级配置模板。
> 从 shuxia-project 实战验证中通用化提取。不是另一个技能包，而是项目初始化时可复制的 `.trae/` 配置。

## 定位

fullstack-auto 解决一个核心问题：**装好了 fullstack4traev7 之后，项目层面还需要配什么？**

答案在 `templates/` 目录里：
- `templates/AGENTS.md` → 项目入口，集成四个技能包 + 决策链 + 门禁 + 铁律
- `templates/rules/` → `.trae/rules/` 的通用化版本，剥离了项目专属内容

## 使用方法

```bash
# 1. 安装 fullstack4traev7 + coding-xinfa + goal-mode skills
# 2. 复制模板到项目
cp -r skill-markets/fullstack-auto/templates/AGENTS.md ./AGENTS.md
cp -r skill-markets/fullstack-auto/templates/rules/* .trae/rules/

# 3. 填写项目专属配置（见 AGENTS.md 底部「项目专属配置区」）
```

## 模板文件

| 文件 | 用途 | 泛化程度 |
|------|------|---------|
| `AGENTS.md` | 项目入口，四技能包集成 + 决策链 + 门禁 + 铁律 | 通用（底部有项目专属配置区占位） |
| `rules/编码心法.md` | coding-xinfa 宪法层 — Goal Mode + 表达风格 | 100% 通用 |
| `rules/agent协调协议.md` | 主上下文只协调不执行的协议 | 100% 通用 |
| `rules/strict.md` | 严格模式 — 11 铁律 + 阶段门禁 + GitNexus + ponytail | 通用（已剔除项目专属引用） |
| `rules/原型设计.md` | 低保真 ASCII 线框图四状态原型方法论 | 通用 |
| `rules/视觉验收.md` | 大脑-眼球流水线 UI 验收 | 通用（工具路径需按项目适配） |
| `rules/gitnexus-铁律.md` | GitNexus 是代码分析唯一通道 | 通用（repo 路径用占位符） |
| `rules/测试避坑.md` | AI 辅助开发测试避坑方法论 | 通用方法论（剥离了项目专属变量名） |

## 与 fullstack4traev7 的关系

```
fullstack4traev7（技能包）          fullstack-auto（项目配置模板）
  ├── 9 Agent 流水线                  ├── AGENTS.md（如何加载技能包）
  ├── AOP 自检 + Schema QA            ├── .trae/rules/（项目级规则）
  ├── 铁律 + 门禁 + 量化验收           ├── 决策链（需求到 Agent 的路由）
  └── 驾驶舱 + 状态卡                 └── 项目专属配置区（用户填写）
```

fullstack4traev7 是引擎，fullstack-auto 是把引擎装进具体项目的安装说明书。

## 项目初始化后检查清单

```
[ ] AGENTS.md 已复制到项目根目录，项目专属配置区已填写
[ ] .trae/rules/ 下 7 个文件已就位
[ ] .trae/hooks/ 配置完成（通过 fullstack4traev7 env-init.py --fix）
[ ] GitNexus 索引已建立
[ ] 目录结构（docs/modules/、docs/specs/changes/、docs/contracts/）已建立
[ ] 技能包条件触发确认：coding-xinfa（始终加载）、goal-mode（/goal 触发）、fullstack（检测到 spec/contract 相关需求时加载）、GitNexus（代码分析时加载）、ponytail（简单任务时加载）
```
