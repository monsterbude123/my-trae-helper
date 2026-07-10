"""校验 spec.md 是否符合 BDD 场景格式规范。

检查项：
1. 包含 L0-L4 段位编号
2. 至少 1 个 Requirement
3. 每个 Requirement 至少有 happy path + error scenario
4. Scenario 使用 WHEN-THEN-AND 格式
5. 使用 SHALL/SHALL NOT 表达契约
"""

import re
import sys
from pathlib import Path


def validate_spec(filepath: str) -> tuple[bool, list[str]]:
    content = Path(filepath).read_text(encoding="utf-8")
    issues = []

    # 1. 检查 L0-L4 编号
    if not re.search(r'>\s*L[0-4]-\d{3}', content):
        issues.append("缺少 L0-L4 段位编号（如 > L0-051）")

    # 2. 检查 Requirement
    requirements = re.findall(r'### Requirement:', content)
    if not requirements:
        issues.append("缺少 Requirement 定义（### Requirement: ...）")

    # 3. 检查每个 Requirement 有 happy path + error scenario
    req_blocks = re.split(r'### Requirement:', content)[1:]
    for i, block in enumerate(req_blocks):
        scenarios = re.findall(r'#### Scenario:', block)
        has_happy = any('happy' in s.lower() or '正常' in s or '成功' in s for s in scenarios)
        has_error = any('error' in s.lower() or '异常' in s or '失败' in s or '错误' in s for s in scenarios)

        if not scenarios:
            issues.append(f"Requirement #{i+1}: 缺少任何 Scenario")
        elif not has_happy:
            issues.append(f"Requirement #{i+1}: 缺少 happy path scenario")
        elif not has_error:
            issues.append(f"Requirement #{i+1}: 缺少 error scenario")

    # 4. 检查 WHEN-THEN 格式
    when_count = len(re.findall(r'\*\*WHEN\b', content))
    then_count = len(re.findall(r'\*\*THEN\b', content))
    if when_count == 0:
        issues.append("未找到 WHEN 关键字（场景需用 **WHEN** 格式）")
    if then_count == 0:
        issues.append("未找到 THEN 关键字（场景需用 **THEN** 格式）")

    # 5. 检查 SHALL/SHALL NOT
    shall_count = len(re.findall(r'\bSHALL\b', content))
    if shall_count == 0:
        issues.append("未使用 SHALL 表达契约（应使用 SHALL / SHALL NOT 替代模糊的'应该''可以'）")

    return len(issues) == 0, issues


def main():
    if len(sys.argv) < 2:
        print("用法: python spec-validate.py <spec.md 路径>")
        sys.exit(1)

    ok, issues = validate_spec(sys.argv[1])
    if ok:
        print("OK: spec.md 格式校验通过")
    else:
        print("FAIL: spec.md 存在以下问题:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
