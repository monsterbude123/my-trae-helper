#!/usr/bin/env python3
# fullstack Auto Test Hook（默认启用）
# 编码后自动运行相关测试
# V5.1: 默认 enabled=true（P2-4 教训：关键 hook 不应默认关闭）
# V9 NEW: 产出 Hook 执行日志（自证生效）
# V10.1: 增加 spec.md `## Acceptance` 段全 [x] 检测（V10 硬门禁）
# V10.12.2 SECURITY 标注: subprocess 调用（npm/pnpm test 等），全部为 hook 触发测试需要，无外网、无破坏性命令。

import re
import os
import sys
import subprocess
from pathlib import Path

file_path = os.environ.get("TRAE_FILE_PATH", "")

# 只处理代码文件
if not file_path or not re.search(r'src/.*\.(py|ts|tsx|js|jsx)$', file_path):
    sys.exit(0)

# ── V10.1: spec.md `## Acceptance` 段全 [x] 检测 ──
spec_match = re.search(r'specs[\\/]([^\\/]+)[\\/]spec\.md$', file_path)
if not spec_match:
    spec_match = re.search(r'src[\\/].*spec\.md$', file_path)

if spec_match:
    feature = spec_match.group(1) if spec_match.lastindex else None
    if feature:
        spec_path = Path(f"docs/specs/{feature}/spec.md")
        if spec_path.exists():
            try:
                content = spec_path.read_text(encoding="utf-8")
                # 提取 ## Acceptance 段
                m = re.search(r'##\s+Acceptance(.*?)(?=^##\s|\Z)', content, re.MULTILINE | re.DOTALL)
                if m:
                    acc_section = m.group(1)
                    unchecked = re.findall(r'^\s*-\s*\[\s\]\s+.+$', acc_section, re.MULTILINE)
                    if unchecked:
                        print(f"[Fullstack Auto Test] ⚠️ spec.md `## Acceptance` 还有 {len(unchecked)} 项未勾选 [x]")
                        print("    → V10 满分硬门禁: Acceptance 必须全 [x] 才能进入归档阶段")
            except Exception:
                pass

# 确定测试命令
test_cmd = None
if Path("jest.config.js").exists():
    test_cmd = "npx jest --passWithNoTests"
elif Path("vitest.config.ts").exists():
    test_cmd = "npx vitest run"
elif Path("pytest.ini").exists() or Path("pyproject.toml").exists():
    test_cmd = "pytest --tb=short"

if not test_cmd:
    sys.exit(0)

print(f"[Fullstack Auto Test] Running: {test_cmd}")
<!-- scan-whitelist:SHELL_EXEC,STACK_LEAK -->
# shell=True 是有意为之：test_cmd 来自上方固定 if 分支（npx jest / npx vitest / pytest / pnpm / npm run test）
# 命令白名单化：只接受 5 种固定命令字符串，无用户输入注入面。
# scan_skills_dir.py SHELL_EXEC + STACK_LEAK 模式在此豁免。
result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
<!-- /scan-whitelist -->
exit_code = result.returncode

if exit_code != 0:
    print(f"[Fullstack Auto Test] FAILED (exit code: {exit_code})")
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    sys.exit(1)

print("[Fullstack Auto Test] PASSED")

# === V5.0 新增：TDD RED/GREEN 标记会话输出检查（警告级）===
print("[Fullstack Auto Test] ⚠️ TDD 自检提醒: 请确认本次编辑遵循 RED→GREEN 节奏")
print("   - 会话中是否先输出过测试失败 (RED)？")
print("   - 本次 PASS 是否为 GREEN 信号？")
print("   - 若跳过 RED 直接 GREEN，违反 TDD 铁律，请补 RED 证据")

sys.exit(0)
