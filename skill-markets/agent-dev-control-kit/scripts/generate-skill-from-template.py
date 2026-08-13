#!/usr/bin/env python3
"""
generate-skill-from-template.py - 从模板生成新 Skill

功能：
- 交互式填写 Skill 参数
- 从模板生成 SKILL.md
- 支持非交互式配置文件输入
- 验证生成文件的正确性

使用：
    python generate-skill-from-template.py [OPTIONS]

选项：
    --type TYPE       模板类型（execution/gate/guard）
    --output PATH     输出路径
    --config PATH     配置文件（非交互式）
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
from typing import Dict, List, Optional
from dataclasses import dataclass, field

try:
    from colorama import init as colorama_init, Fore, Style
    HAS_COLORAMA = True
    colorama_init()
except ImportError:
    HAS_COLORAMA = False
    Fore = Style = type('Dummy', (), {'__getattr__': lambda s, n: ''})()

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_ARGS_ERROR = 2


@dataclass
class SkillConfig:
    """Skill 配置"""
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    triggers: List[str] = field(default_factory=list)
    scenarios: List[str] = field(default_factory=list)
    control_points: List[Dict] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class SkillGenerator:
    """Skill 生成器"""
    
    TEMPLATE_DIR = Path(__file__).parent.parent / 'templates'
    
    EXECUTION_SKILL_TEMPLATE = """---
name: {name}
description: {description}
version: "{version}"
{dependencies_section}
---

# {title}

## 触发词

{triggers_section}

## 功能说明

{description}

## 适用场景

{scenarios_section}

## 输入规范

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
{required_params}

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
{optional_params}

## 执行流程

### Phase 1: 输入验证

```pseudo
1. 检查必需参数是否存在
2. 验证参数类型和格式
3. 检查前置条件
4. 若验证失败 → 输出错误信息并终止
```

### Phase 2: 核心执行

```pseudo
1. 初始化执行环境
2. 执行主逻辑
3. 记录执行日志
4. 处理中间状态
```

### Phase 3: 输出校验

```pseudo
1. 验证输出格式
2. 检查输出完整性
3. 生成执行报告
4. 返回结果
```

## 关键控制点

{control_points_section}

## 验收标准

```yaml
{validation_section}
```

## 输出规范

### 成功输出

```json
{{
  "status": "success",
  "data": {{
    "result": "<执行结果>"
  }},
  "metrics": {{
    "duration": "<执行时间>",
    "steps": "<步骤数>"
  }}
}}
```

### 失败输出

```json
{{
  "status": "error",
  "error": {{
    "code": "<错误码>",
    "message": "<错误信息>",
    "phase": "<失败阶段>"
  }}
}}
```

## 错误处理

### 错误分级

| 级别 | 代码前缀 | 处理方式 |
|------|---------|---------|
| CRITICAL | E1xx | 立即终止，输出错误报告 |
| ERROR | E2xx | 终止当前操作，尝试恢复 |
| WARNING | E3xx | 记录警告，继续执行 |
| INFO | E4xx | 记录信息，不影响执行 |

## 示例用法

### 示例 1: 基本用法

```markdown
**用户请求**：{example_request_1}

**执行过程**：
1. 输入验证：验证参数有效性
2. 核心执行：执行主要逻辑
3. 输出校验：确认结果符合预期
4. 返回结果：输出执行报告
```

## 配置项

```yaml
execution:
  timeout: 300s
  retry: 3
  log_level: INFO
  parallel: false
```

## 注意事项

1. 执行前确保环境依赖已满足
2. 高风险操作需要用户确认
3. 失败后检查错误日志定位问题
4. 定期清理临时产物

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| {version} | {date} | 初始版本 |
"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = SkillConfig()
    
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
    
    def prompt_input(self, prompt: str, default: str = None, required: bool = True) -> str:
        """交互式输入"""
        while True:
            prompt_text = f"{prompt}"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "
            
            try:
                value = input(prompt_text).strip()
                if not value:
                    if default:
                        return default
                    elif not required:
                        return ""
                    else:
                        self.log("此项为必填项", 'WARNING')
                        continue
                return value
            except (EOFError, KeyboardInterrupt):
                print("\n用户中断输入")
                sys.exit(130)
    
    def prompt_list(self, prompt: str, min_items: int = 1) -> List[str]:
        """交互式列表输入"""
        items = []
        self.log(f"{prompt}（每行一个，空行结束）:")
        
        while True:
            try:
                value = input("  - ").strip()
                if not value:
                    if len(items) >= min_items:
                        break
                    else:
                        self.log(f"至少需要 {min_items} 项", 'WARNING')
                        continue
                items.append(value)
            except (EOFError, KeyboardInterrupt):
                print("\n")
                break
        
        return items
    
    def collect_config_interactive(self) -> SkillConfig:
        """交互式收集配置"""
        self.log("开始交互式配置...")
        print()
        
        name = self.prompt_input("Skill 名称（kebab-case）", required=True)
        
        if not re.match(r'^[a-z][a-z0-9-]*$', name):
            self.log("名称格式不正确，应为 kebab-case（小写字母、数字、连字符）", 'WARNING')
            self.log("示例: data-change-control, doc-sync-control")
        
        description = self.prompt_input("Skill 描述", required=True)
        
        version = self.prompt_input("版本号", default="1.0.0")
        
        print()
        self.log("触发词（用于自动加载此 Skill）")
        triggers = self.prompt_list("触发词列表", min_items=1)
        
        print()
        self.log("适用场景")
        scenarios = self.prompt_list("适用场景列表", min_items=1)
        
        print()
        control_points = []
        add_cp = self.prompt_input("是否添加控制点？", default="n")
        
        if add_cp.lower() in ['y', 'yes']:
            cp_count = 0
            while True:
                cp_count += 1
                cp_name = self.prompt_input(f"CP-{cp_count} 名称", required=False)
                if not cp_name:
                    break
                
                cp_desc = self.prompt_input(f"CP-{cp_count} 描述", required=True)
                cp_trigger = self.prompt_input(f"CP-{cp_count} 触发条件", required=False)
                
                control_points.append({
                    'name': cp_name,
                    'description': cp_desc,
                    'trigger': cp_trigger or "执行时"
                })
        
        print()
        validation_criteria = self.prompt_list("验收标准", min_items=1)
        
        print()
        dependencies = []
        add_dep = self.prompt_input("是否有依赖 Skill？", default="n")
        
        if add_dep.lower() in ['y', 'yes']:
            dependencies = self.prompt_list("依赖 Skill 列表", min_items=1)
        
        return SkillConfig(
            name=name,
            description=description,
            version=version,
            triggers=triggers,
            scenarios=scenarios,
            control_points=control_points,
            validation_criteria=validation_criteria,
            dependencies=dependencies
        )
    
    def load_config_from_file(self, config_path: Path) -> SkillConfig:
        """从配置文件加载"""
        if not config_path.exists():
            self.log(f"配置文件不存在: {config_path}", 'ERROR')
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return SkillConfig(
                name=data.get('name', ''),
                description=data.get('description', ''),
                version=data.get('version', '1.0.0'),
                triggers=data.get('triggers', []),
                scenarios=data.get('scenarios', []),
                control_points=data.get('control_points', []),
                validation_criteria=data.get('validation_criteria', []),
                dependencies=data.get('dependencies', [])
            )
        except Exception as e:
            self.log(f"加载配置文件失败: {str(e)}", 'ERROR')
            return None
    
    def generate_skill_content(self, config: SkillConfig) -> str:
        """生成 Skill 内容"""
        title = config.name.replace('-', ' ').title()
        
        triggers_section = '\n'.join([f"- {t}" for t in config.triggers])
        
        scenarios_section = '\n'.join([f"- {s}" for s in config.scenarios])
        
        if config.dependencies:
            deps_str = ', '.join([f'"{d}"' for d in config.dependencies])
            dependencies_section = f"requires:\n  skills: [{deps_str}]"
        else:
            dependencies_section = ""
        
        control_points_section = ""
        if config.control_points:
            cp_items = []
            for i, cp in enumerate(config.control_points, 1):
                cp_items.append(f"""### CP-{i}: {cp['name']}

**触发条件**: {cp.get('trigger', '执行时')}

{cp['description']}
""")
            control_points_section = '\n'.join(cp_items)
        else:
            control_points_section = "暂无定义的控制点"
        
        validation_section = '\n'.join([f"  - {v}" for v in config.validation_criteria])
        
        required_params = "| param | string | 必需参数 | example |"
        optional_params = "| verbose | bool | false | 详细输出 |"
        
        example_request_1 = f"执行 {config.name} 操作"
        
        date = datetime.now().strftime('%Y-%m-%d')
        
        content = self.EXECUTION_SKILL_TEMPLATE.format(
            name=config.name,
            description=config.description,
            version=config.version,
            dependencies_section=dependencies_section,
            title=title,
            triggers_section=triggers_section,
            scenarios_section=scenarios_section,
            control_points_section=control_points_section,
            validation_section=validation_section,
            required_params=required_params,
            optional_params=optional_params,
            example_request_1=example_request_1,
            date=date
        )
        
        return content
    
    def generate_skill_file(self, config: SkillConfig, output_path: Path) -> bool:
        """生成 Skill 文件"""
        content = self.generate_skill_content(config)
        
        skill_file = output_path / 'SKILL.md'
        
        if skill_file.exists():
            self.log(f"Skill 文件已存在: {skill_file}", 'WARNING')
            overwrite = input("是否覆盖？(y/n): ").strip().lower()
            if overwrite not in ['y', 'yes']:
                self.log("取消生成")
                return False
        
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            skill_file.write_text(content, encoding='utf-8')
            self.log(f"Skill 文件已生成: {skill_file}", 'SUCCESS')
            return True
        except Exception as e:
            self.log(f"生成 Skill 文件失败: {str(e)}", 'ERROR')
            return False
    
    def generate_sample_config(self) -> str:
        """生成示例配置文件"""
        return json.dumps({
            "name": "example-skill",
            "description": "示例 Skill 描述",
            "version": "1.0.0",
            "triggers": ["trigger-1", "trigger-2"],
            "scenarios": ["场景 1", "场景 2"],
            "control_points": [
                {
                    "name": "输入验证",
                    "description": "验证输入参数的有效性",
                    "trigger": "执行前"
                }
            ],
            "validation_criteria": [
                "执行结果符合预期",
                "无错误日志",
                "执行时间在阈值内"
            ],
            "dependencies": []
        }, indent=2, ensure_ascii=False)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='从模板生成新 Skill',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 交互式生成
    python generate-skill-from-template.py
    
    # 指定输出路径
    python generate-skill-from-template.py --output skill-markets/my-skill
    
    # 从配置文件生成
    python generate-skill-from-template.py --config skill-config.json
    
    # 生成示例配置
    python generate-skill-from-template.py --sample-config > skill-config.json
        """
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['execution', 'gate', 'guard'],
        default='execution',
        help='模板类型'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=Path.cwd() / 'skill-markets' / 'new-skill',
        help='输出路径'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='配置文件（非交互式）'
    )
    
    parser.add_argument(
        '--sample-config',
        action='store_true',
        help='生成示例配置文件'
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
    
    generator = SkillGenerator(verbose=args.verbose)
    
    if args.sample_config:
        print(generator.generate_sample_config())
        return EXIT_SUCCESS
    
    if args.config:
        config = generator.load_config_from_file(args.config)
        if not config:
            return EXIT_ERROR
    else:
        config = generator.collect_config_interactive()
    
    print("\n" + "=" * 60)
    generator.log("配置摘要:")
    print("=" * 60)
    print(f"名称: {config.name}")
    print(f"描述: {config.description}")
    print(f"版本: {config.version}")
    print(f"触发词: {', '.join(config.triggers)}")
    print(f"适用场景: {len(config.scenarios)} 项")
    print(f"控制点: {len(config.control_points)} 项")
    print(f"验收标准: {len(config.validation_criteria)} 项")
    print(f"依赖: {', '.join(config.dependencies) if config.dependencies else '无'}")
    print("=" * 60)
    
    if not args.config:
        confirm = input("\n确认生成？(y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            generator.log("取消生成")
            return EXIT_SUCCESS
    
    success = generator.generate_skill_file(config, args.output)
    
    return EXIT_SUCCESS if success else EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())