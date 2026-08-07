"""V10 共享工具库 — 借鉴 spec-kit common.py 模式

模块职责:
  - 路径解析 (find_v10_root / get_project_root)
  - feature 标准路径集合 (FeaturePaths)
  - 阶段识别 (V10_PHASES / phase_index)
  - JSON/错误输出 (emit_json / error_exit)

借鉴来源:
  - spec-kit scripts/python/common.py (find_specify_root / get_repo_root)
  - spec-kit FeaturePaths dataclass

V10 适配:
  - 用 docs/specs/ 替代 .specify/ 作为项目根锚点
  - V10_FEATURE 环境变量替代 SPECIFY_FEATURE
  - 5 阶段: plan / spec / contract / implement / review
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# === 阶段定义（V10 5 阶段硬门禁链） ===

V10_PHASES: List[str] = ["plan", "spec", "contract", "implement", "review"]

# 阶段 → 前置依赖（用于 check_prerequisites.py）
V10_PHASE_PREREQS: dict = {
    "plan": [],                                   # 全新起点，无前置
    "spec": ["plan.md"],                          # 需要 Plan 阶段产物
    "contract": ["spec.md"],                      # 需要 Spec 阶段产物
    "implement": ["spec.md", "contracts/api-contracts.md"],  # 需要契约
    "review": ["spec.md", "contracts/api-contracts.md", "tasks.md"],  # 需要完整产物
}


# === 路径解析 ===

def find_v10_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """向上查找 V10 项目根（含 docs/specs/ 目录）

    借鉴 spec-kit find_specify_root,锚点从 .specify/ 改为 docs/specs/。
    """
    current = (start_dir or Path.cwd()).resolve()
    while True:
        if (current / "docs" / "specs").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def get_project_root(start_path: Optional[Path] = None) -> Path:
    """V10 项目根（找不到则用当前目录）

    借鉴 spec-kit get_repo_root。
    """
    root = find_v10_root(start_path)
    return root if root else Path.cwd().resolve()


def get_current_feature() -> str:
    """当前 feature 名（从环境变量 V10_FEATURE 读取）

    借鉴 spec-kit get_current_branch。
    """
    return os.environ.get("V10_FEATURE", "")


def resolve_feature_dir(project_root: Path, feature: Optional[str] = None) -> Path:
    """解析 feature 目录路径

    优先级: 命令行参数 > V10_FEATURE 环境变量 > 路径末尾段

    Args:
        project_root: V10 项目根
        feature: feature 名（可选）

    Returns:
        docs/specs/{feature}/ 路径（默认 V10 标准布局）
    """
    name = feature or get_current_feature()
    if not name:
        # 兜底：取项目根的目录名（不推荐，仅用于降级）
        name = project_root.name
    return detect_feature_dir(project_root, name)


def detect_feature_dir(project_root: Path, feature_name: str) -> Path:
    """自动检测 feature 目录布局（V10 兼容 AIGCMediaDesktop 嵌套布局）

    优先级：
      1. docs/specs/{feature}/              (V10 标准布局)
      2. docs/specs/changes/{feature}/      (AIGCMediaDesktop 嵌套布局)
      3. docs/specs/archive/out/spec-purge/{feature}/  (v9 legacy + purge 后)

    如果三个都不存在，返回 V10 标准位置（用于创建）。
    """
    specs = project_root / "docs" / "specs"
    candidates = [
        specs / feature_name,                                # V10 标准
        specs / "changes" / feature_name,                    # 嵌套布局
        specs / "archive" / "out" / "spec-purge" / feature_name,  # 已 purge
    ]
    for c in candidates:
        if c.is_dir():
            return c
    # 不存在则返回 V10 标准位置（用于创建）
    return candidates[0]


# === FeaturePaths 数据类 ===

@dataclass(frozen=True)
class FeaturePaths:
    """feature 标准路径集合

    借鉴 spec-kit FeaturePaths,但对齐 V10 5 阶段产物。
    """
    project_root: Path
    feature: str
    feature_dir: Path
    plan: Path
    spec: Path
    tasks: Path
    define: Path
    contracts_dir: Path
    prototypes_dir: Path
    state_card: Path

    @classmethod
    def from_root(
        cls,
        project_root: Path,
        feature: str,
    ) -> "FeaturePaths":
        """从项目根 + feature 名构建路径集合

        Args:
            project_root: V10 项目根（含 docs/specs/）
            feature: feature 名（格式: NN-NN-name）

        布局自动检测（兼容 AIGCMediaDesktop 嵌套布局）：
          1. docs/specs/{feature}/
          2. docs/specs/changes/{feature}/
          3. docs/specs/archive/out/spec-purge/{feature}/
        """
        feature_dir = detect_feature_dir(project_root, feature)
        return cls(
            project_root=project_root,
            feature=feature,
            feature_dir=feature_dir,
            plan=feature_dir / "plan.md",
            spec=feature_dir / "spec.md",
            tasks=feature_dir / "tasks.md",
            define=feature_dir / "define.md",
            contracts_dir=feature_dir / "contracts",
            prototypes_dir=feature_dir / "prototypes",
            state_card=feature_dir / ".state-card.md",
        )

    def to_dict(self) -> dict:
        """导出为 dict（用于 JSON 输出）"""
        return {
            "project_root": str(self.project_root),
            "feature": self.feature,
            "feature_dir": str(self.feature_dir),
            "plan": str(self.plan),
            "spec": str(self.spec),
            "tasks": str(self.tasks),
            "define": str(self.define),
            "contracts_dir": str(self.contracts_dir),
            "prototypes_dir": str(self.prototypes_dir),
            "state_card": str(self.state_card),
        }


# === 工具函数 ===

def emit_json(payload: dict) -> None:
    """JSON 输出到 stdout（机械验证可解析）

    借鉴 spec-kit _json_line。
    """
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def emit_json_line(payload: dict) -> None:
    """JSON 输出 + 换行（更易流式消费）"""
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def error_exit(msg: str, code: int = 1) -> None:
    """错误退出（stderr 输出 + SystemExit）

    借鉴 spec-kit SystemExit 模式。
    """
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def validate_feature_name(name: str) -> bool:
    """校验 feature 名格式（NN-NN-name 或 NN-NN-name-ext）

    V10 规范: 必须以 NN-NN 开头,后接 kebab-case 描述。
    """
    import re
    pattern = r"^\d{2}-\d{2}(-[a-z0-9]+)+$"
    return bool(re.match(pattern, name))


def phase_index(phase: str) -> int:
    """阶段 → 索引（用于顺序比较）"""
    try:
        return V10_PHASES.index(phase)
    except ValueError:
        return -1


def has_unfinished_tasks(tasks_path: Path) -> bool:
    """检查 tasks.md 是否还有未勾选任务

    Returns:
        True: 有未勾选任务
        False: 全部勾选 或 tasks.md 不存在
    """
    if not tasks_path.is_file():
        return False
    try:
        content = tasks_path.read_text(encoding="utf-8")
    except OSError:
        return False
    return "- [ ]" in content


def dir_has_entries(path: Path) -> bool:
    """检查目录是否存在且非空

    借鉴 spec-kit _dir_has_entries。
    """
    try:
        return path.is_dir() and any(path.iterdir())
    except OSError:
        return False


# === 模板解析（Spec-Kit 2 层简化栈） ===

def resolve_template(
    project_root: Path,
    template_name: str,
    package_root: Path,
) -> Optional[Path]:
    """解析模板路径（2 层栈：项目 overrides > V10 内置）

    借鉴 spec-kit resolve_template，简化为 2 层（砍掉 presets/extensions 层）：
      1. {project_root}/docs/templates/overrides/{name}.md  — 项目级覆盖
      2. {package_root}/templates/{name}.md                 — V10 内置默认

    设计原因（与 spec-kit 4 层栈的差异）:
      - 砍掉 presets 层: V10 用 docs/specs/{feature}/ 而非多组织堆叠
      - 砍掉 extensions 层: V10 用 agents/ + references/ 扩展能力,不用模板扩展
      - 保留 overrides 层: 项目可在不动技能源码前提下局部调整模板

    Args:
        project_root: V10 项目根（含 docs/）
        template_name: 模板名（不含 .md 后缀，如 "spec-template"）
        package_root: V10 技能包根（含 templates/）

    Returns:
        匹配的模板路径（找不到返回 None）
    """
    # L1: 项目级 overrides
    override = (
        project_root / "docs" / "templates" / "overrides" / f"{template_name}.md"
    )
    if override.is_file():
        return override
    # L2: V10 内置
    core = package_root / "templates" / f"{template_name}.md"
    if core.is_file():
        return core
    return None


# === 主入口（自检） ===

if __name__ == "__main__":
    # 自检模式: 输出当前解析结果
    project_root = get_project_root()
    feature = get_current_feature()

    result = {
        "project_root": str(project_root),
        "feature": feature or "(unset)",
        "phases": V10_PHASES,
        "is_v10_root": find_v10_root() is not None,
    }

    if feature:
        paths = FeaturePaths.from_root(project_root, feature)
        result["feature_paths"] = paths.to_dict()
        result["valid_feature_name"] = validate_feature_name(feature)

    emit_json(result)
