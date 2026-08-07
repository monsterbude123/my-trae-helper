# DOC SYNC（文档同步）

> 知识一致性对齐 — 确保文档反映最新代码状态。

---

## 同步时机

| 变更类型 | 同步时机 |
|----------|---------|
| 新增模块/接口 | 编码前 |
| 修改现有接口 | 编码前 |
| Bug 修复 | 编码后 |
| 纯 UI 样式调整 | 无需同步 |

---

## 同步范围

### P0（必须同步）
- 模块文档：接口契约表、数据模型、职责边界
- 产品文档：功能描述、用户流程
- 契约文档：从 contracts/ 回流到模块文档

### P1（应该同步）
- 关联模块表
- 状态标记（beta → stable）
- 版本号递增

### P2（可以延后）
- ARCHITECTURE.md（模块增减时）
- DECISIONS.md（架构决策时）

---

## 一致性自检

同步完成后：
- [ ] 接口一致性：文档中每个接口，代码中都有对应实现
- [ ] 模型一致性：文档描述的数据模型与实际类型一致
- [ ] 依赖一致性：文档记录的模块依赖与实际 import 一致

---

## 禁止写入

| 禁止 | 原因 |
|------|------|
| Review 评分 | 施工日志，不是架构知识 |
| DOC SYNC 时间戳 | 流程元数据 |
| Bug 修复过程 | 修复过程不是系统描述 |
| 实现细节 | 属于"怎么做"，不是"是什么" |

---

## 迷你同步（小改动）

≤3 文件，单模块内：
1. 更新模块文档中对应的接口/模型描述
2. 添加变更记录
3. 不需要完整同步报告

---

## 文档索引集成（可选）

如已安装 doc-map-manager：
- **定位需更新文档**: `query-index.py --grab "关键词"` → 0.3s 精确定位到行号 + 正文
- **验证文档变更**: `build-index.py --diff` → 检测 docs/ 变更范围
- **更新索引**: `build-index.py --incremental` → 同步后维护索引

未安装时降级为 grep + glob（文件级定位，允许但大项目不推荐）。

---

## 文档索引器范围白名单/黑名单（V10.8 NEW — doc-mgr 噪音修复）

> 根因：未规定索引器扫描范围 → doc-map-manager / spec-knowledge-extract / 自定义 grep 扫描器
> 默认扫描整个 docs/ → archive/bugs/reports/history/_invalidated 等噪音目录被索引 → 事实索引被污染。
> 治理：显式白/黑名单，索引器启动前必读本段，违反 = 索引无效。

### 白名单（可索引 layer=fact 目录）

- `docs/contracts/`、`docs/modules/`、`docs/ARCHITECTURE.md`
- `docs/specs/{active}/`（仅活跃 feature，排除 archive 子目录）
- `docs/api-endpoints/`、`docs/domain-models/`、`docs/events/`（spec-knowledge-extract 产物，layer=fact）
- `AGENTS.md`

### 黑名单（索引器必须显式 exclude）

| 目录/文件 | layer | 排除原因 |
|----------|:-----:|---------|
| `docs/archive/`、`docs/specs/archive/` | log | 归档不可变，索引即污染 |
| `docs/bugs/` | process | Bug 修复记录，非事实源 |
| `docs/reports/` | log | Review 报告，非事实源 |
| `docs/history/`、`.history.md` | log | 完工签名薄，按需 grep |
| `_invalidated/` | process | 回流隔离旧产物 |
| `diagnostic/` | process | 诊断手记 |
| `docs/DECISIONS.md` | process | 决策过程记录 |
| 任何 frontmatter 含 `layer: process` 或 `layer: log` 的文档 | — | 按 layer 标签判定 |

### 明文规定

```
1. 任何文档索引器（doc-map-manager / spec-knowledge-extract / 自定义 grep 扫描）
   启动前必须读本段，确认扫描范围符合白/黑名单
2. 索引器实现必须显式 exclude 黑名单目录，禁止"默认全扫描"
3. 违反 = 索引结果无效，必须重建索引
4. 外部索引器示例: doc-map-manager skill 的 build-index.py
```

### 反例

- 现象：索引器默认扫描 docs/ → query 返回 archive 旧契约 + bugs 修复记录 → agent 拿到过时事实
- 根因：索引器未配置 exclude，默认全扫描污染事实层
- 教训：索引器必须显式 exclude 黑名单，启动前必读 doc-sync.md §索引器范围
- 来源：absorption-plan §一（doc-mgr 噪音修复 P0）
