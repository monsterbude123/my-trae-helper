#!/usr/bin/env python3
"""
ai-testmate 结构守卫
- 8 条雷检测(参见 references/trap-instructions.yaml)
- 三态自检支持(--test-pass / --test-block / --test-edge)
"""

import sys
import pathlib
import re
import argparse

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent


def check_ap1() -> str | None:
    """工作空间硬编码"""
    pattern = re.compile(r"/workspace/|/Users/[^/]+/|C:\\\\workspace|C:/workspace")
    for sh in (SKILL_DIR / "scripts").glob("*.sh"):
        text = sh.read_text(encoding="utf-8")
        if pattern.search(text):
            return f"AP-1 命中:{sh.name} 含工作空间硬编码"
    return None


def _strip_code_fences(text: str) -> str:
    """移除 markdown 代码块(```...```),防止文档中示例命令被误判"""
    return re.sub(r"```.*?\n.*?\n```", "", text, flags=re.DOTALL)


def _strip_comment_lines(text: str, markers: tuple) -> str:
    """移除以指定标记开头的行(注释行豁免)"""
    lines = text.splitlines()
    return "\n".join(l for l in lines if not l.lstrip().startswith(markers))


def check_ap2() -> str | None:
    """账号池泄露(.env.example 外)
    豁免:.env.example + guard 自身 + markdown 代码块 + 注释行"""
    pattern = re.compile(r"TEST_USER_[A-Z]_PASSWORD=[^_\s]")
    for f in SKILL_DIR.rglob("*"):
        if f.is_file() and f.name != ".env.example":
            rel = f.relative_to(SKILL_DIR)
            # 守卫自身豁免(检测器代码里必然有测试样本字符串)
            if rel == pathlib.Path("scripts/ai-testmate-guard.py"):
                continue
            try:
                text = f.read_text(encoding="utf-8")
                cleaned = _strip_code_fences(text)
                cleaned = _strip_comment_lines(cleaned, ("#", "//", "<!--"))
                if pattern.search(cleaned):
                    return f"AP-2 命中:{rel} 含真实密码赋值"
            except (UnicodeDecodeError, PermissionError):
                continue
    return None


def check_ap3() -> str | None:
    """禅道写权越界
    豁免:markdown 代码块(文档中示例命令)"""
    pattern = re.compile(r"zentao (bug|testtask) create")
    agents = SKILL_DIR / "agents"
    for md in agents.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        cleaned = _strip_code_fences(text)
        if pattern.search(cleaned):
            if md.name != "reporter.md":
                return f"AP-3 命中:{md.name} 含 zentao 写命令(只能 reporter.md)"
    return None


def check_ap4() -> str | None:
    """飞书直连 webhook"""
    pattern = re.compile(r"hooks\.lark|open\.feishu\.cn/open-apis/bot/v2/hook|webhook.*http")
    for sh in (SKILL_DIR / "scripts").glob("*.sh"):
        text = sh.read_text(encoding="utf-8")
        if pattern.search(text):
            return f"AP-4 命中:{sh.name} 含 webhook 直连"
    return None


def check_ap5() -> str | None:
    """截图脱敏漏做"""
    ui = SKILL_DIR / "agents" / "ui-tester.md"
    if not ui.exists():
        return "AP-5:ui-tester.md 不存在"
    text = ui.read_text(encoding="utf-8")
    if not re.search(r"mask|redact|脱敏", text):
        return "AP-5 命中:ui-tester.md 无 mask/redact/脱敏 关键字"
    return None


def check_ap6() -> str | None:
    """跨平台 Python 路径硬编码
    豁免:detect-python.sh 内部探测路径 + 注释行"""
    pattern = re.compile(r"/mnt/c/|/usr/bin/python|C:/ProgramData/")
    for sh in (SKILL_DIR / "scripts").glob("*.sh"):
        if sh.name == "detect-python.sh":
            continue
        text = sh.read_text(encoding="utf-8")
        cleaned = _strip_comment_lines(text, ("#",))
        if pattern.search(cleaned):
            return f"AP-6 命中:{sh.name} 含 Python 路径硬编码"
    return None


def check_ap7() -> str | None:
    """报告无时间戳"""
    rt = SKILL_DIR / "scripts" / "run-test.sh"
    if not rt.exists():
        return "AP-7:run-test.sh 不存在(本检查依赖此脚本)"
    text = rt.read_text(encoding="utf-8")
    if not re.search(r"YYYYMMDD|%Y%m%d|%y%m%d", text):
        return "AP-7 命中:run-test.sh 缺时间戳格式"
    return None


def check_ap8() -> str | None:
    """SKILL.md 超 350 行"""
    skill = SKILL_DIR / "SKILL.md"
    if not skill.exists():
        return "AP-8:SKILL.md 不存在"
    lines = len(skill.read_text(encoding="utf-8").splitlines())
    if lines > 350:
        return f"AP-8 命中:SKILL.md {lines} 行 > 350 上限"
    return None


CHECKS = [
    ("AP-1", check_ap1),
    ("AP-2", check_ap2),
    ("AP-3", check_ap3),
    ("AP-4", check_ap4),
    ("AP-5", check_ap5),
    ("AP-6", check_ap6),
    ("AP-7", check_ap7),
    ("AP-8", check_ap8),
]


def run_all() -> list[str]:
    fails = []
    for name, fn in CHECKS:
        try:
            result = fn()
            if result:
                fails.append(result)
                print(f"  ❌ {result}")
            else:
                print(f"  ✅ {name} PASS")
        except Exception as e:
            fails.append(f"{name} 检测异常:{e}")
            print(f"  ⚠️  {name} 异常:{e}")
    return fails


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-pass", action="store_true", help="PASS 态自检")
    parser.add_argument("--test-block", action="store_true", help="BLOCK 态自检")
    parser.add_argument("--test-edge", action="store_true", help="边界态自检")
    args = parser.parse_args()

    print("=== ai-testmate 结构守卫 ===")

    if args.test_block:
        # 模拟 BLOCK:在 skill 根临时建一个含真实密码赋值的脚本,跑完删除
        trap_dir = SKILL_DIR / "scripts"
        trap_file = trap_dir / "_block_trap_test.sh"
        trap_file.write_text(
            "#!/usr/bin/env bash\nTEST_USER_A_PASSWORD=real_password_123\necho leaked\n",
            encoding="utf-8",
        )
        fails = run_all()
        trap_file.unlink()
        if fails:
            print(f"\n🛑 BLOCK 态自检成功(检测到 {len(fails)} 项违规)")
            return 1
        print("\n❌ BLOCK 态自检失败(应检测到违规但未检测)")
        return 1

    if args.test_pass:
        # 正常 PASS
        fails = run_all()
        if fails:
            print(f"\n❌ PASS 态失败:{len(fails)} 项")
            return 1
        print("\n✅ PASS")
        return 0

    if args.test_edge:
        # 边界:.env.example 含变量名但密码字段为空字符串(不应触发 AP-2)
        env_ex = SKILL_DIR / ".env.example"
        if env_ex.exists():
            original = env_ex.read_text(encoding="utf-8")
        else:
            original = None
        env_ex.write_text("TEST_USER_A_PASSWORD=\n", encoding="utf-8")
        fails = run_all()
        if original is not None:
            env_ex.write_text(original, encoding="utf-8")
        else:
            env_ex.unlink()
        # 只关心 AP-2 是否误报
        ap2_fail = [f for f in fails if "AP-2" in f]
        if ap2_fail:
            print(f"\n❌ 边界态误报:{ap2_fail}")
            return 1
        print("\n✅ 边界态 PASS(无误报)")
        return 0

    # 默认:跑全量
    fails = run_all()
    if fails:
        print(f"\n🛑 BLOCKED:{len(fails)} 项违规")
        return 1
    print("\n✅ ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())