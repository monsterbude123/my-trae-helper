"""
V11 paths 配置加载器(2026-08-18 V11.8.7.1 — 单 archive 路径,移除 changes_archive)

V11.8.7.1 修复:
  - 移除 `changes_archive: docs/specs/changes/archive` 双路径
  - 真相源 = `docs/archive/done/{change-id}/`(由 spec-purge.py 写入)
  - 唯一路径键 = `archive`(V11 Constitution Article VIII 不可变)
  - 删 `get_changes_archive_dir()` 函数(残留兼容,无调用方)

目的:把 V11 散落在 5 处脚本的 archive 路径硬编码,收敛到
    .trae/fullstack4traev11.config.yaml 的 paths.archive 字段。

加载顺序:
  1. 读 .trae/fullstack4traev11.config.yaml
  2. 若存在 paths.archive 字段 → 用配置值
  3. 若缺字段/缺文件/yaml 未装 → 用默认值

默认值与现状一致(spec-purge.py 走 docs/archive/done;init-from-zero.py 走 docs/archive/done)。

用法:
  from _lib_paths import load_paths
  paths = load_paths(project_root)
  archive_dir = project_root / paths["archive"] / change_id

Exit:不抛异常(失败回退到默认值)。
"""
import pathlib
from typing import Dict

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

# V11.8.7.1: 单 archive 路径(真相源),删除 changes_archive 双键
DEFAULT_PATHS: Dict[str, str] = {
    "archive": "docs/archive/done",
}

CONFIG_FILENAME = "fullstack4traev11.config.yaml"


def load_paths(project_root: pathlib.Path) -> Dict[str, str]:
    """加载项目 paths 配置。

    Args:
        project_root: 项目根目录。

    Returns:
        dict:仅含 archive 路径键。永不抛异常。
    """
    paths = dict(DEFAULT_PATHS)
    config_path = project_root / ".trae" / CONFIG_FILENAME

    if not config_path.exists() or yaml is None:
        return paths

    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        if not isinstance(cfg, dict):
            return paths
        user_paths = cfg.get("paths") or {}
        if not isinstance(user_paths, dict):
            return paths
        for key in DEFAULT_PATHS:
            if key in user_paths and isinstance(user_paths[key], str) and user_paths[key].strip():
                paths[key] = user_paths[key]
    except Exception:
        # 配置损坏不阻断,回退默认值
        pass

    return paths


def get_archive_dir(project_root: pathlib.Path) -> pathlib.Path:
    """返回 archive 根目录(不含 change_id 子层)。

    V11.8.7.1: 唯一真相源 = `docs/archive/done/`(V11 Constitution Article VIII)。
    """
    paths = load_paths(project_root)
    return project_root / paths["archive"]