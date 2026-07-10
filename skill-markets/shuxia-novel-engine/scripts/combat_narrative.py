"""
combat_narrative.py · 武戏量化评分

用法:
  python combat_narrative.py --chapter 82
  python combat_narrative.py --file path/to/chapter.md

四维: 节奏(R) / 空间(S) / 力量逆转(P) / 画面感(V)
公式: QS = w_R·R + w_S·S + w_P·P + w_V·V
参考: references/combat_model.md
"""
import argparse
import io
import os
import re
import sys

# Windows UTF-8 兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# — 关键词库 (从 combat_model.md 提炼) —
RHYTHM_FAST = re.compile(r'(爆发|冲刺|疾|瞬|闪|劈|斩|轰|爆|炸|裂|碎|崩)')
RHYTHM_SLOW = re.compile(r'(屏息|潜伏|暗处|阴影|缓慢|挪|匍匐|躲|藏|隐|蛰)')
RHYTHM_BREATH = re.compile(r'(喘息|呼吸|停顿|静|默|僵|凝)')
SPACE_VERT = re.compile(r'(上|下|顶层|底层|天花板|通风管|管道|井|梁|檐|屋顶|地下|坑)')
SPACE_DIM = re.compile(r'(狭窄|宽阔|空旷|逼仄|三(尺|米|丈)|五(尺|米|丈)|十(尺|米|丈))')
POWER_SHIFT = re.compile(r'(逆转|反而|竟然|不料|谁知|不料|翻盘|反制|反杀)')
VISUAL_FRAME = re.compile(r'(看见|只见|眼中|视野|血雾|碎屑|光芒|暗影|轮廓|残影)')

CHAPTER_PATTERN = re.compile(r'第(\d+)章')

def _find_chapter(project_root, chapter_num):
    """查找章节文件"""
    search_dirs = [
        os.path.join(project_root, '创作正文', '章节规划', '卷一'),
        os.path.join(project_root, '创作正文', '章节规划'),
        os.path.join(project_root, '创作正文', '剧情'),
    ]
    for sd in search_dirs:
        if not os.path.isdir(sd):
            continue
        for fname in os.listdir(sd):
            if not fname.endswith('.md'):
                continue
            m = CHAPTER_PATTERN.search(fname)
            if m and int(m.group(1)) == chapter_num:
                return os.path.join(sd, fname)
    # Fallback: search all md files
    for root, dirs, files in os.walk(os.path.join(project_root, '创作正文')):
        for fname in files:
            if fname.endswith('.md'):
                m = CHAPTER_PATTERN.search(fname)
                if m and int(m.group(1)) == chapter_num:
                    return os.path.join(root, fname)
    return None

def _find_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    return os.path.dirname(skill_dir)

def score_combat(chapter_num=None, file_path=None):
    project_root = _find_project_root()
    
    if file_path:
        chapter_file = file_path
    elif chapter_num:
        chapter_file = _find_chapter(project_root, chapter_num)
    else:
        print("[ERROR] 需要 --chapter 或 --file")
        sys.exit(1)
    
    if not chapter_file or not os.path.exists(chapter_file):
        print(f"[ERROR] 章节文件未找到: chapter={chapter_num}")
        sys.exit(1)
    
    with open(chapter_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 检测是否为武戏章
    is_combat = bool(re.search(r'(战斗|厮杀|激战|对决|围杀|伏击|截杀)', text))
    
    words = len(re.findall(r'[\u4e00-\u9fff]', text))
    word_count = max(words, 1)
    
    # — 四维评分 —
    # R: 节奏密度
    fast_hits = len(RHYTHM_FAST.findall(text))
    slow_hits = len(RHYTHM_SLOW.findall(text))
    breath_hits = len(RHYTHM_BREATH.findall(text))
    total_rhythm = fast_hits + slow_hits + breath_hits
    rhythm_density = total_rhythm / (word_count / 1000) if word_count else 0
    # 理想密度 ~15-25/千字
    if rhythm_density < 5:
        R = 30
    elif rhythm_density < 10:
        R = 50
    elif rhythm_density < 25:
        R = 80
    elif rhythm_density < 40:
        R = 70
    else:
        R = 50  # 过密→疲劳
    # 躲藏型慢态奖励
    if slow_hits > fast_hits * 0.5 and is_combat:
        R = min(100, R + 10)
    
    # S: 空间利用
    vert_hits = len(SPACE_VERT.findall(text))
    dim_hits = len(SPACE_DIM.findall(text))
    S = min(100, (vert_hits * 8 + dim_hits * 6))
    
    # P: 力量逆转
    shift_hits = len(POWER_SHIFT.findall(text))
    P = min(100, shift_hits * 15 + 40)
    
    # V: 画面感
    frame_hits = len(VISUAL_FRAME.findall(text))
    frame_density = frame_hits / (word_count / 1000) if word_count else 0
    V = min(100, frame_density * 5 + 50)
    
    # — 加权综合 —
    w_R, w_S, w_P, w_V = 0.30, 0.25, 0.25, 0.20
    QS = w_R * R + w_S * S + w_P * P + w_V * V
    
    # — 等级 —
    if QS >= 85:
        grade = "卓越"
    elif QS >= 70:
        grade = "优秀"
    elif QS >= 55:
        grade = "合格"
    else:
        grade = "需改进"
    
    print(f"\n=== 武戏评估 · 第 {chapter_num or file_path} 章 ===")
    print(f"类型: {'武戏章' if is_combat else '非武戏章(以躲藏/潜行为主)'}")
    print(f"字数: {words}")
    print(f"节奏(R): {R:.0f}/100 (快{fast_hits} 慢{slow_hits} 呼吸{breath_hits} 密度{rhythm_density:.1f}/千字)")
    print(f"空间(S): {S:.0f}/100 (垂直{vert_hits} 尺度{dim_hits})")
    print(f"逆转(P): {P:.0f}/100 (逆转信号{shift_hits})")
    print(f"画面(V): {V:.0f}/100 (关键帧{frame_hits} 密度{frame_density:.1f}/千字)")
    print(f"综合: {QS:.1f}/100 [{grade}]")
    
    return {'R': R, 'S': S, 'P': P, 'V': V, 'QS': QS, 'grade': grade}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='武戏量化评分')
    parser.add_argument('--chapter', type=int, help='章节号')
    parser.add_argument('--file', type=str, help='章节文件路径')
    args = parser.parse_args()
    score_combat(args.chapter, args.file)
