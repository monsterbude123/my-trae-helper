"""
Spec 格式机械验证 — 零依赖，确定性校验。

用法:
  python spec-validate.py <spec.md路径> [--mode delta|full]

退出码: 0=通过, 1=格式错误

输出 JSON:
  {"pass": true, "errors": [], "warnings": []}
  {"pass": false, "errors": ["E001: ..."]}
"""

import re
import sys
import json


class SpecValidator:
    """机械验证 Spec 格式，不依赖 LLM 推理。"""

    SCENARIO_PATTERN = re.compile(r'^(#{1,5})\s*Scenario:')
    REQUIREMENT_PATTERN = re.compile(r'^###\s+Requirement:')
    INVARIANT_PATTERN = re.compile(r'^-\s*INV-\d+:')
    E2E_PATTERN = re.compile(r'^###\s+E2E-\d+:')
    ACCEPTANCE_PATTERN = re.compile(r'^-\s*\[[ x]\]')
    DELTA_HEADER_PATTERN = re.compile(r'^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements')
    REMOVED_HEADER = re.compile(r'^##\s+REMOVED\s+Requirements')

    VALID_DELTA_HEADERS = {'ADDED', 'MODIFIED', 'REMOVED', 'RENAMED'}

    def __init__(self, filepath: str, mode: str = 'full'):
        self.filepath = filepath
        self.mode = mode  # 'full' | 'delta'
        self.errors = []
        self.warnings = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    # ─── 主方法 ───────────────────────────────────────

    def validate(self) -> dict:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return self._result([f"文件不存在: {self.filepath}"])
        except UnicodeDecodeError as e:
            return self._result([f"编码错误: {e}"])

        self._check_scenario_format(lines)
        self._check_requirement_has_scenario(lines)
        self._check_counts(lines)

        if self.mode == 'delta':
            self._check_delta_structure(lines)

        return self._result()

    # ─── 检查项 ───────────────────────────────────────

    def _check_scenario_format(self, lines):
        """E001: Scenario 必须用 4 个 # (####)"""
        for i, line in enumerate(lines, 1):
            m = self.SCENARIO_PATTERN.match(line)
            if m and m.group(1) != '####':
                self.errors.append(
                    f"E001: 第{i}行 Scenario 格式错误（{m.group(1)} Scenario: → 应为 #### Scenario:）"
                )

    def _check_requirement_has_scenario(self, lines):
        """E002: 每个 Requirement 必须有 ≥ 1 个 Scenario（REMOVED 段除外）"""
        current_req_line = None
        has_scenario = False
        in_removed = False

        def _flush():
            nonlocal current_req_line, has_scenario
            if current_req_line is not None and not has_scenario and not in_removed:
                self.errors.append(
                    f"E002: 第{current_req_line}行 Requirement 缺少 Scenario"
                )
            current_req_line = None
            has_scenario = False

        for i, line in enumerate(lines, 1):
            m = self.DELTA_HEADER_PATTERN.match(line)
            if m and self.mode == 'delta':
                _flush()
                in_removed = (m.group(1) == 'REMOVED')
                continue

            if self.REQUIREMENT_PATTERN.match(line):
                _flush()
                current_req_line = i
                has_scenario = False
            if self.SCENARIO_PATTERN.match(line):
                has_scenario = True

        _flush()

    def _check_counts(self, lines):
        """E003: Requirement 数量；W001/W002/W003 仅 full 模式检查"""
        req_count = sum(1 for l in lines if self.REQUIREMENT_PATTERN.match(l))
        e2e_count = sum(1 for l in lines if self.E2E_PATTERN.match(l))
        inv_count = sum(1 for l in lines if self.INVARIANT_PATTERN.match(l))
        acc_count = sum(1 for l in lines if self.ACCEPTANCE_PATTERN.match(l))

        min_req = 1 if self.mode == 'delta' else 2
        if req_count < min_req:
            self.errors.append(
                f"E003: Requirement 数量不足（{req_count} < {min_req}）"
            )

        # full 模式下检查 E2E/Invariants/Acceptance；delta 模式下不要求
        if self.mode == 'full':
            if e2e_count < 2:
                self.warnings.append(f"W001: E2E Scenario 不足（{e2e_count} < 2）")
            if inv_count < 1:
                self.warnings.append(f"W002: Invariants 缺失")
            if acc_count < 3:
                self.warnings.append(f"W003: Acceptance 可验证条件不足（{acc_count} < 3）")

    def _check_delta_structure(self, lines):
        """E005: Delta 段头必须合法"""
        for i, line in enumerate(lines, 1):
            m = self.DELTA_HEADER_PATTERN.match(line)
            if m:
                header = m.group(1)
                if header not in self.VALID_DELTA_HEADERS:
                    self.errors.append(f"E005: 第{i}行 非法的 Delta 段头: {header}")

    # ─── 输出 ─────────────────────────────────────────

    def _result(self, extra_errors=None) -> dict:
        if extra_errors:
            self.errors.extend(extra_errors)
        return {"pass": self.passed, "errors": self.errors, "warnings": self.warnings}


# ─── CLI ──────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Spec 格式机械验证")
    parser.add_argument("spec_path", help="spec.md 路径")
    parser.add_argument("--mode", choices=["delta", "full"], default="full")
    args = parser.parse_args()

    validator = SpecValidator(args.spec_path, args.mode)
    result = validator.validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
