#!/usr/bin/env python3
"""
Skill Security Guard — 技能安全守卫

继承自 agent-dev-control-kit/skills/guard-control

检查维度: HIGH/MEDIUM/LOW 风险 + SHELL_EXEC + HTTP_INSECURE + HARDCODED_SECRET
触发时机: pre-commit (新建/修改技能时)

Usage:
    python scripts/skill-security-guard.py skill-markets/<skill_name>

注意: 与 skill-acceptance/scripts/verify.py 的关系
  - verify.py: 6 项检查的元数据合规准入(含 security 子调用)
  - 本脚本: 纯安全单点检查(更细的硬编码密钥判定)
  - 互补,非冗余
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from typing import Dict, List

SECURITY_SCAN_SCRIPT = Path(__file__).parent.parent / "skill-markets" / "trae-security-review" / "scripts" / "scan_skills_dir.py"

FORBIDDEN_PATTERNS = [
    (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'HARDCODED_SECRET', '硬编码密码'),
    (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', 'HARDCODED_SECRET', '硬编码 API Key'),
    (r'secret\s*=\s*[\'"][^\'"]+[\'"]', 'HARDCODED_SECRET', '硬编码密钥'),
]

WHITELIST_FILES = [
    'risk-patterns.md',
    'local-usage.md',
    'api-inference.md',
]


def run_security_guard(skill_path: str) -> Dict:
    """
    执行技能安全守卫

    Args:
        skill_path: 技能目录路径

    Returns:
        {
            'status': 'PASS' | 'WARN' | 'BLOCK',
            'message': str,
            'high_count': int,
            'medium_count': int,
            'low_count': int,
            'details': List[str]
        }
    """
    skill_dir = Path(skill_path)
    if not skill_dir.exists():
        return {
            'status': 'BLOCK',
            'message': f'技能目录不存在: {skill_path}',
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'details': []
        }

    if not SECURITY_SCAN_SCRIPT.exists():
        return {
            'status': 'BLOCK',
            'message': f'安全扫描脚本不存在: {SECURITY_SCAN_SCRIPT}',
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'details': []
        }

    result = subprocess.run(
        [
            'python',
            str(SECURITY_SCAN_SCRIPT),
            str(skill_dir),
            'auto_reports'
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {
            'status': 'BLOCK',
            'message': f'安全扫描执行失败: {result.stderr}',
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'details': []
        }

    high_count, medium_count, low_count = parse_scan_result(result.stdout)

    real_high = check_real_risks(skill_dir)

    if real_high > 0:
        return {
            'status': 'BLOCK',
            'message': f'发现 {real_high} 个真实 HIGH 风险',
            'high_count': real_high,
            'medium_count': medium_count,
            'low_count': low_count,
            'details': extract_real_high_details(skill_dir)
        }

    if high_count > 0:
        return {
            'status': 'WARN',
            'message': f'发现 {high_count} 个 HIGH 风险（文档引用，建议确认）',
            'high_count': high_count,
            'medium_count': medium_count,
            'low_count': low_count,
            'details': []
        }

    if medium_count > 3:
        return {
            'status': 'WARN',
            'message': f'MEDIUM 风险过多: {medium_count}（阈值 3）',
            'high_count': high_count,
            'medium_count': medium_count,
            'low_count': low_count,
            'details': []
        }

    return {
        'status': 'PASS',
        'message': '安全扫描通过',
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
        'details': []
    }


def parse_scan_result(stdout: str) -> tuple:
    """解析扫描结果"""
    high_match = re.search(r'HIGH:\s*(\d+)', stdout)
    medium_match = re.search(r'MEDIUM:\s*(\d+)', stdout)
    low_match = re.search(r'LOW:\s*(\d+)', stdout)

    high_count = int(high_match.group(1)) if high_match else 0
    medium_count = int(medium_match.group(1)) if medium_match else 0
    low_count = int(low_match.group(1)) if low_match else 0

    return high_count, medium_count, low_count


def check_real_risks(skill_dir: Path) -> int:
    """检查真实 HIGH 风险（排除文档引用）"""
    real_high = 0

    for file_path in skill_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.py', '.js', '.mjs', '.ts', '.sh', '.ps1']:
            content = file_path.read_text(errors='ignore')

            for pattern, risk_type, desc in FORBIDDEN_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    if not is_whitelisted(file_path):
                        real_high += 1

    return real_high


def is_whitelisted(file_path: Path) -> bool:
    """检查文件是否在白名单"""
    for whitelist_file in WHITELIST_FILES:
        if whitelist_file in file_path.parts:
            return True
    return False


def extract_real_high_details(skill_dir: Path) -> List[str]:
    """提取真实 HIGH 风险详情"""
    details = []

    for file_path in skill_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.py', '.js', '.mjs', '.ts', '.sh', '.ps1']:
            content = file_path.read_text(errors='ignore')

            for pattern, risk_type, desc in FORBIDDEN_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches and not is_whitelisted(file_path):
                    details.append(f"{file_path.relative_to(skill_dir)}: {desc} ({len(matches)} 处)")

    return details


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python scripts/skill-security-guard.py skill-markets/<skill_name>")
        sys.exit(1)

    skill_path = sys.argv[1]
    result = run_security_guard(skill_path)

    print(json.dumps(result, indent=2))

    if result['status'] == 'BLOCK':
        sys.exit(1)
    elif result['status'] == 'WARN':
        sys.exit(2)
    else:
        sys.exit(0)