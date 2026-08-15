"""状态卡 frontmatter 解析共用库

3 个脚本(state-card-validator / stage-gate / change-status)共用。
优先用 PyYAML(精确解析嵌套),未安装时回退手写解析(仅顶层字段)。
"""

import pathlib


def parse_state_card(path: pathlib.Path) -> dict:
    """解析状态卡 frontmatter。

    返回 dict;失败返回 {"error": "..."}。
    """
    if not path.exists():
        return {"error": f"状态卡文件不存在: {path}"}

    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {"error": "状态卡缺 frontmatter 分隔符 ---"}

    try:
        end = content.index("\n---", 3)
    except ValueError:
        return {"error": "状态卡 frontmatter 未闭合"}

    fm_text = content[3:end]

    # 优先用 PyYAML(精确解析嵌套结构)
    try:
        import yaml
        try:
            fields = yaml.safe_load(fm_text) or {}
        except Exception as e:
            return {"error": f"YAML 解析失败: {e}"}
    except ImportError:
        fields = _parse_fallback(fm_text)

    # 清理字符串字段的外层引号
    for k, v in list(fields.items()):
        if isinstance(v, str):
            if len(v) >= 2 and v[0] in ('"', "'") and v[-1] == v[0]:
                fields[k] = v[1:-1]

    return fields


def _parse_fallback(fm_text: str) -> dict:
    """手写解析回退(仅顶层字段,不支持嵌套)。"""
    fields = {}
    current_key = None
    for line in fm_text.strip().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val:
                fields[key] = val.strip('"').strip("'")
            else:
                current_key = key
                fields[key] = {}
        elif current_key and stripped.startswith("-"):
            item = stripped[1:].strip()
            if isinstance(fields.get(current_key), list):
                fields[current_key].append(item)
            elif isinstance(fields.get(current_key), dict):
                fields[current_key][item] = True
    return fields


def compute_hash(content: str) -> str:
    """计算内容的 SHA-256 哈希值
    
    Args:
        content: 文件内容（字符串）
    
    Returns:
        str: SHA-256 哈希值（hex）
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def audit_state_card_change(
    path: pathlib.Path,
    operation: str,
    actor: str = None,
    content_before: str = None,
    content_after: str = None,
    project_root: pathlib.Path = None
) -> dict:
    """记录状态卡变更审计日志
    
    Args:
        path: 状态卡文件路径
        operation: 操作类型（create / update / delete / stage-change）
        actor: 操作者（默认从环境变量 V11_GATE_CALLER 获取）
        content_before: 变更前内容（用于计算 hash_before）
        content_after: 变更后内容（用于计算 hash_after）
        project_root: 项目根路径（默认从 path 推断）
    
    Returns:
        dict: 审计日志条目（timestamp / operation / actor / hash_before / hash_after / path）
    
    Side effect:
        写入审计日志到 <project_root>/.trae/logs/state-card-audit.jsonl
    """
    if actor is None:
        actor = os.getenv("V11_GATE_CALLER", "unknown-agent")
    
    hash_before = compute_hash(content_before) if content_before else None
    hash_after = compute_hash(content_after) if content_after else None
    
    if project_root is None:
        project_root = path.parent.parent.parent
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "actor": actor,
        "hash_before": hash_before,
        "hash_after": hash_after,
        "path": str(path.relative_to(project_root)) if path.is_relative_to(project_root) else str(path),
        "gate_stage": os.getenv("V11_GATE_STAGE", ""),
        "gate_enforced": os.getenv("V11_GATE_ENFORCED", "")
    }
    
    log_dir = project_root / ".trae/logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "state-card-audit.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    return log_entry


# === 状态机解析（V11.5 NEW — flow 层程序化）===
# 状态卡 = 状态机。registry/state-machine.yaml 定义状态/转换/驾驶舱角色。
# 由 _lib_state_card 程序化消费，取代 agent 硬读 md 字段。

def load_state_machine(registry_dir: pathlib.Path) -> dict:
    """加载 registry/state-machine.yaml，返回状态机 dict；失败返回 {"error": ...}。

    Args:
        registry_dir: registry 目录路径（含 state-machine.yaml）

    Returns:
        dict: 状态机声明（states / transitions / initial_state / terminal_states / pilot）
            解析失败时返回 {"error": "..."}
    """
    sm_path = registry_dir / "state-machine.yaml"
    if not sm_path.exists():
        return {"error": f"状态机文件不存在: {sm_path}"}

    try:
        import yaml
        with open(sm_path, encoding="utf-8") as f:
            state_machine = yaml.safe_load(f) or {}
    except ImportError:
        return {"error": "缺少 PyYAML，无法解析状态机"}
    except Exception as e:
        return {"error": f"状态机 YAML 解析失败: {e}"}

    if "states" not in state_machine:
        return {"error": "状态机缺 states 声明"}

    return state_machine


def validate_transition(state_machine: dict, from_stage: str, to_stage: str) -> tuple:
    """校验 from_stage -> to_stage 是否合法转换。

    依据状态机的 states[].allowed_transitions 判定。
    返回 (valid: bool, reason: str)。合法返回 (True, "");非法返回 (False, reason)。
    """
    if "error" in state_machine:
        return (False, f"状态机加载失败: {state_machine['error']}")

    # 先查显式 transitions 声明
    for t in state_machine.get("transitions", []) or []:
        if t.get("from") == from_stage and t.get("to") == to_stage:
            return (True, "")

    # 再查 states 的 allowed_transitions
    for s in state_machine.get("states", []) or []:
        if s.get("id") == from_stage:
            allowed = s.get("allowed_transitions", []) or []
            if to_stage in allowed:
                return (True, "")
            return (False, f"非法转换: {from_stage} -> {to_stage}（不允许）")

    return (False, f"未知状态: {from_stage}")


def is_terminal_state(state_machine: dict, stage: str) -> bool:
    """判断 stage 是否为终止状态。"""
    if "error" in state_machine:
        return False
    terminals = state_machine.get("terminal_states", []) or []
    return stage in terminals


def get_pilot_actor(state_machine: dict) -> str:
    """返回驾驶舱角色（应为 main-context）。"""
    if "error" in state_machine:
        return ""
    return state_machine.get("pilot", "")
