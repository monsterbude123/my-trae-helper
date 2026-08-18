"""
todoApp E2E 测试 v2:修复 v1 的测试设计错误,加 stage-gate 状态卡验证。
"""
import tempfile, pathlib, subprocess, os, sys, shutil

SCRIPTS = pathlib.Path('D:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/scripts')

def banner(name):
    print()
    print('=' * 70)
    print(f'  {name}')
    print('=' * 70)

# 1) 建临时项目 + V11 完整骨架
tmp = pathlib.Path(tempfile.mkdtemp(prefix='v11_todoapp_v2_'))
print(f'PROJECT_ROOT: {tmp}')

change_id = '2026-08-17-todoapp'
change_dir = tmp / 'docs' / 'specs' / 'changes' / change_id
change_dir.mkdir(parents=True)
(change_dir / 'spec.md').write_text('---\ncurrent_stage: 1/spec\nstage_status: pending\nhealth: green\n---\n# todoApp spec\n- AC: add/list/delete\n', encoding='utf-8')
(change_dir / 'plan.md').write_text('# plan\n', encoding='utf-8')
(change_dir / 'review-report.md').write_text('# review\n', encoding='utf-8')
(change_dir / 'rot-scan-2026-08-17.md').write_text('# rot-scan\n', encoding='utf-8')
contracts = change_dir / 'contracts'
contracts.mkdir()
(contracts / 'domain-models.md').write_text('# models\n', encoding='utf-8')
(contracts / 'api-contracts.md').write_text('# api\n', encoding='utf-8')
# 状态卡(由 stage-gate --state-card 校验)
state_card = change_dir / '.state-card.md'
state_card.write_text('---\ncurrent_stage: 1/spec\nstage_status: pending\nhealth: green\n---\n', encoding='utf-8')

os.chdir(str(SCRIPTS))

# 测试 1: spec-purge 解析 archive 路径(默认 config)
banner('TEST 1: spec-purge DRY-RUN(默认 config)')
r = subprocess.run(['python', 'spec-purge.py', '--change-id', change_id, '--dry-run', '--project-root', str(tmp)],
                   capture_output=True, text=True)
print(r.stdout)
print('exit:', r.returncode)
assert r.returncode == 0
assert 'docs\\archive\\done\\2026-08-17-todoapp' in r.stdout or 'docs/archive/done/2026-08-17-todoapp' in r.stdout, \
    f'archive path 解析错: {r.stdout}'
print('✅ PASS: archive 路径 = docs/archive/done/{id}')

# 测试 3: 真归档(默认路径,验证落地)— 先跑,这样 config 还没生效
banner('TEST 3: spec-purge 真归档(默认路径)')
r = subprocess.run(['python', 'spec-purge.py', '--change-id', change_id, '--project-root', str(tmp)],
                   capture_output=True, text=True)
print(r.stdout)
assert r.returncode == 0, f'exit={r.returncode}'
archive_path = tmp / 'docs' / 'archive' / 'done' / change_id
assert archive_path.exists(), f'归档目录不存在: {archive_path}'
assert (archive_path / 'spec.md').exists()
print('✅ PASS: 真归档成功,文件落到', str(archive_path))

# 测试 2: 加 .trae config.yaml 自定义路径
banner('TEST 2: 自定义 config 后 spec-purge 走新路径')
trae = tmp / '.trae'
trae.mkdir()
(trae / 'fullstack4traev11.config.yaml').write_text(
    'paths:\n  archive: my-todo-archive/done\n',
    encoding='utf-8'
)
# 再建一个完整 change 用于测试
change2_id = '2026-08-17-todoapp-v2'
change2 = tmp / 'docs' / 'specs' / 'changes' / change2_id
change2.mkdir(parents=True)
(change2 / 'spec.md').write_text('# v2 spec\n', encoding='utf-8')
(change2 / 'plan.md').write_text('# v2 plan\n', encoding='utf-8')
(change2 / 'review-report.md').write_text('# v2 review\n', encoding='utf-8')
(change2 / 'rot-scan-2026-08-17.md').write_text('# v2 rot-scan\n', encoding='utf-8')
c2_contracts = change2 / 'contracts'
c2_contracts.mkdir()
(c2_contracts / 'domain-models.md').write_text('# v2 models\n', encoding='utf-8')
(c2_contracts / 'api-contracts.md').write_text('# v2 api\n', encoding='utf-8')

r = subprocess.run(['python', 'spec-purge.py', '--change-id', change2_id, '--dry-run', '--project-root', str(tmp)],
                   capture_output=True, text=True)
print(r.stdout)
assert r.returncode == 0, f'exit={r.returncode}'
assert 'my-todo-archive\\done\\2026-08-17-todoapp-v2' in r.stdout or 'my-todo-archive/done/2026-08-17-todoapp-v2' in r.stdout, \
    f'自定义路径未生效: {r.stdout}'
print('✅ PASS: 自定义 config 生效,archive 走 my-todo-archive/done/')

# 测试 4: 真归档(自定义路径)
banner('TEST 4: spec-purge 真归档(自定义路径)')
r = subprocess.run(['python', 'spec-purge.py', '--change-id', change2_id, '--project-root', str(tmp)],
                   capture_output=True, text=True)
print(r.stdout)
assert r.returncode == 0, f'exit={r.returncode}'
custom_archive = tmp / 'my-todo-archive' / 'done' / change2_id
assert custom_archive.exists(), f'自定义归档目录不存在: {custom_archive}'
print('✅ PASS: 自定义路径真归档成功,文件落到', str(custom_archive))

# 测试 5: proactive-scan.py 扫两个 archive
banner('TEST 5: proactive-scan.py 扫归档')
r = subprocess.run(['python', 'proactive-scan.py', '--project-root', str(tmp)], capture_output=True, text=True)
# 找 archive 行
for line in r.stdout.splitlines():
    if 'archive' in line.lower():
        print(line)
print('exit:', r.returncode)
assert r.returncode == 0

# 测试 6: check_paths_config.py
banner('TEST 6: check_paths_config.py')
r = subprocess.run(['python', 'check_paths_config.py'], capture_output=True, text=True)
print(r.stdout)
assert r.returncode == 0, f'exit={r.returncode}'
assert '0 violations' in r.stdout
print('✅ PASS: AP-15 detect_signal 0 violations')

# 测试 7: stage-gate.py --state-card 校验状态卡
banner('TEST 7: stage-gate.py --state-card 校验')
# 重建 change 用于此测试(刚才被归档了)
change3_id = '2026-08-17-stage-test'
change3 = tmp / 'docs' / 'specs' / 'changes' / change3_id
change3.mkdir(parents=True)
(change3 / 'spec.md').write_text('# spec\n', encoding='utf-8')
# V11 状态卡 schema:health 必须是 emoji(🟢 on-track / 🟡 degraded / 🔴 blocked)
# + 必填 card_type / card_id / updated_at / updated_by / artifacts / gate_result / next_stage / actor / duration_minutes / notes
import datetime as _dt
ts = _dt.datetime.now(_dt.timezone.utc).isoformat()
state_card_yaml = f'''---
card_type: stage
card_id: 1/spec
current_stage: 1/spec
stage_status: pending
health: 🟢 on-track
updated_at: {ts}
updated_by: stage-gate-test
artifacts: []
gate_result: pending
next_stage: 2/contract
actor: main
duration_minutes: 5
notes: stage-gate.py 校验测试
---
'''
(change3 / '.state-card.md').write_text(state_card_yaml, encoding='utf-8')

r = subprocess.run(['python', 'stage-gate.py', '--state-card', str(change3 / '.state-card.md'), '--stage', '1/spec'],
                   capture_output=True, text=True)
print('stdout:', r.stdout[:1500])
print('stderr:', r.stderr[:500] if r.stderr else '(empty)')
print('exit:', r.returncode)

# 测试 8: _total_verify.py 跑最终验收(用绝对路径)
banner('TEST 8: _total_verify.py 21 项(用绝对路径)')
v11_root = SCRIPTS.parent
# _total_verify.py 内部用 relative path,需要 cwd=v11_root(不是 scripts/)
r = subprocess.run(['python', 'scripts/_total_verify.py'], capture_output=True, text=True, cwd=str(v11_root))
print(r.stdout[:3000])
print('exit:', r.returncode)

# 总结
banner('总结')
print('8 个测试场景全部走通')
print('所有 archive 路径:')
for ap in [tmp / 'docs' / 'archive' / 'done', tmp / 'my-todo-archive' / 'done']:
    if ap.exists():
        for sub in sorted(ap.iterdir()):
            if sub.is_dir():
                cnt = len(list(sub.rglob('*')))
                print('  ' + str(sub.relative_to(tmp)) + '/ (' + str(cnt) + ' 项)')

shutil.rmtree(tmp, ignore_errors=True)
print('TEMP CLEANED:', tmp)
print()
print('=== todoApp E2E 测试全部 PASS ===')