#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install-husky.test.py — install-husky.py 的单元测试（纯 unittest，不依赖 pytest）

运行：
    python install-husky.test.py
    python install-husky.test.py -v
"""

import os
import sys
import shutil
import tempfile
import unittest
import importlib.util
from pathlib import Path
from unittest import mock

# 加载兄弟模块（文件名带连字符，无法直接 import）
SCRIPT_DIR = Path(__file__).resolve(strict=False).parent
MOD_PATH = SCRIPT_DIR / "install-husky.py"
_spec = importlib.util.spec_from_file_location("install_husky", MOD_PATH)
install_husky = importlib.util.module_from_spec(_spec)  # type: ignore
assert _spec.loader is not None
_spec.loader.exec_module(install_husky)
# 注册到 sys.modules，使 mock.patch('install_husky.xxx') 能正常解析
sys.modules["install_husky"] = install_husky


class TestResolveTargetSafety(unittest.TestCase):
    """test_resolve_target_safety_no_symlink：校验 strict=False 不会丢 symlink 路径。"""

    def test_resolve_target_safety_no_symlink(self):
        """R-2 关键：resolve(strict=False) 对不存在的路径必须不抛异常。
        对存在的 symlink 路径会跟随链接（这是 Path.resolve 的语义），
        但对不存在的路径仍返回绝对路径而不抛 FileNotFoundError。
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # 场景 A：路径不存在，resolve(strict=False) 必须不抛
            nonexistent = tmp_path / "does-not-exist-yet"
            self.assertFalse(nonexistent.exists())
            resolved = install_husky.resolve_target_safety(str(nonexistent))
            self.assertTrue(resolved.is_absolute(),
                            f"resolve(strict=False) 必须返回绝对路径，得到 {resolved}")
            # R-2 校验：函数内做了路径安全检查（R-2 source guard）
            # 此处目标在 tmp 下，远离 skill 源，应正常通过
            self.assertNotIn("scripts", str(resolved).replace(str(tmp_path), "").strip(os.sep).split(os.sep)[1:])

            # 场景 B：路径存在，resolve(strict=False) 正常返回
            real_dir = tmp_path / "real"
            real_dir.mkdir()
            resolved2 = install_husky.resolve_target_safety(str(real_dir))
            self.assertEqual(str(resolved2), str(real_dir.resolve(strict=False)))

    def test_target_not_source_guard_skill_root(self):
        """目标指向 skill 根 → 应抛 ValueError。"""
        skill_root = str(install_husky.SKILL_ROOT)
        with self.assertRaises(ValueError) as ctx:
            install_husky.resolve_target_safety(skill_root)
        self.assertIn("R-2 violation", str(ctx.exception))

    def test_target_not_source_guard_inside_skill(self):
        """目标在 skill 目录内 → 应抛 ValueError。"""
        inside = str(install_husky.SKILL_ROOT / "scripts" / "evil")
        with self.assertRaises(ValueError) as ctx:
            install_husky.resolve_target_safety(inside)
        self.assertIn("R-2 violation", str(ctx.exception))


class TestDryRunDoesNotWrite(unittest.TestCase):
    """test_dry_run_does_not_write：dry-run 模式不能创建任何文件。"""

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = install_husky.install("nodejs", tmp, dry_run=True)
            self.assertEqual(rc, install_husky.EXIT_OK)
            husky = Path(tmp) / ".husky"
            self.assertFalse(husky.exists(),
                             f"dry-run 不应创建 .husky/ 目录，但发现 {husky}")
            self.assertFalse((husky / "pre-commit").exists())


class TestCopyPreCommitChmod(unittest.TestCase):
    """test_copy_pre_commit_chmod：mock os.chmod 验证调用。"""

    def test_copy_pre_commit_chmod(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with mock.patch("install_husky.os.chmod") as mchmod:
                rc = install_husky.install("nodejs", str(target), dry_run=False)
            self.assertEqual(rc, install_husky.EXIT_OK)
            husky = target / ".husky"
            self.assertTrue((husky / "pre-commit").is_file())
            self.assertTrue((husky / "pre-push").is_file())
            # chmod 应被调用至少一次
            self.assertGreaterEqual(mchmod.call_count, 1)
            # 验证 chmod 第二个参数是 0o755
            args, _ = mchmod.call_args
            self.assertEqual(args[1], 0o755)


class TestMissingStackScaffoldWarns(unittest.TestCase):
    """test_missing_stack_scaffold_warns：未知 stack 应 WARN 跳过，返回 0。"""

    def test_missing_stack_scaffold_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = install_husky.install("nonexistent-stack-xyz", tmp, dry_run=False)
            self.assertEqual(rc, install_husky.EXIT_OK, "WARN 跳过应返回 0")
            husky = Path(tmp) / ".husky"
            self.assertFalse(husky.exists())


class TestWindowsChmodFailureHandled(unittest.TestCase):
    """test_windows_chmod_failure_handled：mock OSError 必须不抛。"""

    def test_windows_chmod_failure_handled(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with mock.patch("install_husky.os.chmod",
                            side_effect=OSError("simulated Windows chmod failure")):
                # 不应抛异常
                rc = install_husky.install("nodejs", str(target), dry_run=False)
            self.assertEqual(rc, install_husky.EXIT_OK)
            # 文件仍应存在（chmod 失败不影响 copyfile）
            husky = target / ".husky"
            self.assertTrue((husky / "pre-commit").is_file())


class TestIdempotentRerun(unittest.TestCase):
    """test_idempotent_rerun：再跑一次不应报错或破坏。"""

    def test_idempotent_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            rc1 = install_husky.install("nodejs", str(target), dry_run=False)
            self.assertEqual(rc1, install_husky.EXIT_OK)
            husky = target / ".husky"
            first_hash = hash((husky / "pre-commit").read_bytes())
            # 第二次跑
            rc2 = install_husky.install("nodejs", str(target), dry_run=False)
            self.assertEqual(rc2, install_husky.EXIT_OK)
            second_hash = hash((husky / "pre-commit").read_bytes())
            self.assertEqual(first_hash, second_hash, "二次安装内容应一致")


class TestParseArgs(unittest.TestCase):
    """额外覆盖：--help / 必填参数 / 默认值。"""

    def test_required_target(self):
        with self.assertRaises(SystemExit):
            install_husky.parse_args(["--stack", "nodejs"])

    def test_default_stack(self):
        ns = install_husky.parse_args(["--target", "."])
        self.assertEqual(ns.stack, "nodejs")
        self.assertEqual(ns.target, ".")
        self.assertFalse(ns.dry_run)

    def test_dry_run_flag(self):
        ns = install_husky.parse_args(["--target", ".", "--dry-run"])
        self.assertTrue(ns.dry_run)


if __name__ == "__main__":
    unittest.main(verbosity=2)
