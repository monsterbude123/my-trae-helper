#!/usr/bin/env python3
"""
validate-execution-skill.py - 验证 Execution Skill 模板

功能：
- 验证 SKILL.md 文件格式
- 检查必需章节是否存在
- 验证 YAML frontmatter 完整性
- 检查控制点规范性
- 输出验证报告

使用：
    python validate-execution-skill.py [OPTIONS]

选项：
    --file PATH       验证单个 Skill 文件
    --dir PATH        验证整个目录
    --report PATH     输出验证报告文件
    --required-only   仅检查必需章节
    --verbose         详细输出模式
    --help            显示帮助信息

依赖：
    - Python 3.8+
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from colorama import init as colorama_init, Fore, Style
    HAS_COLORAMA = True
    colorama_init()
except ImportError:
    HAS_COLORAMA = False
    Fore = Style = type('Dummy', (), {'__getattr__': lambda s, n: ''})()

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_VALIDATION_FAILED = 4


@dataclass
class ValidationIssue:
    """验证问题"""
    severity: str  # ERROR, WARNING, INFO
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果"""
    file_path: str
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_error(self, message: str, location: str = None, suggestion: str = None):
        self.issues.append(ValidationIssue('ERROR', message, location, suggestion))
        self.is_valid = False
    
    def add_warning(self, message: str, location: str = None, suggestion: str = None):
        self.issues.append(ValidationIssue('WARNING', message, location, suggestion))
    
    def add_info(self, message: str, location: str = None, suggestion: str = None):
        self.issues.append(ValidationIssue('INFO', message, location, suggestion))


class ExecutionSkillValidator:
    """Execution Skill 验证器"""
    
    REQUIRED_FRONTMATTER = ['name', 'description']
    RECOMMENDED_FRONTMATTER = ['version']
    
    REQUIRED_SECTIONS = [
        '适用场景',
        '执行流程',
        '验收标准',
    ]
    
    RECOMMENDED_SECTIONS = [
        '触发词',
        '输入规范',
        '输出规范',
        '错误处理',
        '示例用法',
    ]
    
    CONTROL_POINT_PATTERN = re.compile(r'^###\s+CP-\d+[：:]', re.MULTILINE)
    FLOW_DIAGRAM_PATTERN = re.compile(r'```mermaid.*?graph\s+TD.*?```', re.DOTALL)
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ValidationResult] = []
    
    def log(self, message: str, level: str = 'INFO') -> None:
        """输出日志消息"""
        if level == 'SUCCESS':
            prefix = f'{Fore.GREEN}✅{Style.RESET_ALL}' if HAS_COLORAMA else '✅'
        elif level == 'WARNING':
            prefix = f'{Fore.YELLOW}⚠️{Style.RESET_ALL}' if HAS_COLORAMA else '⚠️'
        elif level == 'ERROR':
            prefix = f'{Fore.RED}🛑{Style.RESET_ALL}' if HAS_COLORAMA else '🛑'
        else:
            prefix = f'{Fore.CYAN}ℹ️{Style.RESET_ALL}' if HAS_COLORAMA else 'ℹ️'
        
        print(f"{prefix} {message}")
    
    def extract_frontmatter(self, content: str) -> Tuple[Optional[Dict], Optional[str]]:
        """提取 YAML frontmatter"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None, None
        
        frontmatter_text = match.group(1)
        
        if not HAS_YAML:
            return {}, frontmatter_text
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter, frontmatter_text
        except yaml.YAMLError as e:
            return None, frontmatter_text
    
    def validate_frontmatter(self, content: str, result: ValidationResult) -> Optional[Dict]:
        """验证 YAML frontmatter"""
        frontmatter, raw_text = self.extract_frontmatter(content)
        
        if frontmatter is None and raw_text is None:
            result.add_error(
                "缺少 YAML frontmatter",
                location="文件开头",
                suggestion="在文件开头添加 YAML frontmatter:\n---\nname: skill-name\ndescription: 技能描述\n---"
            )
            return None
        
        if frontmatter is None:
            result.add_error(
                "YAML frontmatter 格式错误",
                location="YAML frontmatter",
                suggestion="检查 YAML 语法，确保正确缩进和格式"
            )
            return None
        
        for field_name in self.REQUIRED_FRONTMATTER:
            if field_name not in frontmatter:
                result.add_error(
                    f"缺少必需的 frontmatter 字段: {field_name}",
                    location="YAML frontmatter",
                    suggestion=f"添加字段: {field_name}: <value>"
                )
            elif not frontmatter[field_name]:
                result.add_warning(
                    f"frontmatter 字段为空: {field_name}",
                    location="YAML frontmatter",
                    suggestion=f"为 {field_name} 提供有效值"
                )
        
        for field_name in self.RECOMMENDED_FRONTMATTER:
            if field_name not in frontmatter:
                result.add_warning(
                    f"建议添加 frontmatter 字段: {field_name}",
                    location="YAML frontmatter"
                )
        
        if 'name' in frontmatter:
            name = frontmatter['name']
            if not re.match(r'^[a-z][a-z0-9-]*$', str(name)):
                result.add_warning(
                    f"name 字段格式不规范: {name}",
                    location="YAML frontmatter",
                    suggestion="name 应为 kebab-case 格式（小写字母、数字、连字符）"
                )
        
        return frontmatter
    
    def extract_sections(self, content: str) -> Dict[str, str]:
        """提取章节内容"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            section_match = re.match(r'^##\s+(.+)$', line)
            if section_match:
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = section_match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def validate_sections(self, content: str, result: ValidationResult, required_only: bool = False) -> None:
        """验证章节完整性"""
        sections = self.extract_sections(content)
        
        for section_name in self.REQUIRED_SECTIONS:
            if section_name not in sections:
                result.add_error(
                    f"缺少必需章节: {section_name}",
                    suggestion=f"添加章节:\n## {section_name}\n\n<章节内容>"
                )
            else:
                section_content = sections[section_name]
                if len(section_content.strip()) < 20:
                    result.add_warning(
                        f"章节内容过短: {section_name}",
                        location=f"## {section_name}",
                        suggestion="补充更详细的内容"
                    )
        
        if not required_only:
            for section_name in self.RECOMMENDED_SECTIONS:
                if section_name not in sections:
                    result.add_warning(
                        f"建议添加章节: {section_name}",
                        suggestion=f"添加章节:\n## {section_name}\n\n<章节内容>"
                    )
    
    def validate_control_points(self, content: str, result: ValidationResult) -> None:
        """验证控制点规范性"""
        control_points = self.CONTROL_POINT_PATTERN.findall(content)
        
        if not control_points:
            result.add_info(
                "未检测到控制点定义（CP-1, CP-2...）",
                suggestion="对于复杂的 Execution Skill，建议定义明确的控制点"
            )
            return
        
        for cp in control_points:
            cp_section_pattern = re.compile(
                rf'{re.escape(cp)}.*?(?=###\s+CP-|\n##\s+|\Z)',
                re.DOTALL
            )
            cp_match = cp_section_pattern.search(content)
            
            if cp_match:
                cp_content = cp_match.group(0)
                
                if '触发条件' not in cp_content and '判定标准' not in cp_content:
                    result.add_warning(
                        f"控制点缺少关键要素: {cp}",
                        location=cp,
                        suggestion="控制点应包含：触发条件、执行步骤、判定标准、输出产物"
                    )
    
    def validate_flow_diagrams(self, content: str, result: ValidationResult) -> None:
        """验证流程图规范性"""
        flow_diagrams = self.FLOW_DIAGRAM_PATTERN.findall(content)
        
        if flow_diagrams:
            for diagram in flow_diagrams:
                if 'graph TD' not in diagram and 'graph TB' not in diagram:
                    result.add_warning(
                        "流程图建议使用 graph TD 或 graph TB（自上而下）",
                        location="Mermaid 流程图"
                    )
                
                if '[' not in diagram and '{' not in diagram:
                    result.add_warning(
                        "流程图应包含判定节点（菱形 { }）或操作节点（方框 [ ]）",
                        location="Mermaid 流程图"
                    )
    
    def validate_file(self, file_path: Path, required_only: bool = False) -> ValidationResult:
        """验证单个文件"""
        result = ValidationResult(file_path=str(file_path))
        
        if not file_path.exists():
            result.add_error(f"文件不存在: {file_path}")
            return result
        
        if not file_path.is_file():
            result.add_error(f"路径不是文件: {file_path}")
            return result
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.add_error(f"读取文件失败: {str(e)}")
            return result
        
        if not content.strip():
            result.add_error("文件内容为空")
            return result
        
        frontmatter = self.validate_frontmatter(content, result)
        self.validate_sections(content, result, required_only)
        self.validate_control_points(content, result)
        self.validate_flow_diagrams(content, result)
        
        return result
    
    def validate_directory(self, dir_path: Path, required_only: bool = False) -> List[ValidationResult]:
        """验证目录中的所有 SKILL.md 文件"""
        results = []
        
        skill_files = list(dir_path.glob('**/SKILL.md'))
        
        if not skill_files:
            result = ValidationResult(file_path=str(dir_path))
            result.add_warning("未找到 SKILL.md 文件")
            results.append(result)
            return results
        
        for skill_file in skill_files:
            result = self.validate_file(skill_file, required_only)
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[ValidationResult]) -> str:
        """生成验证报告"""
        report_lines = [
            "# Execution Skill 验证报告",
            f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**文件数量**: {len(results)}",
            ""
        ]
        
        valid_count = sum(1 for r in results if r.is_valid)
        report_lines.append(f"**验证通过**: {valid_count} / {len(results)}")
        report_lines.append("")
        
        for result in results:
            report_lines.append(f"## {result.file_path}")
            report_lines.append(f"\n**状态**: {'✅ 通过' if result.is_valid else '❌ 失败'}")
            
            if result.issues:
                report_lines.append("\n### 问题列表\n")
                
                for issue in result.issues:
                    severity_map = {
                        'ERROR': '❌ ERROR',
                        'WARNING': '⚠️ WARNING',
                        'INFO': 'ℹ️ INFO'
                    }
                    severity_str = severity_map.get(issue.severity, issue.severity)
                    
                    report_lines.append(f"- **{severity_str}**: {issue.message}")
                    
                    if issue.location:
                        report_lines.append(f"  - 位置: {issue.location}")
                    
                    if issue.suggestion:
                        report_lines.append(f"  - 建议: {issue.suggestion}")
            
            report_lines.append("")
        
        return '\n'.join(report_lines)
    
    def print_summary(self, results: List[ValidationResult]) -> None:
        """打印摘要"""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        errors = sum(len([i for i in r.issues if i.severity == 'ERROR']) for r in results)
        warnings = sum(len([i for i in r.issues if i.severity == 'WARNING']) for r in results)
        
        print("\n" + "=" * 60)
        print("验证摘要")
        print("=" * 60)
        print(f"文件总数: {total}")
        print(f"验证通过: {valid}")
        print(f"验证失败: {total - valid}")
        print(f"错误数量: {errors}")
        print(f"警告数量: {warnings}")
        print("=" * 60)
        
        if valid == total:
            self.log("所有文件验证通过", 'SUCCESS')
        else:
            self.log("部分文件验证失败", 'ERROR')


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='验证 Execution Skill 模板',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 验证单个 Skill 文件
    python validate-execution-skill.py --file skill-markets/my-skill/SKILL.md
    
    # 验证整个目录
    python validate-execution-skill.py --dir skill-markets/my-skill
    
    # 输出验证报告
    python validate-execution-skill.py --file SKILL.md --report validation-report.md
    
    # 仅检查必需章节
    python validate-execution-skill.py --file SKILL.md --required-only
        """
    )
    
    parser.add_argument(
        '--file',
        type=Path,
        help='验证单个 Skill 文件'
    )
    
    parser.add_argument(
        '--dir',
        type=Path,
        help='验证整个目录'
    )
    
    parser.add_argument(
        '--report',
        type=Path,
        help='输出验证报告文件'
    )
    
    parser.add_argument(
        '--required-only',
        action='store_true',
        help='仅检查必需章节'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出模式'
    )
    
    return parser.parse_args()


def main() -> int:
    """主函数"""
    args = parse_args()
    
    if not args.file and not args.dir:
        print("错误: 必须指定 --file 或 --dir", file=sys.stderr)
        return EXIT_ERROR
    
    validator = ExecutionSkillValidator(verbose=args.verbose)
    
    results = []
    
    if args.file:
        validator.log(f"验证文件: {args.file}")
        result = validator.validate_file(args.file, args.required_only)
        results.append(result)
        
        for issue in result.issues:
            if issue.severity == 'ERROR':
                validator.log(f"{issue.message}", 'ERROR')
            elif issue.severity == 'WARNING':
                validator.log(f"{issue.message}", 'WARNING')
            else:
                validator.log(f"{issue.message}", 'INFO')
    
    if args.dir:
        validator.log(f"验证目录: {args.dir}")
        results.extend(validator.validate_directory(args.dir, args.required_only))
    
    validator.print_summary(results)
    
    if args.report:
        report_content = validator.generate_report(results)
        args.report.write_text(report_content, encoding='utf-8')
        validator.log(f"验证报告已保存: {args.report}", 'SUCCESS')
    
    all_valid = all(r.is_valid for r in results)
    return EXIT_SUCCESS if all_valid else EXIT_VALIDATION_FAILED


if __name__ == '__main__':
    sys.exit(main())