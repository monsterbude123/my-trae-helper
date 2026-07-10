"""
MyModelScope 配置管理

从 .mymodelscope.env 读取配置。查找顺序：
1. 当前目录
2. 模型仓库根目录（如果 MYMODELSCOPE_REPO_PATH 已设置）
3. 用户家目录（%USERPROFILE%）
"""

import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    repo_path: str = ""
    cold_storage: str = ""
    db_path: str = ""
    scan_exclude: list[str] = field(default_factory=lambda: ["._*", "*.tmp", ".metadata-only"])

    @property
    def is_valid(self) -> bool:
        return bool(self.repo_path and Path(self.repo_path).exists())


def _find_env_file() -> Path | None:
    """按优先级查找 .mymodelscope.env"""
    candidates = [
        Path.cwd() / ".mymodelscope.env",
        Path.home() / ".mymodelscope.env",
    ]
    # 如果当前目录下已经有 .mymodelscope.env
    for base in [Path.cwd(), Path.home()]:
        env_file = base / ".mymodelscope.env"
        if env_file.exists():
            return env_file
    return None


def _parse_env(filepath: Path) -> dict[str, str]:
    """解析 .env 文件，返回键值对字典"""
    result = {}
    if not filepath.exists():
        return result
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                # 展开环境变量引用
                if value.startswith("${") and value.endswith("}"):
                    ref_key = value[2:-1]
                    value = os.environ.get(ref_key, result.get(ref_key, ""))
                result[key] = value
    return result


def load_config(env_path: str | None = None) -> Config:
    """加载配置。

    优先级：env_path 参数 > 当前目录 > 用户家目录
    """
    if env_path:
        filepath = Path(env_path)
    else:
        filepath = _find_env_file()

    if not filepath:
        return Config()

    env = _parse_env(filepath)
    repo_path = env.get("MYMODELSCOPE_REPO_PATH", "")

    # 展开变量引用
    for key in list(env.keys()):
        val = env[key]
        if "${" in val:
            for ref_key, ref_val in env.items():
                val = val.replace(f"${{{ref_key}}}", ref_val)
            val = val.replace("${MYMODELSCOPE_REPO_PATH}", repo_path)
            env[key] = val

    config = Config(
        repo_path=repo_path,
        cold_storage=env.get("MYMODELSCOPE_COLD_STORAGE", os.path.join(repo_path, "_archive") if repo_path else ""),
        db_path=env.get("MYMODELSCOPE_DB_PATH", "") or os.path.join(repo_path, ".mymodelscope.db") if repo_path else "",
        scan_exclude=[x.strip() for x in env.get("MYMODELSCOPE_SCAN_EXCLUDE", "._*,*.tmp,.metadata-only").split(",") if x.strip()],
    )
    return config
