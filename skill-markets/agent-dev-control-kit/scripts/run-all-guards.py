#!/usr/bin/env python3
"""
run-all-guards.py - 批量运行所有 Guard 检查

功能：
- 批量运行多个 Guard 检查
- 支持指定检查范围
- 输出汇总报告
- 支持失败阈值设置

使用：
    python run-all-guards.py [OPTIONS]

选项：
    --guards LIST     运行指定 Guard（逗号分隔）
    --scope PATH      指定检查范围
    --report PATH     输出报告文件
    --fail-on LEVEL   失败阈值（BLOCK/WARN）
    --config PATH     指定配置文件
    --verbose         详细输出模式
    --help            显示帮助信息

依赖：
    - Python 3.8+
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

try:
    from colorama import init as colorama_init, Fore, Style
    HAS_COLORAMA = True
    colorama_init()
except ImportError:
    HAS_COLORAMA = False
    Fore = Style = type('Dummy', (), {'__getattr__': lambda s, n: ''})()

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_GUARD_FAILED = 5


class GuardStatus(Enum):
    """Guard 检查状态"""
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class GuardCheckResult:
    """Guard 检查结果"""
    guard_name: str
    status: GuardStatus
    message: str = ""
    details: List[Dict] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass
class GuardReport:
    """Guard 汇总报告"""
    timestamp: str
    total_guards: int
    passed: int = 0
    warned: int = 0
    blocked: int = 0
    skipped: int = 0
    errors: int = 0
    results: List[GuardCheckResult] = field(default_factory=list)


class GuardRunner:
    """Guard 执行器"""
    
    AVAILABLE_GUARDS = {
        'api-contract': {
            'description': 'API 契约检查',
            'severity': 'HIGH',
            'default_enabled': True
        },
        'architecture': {
            'description': '架构约束检查',
            'severity': 'HIGH',
            'default_enabled': True
        },
        'test-coverage': {
            'description': '测试覆盖检查',
            'severity': 'HIGH',
            'default_enabled': True
        },
        'security': {
            'description': '安全约束检查',
            'severity': 'CRITICAL',
            'default_enabled': True
        },
        'performance': {
            'description': '性能约束检查',
            'severity': 'MEDIUM',
            'default_enabled': False
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None, scope: Optional[Path] = None, verbose: bool = False):
        self.config_path = config_path
        self.scope = scope or Path.cwd()
        self.verbose = verbose
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            'guards': {name: info['default_enabled'] for name, info in self.AVAILABLE_GUARDS.items()},
            'fail_on': 'BLOCK',
            'report_format': 'json'
        }
        
        if self.config_path and self.config_path.exists():
            try:
                import yaml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config:
                        default_config.update(config)
            except Exception as e:
                if self.verbose:
                    print(f"加载配置文件失败: {str(e)}")
        
        return default_config
    
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
    
    def check_directory_structure(self) -> GuardCheckResult:
        """检查目录结构"""
        result = GuardCheckResult(
            guard_name='architecture',
            status=GuardStatus.PASS,
            message='目录结构检查'
        )
        
        required_dirs = ['guards', 'gates', 'hooks']
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (self.scope / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            result.status = GuardStatus.BLOCK
            result.message = f"缺少必需目录: {', '.join(missing_dirs)}"
            result.details = [{'missing_dir': d} for d in missing_dirs]
        else:
            result.message = "目录结构完整"
        
        return result
    
    def check_config_files(self) -> GuardCheckResult:
        """检查配置文件"""
        result = GuardCheckResult(
            guard_name='architecture',
            status=GuardStatus.PASS,
            message='配置文件检查'
        )
        
        required_configs = {
            'guards/guard-config.yaml': 'Guard 配置文件',
            'gates/gate-config.json': 'Gate 配置文件',
        }
        
        missing_configs = []
        for config_path, description in required_configs.items():
            full_path = self.scope / config_path
            if not full_path.exists():
                missing_configs.append({'path': config_path, 'description': description})
        
        if missing_configs:
            result.status = GuardStatus.WARN
            result.message = f"缺少配置文件: {len(missing_configs)} 个"
            result.details = missing_configs
        else:
            result.message = "配置文件完整"
        
        return result
    
    def run_api_contract_guard(self) -> GuardCheckResult:
        """运行 API 契约检查"""
        result = GuardCheckResult(
            guard_name='api-contract',
            status=GuardStatus.PASS,
            message='API 契约检查'
        )
        
        api_files = list(self.scope.glob('**/*api*.py')) + \
                   list(self.scope.glob('**/*api*.ts')) + \
                   list(self.scope.glob('**/openapi.yaml'))
        
        if not api_files:
            result.status = GuardStatus.SKIP
            result.message = "未找到 API 定义文件"
            return result
        
        issues = []
        for api_file in api_files[:10]:
            if self.verbose:
                self.log(f"检查文件: {api_file}")
            
            content = api_file.read_text(encoding='utf-8', errors='ignore')
            
            if '@api' in content or '/api/' in content:
                if 'schema' not in content.lower() and 'response' not in content.lower():
                    issues.append({
                        'file': str(api_file),
                        'issue': '缺少响应 Schema 定义'
                    })
        
        if issues:
            result.status = GuardStatus.WARN
            result.message = f"发现 {len(issues)} 个 API 契约问题"
            result.details = issues
        else:
            result.message = f"检查了 {len(api_files)} 个 API 文件，未发现问题"
        
        return result
    
    def run_architecture_guard(self) -> GuardCheckResult:
        """运行架构约束检查"""
        result = GuardCheckResult(
            guard_name='architecture',
            status=GuardStatus.PASS,
            message='架构约束检查'
        )
        
        dir_result = self.check_directory_structure()
        config_result = self.check_config_files()
        
        result.details = [
            {'check': 'directory_structure', 'status': dir_result.status.value, 'message': dir_result.message},
            {'check': 'config_files', 'status': config_result.status.value, 'message': config_result.message}
        ]
        
        if dir_result.status == GuardStatus.BLOCK or config_result.status == GuardStatus.BLOCK:
            result.status = GuardStatus.BLOCK
            result.message = "架构检查失败"
        elif dir_result.status == GuardStatus.WARN or config_result.status == GuardStatus.WARN:
            result.status = GuardStatus.WARN
            result.message = "架构检查发现警告"
        else:
            result.message = "架构检查通过"
        
        return result
    
    def run_test_coverage_guard(self) -> GuardCheckResult:
        """运行测试覆盖检查"""
        result = GuardCheckResult(
            guard_name='test-coverage',
            status=GuardStatus.PASS,
            message='测试覆盖检查'
        )
        
        test_dirs = ['tests/unit', 'tests/integration', 'tests/e2e']
        existing_test_dirs = []
        
        for test_dir in test_dirs:
            test_path = self.scope / test_dir
            if test_path.exists():
                existing_test_dirs.append(test_dir)
        
        if not existing_test_dirs:
            result.status = GuardStatus.WARN
            result.message = "未找到测试目录"
            return result
        
        test_files = []
        for test_dir in existing_test_dirs:
            test_files.extend((self.scope / test_dir).glob('**/*test*.py'))
            test_files.extend((self.scope / test_dir).glob('**/*test*.ts'))
        
        if len(test_files) < 1:
            result.status = GuardStatus.WARN
            result.message = f"测试文件数量过少: {len(test_files)}"
        else:
            result.message = f"找到 {len(test_files)} 个测试文件"
        
        result.details = [
            {'test_dirs': existing_test_dirs},
            {'test_file_count': len(test_files)}
        ]
        
        return result
    
    def run_security_guard(self) -> GuardCheckResult:
        """运行安全约束检查"""
        result = GuardCheckResult(
            guard_name='security',
            status=GuardStatus.PASS,
            message='安全约束检查'
        )
        
        patterns = {
            'hardcoded_secret': [
                (r'password\s*=\s*[\'"][^\'"]+[\'"]', '硬编码密码'),
                (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', '硬编码 API Key'),
                (r'secret\s*=\s*[\'"][^\'"]+[\'"]', '硬编码密钥'),
            ],
            'sql_injection': [
                (r'execute\s*\(\s*[f]?[\'"].*?\+.*?[\'"]\s*\)', 'SQL 字符串拼接'),
            ]
        }
        
        issues = []
        source_files = list(self.scope.glob('**/*.py')) + list(self.scope.glob('**/*.ts'))
        source_files = [f for f in source_files if 'node_modules' not in str(f) and '.venv' not in str(f)][:50]
        
        for source_file in source_files:
            try:
                content = source_file.read_text(encoding='utf-8', errors='ignore')
                
                for category, pattern_list in patterns.items():
                    for pattern, description in pattern_list:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append({
                                'file': str(source_file),
                                'category': category,
                                'issue': description
                            })
            except Exception:
                continue
        
        if issues:
            result.status = GuardStatus.WARN
            result.message = f"发现 {len(issues)} 个潜在安全问题"
            result.details = issues[:10]
        else:
            result.message = f"检查了 {len(source_files)} 个文件，未发现明显安全问题"
        
        return result
    
    def run_performance_guard(self) -> GuardCheckResult:
        """运行性能约束检查"""
        result = GuardCheckResult(
            guard_name='performance',
            status=GuardStatus.PASS,
            message='性能约束检查'
        )
        
        patterns = {
            'n_plus_one': r'for\s+\w+\s+in\s+.+:\s*\n.*?\.\s*(get|find|query|fetch)\s*\(',
            'large_loop': r'for\s+\w+\s+in\s+.+:\s*\n.*?\.\s*append\s*\(',
        }
        
        issues = []
        source_files = list(self.scope.glob('**/*.py')) + list(self.scope.glob('**/*.ts'))
        source_files = [f for f in source_files if 'node_modules' not in str(f) and '.venv' not in str(f)][:30]
        
        for source_file in source_files:
            try:
                content = source_file.read_text(encoding='utf-8', errors='ignore')
                
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, content, re.MULTILINE):
                        issues.append({
                            'file': str(source_file),
                            'pattern': pattern_name,
                            'issue': f'可能的 {pattern_name} 问题'
                        })
            except Exception:
                continue
        
        if issues:
            result.status = GuardStatus.WARN
            result.message = f"发现 {len(issues)} 个潜在性能问题"
            result.details = issues[:5]
        else:
            result.message = f"检查了 {len(source_files)} 个文件，未发现明显性能问题"
        
        return result
    
    def run_guard(self, guard_name: str) -> GuardCheckResult:
        """运行单个 Guard"""
        guard_methods = {
            'api-contract': self.run_api_contract_guard,
            'architecture': self.run_architecture_guard,
            'test-coverage': self.run_test_coverage_guard,
            'security': self.run_security_guard,
            'performance': self.run_performance_guard,
        }
        
        if guard_name not in guard_methods:
            return GuardCheckResult(
                guard_name=guard_name,
                status=GuardStatus.SKIP,
                message=f"未知的 Guard 类型: {guard_name}"
            )
        
        start_time = datetime.now()
        result = guard_methods[guard_name]()
        result.execution_time = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def run_all_guards(self, guard_list: Optional[List[str]] = None) -> GuardReport:
        """运行所有 Guard"""
        report = GuardReport(
            timestamp=datetime.now().isoformat(),
            total_guards=0
        )
        
        if guard_list:
            guards_to_run = guard_list
        else:
            guards_to_run = [
                name for name, info in self.AVAILABLE_GUARDS.items()
                if self.config.get('guards', {}).get(name, info['default_enabled'])
            ]
        
        report.total_guards = len(guards_to_run)
        
        self.log(f"开始运行 {len(guards_to_run)} 个 Guard 检查...")
        
        for guard_name in guards_to_run:
            self.log(f"运行 Guard: {guard_name}")
            result = self.run_guard(guard_name)
            report.results.append(result)
            
            if result.status == GuardStatus.PASS:
                report.passed += 1
                self.log(f"{guard_name}: {result.status.value}", 'SUCCESS')
            elif result.status == GuardStatus.WARN:
                report.warned += 1
                self.log(f"{guard_name}: {result.status.value} - {result.message}", 'WARNING')
            elif result.status == GuardStatus.BLOCK:
                report.blocked += 1
                self.log(f"{guard_name}: {result.status.value} - {result.message}", 'ERROR')
            elif result.status == GuardStatus.SKIP:
                report.skipped += 1
                self.log(f"{guard_name}: {result.status.value} - {result.message}")
            else:
                report.errors += 1
                self.log(f"{guard_name}: {result.status.value}", 'ERROR')
        
        return report
    
    def generate_report_json(self, report: GuardReport) -> str:
        """生成 JSON 格式报告"""
        report_dict = {
            'timestamp': report.timestamp,
            'summary': {
                'total': report.total_guards,
                'passed': report.passed,
                'warned': report.warned,
                'blocked': report.blocked,
                'skipped': report.skipped,
                'errors': report.errors
            },
            'results': [
                {
                    'guard_name': r.guard_name,
                    'status': r.status.value,
                    'message': r.message,
                    'details': r.details,
                    'execution_time': r.execution_time
                }
                for r in report.results
            ]
        }
        return json.dumps(report_dict, indent=2, ensure_ascii=False)
    
    def print_summary(self, report: GuardReport) -> None:
        """打印摘要"""
        print("\n" + "=" * 60)
        print("Guard 检查汇总")
        print("=" * 60)
        print(f"总计: {report.total_guards}")
        print(f"通过: {report.passed}")
        print(f"警告: {report.warned}")
        print(f"阻断: {report.blocked}")
        print(f"跳过: {report.skipped}")
        print(f"错误: {report.errors}")
        print("=" * 60)
        
        if report.blocked == 0 and report.errors == 0:
            self.log("所有 Guard 检查完成", 'SUCCESS')
        else:
            self.log("部分 Guard 检查失败", 'ERROR')


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='批量运行所有 Guard 检查',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 运行所有 Guard
    python run-all-guards.py
    
    # 运行指定 Guard
    python run-all-guards.py --guards api-contract,architecture
    
    # 指定检查范围
    python run-all-guards.py --scope src/api
    
    # 输出汇总报告
    python run-all-guards.py --report reports/guards-summary.json
    
    # 设置失败阈值
    python run-all-guards.py --fail-on WARN
        """
    )
    
    parser.add_argument(
        '--guards',
        type=str,
        help='运行指定 Guard（逗号分隔）'
    )
    
    parser.add_argument(
        '--scope',
        type=Path,
        default=Path.cwd(),
        help='指定检查范围'
    )
    
    parser.add_argument(
        '--report',
        type=Path,
        help='输出报告文件'
    )
    
    parser.add_argument(
        '--fail-on',
        type=str,
        choices=['BLOCK', 'WARN'],
        default='BLOCK',
        help='失败阈值'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='指定配置文件'
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
    
    runner = GuardRunner(
        config_path=args.config,
        scope=args.scope,
        verbose=args.verbose
    )
    
    guard_list = args.guards.split(',') if args.guards else None
    
    report = runner.run_all_guards(guard_list)
    
    runner.print_summary(report)
    
    if args.report:
        report_json = runner.generate_report_json(report)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report_json, encoding='utf-8')
        runner.log(f"报告已保存: {args.report}", 'SUCCESS')
    
    if args.fail_on == 'BLOCK' and report.blocked > 0:
        return EXIT_GUARD_FAILED
    elif args.fail_on == 'WARN' and (report.blocked > 0 or report.warned > 0):
        return EXIT_GUARD_FAILED
    
    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())