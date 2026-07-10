"""
enumerate.py · 可能性枚举引擎

用法:
  python enumerate.py --chapter 82
  python enumerate.py --chapter 82 --count 5

核心算法: 四层约束过滤 + 三维评分(逻辑40%/惊喜35%/主题25%)
参考: references/enumeration_engine.md
"""
import argparse
import io
import os
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

def _extract_snapshot(text):
    """从章节文本提取关键状态快照"""
    snapshot = {
        'location': '',
        'characters': [],
        'tech_level': [],
        'threats': [],
        'goals': [],
    }
    # 位置
    loc_m = re.search(r'(?:地点|位置|所在)[：:]\s*(.+?)(?:\n|$)', text)
    if loc_m:
        snapshot['location'] = loc_m.group(1).strip()
    # 角色
    names = re.findall(r'(?:陆之一|小真|苏晚晴|陈砚秋|老猫|严峰|林岳|万象宗)', text)
    snapshot['characters'] = list(set(names))
    # 科技
    techs = re.findall(r'(?:潜蛟|灵纹|灵场|聚灵|灵压|灵子|BEC|超辐射)', text)
    snapshot['tech_level'] = list(set(techs))
    # 威胁
    threats = re.findall(r'(?:追[捕杀踪]|危险|危机|暴露|围[剿杀堵]|伏击)', text)
    snapshot['threats'] = list(set(threats))
    # 目标
    goals = re.findall(r'(?:目标|计划|打算|准备|决定|必须|需要)[^。]{5,30}', text)
    snapshot['goals'] = goals[-3:] if goals else []
    
    return snapshot

def enumerate_candidates(chapter_num, count=5):
    project_root = _find_project_root()
    chapter_file = _find_chapter(project_root, chapter_num)
    
    if not chapter_file or not os.path.exists(chapter_file):
        print(f"[ERROR] 章节文件未找到: chapter={chapter_num}")
        sys.exit(1)
    
    with open(chapter_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    snapshot = _extract_snapshot(text)
    
    print(f"\n[enumerate] 第 {chapter_num} 章 · 可能性枚举")
    print(f"[enumerate] 约束空间分析:")
    print(f"  位置: {snapshot['location'] or '(未检测)'}")
    print(f"  在场角色: {', '.join(snapshot['characters'][:6]) or '(未检测)'}")
    print(f"  科技树: {', '.join(snapshot['tech_level'][:6]) or '(未检测)'}")
    print(f"  威胁信号: {', '.join(snapshot['threats'][:6]) or '(无)'}")
    print(f"  近期目标: {'; '.join(snapshot['goals'][:3]) or '(未检测)'}")
    
    # 基于快照生成约束建议
    constraints = []
    if '追' in ' '.join(snapshot['threats']):
        constraints.append("⚠ 追踪威胁激活 → 候选必须包含隐藏/反追踪元素")
    if '陆之一' in snapshot['characters'] and not snapshot['tech_level']:
        constraints.append("⚠ 无科技信号 → 提醒: 三段式发明(经典→L场→量化)")
    if '暴露' in ' '.join(snapshot['threats']):
        constraints.append("⚠ 暴露风险 → 候选应优先解决暴露问题")
    
    print(f"\n[enumerate] 约束提示 ({len(constraints)}):")
    for c in constraints:
        print(f"  {c}")
    
    print(f"\n[enumerate] 下一步引擎建议:")
    candidates = [
        {"desc": "基于当前快照的延续事件", "logic": 7, "surprise": 4, "theme": 6},
        {"desc": "引入外部变量打破僵局", "logic": 5, "surprise": 8, "theme": 7},
        {"desc": "角色内在成长触发新能力", "logic": 6, "surprise": 6, "theme": 8},
    ]
    for i, c in enumerate(candidates[:count], 1):
        score = c['logic'] * 0.4 + c['surprise'] * 0.35 + c['theme'] * 0.25
        print(f"  候选{i}: {c['desc']} (总分{score:.1f})")
    
    print(f"\n[enumerate] 提示: 完整实现需要 schema 数据库。当前为模式匹配版。")
    return candidates

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='可能性枚举引擎')
    parser.add_argument('--chapter', type=int, required=True)
    parser.add_argument('--count', type=int, default=5)
    args = parser.parse_args()
    enumerate_candidates(args.chapter, args.count)
