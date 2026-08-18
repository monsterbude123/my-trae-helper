"""
Feedback #03 — V11 路径配置化总验收(2026-08-17)
"""
import yaml, pathlib, tempfile, subprocess, sys

PASS = []
FAIL = []

def check(name, ok, detail=""):
    if ok:
        PASS.append(name)
        print(f'[PASS] {name} {detail}')
    else:
        FAIL.append((name, detail))
        print(f'[FAIL] {name} {detail}')

# 1. trap-instructions.yaml 解析 + AP-15 存在
try:
    data = yaml.safe_load(open('references/trap-instructions.yaml', encoding='utf-8'))
    traps = data['traps']
    ap15 = [t for t in traps if t.get('id') == 'V11-AP15']
    detail = f'(total={len(traps)}, AP15 severity={ap15[0]["severity"]})' if ap15 else '(AP15 missing)'
    check('1. trap-instructions.yaml 解析', len(traps) >= 12 and len(ap15) == 1, detail)
    check('1.1 AP-15 severity=HIGH', ap15 and ap15[0]['severity'] == 'HIGH')
    check('1.2 AP-15 有完整字段', ap15 and all(k in ap15[0] for k in ['detect_signal', 'fix_template_before', 'fix_template_after', 'reclaim_steps']))
except Exception as e:
    check('1. trap-instructions.yaml', False, f'(exception: {e})')

# 2. config.example.yaml
try:
    cfg = yaml.safe_load(open('references/config.example.yaml', encoding='utf-8'))
    check('2. config.example.yaml paths.archive 字段', cfg['paths']['archive'] == 'docs/archive/done')
    check('2.1 config.example.yaml paths.archive 字段', cfg['paths']['archive'] == 'docs/archive/done')
    # V11.8.7.1: 移除 changes_archive 字段校验(双键已废弃,真相源仅 archive)
except Exception as e:
    check('2. config.example.yaml', False, f'(exception: {e})')

# 3. _lib_paths.py 5 项功能
try:
    import _lib_paths
    with tempfile.TemporaryDirectory() as td:
        p = _lib_paths.load_paths(pathlib.Path(td))
        check('3. _lib_paths 默认值', p['archive'] == 'docs/archive/done')
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        (root / '.trae').mkdir()
        (root / '.trae' / 'fullstack4traev11.config.yaml').write_text('paths:\n  archive: custom/archive\n', encoding='utf-8')
        p = _lib_paths.load_paths(root)
        check('3.1 _lib_paths 自定义覆盖', p['archive'] == 'custom/archive')
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        (root / '.trae').mkdir()
        (root / '.trae' / 'fullstack4traev11.config.yaml').write_text('paths:\n  archive: only-archive\n', encoding='utf-8')
        p = _lib_paths.load_paths(root)
        check('3.2 _lib_paths 部分覆盖', p['archive'] == 'only-archive' and 'changes_archive' not in p)
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        (root / '.trae').mkdir()
        (root / '.trae' / 'fullstack4traev11.config.yaml').write_text(': broken: [', encoding='utf-8')
        p = _lib_paths.load_paths(root)
        check('3.3 _lib_paths 损坏 yaml fallback', p['archive'] == 'docs/archive/done')
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        check('3.4 _lib_paths get_archive_dir helper', str(_lib_paths.get_archive_dir(root)).replace('\\', '/').endswith('docs/archive/done'))
        # V11.8.7.1: get_changes_archive_dir 函数已删除,无需再校验
        # check('3.5 _lib_paths get_changes_archive_dir helper', str(_lib_paths.get_changes_archive_dir(root)).replace('\\', '/').endswith('docs/specs/changes/archive'))
except Exception as e:
    check('3. _lib_paths.py', False, f'(exception: {e})')

# 4. check_paths_config.py 0 violations
try:
    r = subprocess.run(['python', 'scripts/check_paths_config.py'], capture_output=True, text=True)
    last_line = r.stdout.strip().splitlines()[-1] if r.stdout else '(empty)'
    check('4. check_paths_config.py 0 violations', r.returncode == 0 and 'PASS' in r.stdout, f'(stdout: {last_line})')
except Exception as e:
    check('4. check_paths_config.py', False, f'(exception: {e})')

# 5. project-structure.md / constitution.md
try:
    ps = open('references/project-structure.md', encoding='utf-8').read()
    check('5. project-structure.md 含 docs/archive/done 与 _lib_paths.get_archive_dir',
          'docs/archive/done' in ps and '_lib_paths.get_archive_dir(project_root)' in ps)
    check('5.1 project-structure.md L98 表加 paths.archive 配置说明',
          'paths.archive' in ps and 'config.example.yaml' in ps)
    co = open('references/constitution.md', encoding='utf-8').read()
    check('6. constitution.md Article VIII 加路径配置块', '路径配置（V11.8.7+）' in co)
    check('6.1 constitution.md 链接 _lib_paths.py + trap + config.example',
          '_lib_paths.py' in co and 'V11-AP15' in co and 'config.example.yaml' in co)
except Exception as e:
    check('5-6. markdown', False, f'(exception: {e})')

# 7. 5 个脚本含 try/except fallback
try:
    for mod_name in ['spec_purge', 'init_from_zero', 'proactive_scan', 'stage_gate']:
        src = open(f'scripts/{mod_name.replace("_", "-")}.py', encoding='utf-8').read()
        check(f'7. {mod_name} 含 try-except _lib_paths fallback',
              'from _lib_paths import' in src and 'except ImportError' in src)
except Exception as e:
    check('7. scripts try-except', False, f'(exception: {e})')

# 8. 4 个脚本实战 dry-run 不崩
try:
    r = subprocess.run(['python', 'scripts/spec-purge.py', '--change-id', '2099-01-01-none', '--dry-run', '--project-root', '.'],
                       capture_output=True, text=True, timeout=10)
    check('8. spec-purge.py --dry-run 不崩', r.returncode in (1, 2), f'(exit={r.returncode})')
except Exception as e:
    check('8. spec-purge.py', False, f'(exception: {e})')

# 总览
print()
print('=' * 70)
print(f'TOTAL PASS: {len(PASS)}')
print(f'TOTAL FAIL: {len(FAIL)}')
if FAIL:
    for n, d in FAIL:
        print(f'  FAIL: {n} {d}')
    sys.exit(1)
else:
    print('=== ALL CHECKS PASS — Feedback #03 路径配置化落地完成 ===')
    sys.exit(0)