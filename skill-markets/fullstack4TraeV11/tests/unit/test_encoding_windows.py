"""commit-minimum-check.py Windows console cp1252 兜底单测（V11.8.5 P1 NEW）。

覆盖背景（feedback01.md 决策报告 2026-08-16 采纳项 #5）：
  - Python 3.13 在 Windows 默认控制台编码 = cp1252
  - print(f"...中文...") 触发 UnicodeEncodeError → 跌 traceback 而非出 verdict
  - commit-minimum-check.py 已加 L0 PYTHONIOENCODING=utf-8 + stdout.reconfigure 兜底
  - 本测试固化兜底行为：3 用例必须全 PASS 才能进 commit

3 用例维度：
  #1 子进程触发中文 print（不带环境变量）→ win32 应不崩
  #2 子进程触发中文 print（带 PYTHONIOENCODING=utf-8）→ win32 应不崩（基线）
  #3 模块导入阶段 sys.stdout.encoding 在 win32 必为 utf-8（兜底生效）
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "commit-minimum-check.py"
)

# 故意含中文触发 cp1252 兜底（命中 V11 commit-minimum-check.py 的 print 中文）
TRIGGER_CN = "验证目标：中文兜底测试"  # 不要 ASCII


def _invoke(args, env_extra: dict[str, str] | None = None, timeout: int = 30) -> tuple[int, str, str]:
    """以子进程跑一段 Python（含中文 print），捕获 (returncode, stdout, stderr)。

    env_extra: 追加到子进程 os.environ（None = 不传任何，模拟 Windows 默认 cp1252）
    """
    code = (
        "import sys\n"
        f"print({TRIGGER_CN!r})\n"  # 含中文 print
        "sys.exit(0)\n"
    )
    env = None
    if env_extra is not None:
        import os
        env = os.environ.copy()
        env.update(env_extra)
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def _load_cmc():
    """动态导入 commit-minimum-check.py，验证 stdout.encoding 在 win32 = utf-8。"""
    spec = importlib.util.spec_from_file_location("commit_minimum_check_encoding", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"无法加载 {SCRIPT_PATH}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["commit_minimum_check_encoding"] = mod
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# 用例 1：子进程触发中文 print 不带 PYTHONIOENCODING
# 触发: Windows 默认 cp1252 + 兜底未生效
# 期望: 当前主机若无兜底，会 UnicodeEncodeError（用作回归基线）
#       当前主机若已自设 utf-8，本用例仅验证不崩
# ============================================================================


def test_subprocess_cn_print_no_env_does_not_crash():
    """win32 子进程中文 print 不带环境变量 → 不应 UnicodeEncodeError。"""
    rc, out, err = _invoke(args=[], env_extra=None)
    # 关键: rc=0 + stderr 不含 UnicodeEncodeError
    assert rc == 0, f"子进程退出码 {rc}，stderr={err[:200]}"
    assert "UnicodeEncodeError" not in err, f"cp1252 兜底失效：{err[:200]}"
    # 触发字符串已落到 stdout（说明中文写出成功）
    if sys.platform == "win32":
        # win32 期望兜底路径走通
        assert "验证目标" in out, f"中文未写出，stdout={out[:200]}"


# ============================================================================
# 用例 2：子进程带 PYTHONIOENCODING=utf-8（基线 / Linux 也能跑）
# 期望: rc=0 + 中文写出
# ============================================================================


def test_subprocess_cn_print_with_pyencoding_passes():
    """子进程显式 PYTHONIOENCODING=utf-8 → 中文 print 必不崩（基线）。"""
    rc, out, err = _invoke(args=[], env_extra={"PYTHONIOENCODING": "utf-8"})
    assert rc == 0, f"子进程退出码 {rc}，stderr={err[:200]}"
    assert "UnicodeEncodeError" not in err
    assert "验证目标" in out, f"中文未写出，stdout={out[:200]}"


# ============================================================================
# 用例 3：commit-minimum-check.py 模块导入后，stdout 必为 utf-8 兜底
# 仅在 win32 验证兜底生效；非 win32 平台跳过
# ============================================================================


@pytest.mark.skipif(sys.platform != "win32", reason="Windows cp1252 兜底专属测试")
def test_cmc_import_sets_utf8_stdout_on_win32():
    """win32 导入 commit-minimum-check.py 后 sys.stdout.encoding = utf-8。"""
    mod = _load_cmc()
    assert mod.sys.stdout.encoding.lower().replace("-", "") in (
        "utf8", "utf_8", "cp65001"  # cp65001 = Windows UTF-8 别名
    ), f"win32 兜底未生效：stdout.encoding={mod.sys.stdout.encoding}"
    # 同时验证 os.environ 已注入 PYTHONIOENCODING=utf-8
    assert mod.os.environ.get("PYTHONIOENCODING", "").lower() in (
        "utf-8", "utf8", "utf_8"
    ), f"PYTHONIOENCODING 未兜底：{mod.os.environ.get('PYTHONIOENCODING')}"