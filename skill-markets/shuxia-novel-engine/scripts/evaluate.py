# -*- coding: utf-8 -*-
"""
evaluate.py — 六维评估引擎 (v2.0 · 配置驱动)

用法:
  python evaluate.py --chapter 82
  python evaluate.py --chapter 82 --type combat

配置 (优先级: 环境变量 > evaluate_config.json > 内置默认):
  1. 复制 evaluate.env.example → evaluate.env        (路径/阈值覆盖)
  2. 复制 evaluate_config.example.json → evaluate_config.json (关键词/权重覆盖)
  3. 都不存在 → 使用内置默认值，开箱即用

六维: World / Society / Character / Plot / Theme / Aesthetic
参考: references/six_dim_evaluation.md
"""
import argparse
import glob
import json
import math
import os
import re
import sys
import io

# Windows UTF-8 兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



# ═══════════════════════════════════════════════════════════════
# §0 · 配置加载
# ═══════════════════════════════════════════════════════════════

def _script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _project_root():
    return os.path.dirname(os.path.dirname(_script_dir()))


def _resolve_path(maybe_rel):
    """相对路径 → 基于项目根解析"""
    if not maybe_rel:
        return None
    if os.path.isabs(maybe_rel):
        return maybe_rel
    return os.path.normpath(os.path.join(_project_root(), maybe_rel))


def _load_dotenv():
    """手动解析 .env 文件，返回 dict（零依赖）"""
    env_path = os.path.join(_script_dir(), 'evaluate.env')
    if not os.path.isfile(env_path):
        return {}
    result = {}
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().lstrip('\ufeff')
                val = val.strip().strip('"').strip("'")
                result[key] = val
    return result


def _load_json_config(dotenv):
    """加载 JSON 配置，dotenv 中的 EVAL_CONFIG_PATH 优先"""
    cfg_path = dotenv.get('EVAL_CONFIG_PATH', '')
    if not cfg_path:
        # 默认同目录下的 evaluate_config.json
        default = os.path.join(_script_dir(), 'evaluate_config.json')
        if os.path.isfile(default):
            cfg_path = default
    cfg_path = _resolve_path(cfg_path)
    if not cfg_path or not os.path.isfile(cfg_path):
        return {}
    with open(cfg_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _env_int(dotenv, key, default):
    v = dotenv.get(key, '')
    return int(v) if v else default


def _env_float(dotenv, key, default):
    v = dotenv.get(key, '')
    return float(v) if v else default


# 加载
_DOTENV = _load_dotenv()
_JSON_CFG = _load_json_config(_DOTENV)


def _cfg(key, default):
    """优先 JSON 配置，回退默认"""
    return _JSON_CFG.get(key, default)


def _env_or_cfg(dotenv_key, json_key, default):
    """环境变量 > JSON > 默认"""
    v = _DOTENV.get(dotenv_key, '')
    if v:
        return v
    return _JSON_CFG.get(json_key, default)


# ═══════════════════════════════════════════════════════════════
# §1 · 路径 / 阈值 / 正则（均可覆盖）
# ═══════════════════════════════════════════════════════════════

PROJECT_ROOT = _project_root()
CHAPTER_ROOT = _resolve_path(
    _DOTENV.get('EVAL_CHAPTER_ROOT', '')
) or os.path.join(PROJECT_ROOT, '创作正文', '章节规划')

# 等级阈值
GRADE_S = _env_int(_DOTENV, 'EVAL_GRADE_S', 95)
GRADE_A = _env_int(_DOTENV, 'EVAL_GRADE_A', 85)
GRADE_B = _env_int(_DOTENV, 'EVAL_GRADE_B', 75)
GRADE_C = _env_int(_DOTENV, 'EVAL_GRADE_C', 65)

# CONDITIONAL 判定
LOW_DIM_WEIGHT = _env_float(_DOTENV, 'EVAL_LOW_DIM_WEIGHT', 0.10)
LOW_DIM_SCORE = _env_int(_DOTENV, 'EVAL_LOW_DIM_SCORE', 70)

# 量化密度期望
QUANT_DENSITY = {
    'combat':     _env_float(_DOTENV, 'EVAL_QUANT_DENSITY_COMBAT', 2.0),
    'drama':      _env_float(_DOTENV, 'EVAL_QUANT_DENSITY_DRAMA', 1.0),
    'reveal':     _env_float(_DOTENV, 'EVAL_QUANT_DENSITY_REVEAL', 1.5),
    'transition': _env_float(_DOTENV, 'EVAL_QUANT_DENSITY_TRANSITION', 1.2),
}

# 量化参数正则
_quant_regex_str = _env_or_cfg('EVAL_QUANT_REGEX', 'quant_regex',
    r'\d+\.?\d*\s*(?:息|米|公里|千米|尺|丈|秒|分钟|小时|天|年|'
    r'Hz|kHz|MHz|dB|kW|W|%|倍|息/秒|息/米|息/立方米)')
QUANT_PATTERN = re.compile(_quant_regex_str)

# Unicode 进度条
NO_UNICODE_BAR = _DOTENV.get('EVAL_NO_UNICODE_BAR', '0') == '1'

# ═══════════════════════════════════════════════════════════════
# §2 · 结构化配置（JSON 覆盖 > 内置默认）
# ═══════════════════════════════════════════════════════════════

WEIGHTS = _cfg('weights', {
    'combat':     {'World':0.40, 'Society':0.05, 'Character':0.10, 'Plot':0.20, 'Theme':0.05, 'Aesthetic':0.20},
    'drama':      {'World':0.05, 'Society':0.10, 'Character':0.30, 'Plot':0.10, 'Theme':0.15, 'Aesthetic':0.30},
    'reveal':     {'World':0.25, 'Society':0.15, 'Character':0.15, 'Plot':0.20, 'Theme':0.20, 'Aesthetic':0.05},
    'transition': {'World':0.15, 'Society':0.10, 'Character':0.20, 'Plot':0.25, 'Theme':0.10, 'Aesthetic':0.20},
})

FORBIDDEN_KEYWORDS = _cfg('forbidden_keywords', [
    {'role': '林岳', 'keywords': [
        '调监控', '逐帧看', '查数据库', '用算法', '系统标记', '算法扫描',
        '非人格化清除', '关键词扫描系统', '算法判断', '系统自动标记',
        '污染面评估', '高效杀毒软件', '杀毒软件', '逐帧筛查', '一帧一帧',
        '监控录像', '监控画面', '调取监控录像', '调取监控']},
    {'role': '严峰', 'keywords': [
        '调监控', '逐帧看', '查数据库', '用算法', '监控', '摄像头',
        '逐帧筛查', '一帧一帧', '监控录像', '监控画面', '调取监控录像',
        '调取监控', '屏幕查询']},
    {'role': '清洗司', 'keywords': [
        'SOP', '例行扫描', '自动巡检', '算法扫描', '系统判定', '算法判定',
        '标记库', '关键词扫描系统', '系统自动标记']},
])

_SKW = _cfg('scoring_keywords', {})
SKW_PHYSICS      = _SKW.get('world_physics', ['灵场', '灵子', '耦合', 'L场', 'Klein-Gordon', 'BEC', '退相干', '相干', '灵压', '灵导率', 'Maxwell', '反相'])
SKW_LINGYA       = _SKW.get('world_lingya_signal', ['灵压', '绝灵之地', 'P_L', '息'])
SKW_FACTIONS     = _SKW.get('society_factions', ['清洗司', '万象宗', '万象', '辛国', '宗门', '商会', '妖族'])
SKW_CLASS        = _SKW.get('society_class', ['阶级', '阶层', '凡人', '修真者', '傲慢', '蔑视', '高贵', '低贱', '体制', '不平等', '压迫', '特权'])
SKW_WIN          = _SKW.get('plot_win', ['赢面', '生存博弈', '认知纵深', '信息不对称', '技术代偿', '系统性盲区', '内部管理', '认知框架', '执行链衰减', '路径依赖', '结构性弱点', '天时地利', '灵压环境', '力量差', '不可重复', '生存智慧', '代价', '敌人学习'])
SKW_WAIWU        = _SKW.get('theme_waiwu', ['屏障', '石眼', '电池', '装置', '外物', '工具', '装备', '法器', '灵玉', '监测器', '套件', '经典物理', '频谱', '罗盘'])
SKW_COLLISION    = _SKW.get('theme_collision', ['神识', '灵场', '修真', '经典物理', '科技', '频谱', 'L场', '凡人', '修真者', '两种', '碰撞'])
SKW_TEMPLATE_BAN = _SKW.get('theme_template_blacklist', ['飞升', '天道意志', '混沌珠', '位面之子', '气运', '天命'])
SKW_SENSES       = _SKW.get('aesthetic_senses', {
    '视觉': ['看到', '画面', '红外', '目视', '暗处', '光', '颜色'],
    '听觉': ['听到', '声音', '沉默', '脚步', '通讯', '噪音'],
    '触觉': ['压迫', '距离', '近身', '擦肩', '温度', '冷', '热'],
    '灵场': ['神识', '灵波', '灵压', '灵场', '罗盘', '信号'],
})

SOCIETY_BASE = _cfg('society_base_scores', {'combat': 40, 'drama': 55, 'reveal': 50, 'transition': 45})
SUB_WORLD     = _cfg('subfactor_weights', {}).get('world',     [25, 25, 20, 15, 15])
SUB_PLOT      = _cfg('subfactor_weights', {}).get('plot',      [30, 25, 20, 15, 10])
SUB_THEME     = _cfg('subfactor_weights', {}).get('theme',     [37, 31, 19, 13])
SUB_AESTHETIC = _cfg('subfactor_weights', {}).get('aesthetic', [28, 35, 19, 18])

W_PHYSICS_THRESHOLD    = _cfg('world_physics_threshold', 4)
W_DEP_REFS_THRESHOLD   = _cfg('world_dep_refs_threshold', 5)
T_WAIWU_THRESHOLD      = _cfg('theme_waiwu_threshold', 5)
T_COLLISION_THRESHOLD  = _cfg('theme_collision_threshold', 5)
P_FORESHADOW_THRESHOLD = _cfg('plot_foreshadow_threshold', 3)
P_WIN_THRESHOLD        = _cfg('plot_win_threshold', 3)
P_INFO_GAP_THRESHOLD   = _cfg('plot_info_gap_threshold', 2)

CHAR_BASE          = _cfg('character_base_score', 95)
CHAR_PENALTY       = _cfg('character_penalty_per_hit', 12)
CHAR_MIN           = _cfg('character_min_score', 30)
CHAR_EMOTION_CAP   = _cfg('character_emotion_bonus_cap', 5)


# ═══════════════════════════════════════════════════════════════
# §3 · 辅助解析函数
# ═══════════════════════════════════════════════════════════════

def find_chapter_file(chapter_num):
    """按章号查找章节规划文件"""
    pattern = os.path.join(CHAPTER_ROOT, '*', f'第{chapter_num}章-*.md')
    files = glob.glob(pattern)
    if not files:
        for root, dirs, filenames in os.walk(CHAPTER_ROOT):
            for f in filenames:
                if re.match(rf'第{chapter_num}章[-·].*\.md$', f):
                    return os.path.join(root, f)
        return None
    return files[0]


def parse_section(text, heading):
    """从 Markdown 文本中提取指定标题下的内容（不含下级标题）"""
    pattern = rf'^## {re.escape(heading)}\s*$'
    lines = text.split('\n')
    in_section = False
    result = []
    for line in lines:
        if re.match(pattern, line):
            in_section = True
            continue
        if in_section:
            if re.match(r'^##\s', line):
                break
            result.append(line)
    return '\n'.join(result)


def parse_kv_lines(text):
    """解析 '- key: value' 格式的行"""
    result = {}
    for line in text.split('\n'):
        m = re.match(r'-\s*\*\*(.+?)\*\*[：:]\s*(.+)', line)
        if m:
            result[m.group(1).strip()] = m.group(2).strip()
        else:
            m2 = re.match(r'-\s*(.+?)[：:]\s*(.+)', line)
            if m2:
                result[m2.group(1).strip()] = m2.group(2).strip()
    return result


def parse_table_rows(text):
    """解析 Markdown 表格行"""
    rows = []
    lines = text.split('\n')
    header = None
    for i, line in enumerate(lines):
        if line.startswith('|') and '---' in line:
            header = [c.strip() for c in lines[i-1].split('|')[1:-1]]
            continue
        if header and line.startswith('|') and '---' not in line:
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) == len(header):
                rows.append(dict(zip(header, cells)))
    return rows


def count_quantified_params(text):
    """统计文本中量化参数的数量"""
    return len(QUANT_PATTERN.findall(text))


def scan_forbidden(text):
    """扫描文本中的禁止方法关键词"""
    hits = []
    paragraphs = text.split('\n\n')
    for entry in FORBIDDEN_KEYWORDS:
        role = entry['role']
        keywords = entry['keywords']
        seen_kw = set()
        for para in paragraphs:
            if role not in para:
                continue
            for kw in keywords:
                if kw in para and kw not in seen_kw:
                    hits.append((role, kw))
                    seen_kw.add(kw)
    return hits


# ═══════════════════════════════════════════════════════════════
# §4 · 六维评分函数
# ═══════════════════════════════════════════════════════════════

def score_world(chapter_data):
    full_text = chapter_data['raw']
    word_estimate = int(chapter_data.get('字数预估', 4000))
    world_points_section = chapter_data.get('世界观要点', '')
    deps_section = chapter_data.get('前置依赖', '')

    quant_count = count_quantified_params(full_text)
    quant_density = quant_count / (word_estimate / 100.0)
    scene_type = chapter_data.get('scene_type', 'combat')
    expected_density = QUANT_DENSITY.get(scene_type, 2.0)
    w5 = min(1.0, quant_density / max(0.01, expected_density))

    physics_count = sum(1 for kw in SKW_PHYSICS if kw in world_points_section)
    w2 = min(1.0, physics_count / W_PHYSICS_THRESHOLD)

    dep_refs = len(re.findall(r'ch\d+|《[^》]+》', deps_section))
    w3 = min(1.0, dep_refs / W_DEP_REFS_THRESHOLD)

    has_lingya = any(kw in full_text for kw in SKW_LINGYA)
    w1 = 0.9 if has_lingya else 0.5

    scenes_section = chapter_data.get('关键场景', '')
    has_location = bool(re.search(r'[工厂|医院|节点|管道|仓库|城区|街道]', scenes_section))
    w4 = 0.85 if has_location else 0.6

    score = (w1 * SUB_WORLD[0] + w2 * SUB_WORLD[1] + w3 * SUB_WORLD[2] +
             w4 * SUB_WORLD[3] + w5 * SUB_WORLD[4])
    meta = [f'量化密度{quant_count}个/百字{quant_density:.2f}',
            f'物理概念{physics_count}个',
            f'前置引用{dep_refs}条']
    return round(score), meta


def score_society(chapter_data):
    full_text = chapter_data['raw']

    factions = set()
    for kw in SKW_FACTIONS:
        if kw in full_text:
            factions.add(kw)

    class_signals = sum(1 for kw in SKW_CLASS if kw in full_text)

    scene_type = chapter_data.get('scene_type', 'combat')
    base = SOCIETY_BASE.get(scene_type, 45)

    score = base
    score += min(15, len(factions) * 5)
    score += min(15, class_signals * 5)
    score = min(100, score)

    meta = []
    if factions:
        meta.append(f'势力{len(factions)}个: {",".join(sorted(factions)[:3])}')
    else:
        meta.append('无明确势力划分')
    meta.append(f'阶级信号{class_signals}处')
    return score, meta


def score_character(chapter_data):
    full_text = chapter_data['raw']
    forbidden_hits = scan_forbidden(full_text)

    penalty = len(forbidden_hits) * CHAR_PENALTY
    score = max(CHAR_MIN, CHAR_BASE - penalty)

    meta = []
    if forbidden_hits:
        for char, kw in forbidden_hits:
            meta.append(f'{char}使用"{kw}" ✗')
        meta.append(f'{len(forbidden_hits)}处违规')
    else:
        meta.append('行为锚点匹配 ✓')

    emotion = chapter_data.get('情绪基调', '')
    if emotion:
        emotion_parts = [e.strip() for e in re.split(r'[/／→]', emotion)]
        if len(emotion_parts) >= 2:
            meta.append(f'情绪转折{len(emotion_parts)}层')
            score += min(CHAR_EMOTION_CAP, len(emotion_parts))

    return min(100, score), meta


def score_plot(chapter_data):
    full_text = chapter_data['raw']
    plot_section = chapter_data.get('剧情推进', '')

    scene_count = len(re.findall(r'^\d+\.', full_text, re.MULTILINE))
    if scene_count < 1:
        scene_count = chapter_data.get('scene_count', 3)
    p1 = min(1.0, scene_count / 4.0)

    foreshadow_count = len(re.findall(r'F\d+|伏笔|埋设|推进|回收', plot_section))
    p2 = min(1.0, foreshadow_count / P_FORESHADOW_THRESHOLD)

    win_signals = sum(1 for kw in SKW_WIN if kw in plot_section)
    p3 = min(1.0, win_signals / P_WIN_THRESHOLD)

    info_gap = len(re.findall(r'信息差', plot_section))
    p4 = min(1.0, info_gap / P_INFO_GAP_THRESHOLD)

    word_est = int(chapter_data.get('字数预估', 4000))
    event_rate = scene_count / max(1, word_est / 1000.0)
    expected_rate = 3.0 if chapter_data.get('scene_type') == 'combat' else 1.5
    p5 = min(1.0, event_rate / max(0.01, expected_rate))

    score = round((p1 * SUB_PLOT[0] + p2 * SUB_PLOT[1] + p3 * SUB_PLOT[2] +
                   p4 * SUB_PLOT[3] + p5 * SUB_PLOT[4]))
    meta = [f'场景{scene_count}个', f'伏笔{foreshadow_count}处',
            f'赢面信号{win_signals}个', f'信息差{info_gap}层']
    return score, meta


def score_theme(chapter_data):
    full_text = chapter_data['raw']
    new_reveal = chapter_data.get('世界观要点', '')

    waiwu_count = sum(1 for kw in SKW_WAIWU if kw in full_text)
    t1 = min(1.0, waiwu_count / T_WAIWU_THRESHOLD)

    collision_count = sum(1 for kw in SKW_COLLISION if kw in full_text)
    t2 = min(1.0, collision_count / T_COLLISION_THRESHOLD)

    has_new = bool(re.search(r'新揭示|首次|此前未', new_reveal))
    t3 = 1.0 if has_new else 0.6

    template_hits = sum(1 for kw in SKW_TEMPLATE_BAN if kw in full_text)
    t4 = 1.0 if template_hits == 0 else max(0.3, 1.0 - template_hits * 0.3)

    score = round((t1 * SUB_THEME[0] + t2 * SUB_THEME[1] +
                   t3 * SUB_THEME[2] + t4 * SUB_THEME[3]))
    meta = [f'外物信号{waiwu_count}处', f'碰撞信号{collision_count}处',
            f'新揭示: {"是" if has_new else "否"}']
    if template_hits:
        meta.append(f'模板词{template_hits}处 ✗')
    return score, meta


def score_aesthetic(chapter_data):
    full_text = chapter_data['raw']
    emotion = chapter_data.get('情绪基调', '')
    narrative_fn = chapter_data.get('叙事功能', '')

    scene_count = len(re.findall(r'^\d+\.', full_text, re.MULTILINE))
    if scene_count < 1:
        scene_count = chapter_data.get('scene_count', 3)
    word_est = int(chapter_data.get('字数预估', 4000))
    keyframe_density = scene_count / max(1, word_est / 1000.0)
    expected = 1.0 if chapter_data.get('scene_type') == 'combat' else 0.8
    a2 = min(1.0, keyframe_density / max(0.01, expected))

    emotion_parts = [e.strip() for e in re.split(r'[/／→/]', emotion)] if emotion else []
    a1 = min(1.0, len(emotion_parts) / 3.0) if emotion_parts else 0.6

    satire = chapter_data.get('讽刺/幽默', '')
    has_satire = bool(satire) or '讽刺' in narrative_fn or '幽默' in narrative_fn or '荒诞' in full_text
    a4 = 0.9 if has_satire else 0.5

    senses_present = 0
    for sense, kws in SKW_SENSES.items():
        if any(kw in full_text for kw in kws):
            senses_present += 1
    a5 = senses_present / max(1, len(SKW_SENSES))

    score = round((a1 * SUB_AESTHETIC[0] + a2 * SUB_AESTHETIC[1] +
                   a4 * SUB_AESTHETIC[2] + a5 * SUB_AESTHETIC[3]))
    meta = [f'关键帧密度{keyframe_density:.2f}/千字',
            f'情绪层数{len(emotion_parts)}',
            f'讽刺: {"是" if has_satire else "否"}',
            f'感官{senses_present}/{len(SKW_SENSES)}']
    return score, meta


# ═══════════════════════════════════════════════════════════════
# §5 · 主评估函数
# ═══════════════════════════════════════════════════════════════

def evaluate_scene(chapter_num, scene_type='combat'):
    # 1. 查找章节文件
    chapter_file = find_chapter_file(chapter_num)
    if not chapter_file:
        print(f'[错误] 找不到第{chapter_num}章的规划文件', file=sys.stderr)
        sys.exit(1)

    # 2. 读取并解析
    with open(chapter_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    chapter_data = {'raw': raw_text, 'scene_type': scene_type}

    loc_section = parse_section(raw_text, '本章定位')
    loc_kv = parse_kv_lines(loc_section)
    chapter_data['所属阶段'] = loc_kv.get('所属阶段', '')
    chapter_data['叙事功能'] = loc_kv.get('叙事功能', '')
    chapter_data['情绪基调'] = loc_kv.get('情绪基调', '')
    word_match = re.search(r'(\d+)', loc_kv.get('字数预估', '4000'))
    chapter_data['字数预估'] = word_match.group(1) if word_match else '4000'
    chapter_data['讽刺/幽默'] = loc_kv.get('讽刺/幽默', '')

    chapter_data['世界观要点'] = parse_section(raw_text, '世界观要点')
    chapter_data['前置依赖'] = parse_section(raw_text, '前置依赖')
    chapter_data['剧情推进'] = parse_section(raw_text, '剧情推进')
    chapter_data['关键场景'] = parse_section(raw_text, '关键场景')

    scenes_rows = parse_table_rows(chapter_data['关键场景'])
    chapter_data['scene_count'] = len(scenes_rows)

    # 3. 六维评分
    w = WEIGHTS.get(scene_type, WEIGHTS.get('transition', {
        'World':0.15,'Society':0.10,'Character':0.20,'Plot':0.25,'Theme':0.10,'Aesthetic':0.20}))

    dims = [
        ('World',     score_world),
        ('Society',   score_society),
        ('Character', score_character),
        ('Plot',      score_plot),
        ('Theme',     score_theme),
        ('Aesthetic', score_aesthetic),
    ]

    results = {}
    all_meta = {}
    for dim_name, scorer in dims:
        score, meta = scorer(chapter_data)
        results[dim_name] = score
        all_meta[dim_name] = meta

    # 4. 总分
    total = 0
    for dim_name in results:
        total += results[dim_name] * w.get(dim_name, 0.15)
    total = round(total)

    # 5. 等级
    if total >= GRADE_S:   grade = 'S'
    elif total >= GRADE_A: grade = 'A'
    elif total >= GRADE_B: grade = 'B'
    elif total >= GRADE_C: grade = 'C'
    else:                  grade = 'D'

    # 6. 条件性判定
    low_dims = [d for d, s in results.items()
                if s < LOW_DIM_SCORE and w.get(d, 0) >= LOW_DIM_WEIGHT]
    verdict = 'CONDITIONAL' if low_dims else 'PASS'

    # 7. 输出
    print(f'\n=== 六维评估 · 第{chapter_num}章 · 类型: {scene_type} ===\n')

    for dim_name in ['World', 'Society', 'Character', 'Plot', 'Theme', 'Aesthetic']:
        score = results[dim_name]
        meta_str = ' | '.join(all_meta[dim_name])
        if NO_UNICODE_BAR:
            bar = '#' * (score // 10) + '-' * (10 - score // 10)
        else:
            bar = chr(0x2588) * (score // 10) + chr(0x2591) * (10 - score // 10)
        if dim_name == 'Society':
            print(f'{dim_name:12s} {score:3d}/100 [{bar}] [基于元数据估算]')
        else:
            print(f'{dim_name:12s} {score:3d}/100 [{bar}]')
        if meta_str:
            print(f'             ({meta_str})')

    print(f'\n总分: {total}/100 [{grade}级] — {verdict}')

    # 8. 改进建议
    suggestions = []
    if results['World'] < 75:
        suggestions.append('World维度偏低，建议补充量化参数和物理机制解释')
    if results['Society'] < 70:
        suggestions.append('Society维度可补充阶级矛盾或势力关系的暗示')
    if results['Character'] < 80:
        suggestions.append('Character维度检测到角色行为锚点违规')
    if results['Plot'] < 75:
        suggestions.append('Plot维度可增强伏笔操作或赢面公式体现')
    if results['Theme'] < 70:
        suggestions.append('Theme维度需强化外物证道或文明碰撞主题')
    if results['Aesthetic'] < 70:
        suggestions.append('Aesthetic维度可增加感官描写或情绪层次')
    if suggestions:
        print(f'改进: {"; ".join(suggestions)}')

    return 0


# ═══════════════════════════════════════════════════════════════
# §6 · CLI 入口
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='亚文化创作引擎 · 六维评估')
    parser.add_argument('--chapter', type=int, required=True)
    parser.add_argument('--type', choices=['combat','drama','reveal','transition'],
                       default='combat')
    args = parser.parse_args()
    sys.exit(evaluate_scene(args.chapter, args.type))