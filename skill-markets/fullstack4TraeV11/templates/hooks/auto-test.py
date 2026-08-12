#!/usr/bin/env python3
"""V11 auto-test.py — PostToolUse Hook（蒸馏自 V10）

编码后自动运行相关测试 + spec.md Acceptance 段检测。

V11 简化:
  - 不再绑定 v10_simplified（V11 改用 state-card-validator.py）
  - 支持 6 种测试命令（jest / vitest / pytest / cargo / go / pnpm）
  - 增加 Article XVII secret 检测（commit 前必扫）

SECURITY 标注: subprocess 调用，全部为 hook 触发测试需要。无外网、无破坏性命令。
<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->
"""

import os
import re
import sys
import subprocess
from pathlib import Path


file_path = os.environ.get("TRAE_FILE_PATH", "")

# 只处理代码文件
if not file_path or not re.search(r'src/.*\.(py|ts|tsx|js|jsx|rs|go)$', file_path):
    sys.exit(0)

# ── Step 1: V11 spec.md Acceptance 段全 [x] 检测 ──
spec_match = re.search(r'specs[\\/]([^\\/]+)[\\/]spec\.md$', file_path)
if spec_match:
    feature = spec_match.group(1)
    spec_path = Path(f"docs/specs/changes/{feature}/spec.md")
    if spec_path.exists():
        try:
            content = spec_path.read_text(encoding="utf-8")
            m = re.search(r'##\s+Acceptance(.*?)(?=^##\s|\Z)', content, re.MULTILINE | re.DOTALL)
            if m:
                acc_section = m.group(1)
                unchecked = re.findall(r'^\s*-\s*\[\s\]\s+.+$', acc_section, re.MULTILINE)
                if unchecked:
                    print(f"[V11 Auto Test] ⚠️ spec.md `## Acceptance` 还有 {len(unchecked)} 项未勾选 [x]")
                    print("    → V11 Article I: Acceptance 必须全 [x] 才能进入归档阶段")
        except Exception:
            pass

# ── Step 2: Article XVII secret 检测（防 secret 误写）──
try:
    content = Path(file_path).read_text(encoding="utf-8")
    # 检测疑似 secret（password / token / api_key 字面量）
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']{6,}["\']',
        r'api[_-]?key\s*=\s*["\'][^"\']{6,}["\']',
        r'secret\s*=\s*["\'][^"\']{6,}["\']',
    ]
    for pat in secret_patterns:
        if re.search(pat, content, re.IGNORECASE):
            print(f"[V11 Auto Test] 🚨 Article XVII: 检测到疑似 secret 字面量 in {file_path}")
            print(f"    → 立即使用环境变量 + 通知用户改密码")
            sys.exit(1)
except Exception:
    pass

# ── Step 3: 确定测试命令 ──
test_cmd = None
if Path("jest.config.js").exists():
    test_cmd = "npx jest --passWithNoTests"
elif Path("vitest.config.ts").exists():
    test_cmd = "npx vitest run --reporter=verbose"
elif Path("pytest.ini").exists() or Path("pyproject.toml").exists():
    test_cmd = "pytest --tb=short -q"
elif Path("Cargo.toml").exists():
    test_cmd = "cargo test --quiet"
elif Path("go.mod").exists():
    test_cmd = "go test ./..."

if not test_cmd:
    sys.exit(0)

print(f"[V11 Auto Test] Running: {test_cmd}")
result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=120)
exit_code = result.returncode

if exit_code != 0:
    print(f"[V11 Auto Test] ❌ FAILED (exit code: {exit_code})")
    print(result.stdout[-2000:])  # 仅最后 2000 字符
    if result.stderr:
        print(result.stderr[-1000:])
else:
    print(f"[V11 Auto Test] ✅ PASS")

sys.exit(exit_code)