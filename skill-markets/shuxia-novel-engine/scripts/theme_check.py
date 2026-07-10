"""
theme_check.py · 主题一致性检查

用法:
  python theme_check.py --chapter 82
  python theme_check.py --file path/to/chapter.md

检测: 25 个主题信号 + 6 类偏离 + 密度模型
参考: references/theme_model.md
"""
import argparse
import io
import os
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# — T1 外物证道信号 —
T1_SIGNALS = re.compile(r'(量化|功率|瓦|千瓦|毫瓦|频率|赫兹|电路|芯片|算法|传感器|示波器|示波|BEC|超辐射|灵场耦合|EM波|量子隧穿|热力学|熵|退相干)')
# — T2 文明碰撞信号 —
T2_SIGNALS = re.compile(r'(修真者|凡人|傲慢|不屑|蝼蚁|蚂蚁|蝼蚁之辈|法力|灵气|灵压|灵子|神识|修士|宗门|功法|大阵)')
# — T3 认知差即武器信号 —
T3_SIGNALS = re.compile(r'(不知道|不知道的是|从未见过|无法理解|认知|盲区|信息差|误解|低估|高估|没想到|不料|竟然|怎么会|怎么可能)')

# — 偏离检测 —
D1_PROTAGONIST_ARMOR = re.compile(r'(侥幸|恰好|正好|正巧|幸运|运气|命大|天意|天不绝|必死|绝境.*[幸存生还])')
D2_GENERIC_TEMPLATE = re.compile(r'(飞升|渡劫|天道意志|主角光环|混沌珠|穿越者福利|天选之人|天命所归)')
D3_TECH_DEGRADE = re.compile(r'(竟忘了|顾不上|来不及.*科技|科技.*来不及|科学.*没用)')
D4_ENEMY_NERF = re.compile(r'(竟然怕了|竟然退缩|胆怯|畏缩|恐惧.*敌人|敌人.*恐惧|怂了)')
D5_OVER_THEMING = re.compile(r'(.{0,10}文明.{0,10}文明.{0,10}|.{0,10}主题.{0,10}主题.{0,10})')
D6_TERM_RESIDUE = re.compile(r'(调监控|逐帧|数据库.*筛查|关键词.*扫描|算法.*标记)')

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

def check_theme(chapter_num=None, file_path=None):
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
    
    # — 信号扫描 —
    t1_hits = len(T1_SIGNALS.findall(text))
    t2_hits = len(T2_SIGNALS.findall(text))
    t3_hits = len(T3_SIGNALS.findall(text))
    
    t1_density = t1_hits / (word_count / 1000)
    t2_density = t2_hits / (word_count / 1000)
    t3_density = t3_hits / (word_count / 1000)
    
    # — 偏离检测 —
    deviations = []
    for label, pattern, severity in [
        ('D1 主角光环化', D1_PROTAGONIST_ARMOR, 5),
        ('D2 通用修仙模板', D2_GENERIC_TEMPLATE, 5),
        ('D3 科技手段退化', D3_TECH_DEGRADE, 5),
        ('D4 敌人不合理弱化', D4_ENEMY_NERF, 5),
        ('D5 说教化', D5_OVER_THEMING, 1),
        ('D6 术语残留(科技手段写修真者)', D6_TERM_RESIDUE, 5),
    ]:
        hits = pattern.findall(text)
        if hits:
            deviations.append({
                'type': label,
                'count': len(hits),
                'severity': severity,
                'samples': hits[:3]
            })
    
    # — 主题评分 —
    # T1期望密度: 3-10/千字 (太低=科技缺失, 太高=过度量化)
    if t1_density < 1:
        t1_score = 20
        t1_flag = "⚠ 外物证道信号严重不足"
    elif t1_density < 3:
        t1_score = 50
        t1_flag = "⚠ 外物证道信号偏低"
    elif t1_density <= 10:
        t1_score = 85
        t1_flag = "✓ 外物证道信号正常"
    else:
        t1_score = 65
        t1_flag = "⚠ 量化信号过密，注意节奏"
    
    if t2_density < 2:
        t2_score = 30
        t2_flag = "⚠ 文明碰撞信号不足"
    elif t2_density <= 12:
        t2_score = 85
        t2_flag = "✓ 文明碰撞信号正常"
    else:
        t2_score = 70
        t2_flag = "⚠ 文明碰撞过密"
    
    if t3_density < 1:
        t3_score = 20
        t3_flag = "⚠ 认知差信号严重不足"
    elif t3_density < 2:
        t3_score = 50
        t3_flag = "⚠ 认知差信号偏低"
    elif t3_density <= 8:
        t3_score = 85
        t3_flag = "✓ 认知差信号正常"
    else:
        t3_score = 65
        t3_flag = "⚠ 认知差信号过密"
    
    theme_score = (t1_score + t2_score + t3_score) / 3
    
    # — 偏离扣分 —
    deviation_penalty = sum(d['count'] * d['severity'] for d in deviations)
    final_score = max(0, theme_score - deviation_penalty)
    
    # — 输出 —
    print(f"\n=== 主题检查 · 第 {chapter_num or file_path} 章 ===")
    print(f"字数: {words}")
    print(f"\n--- 信号密度 ---")
    print(f"T1 外物证道: {t1_density:.1f}/千字 ({t1_hits}次) → {t1_score}/100 {t1_flag}")
    print(f"T2 文明碰撞: {t2_density:.1f}/千字 ({t2_hits}次) → {t2_score}/100 {t2_flag}")
    print(f"T3 认知差:   {t3_density:.1f}/千字 ({t3_hits}次) → {t3_score}/100 {t3_flag}")
    print(f"主题均分: {theme_score:.0f}/100")
    
    if deviations:
        print(f"\n--- 偏离检测 ({len(deviations)}类, 扣{deviation_penalty}分) ---")
        for d in deviations:
            print(f"  [{d['type']}] ×{d['count']} (扣{d['count']*d['severity']}分)")
            for s in d['samples']:
                print(f"    → ...{str(s)[:40]}...")
    
    # — 门禁判定 —
    if final_score < 60:
        gate = "FAIL ⛔ 主题严重偏离，阻塞发布"
    elif final_score < 85:
        gate = "CONDITIONAL ⚠ 需改进后发布"
    else:
        gate = "PASS ✓ 主题一致性通过"
    
    print(f"\n总分: {final_score:.0f}/100 | {gate}")
    
    return {
        't1_density': t1_density, 't2_density': t2_density, 't3_density': t3_density,
        'theme_score': theme_score, 'deviation_penalty': deviation_penalty,
        'final_score': final_score, 'deviations': deviations
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='主题一致性检查')
    parser.add_argument('--chapter', type=int, help='章节号')
    parser.add_argument('--file', type=str, help='章节文件路径')
    args = parser.parse_args()
    check_theme(args.chapter, args.file)
