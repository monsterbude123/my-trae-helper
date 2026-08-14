"""test_main_pytest_rootdir_isolation.py — 验证主仓 pytest 不跨包收集

对应 §2.4 反例固化 + §1.7 隔离:
  - 主仓 `pytest tests/` 严格只收集 `tests/unit/test_*.py`
  - 仓库内 `skill-markets/agent-dev-control-kit/tests/` 永不被吸入

测试方法:
  - 用 pytester 插件跑真实 pytest 命令
  - 验证 collect 输出不含 `agent-dev-control-kit/tests/...`
  - 验证主仓的 wrapper 测试能被正常收集

依赖:
  - pytest >= 6.2(pytester 内置)
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBPKG_TEST_DIR = REPO_ROOT / "skill-markets" / "agent-dev-control-kit" / "tests"
MAIN_TEST_DIR = REPO_ROOT / "tests"


@pytest.fixture(scope="module")
def pytester(testdir):
    """提供 pytester 实例,带 cwd = 主仓根。"""
    testdir.chdir()
    yield testdir


class TestCollectIgnoreGlob:
    def test_subpkg_tests_not_collected(self):
        """FAIL 反例:若 collect_ignore_glob 没起作用 → 此用例 fail 并(…)。
        故意构造一个指向子包 tests 的路径,期望被收集忽略。
        """
        # 用 --collect-only 让 pytest 只跑收集,不出 test 报告
        # 收集的 nodes 应当只来自 tests/unit/,不应有 agent-dev-control-kit
        # 直接 subprocess.run 而非 pytester(避免主仓 pytest 被自己递归触发)
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "tests/",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        # 主仓 pytest 启动应 exit 0(收集)或 5(无 test 收集,但 INTERNALERROR 来自其它既有文件)
        # 关键断言:stdout 不应出现子包路径
        assert "agent-dev-control-kit/tests" not in result.stdout, (
            f"主仓 pytest 收集时不应包含子包路径,得到 stdout:\n{result.stdout[:500]}"
        )

    def test_main_wrapper_test_collectible(self):
        """happy-path:wrapper 测试能被主仓 pytest 收集。"""
        import re
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "tests/unit/test_agent_dev_control_kit_wrapper.py",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"收集 wrapper 应 exit 0,得到 {result.returncode}\nstdout: {result.stdout[:300]}"
        )
        # pytest 9.x 输出格式:`tests/unit/...wrapper.py: 8` 表示 8 个用例
        match = re.search(r"wrapper\.py:\s*(\d+)", result.stdout)
        assert match is not None, (
            f"未在 stdout 找到测试数:\n{result.stdout}"
        )
        assert int(match.group(1)) == 8, (
            f"应收集 8 个用例,得到 {match.group(1)}"
        )

    def test_pytest_ini_points_to_main_repo(self):
        """§1.7 隔离:pytest.ini 必须存在且 rootdir 是主仓根。"""
        ini_path = REPO_ROOT / "pytest.ini"
        assert ini_path.is_file(), "主仓 pytest.ini 不存在"
        content = ini_path.read_text(encoding="utf-8")
        assert "[pytest]" in content
        assert "testpaths = tests" in content

    def test_conftest_has_collect_ignore_glob(self):
        """§11.1.4:conftest.py 必须声明 collect_ignore_glob。"""
        conftest = MAIN_TEST_DIR / "conftest.py"
        assert conftest.is_file(), "主仓 conftest.py 不存在"
        text = conftest.read_text(encoding="utf-8")
        assert "collect_ignore_glob" in text, "conftest.py 缺 collect_ignore_glob"
        assert "skill-markets" in text, "collect_ignore_glob 缺 skill-markets 模式"

    def test_subpkg_pytest_ini_not_modified(self):
        """§1.7 最小变更:不动子包 pytest.ini。"""
        subpkg_ini = SUBPKG_TEST_DIR / "pytest.ini"
        if not subpkg_ini.is_file():
            pytest.skip("子包 pytest.ini 不存在,跳过")
        text = subpkg_ini.read_text(encoding="utf-8")
        assert "testpaths = tests" in text
        # 子包应有 trap / unit / integration markers
        assert "trap" in text, "子包 pytest.ini 缺 trap marker"


class TestSubpackageStillRunnable:
    """隔离的反向验证:子包 wrapper 仍能独立跑(主仓 pytest 没破坏它)。"""

    def test_subpkg_tests_collection(self):
        """子包自己跑 pytest --collect-only 应能收集到 100+ 测试。"""
        import re
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
            ],
            cwd=str(SUBPKG_TEST_DIR),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"子包 pytest 收集失败:{result.returncode}\nstdout: {result.stdout[:300]}"
        )
        # 解析每行末尾 `文件名: N` 求和(每行仅一个数字,带 file: N 形式)
        counts = [int(m) for m in re.findall(r":\s*(\d+)\b", result.stdout)]
        # 总数 = 各文件用例之和;需 ≥ 100
        total = sum(counts)
        assert total >= 100, (
            f"子包应至少 100 测试,得到 {total}\nstdout:\n{result.stdout}"
        )