# V11 paths 配置化协议(§15)

> **来源**:V12 SKILL.md §15(case 2 desktop-pet-v11 audit-fix 蒸馏 — AGENTS.md paths.archive 漂移)
> **蒸馏日期**:2026-08-19(从 SKILL.md §15 抽出)
> **目的**:所有路径必须配置化,禁止脚本中字符串硬编码,5 个相关脚本必须走 `_lib_paths.py`

---

## §15.1 必须配置的 4 类路径(V11.8.7.1 — 移除 changes_archive)

```yaml
# .trae/fullstack4traev11.config.yaml
paths:
  archive: docs/archive/done               # spec-purge.py 写入路径(单真相源,V11.8.7.1 起)
  state_card_project: docs/specs/.state-card.md
  state_card_change: docs/specs/changes/{id}/.state-card.md
  state_card_bug: docs/bugs/{id}/.state-card.md
```

---

## §15.2 单一访问源(V11.8.7.1 — 删除 get_changes_archive_dir)

- 任何脚本/agent **必须**通过 `scripts/_lib_paths.py` 提供:
  - `load_paths(project_root)` → dict,读 .trae/fullstack4traev11.config.yaml `paths.*`,缺则用 V11.8.7.1 默认值(`{archive: docs/archive/done}`)
  - `get_archive_dir(project_root)` → pathlib.Path,返回 `paths.archive` 解析值
  - `get_state_card_path(project_root, level, id)` → project/change/bug 三类统一
- **禁止** 脚本中字符串硬编码:`"docs/archive"` / `"docs/specs/archive"` / `"docs/specs/changes/archive"`
- 5 个脚本必须有 `try/except ImportError fallback`(老环境无 _lib_paths 时不阻断)
- **V11.8.7.1 REMOVED**:`get_changes_archive_dir()` 函数已删除(`changes_archive` 双路径废弃),不得复活。

---

## §15.3 自验收协议(必跑)

```bash
# 1. 路径单源一致性:5 个脚本不应硬编码路径字符串
grep -rEn '"docs/archive"|"docs/specs/(changes/)?archive"' skill-markets/fullstack4TraeV11/scripts/*.py
# → 期望 0 命中(除 _lib_paths.py 的默认值 fallback 外)

# 2. _lib_paths.py 函数二件套存在(V11.8.7.1:删除 get_changes_archive_dir)
grep -E "^(def load_paths|def get_archive_dir)" skill-markets/fullstack4TraeV11/scripts/_lib_paths.py
# → 期望 2 行命中

# 3. config.example.yaml paths 字段(V11.8.7.1:不含 changes_archive)
grep -A 3 "^paths:" skill-markets/fullstack4TraeV11/references/config.example.yaml
# → 期望不含 changes_archive
```

---

## §15.4 反例(违反任一 = REJECT)

| 反例 | 后果 |
|------|------|
| 脚本中 `pathlib.Path("docs/archive/done")` | 与 _lib_paths.py 默认值漂移 |
| 文档描述 `docs/specs/archive/` 或 `docs/specs/changes/archive/` | 与 spec-purge.py 写入路径不一致 |
| 缺 `_lib_paths.py` fallback | 老环境跑挂 |
| AGENTS.md 写 `paths.foo` 但 SKILL.md 无声明 | sub-agent 无法识别 |
| **V11.8.7.1 NEW**:`get_changes_archive_dir()` 复活 | 多 archive 路径死灰复燃,见 V11-AP16 |

---

## §15.5 关联引用

- [trap-instructions.yaml AP-15](trap-instructions.yaml) — V11-AP15 反例
- [scripts/_lib_paths.py](../scripts/_lib_paths.py) — 路径单源库
- [references/config.example.yaml](config.example.yaml) — paths 字段定义
- [config-files-glossary.md](config-files-glossary.md) — .trae/fullstack4traev11.config.yaml 字段表
- [project-structure.md](project-structure.md) — V11 标准目录树