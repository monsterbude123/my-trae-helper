"""
drama_narrative.py · 文戏温度评分

用法:
  python drama_narrative.py --chapter 29
  python drama_narrative.py --file path/to/chapter.md

五组件: 情感递进(E) / 关系状态(R) / 对话张力(D) / 留白(O) / 基础温度
公式: T = T_base + E×R×D×O×80
参考: references/drama_model.md
"""
import argparse
import io
import os
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# — 关键词库 —
EMOTION = re.compile(r'(孤独|悲伤|愤怒|恐惧|喜悦|惊讶|厌恶|信任|期待|温暖|冷漠|怀念|悔恨|愧疚|感动|欣慰|释然|绝望|希望|迷茫|坚定|犹豫)')
RELATION = re.compile(r'(信任|依赖|疏远|亲近|敌意|戒备|默契|误会|和解|背叛|守护|牺牲|陪伴|离别|重逢|沉默|凝视|触碰|拥抱|并肩)')
DIALOGUE = re.compile(r'"[^"]{10,}"|"[^"]{10,}"|——[^，。]{5,}|……')
SUB_TEXT = re.compile(r'((?:却|但|然而|只是|其实|原来|竟然|不料)[^。]{5,}(?:没说|没说出口|咽|忍|按捺|压抑))')
BLANK = re.compile(r'(沉默|不语|无言|静|半晌|良久|许久|……|——\s*$)')

CHAPTER_PATTERN = re.compile(r'第(\d+)章')

def _find_chapter(project_root, chapter_num):
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
    for root, dirs, files in os.walk(os.path.join(project_root, '创作正文')):
        for fname in files:
            if fname.endswith('.md'):
                m = CHAPTER_PATTERN.search(fname)
                if m and int(m.group(1)) == chapter_num:
                    return os.path.join(root, fname)
    return None

def _find_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))

def score_drama(chapter_num=None, file_path=None):
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
    
    words = len(re.findall(r'[\u4e00-\u9fff]', text))
    word_count = max(words, 1)
    
    # — 五组件评分 —
    # E: 情感递进
    emotion_hits = len(EMOTION.findall(text))
    E = min(1.0, emotion_hits / max(word_count / 500, 1))  # scale to 0-1
    
    # R: 关系状态
    relation_hits = len(RELATION.findall(text))
    R = min(1.0, relation_hits / max(word_count / 400, 1))
    
    # D: 对话张力
    dialogue_hits = len(DIALOGUE.findall(text))
    subtext_hits = len(SUB_TEXT.findall(text))
    D = min(1.0, (dialogue_hits * 0.6 + subtext_hits * 2.0) / max(word_count / 300, 1))
    
    # O: 留白
    blank_hits = len(BLANK.findall(text))
    O = min(1.0, blank_hits / max(word_count / 500, 0.5))
    if blank_hits < 3:
        O = max(O, 0.15)  # 最少留白基数
    
    # — 基础温度 —
    is_drama = bool(re.search(r'(对话|交谈|倾诉|密谈|谈心|告别|重逢|独白|回忆|沉思)', text))
    T_base = 30 if is_drama else 20
    
    # — 综合温度 —
    T = T_base + E * R * D * O * 80
    
    # — 温度带 —
    if T >= 80:
        band = "T2 炽热"
    elif T >= 55:
        band = "T1 温热"
    elif T >= 40:
        band = "T0 微热"
    elif T >= 25:
        band = "T-1 温"
    else:
        band = "T-2 冷却"
    
    print(f"\n=== 文戏温度 · 第 {chapter_num or file_path} 章 ===")
    print(f"类型: {'文戏章' if is_drama else '非纯文戏章'}")
    print(f"字数: {words}")
    print(f"情感递进(E): {E:.2f} (情感词{emotion_hits})")
    print(f"关系状态(R): {R:.2f} (关系信号{relation_hits})")
    print(f"对话张力(D): {D:.2f} (对话{dialogue_hits} 潜台词{subtext_hits})")
    print(f"留白(O):    {O:.2f} (留白信号{blank_hits})")
    print(f"基础温度:   {T_base:.0f}°")
    print(f"温度(T):    {T:.1f}° [{band}]")
    
    return {'E': E, 'R': R, 'D': D, 'O': O, 'T': T, 'band': band}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='文戏温度评分')
    parser.add_argument('--chapter', type=int, help='章节号')
    parser.add_argument('--file', type=str, help='章节文件路径')
    args = parser.parse_args()
    score_drama(args.chapter, args.file)
