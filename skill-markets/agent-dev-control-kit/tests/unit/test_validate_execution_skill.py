"""validate-execution-skill 反例单元测试

覆盖:
  - Frontmatter 必填字段 / 空字段 / 非法 name
  - 必需章节 + 推荐章节
  - 控制点(CP-N)解析
  - 流程图断言
  - main() CLI 退出码 + report 生成
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


# ============================================================================
# 最小合规 fixture
# ============================================================================
@pytest.fixture
def minimal_skill(tmp_path: Path) -> Path:
    body = """---
name: fixture-skill
description: 测试 fixture
version: 1.0.0
---

# fixture-skill

## 适用场景

在本测试中用作"合规最小集"。这里超过 20 字以绕过"内容过短"警告。

## 执行流程

```mermaid
graph TD
    A[开始] --> B{判定}
    B -->|是| C[走]
    B -->|否| D[停]
```

## 验收标准

- 功能 OK
- 边界 OK

## 触发词

- foo

## 输入规范

- ...

## 输出规范

- ...

## 错误处理

- ...

## 示例用法

- ...
"""
    p = tmp_path / "SKILL.md"
    p.write_text(body, encoding="utf-8")
    return p


# ============================================================================
# TestFrontmatter — Frontmatter 校验
# ============================================================================
class TestFrontmatter:
    def test_minimal_frontmatter_valid(self, validate_execution_skill, minimal_skill):
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(minimal_skill)
        assert result.is_valid is True
        errors = [i for i in result.issues if i.severity == "ERROR"]
        assert errors == [], f"最小合规样本不应有 ERROR,得到 {[i.message for i in errors]}"

    @pytest.mark.trap
    def test_missing_frontmatter_blocks(self, validate_execution_skill, tmp_path):
        p = tmp_path / "SKILL.md"
        p.write_text("# no frontmatter\n\n## 适用场景\nx" * 5, encoding="utf-8")
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(p)
        assert result.is_valid is False
        msgs = " ".join(i.message for i in result.issues)
        assert "YAML frontmatter" in msgs

    @pytest.mark.trap
    def test_missing_required_field_name(self, validate_execution_skill, tmp_path):
        p = tmp_path / "SKILL.md"
        p.write_text(
            "---\n"
            "description: 缺 name\n"
            "version: 1.0.0\n"
            "---\n\n# x\n\n## 适用场景\n" + ("x" * 30),
            encoding="utf-8",
        )
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(p)
        assert result.is_valid is False
        assert any("name" in i.message for i in result.issues if i.severity == "ERROR")

    def test_non_kebab_name_warns(self, validate_execution_skill, minimal_skill):
        # 修改 name 为驼峰
        text = minimal_skill.read_text(encoding="utf-8")
        text = text.replace("name: fixture-skill", "name: FixtureSkill")
        minimal_skill.write_text(text, encoding="utf-8")
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(minimal_skill)
        warns = [i for i in result.issues if i.severity == "WARNING"]
        assert any("name" in i.message for i in warns)


# ============================================================================
# TestSections — 章节校验
# ============================================================================
class TestSections:
    @pytest.mark.trap
    @pytest.mark.parametrize(
        "missing_section",
        ["适用场景", "执行流程", "验收标准"],
    )
    def test_required_section_missing_blocks(
        self, validate_execution_skill, minimal_skill, missing_section
    ):
        text = minimal_skill.read_text(encoding="utf-8")
        # 删除指定章节(整段)
        lines = text.splitlines()
        out, skip = [], False
        for line in lines:
            if line.strip() == f"## {missing_section}":
                skip = True
                continue
            if skip and line.startswith("## "):
                skip = False
            if not skip:
                out.append(line)
        minimal_skill.write_text("\n".join(out), encoding="utf-8")

        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(minimal_skill)
        assert result.is_valid is False, f"缺 `{missing_section}` 必须阻断"
        assert any(missing_section in i.message for i in result.issues if i.severity == "ERROR")

    def test_short_section_warns(self, validate_execution_skill, tmp_path):
        p = tmp_path / "SKILL.md"
        p.write_text(
            "---\nname: short\ndescription: short\n---\n\n# short\n\n## 适用场景\n\n## 执行流程\n" + "x" * 30 + "\n\n## 验收标准\n" + "x" * 30,
            encoding="utf-8",
        )
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(p)
        assert any("过短" in i.message for i in result.issues if i.severity == "WARNING")

    def test_recommended_sections_missing_only_warns(self, validate_execution_skill, tmp_path):
        p = tmp_path / "SKILL.md"
        p.write_text(
            "---\nname: x\ndescription: x\n---\n\n# x\n\n## 适用场景\n"
            + "x" * 30
            + "\n\n## 执行流程\n"
            + "x" * 30
            + "\n\n## 验收标准\n"
            + "x" * 30,
            encoding="utf-8",
        )
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(p)
        assert result.is_valid is True
        msgs = [i.message for i in result.issues if i.severity == "WARNING"]
        assert any("触发词" in m or "输入规范" in m for m in msgs)


# ============================================================================
# TestControlPoints — CP-N 校验
# ============================================================================
class TestControlPoints:
    def test_control_point_without_required_keywords_warns(self, validate_execution_skill, tmp_path):
        p = tmp_path / "SKILL.md"
        p.write_text(
            "---\nname: x\ndescription: x\n---\n\n"
            "# x\n\n## 适用场景\n" + "x" * 30 +
            "\n\n## 执行流程\n" + "x" * 30 +
            "\n\n## 验收标准\n" + "x" * 30 +
            "\n\n### CP-1: 没有关键要素\n无任何解释\n",
            encoding="utf-8",
        )
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(p)
        warn_msgs = [i.message for i in result.issues if i.severity == "WARNING"]
        assert any("CP-1" in m for m in warn_msgs)

    def test_no_control_point_is_only_info(self, validate_execution_skill, minimal_skill):
        # minimal_skill 没有 ### CP-N
        v = validate_execution_skill.ExecutionSkillValidator(verbose=False)
        result = v.validate_file(minimal_skill)
        infos = [i for i in result.issues if i.severity == "INFO"]
        assert any("CP" in i.message for i in infos)


# ============================================================================
# TestMain — CLI 集成(直接 spawn subprocess,验证退出码与报告)
# ============================================================================
class TestMain:
    def test_happy_path_exit_success(self, validate_execution_skill, invoke_cli, minimal_skill):
        rc, stdout, _ = invoke_cli(
            "validate-execution-skill.py",
            ["--file", str(minimal_skill)],
        )
        assert rc == validate_execution_skill.EXIT_SUCCESS

    @pytest.mark.trap
    def test_validation_failed_exit_code(self, validate_execution_skill, invoke_cli, tmp_path):
        bad = tmp_path / "SKILL.md"
        bad.write_text("# no frontmatter\n", encoding="utf-8")
        rc, _, _ = invoke_cli(
            "validate-execution-skill.py",
            ["--file", str(bad)],
        )
        assert rc == validate_execution_skill.EXIT_VALIDATION_FAILED

    def test_missing_args_exit_error(self, validate_execution_skill, invoke_cli):
        rc, _, _ = invoke_cli("validate-execution-skill.py", [])
        assert rc == validate_execution_skill.EXIT_ERROR

    def test_report_file_generated(self, validate_execution_skill, invoke_cli, minimal_skill, tmp_path):
        report = tmp_path / "report.md"
        rc, _, _ = invoke_cli(
            "validate-execution-skill.py",
            ["--file", str(minimal_skill), "--report", str(report), "--required-only"],
        )
        assert rc == validate_execution_skill.EXIT_SUCCESS
        content = report.read_text(encoding="utf-8")
        assert "Execution Skill 验证报告" in content
        assert "SKILL.md" in content or str(minimal_skill) in content
