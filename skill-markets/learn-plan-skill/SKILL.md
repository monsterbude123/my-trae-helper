---
name: learn-plan-skill
description: Create structured technical learning plans (导学 + 实操 lab) for any topic. Invoke when user asks to create learning roadmaps, study plans, skill trees, or course outlines. Follows study-guide.md as theory + lab-*.md as hands-on pattern with numbered progressive directories.
intent: Create structured technical learning plans (导学 + 实操 lab) ...
category: other
audience: [designer]
---
# Learn Plan Skill

## 用途

当你需要为某个技术主题编排学习计划时，使用此 Skill。它定义了"导学 + 实操"双文档架构的标准模板和流程。

## 触发条件

- 用户创建学习路线图 / 学习计划 / 技能树
- 用户需要针对某个技术栈的系统化培训材料
- 用户要求"帮我整理 X 的学习路径"

## 核心架构

```
docs/learning-plan/
├── README.md                     # 总览 + 路线图 + 学时汇总
├── mock-interview-qa.md          # (可选) 模拟面试 QA
│
├── 01-topic-name/                # 每个模块一个编号目录
│   ├── study-guide.md            # 导学：概念、原理、学习路径
│   ├── lab-01-subtopic-name.md   # 实操：命令、代码、检验点
│   ├── lab-02-subtopic-name.md
│   └── ...
│
└── 02-next-topic/
    └── ...
```

## study-guide.md 模板

```markdown
# 编号 — 模块标题（学时）

> 目标：一句话说清楚学完能做什么
> 对照：可选的前置模块引用

---
## 知识全景

### 这是什么
> 一句话定义 + 学习者技术栈类比（如 Java 类比）

2-3 句解释本质

### 核心概念
| 概念 | 说明 | 类比（学习者技术栈） |
|------|------|-------------------|
| **概念1** | 说明 | 类比 |
| **概念2** | 说明 | 类比 |

### 解决的问题
说明核心痛点

### 优势与缺点
| 优势 | 缺点 |
|------|------|
| ... | ... |

### 平替方案
| 方案 | 定位 | 与本章技术的关系 |
|------|------|----------------|
| ... | ... | ... |

### 衍生方案
| 方案 | 说明 |
|------|------|
| ... | ... |

---

## 你的起点 / 痛点（面向学习者画像）

## Day 1：子主题 A（N h）

### 1.1 概念（类比熟悉的技术栈）
### 1.2 核心代码示例

## Day 2：子主题 B（N h）

## 检验清单
- [ ] 能 XX
- [ ] 能 XX

## 不必要学的内容
- ❌ 不要 XX（说明原因）

## 案例实战
[实验1](./lab-01-xxx.md)
[实验2](./lab-02-xxx.md)
```

## lab-*.md 模板

```markdown
# Lab XX-X：标题

> 目标：一句话
> 对照导学：`study-guide.md` §X.X

---

## 步骤 1：XX（附完整可执行命令）

## 步骤 2：XX

## 常见坑（表格）

## 检查点
- [ ] 跑通了 XX
- [ ] 理解了 XX
```

## 设计铁律

1. **递增编号**：目录用 `01-` `02-` 前缀，保持扩展性
2. **双文档分离**：study-guide.md 不动（导学），lab-*.md 不断追加（实操）
3. **类比映射**：每个新概念必须有学习者已有技术栈的类比（如 Java→Python、Spring→LangChain）
4. **知识全景先行**：study-guide 头部 `---` 后紧跟 `## 知识全景`，包含：这是什么、核心概念（含类比表）、解决的问题、优势与缺点、平替方案、衍生方案。让学习者在看代码前先建立概念地图
5. **案例实战收尾**：study-guide 末尾 `## 不必要学的内容` 后添加 `## 案例实战`，列出该模块所有 lab-*.md 的引用链接
6. **检查点驱动**：每个 lab 末尾有 `检查点` 清单，跑通才算过
7. **不必要学清单**：每个 study-guide 末尾列出"暂时不学的内容"及原因
8. **学习者画像前置**：study-guide 开头必须描述"你的起点/痛点"
9. **命令可复制**：所有命令都是完整可复制执行的，不省略参数
10. **模拟面试 QA**：学完所有模块后补充 mock-interview-qa.md

## 学习者画像字段

```markdown
| 维度 | 现状 | 对学习的影响 |
|------|------|-------------|
| **Java** | 5 年经验 | 强 OOP 思维可直接迁移 |
| **Python** | 仅基础 | 需要补习包管理 |
| **AI Coding** | 7 个月 Vibe Coding | 已知道产品形态，缺底层理解 |
```

## 与现有模块的关联

学习计划应标注：
- `README.md` 中列出模块间的依赖关系（前置模块编号）
- lab 文件头部标注 `对照导学: study-guide.md §X.X`
- 每个 lab 的检查点覆盖导学中的概念点

## 版本管理

- `v1.0`：基础学习计划（01-11 模块）
- `v2.0`：进阶扩展（12+ 模块）
- 每次扩展新增目录即可，不动已有模块