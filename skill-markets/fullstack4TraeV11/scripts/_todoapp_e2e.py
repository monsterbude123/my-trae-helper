"""
todoApp E2E 测试:验证 V11 5 个脚本(_lib_paths / spec-purge / proactive-scan / stage-gate / check_paths_config)
在真实路径下能跑通。核心目的:暴露 V11 路径配置改造后是否有 bug。
"""
import tempfile, pathlib, subprocess, os, sys, shutil

SCRIPTS = pathlib.Path('D:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/scripts')

def banner(name):
    print()
    print('=' * 70)
    print(f'  {name}')
    print('=' * 70)

# 1) 创建临时项目
tmp = pathlib.Path(tempfile.mkdtemp(prefix='v11_todoapp_'))
print(f'PROJECT_ROOT: {tmp}')

# 2) 手工建最小 V11 项目骨架
change_dir = tmp / 'docs' / 'specs' / 'changes' / '2026-08-17-todoapp'
change_dir.mkdir(parents=True)
(change_dir / 'spec.md').write_text('# todoApp spec\n- CRUD todo\n- AC: add/list/delete\n', encoding='utf-8')
(change_dir / 'plan.md').write_text('# todoApp plan\n- Node + Express\n', encoding='utf-8')
(change_dir / 'review-report.md').write_text('# review PASS\n', encoding='utf-8')
today = '2026-08-17'
(change_dir / ('rot-scan-' + today + '.md')).write_text('# rot-scan PASS\n', encoding='utf-8')
contracts = change_dir / 'contracts'
contracts.mkdir()
(contracts / 'domain-models.md').write_text('# Todo {id, title, done}\n', encoding='utf-8')
(contracts / 'api-contracts.md').write_text('# POST /todos\n', encoding='utf-8')

# 同时建一个占位 change 用于校验
change2 = tmp / 'docs' / 'specs' / 'changes' / '2026-08-16-stub'
change2.mkdir(parents=True)
(change2 / 'spec.md').write_text('# stub\n', encoding='utf-8')
(change2 / 'plan.md').write_text('# stub plan\n', encoding='utf-8')

# 3) 跑 spec-purge.py DRY-RUN
os.chdir(str(SCRIPTS))
banner('3. spec-purge.py --dry-run(应输出 archive 路径)')
r = subprocess.run(['python', 'spec-purge.py', '--change-id', '2026-08-17-todoapp', '--dry-run', '--project-root', str(tmp)],
                   capture_output=True, text=True)
print(r.stdout)
print('stderr:', r.stderr[:300] if r.stderr else '(empty)')
print('exit:', r.returncode)

# 4) 跑 proactive-scan.py archive scan
banner('4. proactive-scan.py archive 段')
r2 = subprocess.run(['python', 'proactive-scan.py', '--project-root', str(tmp)], capture_output=True, text=True)
for line in r2.stdout.splitlines():
    if 'archive' in line.lower():
        print(line)
print('exit:', r2.returncode)

# 5) 跑 stage-gate.py --reset-to
banner('5. stage-gate.py --reset-to 0/plan')
r3 = subprocess.run(['python', 'stage-gate.py', '--reset-to', '0/plan', '--change-id', '2026-08-17-todoapp', '--project-root', str(tmp)],
                   capture_output=True, text=True)
print(r3.stdout[:1500])
print('stderr:', r3.stderr[:300] if r3.stderr else '(empty)')
print('exit:', r3.returncode)

# 6) check_paths_config.py(我自己写的 detect_signal 工具)
banner('6. check_paths_config.py(AP-15 detect_signal)')
r4 = subprocess.run(['python', 'check_paths_config.py'], capture_output=True, text=True)
print(r4.stdout)
print('exit:', r4.returncode)

# 7) 真归档(去掉 --dry-run)
banner('7. spec-purge.py 真归档')
r5 = subprocess.run(['python', 'spec-purge.py', '--change-id', '2026-08-17-todoapp', '--project-root', str(tmp)],
                   capture_output=True, text=True)
print(r5.stdout)
print('stderr:', r5.stderr[:500] if r5.stderr else '(empty)')
print('exit:', r5.returncode)

# 8) 验证归档真的写到 docs/archive/done/2026-08-17-todoapp/
archive_done = tmp / 'docs' / 'archive' / 'done' / '2026-08-17-todoapp'
banner('8. archive 落地验证')
print('archive path exists:', archive_done.exists())
if archive_done.exists():
    print('archive contents:')
    for f in sorted(archive_done.rglob('*')):
        if f.is_file():
            print('  ', str(f.relative_to(archive_done)))
else:
    print('  ❌ FAIL: archive 目录不存在!')

# 9) 跑 _lib_paths 真值检测
banner('9. _lib_paths 真值')
import _lib_paths
p = _lib_paths.load_paths(tmp)
print('load_paths:', p)
print('get_archive_dir:', _lib_paths.get_archive_dir(tmp))
# V11.8.7.1: get_changes_archive_dir 已删除,不再打印

# 10) 验证孤立 change(模拟重名检查)
banner('10. init-from-zero.py 模拟校验')
# 在 tmp 配 .trae/config.yaml 让 archive 走自定义路径
trae = tmp / '.trae'
trae.mkdir()
(trae / 'fullstack4traev11.config.yaml').write_text(
    'paths:\n  archive: custom-archive/done\n',
    encoding='utf-8'
)
p2 = _lib_paths.load_paths(tmp)
print('config applied:', p2)
print('get_archive_dir:', _lib_paths.get_archive_dir(tmp))
# V11.8.7.1: get_changes_archive_dir 已删除,不再打印
custom = tmp / 'custom-archive' / 'done' / '2026-08-17-todoapp'
print('custom archive exists:', custom.exists(), '(应当 True,因为我们 spec-purge 时没用 config)')
# 注:spec-purge 已经跑过,归档走的是 _lib_paths 默认 docs/archive/done(因为加载 .trae 之前已跑)
# 重新跑看新 config 是否生效
r6 = subprocess.run(['python', 'spec-purge.py', '--change-id', '2026-08-16-stub', '--project-root', str(tmp)],
                   capture_output=True, text=True)
print('--- spec-purge.py with custom config ---')
print(r6.stdout)
print('stderr:', r6.stderr[:500] if r6.stderr else '(empty)')
print('exit:', r6.returncode)
custom_stub = tmp / 'custom-archive' / 'done' / '2026-08-16-stub'
print('custom stub archive exists:', custom_stub.exists(), '(应当 True)')

# 11) 最终总结
banner('11. 总结')
archive_paths = []
if (tmp / 'docs' / 'archive' / 'done').exists():
    archive_paths.append(str(tmp / 'docs' / 'archive' / 'done'))
if (tmp / 'custom-archive' / 'done').exists():
    archive_paths.append(str(tmp / 'custom-archive' / 'done'))
print('all archive paths written:')
for ap in archive_paths:
    print(' ', ap)

# 清理
shutil.rmtree(tmp, ignore_errors=True)
print()
print('TEMP CLEANED:', tmp)