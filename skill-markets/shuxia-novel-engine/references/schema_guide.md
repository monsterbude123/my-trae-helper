# Schema 设计指南

> 版本: v1.0 · 日期: 2026-06-16 · 来源: skill-novel-engine/references/

> 如何为你的亚文化项目建立结构化数据库
> 配合 `skill-novel-engine` 使用

---

## 为什么需要 Schema

Markdown 文件适合人类阅读和 AI 会话。但你需要的查询——"找出所有涉及灵压梯度的章节中，哪些同时涉及严峰"——文件系统做不到。Schema + SQLite 提供结构化查询能力。

## 三层表结构

### L0 底层（世界规则）

```sql
- axiom          公理定义
- timeline_anchor 时间线锚点
- physics_constant 物理常量
```

### L1 协议层（谁/什么）

```sql
- faction        势力
- character      角色（含战力/速度/动机/行为锚点）
- character_relation 角色关系
```

### L2 表示层（概念/依赖）

```sql
- concept        概念注册（含废弃别名）
- concept_chapter_ref 概念-章节引用
- tech_node      科技树节点
- tech_dependency 科技树依赖（有向图）
- artifact       装备/法器
```

### L3 会话层（叙事）

```sql
- volume         卷
- chapter        章
- scene          场景
- foreshadow     伏笔
- chapter_bridge 章节衔接
```

## 最小启动表

如果你的项目刚开始，至少需要这 4 张表：

```sql
CREATE TABLE axiom (id, name, statement, allows, forbids);
CREATE TABLE character (id, name, motivation, allowed_methods, forbidden_methods);
CREATE TABLE concept (id, name, canonical_definition, deprecated_aliases);
CREATE TABLE chapter (num, title, volume, phase);
```

## 从 Markdown 同步

引擎的 `scripts/check.py` 内置了 Markdown → SQLite 同步能力。只需确保：
1. 宪法写在 `.md` 文件中，每条公理有 `allows`/`forbids` 字段
2. 角色档案包含 `allowed_methods`/`forbidden_methods` 字段
3. 概念定义标注了 `deprecated_aliases`

## 通用化说明

- 所有表名、字段名是引擎的约定——可改但需同步更新 scripts
- 表结构参考 `../schema/schema.sql`（万古余烬的完整示例）
- 你可以只建需要的表，引擎会跳过不存在的表
