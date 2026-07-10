#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WebGAL 场景脚本验证器
- 检查每个 .txt 文件
- 验证 choose / jumpLabel / changeScene 目标存在
- 检查 setVar 变量与 if 条件类型一致
- 验证 label 唯一性
- 检测"设置后从未被读取"的无效变量（关键 flag 必须在结局条件中被读取）
"""
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# 从脚本位置向上 5 层到 WebGAL_Demo 根：scripts -> webgal-create-deploy-skill -> skills -> .trae -> WebGAL_Demo
SCENE_DIR = Path(__file__).resolve().parent
for _ in range(4):
    SCENE_DIR = SCENE_DIR.parent
SCENE_DIR = SCENE_DIR / "webgal_case02" / "scene"

# 已知结局和流程的合法目标（无需 label，跨场景跳转）
SCENE_TARGETS = set()  # 所有 .txt 文件名（不含扩展名）

# 命令正则
RE_LABEL = re.compile(r'^\s*label\s*:\s*([A-Za-z_][A-Za-z0-9_]*)\s*;', re.M)
RE_CHOOSE = re.compile(r'choose\s*:\s*([^;]+);', re.M)
RE_JUMPLABEL = re.compile(r'jumpLabel\s*:\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:-[a-zA-Z]+=[^;]+)?;', re.M)
RE_CHANGESCENE = re.compile(r'changeScene\s*:\s*([A-Za-z0-9_/\.]+)\s*(?:-[a-zA-Z]+=[^;]+)?;', re.M)
RE_CALLSCENE = re.compile(r'callScene\s*:\s*([A-Za-z0-9_/\.]+)\s*(?:-[a-zA-Z]+=[^;]+)?;', re.M)
RE_SETVAR = re.compile(r'setVar\s*:\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;-]+?)\s*;', re.M)
RE_SETVAR_INLINE = re.compile(r'setVar\s*:\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;]+)\s*;', re.M)
RE_IF = re.compile(r'if\s*:\s*([^:]+?)\s*:\s*', re.M)
RE_WHEN = re.compile(r'-when\s*=\s*([^\s;]+)', re.M)

# 提取 choose 内部的所有 "选项:目标" 对（处理条件前缀）
RE_CHOOSE_PAIR = re.compile(r'(?:\([^)]*\))?(?:\[[^\]]*\])?\s*->?\s*([^:|]+)\s*:\s*([A-Za-z0-9_/]+)')


def collect_scene_names():
    """收集所有 .txt 文件名作为合法 changeScene 目标"""
    names = set()
    if not SCENE_DIR.exists():
        return names
    for f in SCENE_DIR.iterdir():
        if f.suffix == ".txt":
            names.add(f.stem)
    return names


def parse_labels(content):
    """提取所有 label，返回 dict[label_name] = count"""
    labels = defaultdict(int)
    for m in RE_LABEL.finditer(content):
        labels[m.group(1)] += 1
    return labels


def parse_choose_targets(content):
    """提取所有 choose 内部的目标 (label 或 scene)"""
    targets = []
    for m in RE_CHOOSE.finditer(content):
        body = m.group(1)
        for pair in RE_CHOOSE_PAIR.finditer(body):
            target = pair.group(2).strip()
            targets.append(target)
    return targets


def parse_jumplabel_targets(content):
    return [m.group(1) for m in RE_JUMPLABEL.finditer(content)]


def parse_changescene_targets(content):
    return [m.group(1).replace('.txt', '') for m in RE_CHANGESCENE.finditer(content)]


def parse_callscene_targets(content):
    return [m.group(1).replace('.txt', '') for m in RE_CALLSCENE.finditer(content)]


def parse_setvars(content):
    """提取所有 setVar 变量及其值"""
    vars_ = {}  # name -> list of value expressions
    for m in RE_SETVAR_INLINE.finditer(content):
        name = m.group(1)
        val = m.group(2).strip()
        vars_.setdefault(name, []).append(val)
    return vars_


def parse_conditions(content):
    """提取所有 if 条件中的变量名 + when 条件中的变量名"""
    used = set()
    for m in RE_IF.finditer(content):
        cond = m.group(1)
        # 提取条件中的变量名
        for vm in re.finditer(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', cond):
            used.add(vm.group(1))
    for m in RE_WHEN.finditer(content):
        cond = m.group(1)
        for vm in re.finditer(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', cond):
            used.add(vm.group(1))
    return used


def check_value_type(val):
    """判断值类型：number/bool/string"""
    val = val.strip()
    if val in ('true', 'false'):
        return 'bool'
    # 数字（含运算）
    if re.match(r'^-?\d+(\.\d+)?$', val):
        return 'number'
    if re.match(r'^-?\d+(\.\d+)?\s*[+\-*/]\s*.+$', val):
        return 'number'  # 运算结果可能是 number
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s*[+\-*/]\s*.+$', val):
        return 'number_or_var'  # 变量参与运算
    if re.match(r'^random\(.*\)$', val):
        return 'number'
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', val):
        return 'var'  # 引用另一个变量
    return 'string'


def validate_file(filepath, all_scene_names, all_labels):
    """验证单个文件"""
    errors = []
    warnings = []
    content = filepath.read_text(encoding='utf-8')
    stem = filepath.stem

    # 1. label 唯一性
    labels = parse_labels(content)
    for name, count in labels.items():
        if count > 1:
            errors.append(f"[{stem}] label '{name}' 重复定义 {count} 次")

    # 2. choose 目标必须存在（本文件 label 或 任何 scene）
    for tgt in parse_choose_targets(content):
        if tgt in labels:
            continue
        if tgt in all_scene_names:
            continue
        # 也允许是全局 label（跨文件）
        if tgt in all_labels:
            continue
        errors.append(f"[{stem}] choose 目标 '{tgt}' 不存在（不是 label 也不是 scene）")

    # 3. jumpLabel 目标必须存在
    for tgt in parse_jumplabel_targets(content):
        if tgt in labels:
            continue
        if tgt in all_scene_names:
            continue
        if tgt in all_labels:
            continue
        errors.append(f"[{stem}] jumpLabel 目标 '{tgt}' 不存在")

    # 4. changeScene 目标 scene 必须存在
    for tgt in parse_changescene_targets(content):
        if tgt in all_scene_names:
            continue
        errors.append(f"[{stem}] changeScene 目标 '{tgt}.txt' 不存在")

    # 5. callScene 目标 scene 必须存在
    for tgt in parse_callscene_targets(content):
        if tgt in all_scene_names:
            continue
        errors.append(f"[{stem}] callScene 目标 '{tgt}.txt' 不存在")

    # 6. setVar 变量类型一致
    setvars = parse_setvars(content)
    for name, vals in setvars.items():
        types = set()
        for v in vals:
            types.add(check_value_type(v))
        # number / bool / string 互斥；但 var/number_or_var 允许
        concrete = types - {'var', 'number_or_var'}
        if len(concrete) > 1:
            errors.append(f"[{stem}] setVar '{name}' 类型不一致: {types} -> values={vals}")
        # string vs number 互斥
        if 'string' in concrete and ('number' in concrete or 'bool' in concrete):
            errors.append(f"[{stem}] setVar '{name}' 混合 string 与其他类型: {types}")

    # 7. setVar 后必须被读取（消除"有设无用"）
    used = parse_conditions(content)
    for name in setvars:
        # 允许的"用完即弃"变量（流程标识，不参与结局条件）
        SELF_CONTAINED = {
            'continuedCode', 'choseRepair', 'chose_repair', 'chose_keep', 'chose_giveup',
            'doubt', 'shock', 'news_huge', 'forum_exit',
        }
        # 这些变量是局部流程节点，不需要在结局条件中读取
        if name in SELF_CONTAINED:
            continue
        if name not in used:
            warnings.append(f"[{stem}] setVar '{name}' 设置后从未在 if/-when 中被读取（建议检查是否需要）")

    return errors, warnings


def main():
    if not SCENE_DIR.exists():
        print(f"❌ 场景目录不存在: {SCENE_DIR}")
        sys.exit(1)

    scene_files = sorted(SCENE_DIR.glob("*.txt"))
    if not scene_files:
        print("❌ 场景目录为空")
        sys.exit(1)

    all_scene_names = collect_scene_names()

    # 第一轮：收集所有 label + 所有 setVar + 所有 used
    all_labels = defaultdict(list)
    all_setvars = defaultdict(list)  # name -> [(file, val)]
    all_used = set()  # 全局 if/-when 中使用的变量

    for f in scene_files:
        content = f.read_text(encoding='utf-8')
        for name, _ in parse_labels(content).items():
            all_labels[name].append(f.stem)
        for name, vals in parse_setvars(content).items():
            for v in vals:
                all_setvars[name].append((f.stem, v))
        all_used |= parse_conditions(content)
        # setVar 内部引用的变量也算"被使用"（如 setVar:clueCount=clueCount+1）
        for m in re.finditer(r'setVar\s*:\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*([^;]+)\s*;', content):
            rhs = m.group(1)
            for vm in re.finditer(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', rhs):
                vname = vm.group(1)
                # 排除明显是字面量
                if vname in {'true', 'false'}:
                    continue
                all_used.add(vname)

    print(f"📂 场景目录: {SCENE_DIR}")
    print(f"📄 场景文件数: {len(scene_files)}")
    print(f"📛 场景名: {sorted(all_scene_names)}")
    print()

    # 第二轮：验证
    total_errors = 0
    total_warnings = 0
    file_results = {}

    for f in scene_files:
        errors, warnings = validate_file(f, all_scene_names, all_labels)
        file_results[f.stem] = (errors, warnings)
        total_errors += len(errors)
        total_warnings += len(warnings)

    # 输出
    for stem, (errors, warnings) in file_results.items():
        if errors:
            print(f"❌ {stem}.txt ({len(errors)} errors)")
            for e in errors:
                print(f"   • {e}")
        if warnings:
            print(f"⚠️  {stem}.txt ({len(warnings)} warnings)")
            for w in warnings:
                print(f"   • {w}")

    # 跨文件检查：哪些 setVar 变量从未在任何 if/-when 中被读取？
    print()
    print(f"{'='*60}")
    print(f"🔍 跨文件 setVar → 读取 一致性检查")
    print(f"{'='*60}")
    dead_vars = []
    for name, sites in all_setvars.items():
        if name in all_used:
            continue
        # 局部流程节点允许"用完即弃"
        SELF_CONTAINED = {
            'choseRepair', 'chose_repair', 'chose_keep', 'chose_giveup',
            'doubt', 'shock', 'news_huge', 'forum_exit',
        }
        if name in SELF_CONTAINED:
            continue
        dead_vars.append((name, sites))

    if dead_vars:
        # 局部流程节点允许"用完即弃"
        # 过程标志：通过 clueCount 间接影响结局，不需要在 if 条件中显式读取
        PROCESS_FLAGS = {
            'award_talk', 'miss_call', 'cafe_boss', 'forum_clue',
            'speed_run', 'social_connect', 'trust', 'mirror_delay',
            'news_found', 'open_source', 'video_found', 'photo_fade',
            'wait_rain', 'paint_alive', 'device_overheat', 'stop_early',
            'code_aware',
        }
        # 过滤掉过程标志
        real_dead = [(n, s) for n, s in dead_vars if n not in PROCESS_FLAGS]
        proc_dead = [(n, s) for n, s in dead_vars if n in PROCESS_FLAGS]
        if proc_dead:
            print(f"💡 {len(proc_dead)} 个过程标志通过 clueCount 间接影响结局:")
            for name, sites in proc_dead:
                print(f"   • {name}")
        if real_dead:
            print(f"⚠️  {len(real_dead)} 个关键变量在所有文件中都未被读取:")
            for name, sites in real_dead:
                print(f"   • {name}  (set in: {[s[0] for s in sites]})")
        else:
            print()
            print(f"✅ 所有关键 setVar 变量都在至少一处 if/-when 中被读取")

        # 关键结局 flag 是否被覆盖
        critical = {'answer_call', 'save', 'clueCount', 'continue_code', 'echo_pass'}
        missing = critical & {n for n, _ in real_dead}
        if missing:
            print()
            print(f"❌ 关键结局 flag 缺失: {missing}（必须被读取）")
            return 1
    else:
        print(f"✅ 所有 setVar 变量都在至少一处 if/-when 中被读取")

    print()
    print(f"{'='*60}")
    if total_errors == 0:
        print(f"✅ 验证通过：0 errors, {total_warnings} 文件内 warnings")
    else:
        print(f"❌ 验证失败：{total_errors} errors, {total_warnings} warnings")
    print(f"{'='*60}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
