"""
模型仓库扫描器

扫描 {repo_path} 下的模型文件，与数据库对比，增量更新。
支持的文件格式：.safetensors, .ckpt, .pt, .gguf
目录型模型：通过 config.json 或 .yaml 配置文件识别。
"""

import hashlib
from pathlib import Path
from fnmatch import fnmatch

from .db import Database


# 目录名 → 模型类型映射
DIR_TYPE_MAP = {
    "checkpoints": "checkpoint",
    "loras": "lora",
    "diffusion_models": "diffusion_model",
    "text_encoders": "text_encoder",
    "vae": "vae",
    "controlnet": "controlnet",
    "upscale_models": "upscaler",
    "clip_vision": "clip_vision",
    "audio_encoders": "audio_encoder",
    "llm": "llm",
    "tts": "tts",
}

MODEL_EXTENSIONS = (".safetensors", ".ckpt", ".pt", ".gguf")


def _sha256_file(filepath: Path) -> str:
    """计算文件的 SHA256"""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _should_exclude(name: str, exclude_patterns: list[str]) -> bool:
    """检查文件名/目录名是否匹配排除规则"""
    for pattern in exclude_patterns:
        if fnmatch(name, pattern):
            return True
    return False


def _infer_family(relative_path: str) -> str:
    """从相对路径推断模型家族。

    路径格式: {type_dir}/{family}/{filename}
    例如: checkpoints/flux/flux1_dev.safetensors → flux
          loras/sdxl/my_lora.safetensors → sdxl
    """
    parts = Path(relative_path).parts
    if len(parts) >= 2:
        return parts[1]  # 第二段作为 family
    return "unknown"


def _make_model_id(filename: str, type_dir: str) -> str:
    """生成全局唯一的模型 ID

    ID 格式: {type_dir}_{basename}
    例如: checkpoints_flux1_dev
    """
    stem = Path(filename).stem
    clean = stem.replace(" ", "_").lower()
    # 保留字母数字和下划线
    clean = "".join(c for c in clean if c.isalnum() or c == "_")
    return f"{type_dir}_{clean}"


def scan(db: Database, repo_path: str, exclude_patterns: list[str] = None):
    """扫描仓库并增量更新数据库。

    返回: (found, new, updated, errors)
    """
    if exclude_patterns is None:
        exclude_patterns = ["._*", "*.tmp", ".metadata-only"]

    repo = Path(repo_path)
    if not repo.exists():
        raise FileNotFoundError(f"仓库路径不存在: {repo_path}")

    found = 0
    new = 0
    updated = 0
    errors = []

    for dir_entry in sorted(repo.iterdir()):
        if not dir_entry.is_dir():
            continue
        if dir_entry.name.startswith(".") or dir_entry.name == "_archive":
            continue
        if _should_exclude(dir_entry.name, exclude_patterns):
            continue

        model_type = DIR_TYPE_MAP.get(dir_entry.name)
        if not model_type:
            continue

        # 扫描文件型模型
        for filepath in sorted(dir_entry.rglob("*")):
            if not filepath.is_file():
                continue
            if filepath.suffix.lower() not in MODEL_EXTENSIONS:
                continue
            if _should_exclude(filepath.name, exclude_patterns):
                continue

            found += 1
            try:
                relative = str(filepath.relative_to(repo))
                size_gb = round(filepath.stat().st_size / (1024**3), 4)
                sha256 = _sha256_file(filepath)
                model_id = _make_model_id(filepath.name, dir_entry.name)
                family = _infer_family(relative)

                data = {
                    "id": model_id,
                    "name": filepath.stem,
                    "type": model_type,
                    "family": family,
                    "task": "",
                    "file_path": relative,
                    "file_size_gb": size_gb,
                    "sha256": sha256,
                    "source_url": "",
                    "license": "",
                    "status": "active",
                    "notes": "",
                }
                is_new = db.upsert_model(data)
                if is_new:
                    new += 1
                else:
                    updated += 1
            except Exception as e:
                errors.append(f"{filepath.name}: {e}")

        # 扫描目录型模型（有 config.json 或 yaml 的目录）
        for subdir in sorted(dir_entry.iterdir()):
            if not subdir.is_dir():
                continue
            if _should_exclude(subdir.name, exclude_patterns):
                continue
            has_config = (subdir / "config.json").exists()
            has_yaml = list(subdir.glob("*.yaml")) or list(subdir.glob("*.yml"))
            if not (has_config or has_yaml):
                continue
            # 避免重复计数（文件型模型可能和目录型重叠）
            has_model_files = any(
                f.suffix.lower() in MODEL_EXTENSIONS
                for f in subdir.rglob("*") if f.is_file()
            )
            if has_model_files:
                continue  # 已经在文件型扫描中处理

            found += 1
            try:
                total_size = sum(
                    f.stat().st_size for f in subdir.rglob("*") if f.is_file()
                )
                size_gb = round(total_size / (1024**3), 4)
                relative = str(subdir.relative_to(repo)) + "/"
                model_id = _make_model_id(subdir.name, dir_entry.name)

                data = {
                    "id": model_id,
                    "name": subdir.name,
                    "type": model_type,
                    "family": subdir.name,
                    "task": "",
                    "file_path": relative,
                    "file_size_gb": size_gb,
                    "sha256": "",
                    "source_url": "",
                    "license": "",
                    "status": "active",
                    "notes": "目录型模型",
                }
                is_new = db.upsert_model(data)
                if is_new:
                    new += 1
                else:
                    updated += 1
            except Exception as e:
                errors.append(f"{subdir.name}: {e}")

    # 标记已删除的模型（DB 中有但磁盘上没有）
    db_ids = set(db.get_all_active_models())
    disk_ids = set()
    for dir_entry in repo.iterdir():
        if not dir_entry.is_dir():
            continue
        model_type = DIR_TYPE_MAP.get(dir_entry.name)
        if not model_type:
            continue
        for filepath in dir_entry.rglob("*"):
            if filepath.is_file() and filepath.suffix.lower() in MODEL_EXTENSIONS:
                if not _should_exclude(filepath.name, exclude_patterns):
                    disk_ids.add(_make_model_id(filepath.name, dir_entry.name))
        for subdir in dir_entry.iterdir():
            if subdir.is_dir() and (
                (subdir / "config.json").exists() or list(subdir.glob("*.yaml"))
            ):
                disk_ids.add(_make_model_id(subdir.name, dir_entry.name))

    deleted = db_ids - disk_ids
    if deleted:
        db.mark_archived(list(deleted))

    error_text = "; ".join(errors[:10])
    db.record_scan(repo_path, found, new, updated, error_text)

    return found, new, updated, len(deleted), errors
