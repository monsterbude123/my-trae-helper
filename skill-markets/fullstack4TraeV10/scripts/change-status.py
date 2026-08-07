"""
文件系统真相读取 — 零依赖，不信任 state-card 或 agent 自述。

用法:
  python change-status.py <change目录路径>

退出码: 0=成功

输出 JSON:
  {
    "change_name": "my-feature",
    "artifacts": {
      "proposal": {"done": true, "path": "docs/specs/my-feature/define.md", "lines": 45},
      "specs": {"done": true, "path": "docs/specs/my-feature/spec.md", "lines": 120, "mode": "delta"},
      "design": {"done": true, "path": "docs/specs/my-feature/design.md", "lines": 30},
      "tasks": {"done": true, "path": "docs/specs/my-feature/tasks.md",
                "total": 12, "completed": 10, "pending": 2}
    },
    "ready_to_apply": false,
    "blockers": ["tasks 未全部完成: 10/12"]
  }
"""

import os
import re
import sys
import json


CHECKBOX_PATTERN = re.compile(r'^\s*-\s*\[([ xX])\]\s*')


def count_tasks(filepath: str) -> dict:
    """解析 tasks.md 中 checkbox 完成情况。"""
    total = 0
    completed = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                m = CHECKBOX_PATTERN.match(line)
                if m:
                    total += 1
                    if m.group(1) in ('x', 'X'):
                        completed += 1
    except FileNotFoundError:
        return {"total": 0, "completed": 0, "pending": 0, "exists": False}
    return {"total": total, "completed": completed, "pending": total - completed, "exists": True}


def detect_spec_kind(filepath: str) -> str:
    """检测 spec 是 delta 还是 full。"""
    delta_marker = re.compile(r'^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if delta_marker.match(line):
                    return "delta"
    except FileNotFoundError:
        return "unknown"
    return "full"


def count_lines(filepath: str) -> int:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def read_change_status(change_dir: str) -> dict:
    """读取一个 change 目录的完整状态。"""
    change_name = os.path.basename(os.path.normpath(change_dir))

    artifacts = {}

    # define.md → proposal
    define_path = os.path.join(change_dir, 'define.md')
    define_exists = os.path.isfile(define_path)
    artifacts['proposal'] = {
        "done": define_exists,
        "path": define_path,
        "lines": count_lines(define_path) if define_exists else 0,
    }

    # spec.md → specs
    spec_path = os.path.join(change_dir, 'spec.md')
    spec_exists = os.path.isfile(spec_path)
    artifacts['specs'] = {
        "done": spec_exists,
        "path": spec_path,
        "lines": count_lines(spec_path) if spec_exists else 0,
        "mode": detect_spec_kind(spec_path) if spec_exists else "none",
    }

    # design.md → design
    design_path = os.path.join(change_dir, 'design.md')
    design_exists = os.path.isfile(design_path)
    artifacts['design'] = {
        "done": design_exists,
        "path": design_path,
        "lines": count_lines(design_path) if design_exists else 0,
    }

    # tasks.md → tasks
    tasks_path = os.path.join(change_dir, 'tasks.md')
    tasks_info = count_tasks(tasks_path)
    artifacts['tasks'] = {
        "done": tasks_info['exists'] and tasks_info['pending'] == 0,
        "path": tasks_path,
        "total": tasks_info['total'],
        "completed": tasks_info['completed'],
        "pending": tasks_info['pending'],
    }

    # contracts/ → contract
    contracts_dir = os.path.join(change_dir, 'contracts')
    contract_done = os.path.isdir(contracts_dir) and len(os.listdir(contracts_dir)) > 0
    artifacts['contract'] = {
        "done": contract_done,
        "path": contracts_dir if os.path.isdir(contracts_dir) else None,
    }

    # 判定 ready_to_apply
    blockers = []
    apply_requires = ['proposal', 'specs', 'tasks', 'contract']
    for aid in apply_requires:
        if aid in artifacts and not artifacts[aid]['done']:
            blockers.append(f"{aid} 未完成")

    # tasks 特殊: 存在但未全完成
    if artifacts['tasks'].get('exists') and artifacts['tasks']['pending'] > 0:
        blockers.append(f"tasks 未全部完成: {artifacts['tasks']['completed']}/{artifacts['tasks']['total']}")

    # 检测 spec-purge 归档（V10 取代 V9 _invalidated/）
    # change_dir 通常是 {project_root}/docs/specs/{feature_name}
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(change_dir)))
    spec_purge_dir = os.path.join(project_root, 'docs', 'archive', 'out', 'spec-purge')
    reset_mode = os.path.isdir(spec_purge_dir)
    reset_warning = None
    if reset_mode:
        purged_features = []
        for entry in os.listdir(spec_purge_dir):
            if entry.startswith(f'{change_name}-'):
                full = os.path.join(spec_purge_dir, entry)
                if os.path.isdir(full):
                    purged_features.append(entry)
        reset_warning = (
            f"⚠️ V10 spec-purge 历史 ({len(purged_features)} 次归档): {purged_features[:3]}"
            if purged_features else "⚠️ spec-purge/ 存在（未匹配当前 change_name）"
        )
        if len(purged_features) > 3:
            reset_warning += f" | spec-purge 膨胀: {len(purged_features)} 次，建议清理"

    return {
        "change_name": change_name,
        "change_dir": change_dir,
        "reset_mode": reset_mode,
        "reset_warning": reset_warning,
        "artifacts": artifacts,
        "ready_to_apply": len(blockers) == 0,
        "blockers": blockers,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="文件系统真相读取 — change 状态")
    parser.add_argument("change_dir", help="change 目录路径")
    args = parser.parse_args()

    if not os.path.isdir(args.change_dir):
        print(json.dumps({"error": f"目录不存在: {args.change_dir}"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    result = read_change_status(args.change_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
