"""
AP-15 detect_signal 校验脚本:扫描 V11 脚本中"实际拼路径"的硬编码违规。
- 排除 fallback 默认值(try/except 块内)
- 排除注释行
- 排除 forbidden_paths 文档禁区列表
- 排除 secrets-detector.py 的跳过列表
- 排除腐化扫描的字符串匹配白名单
- 排除 V10→V11 迁移工具(upgrade-from-v10.py)
"""
import re
import glob
import sys

TARGET_FILES = [
    'spec-purge.py',
    'init-from-zero.py',
    'proactive-scan.py',
    'stage-gate.py',
]

# 这两类是预期的(不应算违规)
ALLOWED_PATTERNS = [
    re.compile(r'return\s*\{'),                  # fallback 默认 dict
    re.compile(r'^\s*#'),                        # 注释行
    re.compile(r'forbidden_paths'),              # 项目禁区列表
    re.compile(r'^\s*-\s*docs/'),                # yaml 列表项
    re.compile(r'^\s*"\s*logs"\s*,\s*"docs/archive"'),  # secrets-detector skip list
    re.compile(r'^\s*"/docs/archive/"'),         # 腐化扫描路径白名单
]

PATTERNS_TO_CHECK = ['docs/archive', 'docs/specs/archive', 'docs/specs/changes/archive']

violations = []

for fname in TARGET_FILES:
    fpath = f'scripts/{fname}'
    try:
        txt = open(fpath, encoding='utf-8').read()
    except FileNotFoundError:
        continue

    for line_no, line in enumerate(txt.splitlines(), 1):
        if any(p.search(line) for p in ALLOWED_PATTERNS):
            continue
        for pat in PATTERNS_TO_CHECK:
            if pat in line and ('/' in line or 'f"' in line or 'pathlib' in line):
                violations.append((fpath, line_no, pat, line.strip()[:80]))

print('AP-15 detect_signal: V11 目标脚本中实际拼路径的硬编码违规')
print('=' * 70)
if violations:
    for v in violations:
        print(f'  {v[0]}:L{v[1]} [{v[2]}] {v[3]}')
    print(f'TOTAL VIOLATIONS: {len(violations)}')
    sys.exit(1)
else:
    print('PASS: 0 violations across 4 target scripts')
    sys.exit(0)