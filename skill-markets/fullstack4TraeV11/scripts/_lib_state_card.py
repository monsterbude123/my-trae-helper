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
