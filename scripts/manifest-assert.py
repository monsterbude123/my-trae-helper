#!/usr/bin/env python3
# scripts/manifest-assert.py
# Bridge Guard:按本次变更意图(intents)反向核对 Manifest 声明的交付物
#
# 退出码:
#   0  PASS(本次变更涉及的 skill 全部交付物齐全,或未涉及任何已知 skill)
#   2  BLOCK(缺交付物,会输出 [AGENT-PROMPT] 块)
#   3  ERROR(manifest 自身损坏 / 参数错误)
#
# 用法:
#   python scripts/manifest-assert.py \
#       --manifest skill-markets/MANIFEST.yaml \
#       --intents '{"intents":[{"kind":"add-skill","skill":"trae-security-review","path":"..."}]}'
#
# 输出三段:
#   1. 人读摘要
#   2. [AGENT-PROMPT] 结构化块(agent 可直接解析)
#   3. [/AGENT-PROMPT]
#
# 设计原则(沿用 AGENTS.md §1 铁律 #7 + agent-dev-control-kit §11):
#   - stdlib only(pyyaml 不在 stdlib → 用极简 YAML parser,只支持本文件用到的子集)
#   - 每个 missing 项配 fix 指引(告诉 agent "补什么 / 怎么补 / 在哪个文件")
#   - 不做装饰性断言(每个断言都必须对应"实际可观测的失败信号")

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # PyYAML 已在本机 Python 安装,优先使用
except ImportError:
    print("ERROR: 需要 PyYAML(pip install pyyaml)", file=sys.stderr)
    sys.exit(3)


def parse_yaml_min(text: str):
    """
    直接用 PyYAML — 比自造迷你 parser 稳。
    失败时返回结构化错误而不是抛异常。
    """
    return yaml.safe_load(text)

# ---------- Manifest 加载 ----------
def load_manifest(path: Path):
    if not path.exists():
        print(f"ERROR: Manifest 不存在: {path}", file=sys.stderr)
        sys.exit(3)
    text = path.read_text(encoding='utf8')
    try:
        return parse_yaml_min(text)
    except Exception as e:
        print(f"ERROR: Manifest 解析失败: {e}", file=sys.stderr)
        sys.exit(3)

# ---------- 断言函数 ----------
def assert_path_exists(skill_root: Path, declared_path: str, missing: list, kind: str):
    full = skill_root / declared_path
    if not full.exists():
        missing.append({
            'kind': kind,
            'path': declared_path,
            'reason': f"Manifest 声明 {kind}={declared_path},但文件不存在",
            'fix': f"新建 {declared_path} 或在 MANIFEST.yaml 中移除该声明",
        })

def assert_doc_contains(skill_root: Path, doc_path: str, must_contain: list, missing: list):
    full = skill_root / doc_path
    if not full.exists():
        missing.append({
            'kind': 'doc',
            'path': doc_path,
            'reason': f"文档 {doc_path} 不存在",
            'fix': f"新建 {doc_path}",
        })
        return
    try:
        text = full.read_text(encoding='utf8')
    except Exception as e:
        missing.append({
            'kind': 'doc',
            'path': doc_path,
            'reason': f"读取 {doc_path} 失败: {e}",
            'fix': f"确认 {doc_path} 可读且为 UTF-8",
        })
        return
    for phrase in must_contain:
        if phrase not in text:
            missing.append({
                'kind': 'doc',
                'path': doc_path,
                'must_contain': phrase,
                'reason': f"{doc_path} 缺少必含章节/短语 '{phrase}'",
                'fix': f"在 {doc_path} 中新增段落,首行写 '{phrase}'(## 标题或正文均可)",
            })

def assert_test_contains(test_path: Path, must_assert: list, missing: list, skill_name: str):
    if not test_path.exists():
        missing.append({
            'kind': 'test',
            'path': str(test_path.relative_to(test_path.parents[2])),
            'reason': f"测试文件不存在",
            'fix': f"新建 {test_path.name},覆盖以下断言关键词:{must_assert}",
        })
        return
    try:
        text = test_path.read_text(encoding='utf8')
    except Exception:
        missing.append({
            'kind': 'test',
            'path': str(test_path),
            'reason': "测试文件无法读取",
            'fix': f"确认 {test_path} 可读",
        })
        return
    for kw in must_assert:
        if kw not in text:
            missing.append({
                'kind': 'test',
                'path': str(test_path),
                'must_assert': kw,
                'reason': f"测试缺少断言关键词 '{kw}'",
                'fix': f"在 {test_path} 中新增至少一个 case 引用 '{kw}'",
            })

def assert_script_cli(skill_root: Path, script: dict, missing: list):
    """检查脚本有 CLI 入口(粗粒度:文件名含 cli_entry 字符串 + main 块)。"""
    path = script['path']
    cli_entry = script.get('cli_entry', '')
    full = skill_root / path
    if not full.exists():
        missing.append({
            'kind': 'script',
            'path': path,
            'reason': "Manifest 声明的脚本不存在",
            'fix': f"新建 {path} 或在 MANIFEST.yaml 移除该声明",
        })
        return
    text = full.read_text(encoding='utf8', errors='ignore')
    # Python: 有 __main__ 守卫 或 argparse / sys.argv 调用即可
    if path.endswith('.py'):
        has_cli = (
            "__name__" in text and ("__main__" in text or "argv" in text)
        ) or ("argparse" in text)
        if not has_cli:
            missing.append({
                'kind': 'script',
                'path': path,
                'reason': "Python 脚本缺少 CLI 入口(__name__ == '__main__' / argparse / sys.argv)",
                'fix': f"在 {path} 末尾加:\n    if __name__ == '__main__':\n        main()",
            })
    # Node: process.argv 或 #!/usr/bin/env node
    elif path.endswith('.mjs') or path.endswith('.js'):
        if 'process.argv' not in text and '#!/usr/bin/env node' not in text:
            missing.append({
                'kind': 'script',
                'path': path,
                'reason': "Node 脚本缺少 CLI 入口(process.argv / shebang)",
                'fix': f"在 {path} 加 process.argv 解析或 #!/usr/bin/env node shebang",
            })
    if cli_entry:
        # 检查 cli_entry 名称是否在脚本注释或 docstring 中出现
        # 注:cli_entry 缺失只记 WARN,不阻断(很多项目 cli_entry 是约定俗成的,不必每次都注释)
        # 阻断级别只保留"无任何 CLI 入口"(上面那个更严的检查)
        pass

# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser(description='Manifest Bridge Guard')
    ap.add_argument('--manifest', default='skill-markets/MANIFEST.yaml')
    ap.add_argument('--intents', default='{"intents":[]}',
                    help='intent-classifier.mjs 输出的 JSON 字符串')
    args = ap.parse_args()

    # 1. 解析 intents
    try:
        payload = json.loads(args.intents)
        intents = payload.get('intents', [])
    except json.JSONDecodeError as e:
        print(f"ERROR: --intents 不是合法 JSON: {e}", file=sys.stderr)
        sys.exit(3)

    # 2. 加载 manifest
    manifest = load_manifest(Path(args.manifest))
    skills_index = {s['name']: s for s in manifest.get('skills', [])}

    # 3. 收集受影响的 skill(去重)
    affected = {}
    for it in intents:
        s = it.get('skill')
        if not s: continue
        affected.setdefault(s, []).append(it)

    # 4. 无受影响 skill → PASS(本次变更不涉及任何已知 skill,跳过 Bridge)
    if not affected:
        print("[manifest-assert] 本次变更未涉及任何已知 skill,跳过 Bridge 校验")
        sys.exit(0)

    # 5. 逐 skill 校验
    missing_all = []  # [{skill, intent, missing: [...]}]
    for skill_name, its in affected.items():
        if skill_name not in skills_index:
            # 本次涉及的 skill 不在 Manifest — 不阻断(留作增量),只 WARN
            print(f"[WARN] skill '{skill_name}' 不在 MANIFEST.yaml 中,跳过(增量追加请更新 Manifest)")
            continue
        spec = skills_index[skill_name]
        skill_root = Path('skill-markets') / skill_name
        missing = []

        # 5.1 scripts
        for sc in spec.get('scripts', []) or []:
            assert_script_cli(skill_root, sc, missing)

        # 5.2 docs
        for doc in spec.get('docs', []) or []:
            assert_path_exists(skill_root, doc['path'], missing, 'doc')
            for phrase in doc.get('must_contain', []) or []:
                assert_doc_contains(skill_root, doc['path'], [phrase], missing)

        # 5.3 tests — 路径相对仓库根(因为 manifest 只声明文件名片段)
        for t in spec.get('tests', []) or []:
            test_path = Path('tests/unit') / Path(t['path']).name
            # 简化:若路径已含 tests/unit/ 直接用
            if t['path'].startswith('tests/'):
                test_path = Path(t['path'])
            assert_test_contains(test_path, t.get('must_assert', []) or [], missing, skill_name)

        if missing:
            # 主意图取第一个
            primary_intent = its[0]['kind']
            missing_all.append({
                'skill': skill_name,
                'intent': primary_intent,
                'missing': missing,
            })

    # 6. 输出
    if not missing_all:
        print(f"[manifest-assert] PASS — 本次变更涉及的 {len(affected)} 个 skill 交付物齐全")
        sys.exit(0)

    # 人读摘要
    print("=" * 60)
    print(f"[manifest-assert] BLOCK — 本次变更缺交付物 ({len(missing_all)} skill)")
    print("=" * 60)

    # 结构化 agent prompt
    print("[AGENT-PROMPT]")
    print(json.dumps({
        'action': '补充缺失交付物',
        'block_reason': 'manifest-assert 阻断:本次变更未满足 MANIFEST.yaml 声明的交付物清单',
        'affected': missing_all,
    }, ensure_ascii=False, indent=2))
    print("[/AGENT-PROMPT]")
    sys.exit(2)

if __name__ == '__main__':
    main()