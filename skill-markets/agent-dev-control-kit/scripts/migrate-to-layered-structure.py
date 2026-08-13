#!/usr/bin/env python3
"""
迁移脚本：agent-dev-control-kit 三层架构重构

功能：
1. 备份原目录
2. 创建 registry/ 目录结构
3. 移动模板到 scaffolds/
4. 生成元数据
5. 清理重复目录
6. 更新索引

用法：
    python migrate-to-layered-structure.py [--dry-run] [--verbose] [--force]
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


class MigrationConfig:
    """迁移配置"""

    def __init__(self, base_path: Path, dry_run: bool = False, verbose: bool = False, force: bool = False):
        self.base_path = base_path
        self.dry_run = dry_run
        self.verbose = verbose
        self.force = force
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = base_path / f".backup_{self.timestamp}"

        self.presets_dir = base_path / "presets"
        self.registry_dir = base_path / "registry"
        self.scaffolds_dir = base_path / "scaffolds"
        self.template_project_dir = base_path / "template-project"


class Logger:
    """日志输出器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def info(self, msg: str):
        print(f"[INFO] {msg}")

    def verbose_log(self, msg: str):
        if self.verbose:
            print(f"[VERBOSE] {msg}")

    def warn(self, msg: str):
        print(f"[WARN] {msg}")

    def error(self, msg: str):
        print(f"[ERROR] {msg}", file=sys.stderr)

    def dry_run(self, msg: str):
        print(f"[DRY-RUN] {msg}")


class MigrationValidator:
    """迁移验证器"""

    def __init__(self, config: MigrationConfig, logger: Logger):
        self.config = config
        self.logger = logger

    def validate_prerequisites(self) -> Tuple[bool, List[str]]:
        """验证迁移前提条件"""
        errors = []

        if not self.config.presets_dir.exists():
            errors.append(f"presets/ 目录不存在: {self.config.presets_dir}")
        else:
            index_json = self.config.presets_dir / "_index.json"
            if not index_json.exists():
                errors.append(f"_index.json 不存在: {index_json}")

        if self.config.registry_dir.exists() and not self.config.force:
            errors.append(f"registry/ 已存在: {self.config.registry_dir}，使用 --force 覆盖")

        if self.config.scaffolds_dir.exists() and not self.config.force:
            errors.append(f"scaffolds/ 已存在: {self.config.scaffolds_dir}，使用 --force 覆盖")

        return len(errors) == 0, errors


class RegistryBuilder:
    """注册表构建器"""

    def __init__(self, config: MigrationConfig, logger: Logger):
        self.config = config
        self.logger = logger

    def build_registry(self, presets_data: Dict) -> bool:
        """构建 registry/ 目录结构"""
        if self.config.dry_run:
            self.logger.dry_run(f"将创建目录: {self.config.registry_dir}")
            self.logger.dry_run(f"将创建文件: {self.config.registry_dir / 'stacks.yaml'}")
            return True

        try:
            self.config.registry_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建目录: {self.config.registry_dir}")

            stacks_yaml = self._build_stacks_yaml(presets_data)
            stacks_path = self.config.registry_dir / "stacks.yaml"

            with open(stacks_path, 'w', encoding='utf-8') as f:
                yaml.dump(stacks_yaml, f, default_flow_style=False, allow_unicode=True)

            self.logger.info(f"创建文件: {stacks_path}")

            self._create_guard_templates()
            self._create_gate_templates()

            return True

        except Exception as e:
            self.logger.error(f"构建 registry 失败: {e}")
            return False

    def _build_stacks_yaml(self, presets_data: Dict) -> Dict:
        """从 _index.json 构建 stacks.yaml"""
        stacks = []

        for preset in presets_data.get('presets', []):
            stack_entry = {
                'id': preset['id'],
                'name': preset['name'],
                'description': preset['description'],
                'category': preset.get('category', 'language'),
                'tags': preset.get('tags', []),
                'scaffold': f"scaffolds/{preset['id']}",
                'guards': [
                    'test-coverage',
                    'api-contract'
                ],
                'gates': [
                    'pre-commit',
                    'pre-push'
                ]
            }
            stacks.append(stack_entry)
            self.logger.verbose_log(f"处理技术栈: {preset['id']}")

        return {
            'version': '1.0.0',
            'description': 'agent-dev-control-kit 技术栈注册表',
            'stacks': stacks
        }

    def _create_guard_templates(self):
        """创建 guards.yaml"""
        guards_yaml = {
            'version': '1.0.0',
            'description': '守卫注册表',
            'guards': [
                {
                    'id': 'test-coverage',
                    'name': '测试覆盖率守卫',
                    'description': '确保测试覆盖率达标',
                    'category': 'quality',
                    'config_schema': 'schemas/guards/test-coverage.json'
                },
                {
                    'id': 'api-contract',
                    'name': 'API 契约守卫',
                    'description': '验证 API 契约一致性',
                    'category': 'quality',
                    'config_schema': 'schemas/guards/api-contract.json'
                },
                {
                    'id': 'module-boundary',
                    'name': '模块边界守卫',
                    'description': '检查模块依赖关系',
                    'category': 'architecture',
                    'config_schema': 'schemas/guards/module-boundary.json'
                }
            ]
        }

        guards_path = self.config.registry_dir / "guards.yaml"
        with open(guards_path, 'w', encoding='utf-8') as f:
            yaml.dump(guards_yaml, f, default_flow_style=False, allow_unicode=True)

        self.logger.info(f"创建文件: {guards_path}")

    def _create_gate_templates(self):
        """创建 gates.yaml"""
        gates_yaml = {
            'version': '1.0.0',
            'description': '门禁注册表',
            'gates': [
                {
                    'id': 'pre-commit',
                    'name': '提交前门禁',
                    'description': '执行提交前检查',
                    'triggers': ['git commit'],
                    'guards': ['test-coverage', 'api-contract']
                },
                {
                    'id': 'pre-push',
                    'name': '推送前门禁',
                    'description': '执行推送前检查',
                    'triggers': ['git push'],
                    'guards': ['test-coverage', 'api-contract', 'module-boundary']
                }
            ]
        }

        gates_path = self.config.registry_dir / "gates.yaml"
        with open(gates_path, 'w', encoding='utf-8') as f:
            yaml.dump(gates_yaml, f, default_flow_style=False, allow_unicode=True)

        self.logger.info(f"创建文件: {gates_path}")


class ScaffoldMigrator:
    """脚手架迁移器"""

    def __init__(self, config: MigrationConfig, logger: Logger):
        self.config = config
        self.logger = logger

    def migrate_scaffolds(self, presets_data: Dict) -> bool:
        """迁移模板到 scaffolds/"""
        if self.config.dry_run:
            for preset in presets_data.get('presets', []):
                preset_id = preset['id']
                src = self.config.presets_dir / preset_id / "template"
                dst = self.config.scaffolds_dir / preset_id / "files"
                self.logger.dry_run(f"将移动: {src} -> {dst}")
            return True

        try:
            self.config.scaffolds_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建目录: {self.config.scaffolds_dir}")

            for preset in presets_data.get('presets', []):
                preset_id = preset['id']
                src = self.config.presets_dir / preset_id / "template"
                dst = self.config.scaffolds_dir / preset_id / "files"

                if not src.exists():
                    self.logger.warn(f"模板不存在，跳过: {src}")
                    continue

                dst.parent.mkdir(parents=True, exist_ok=True)

                if dst.exists():
                    if self.config.force:
                        self.logger.warn(f"目标已存在，强制覆盖: {dst}")
                        shutil.rmtree(dst)
                    else:
                        self.logger.warn(f"目标已存在，跳过: {dst}")
                        continue

                shutil.copytree(src, dst)
                self.logger.info(f"移动模板: {src} -> {dst}")

                self._create_scaffold_yaml(preset, dst.parent)

            return True

        except Exception as e:
            self.logger.error(f"迁移 scaffolds 失败: {e}")
            return False

    def _create_scaffold_yaml(self, preset: Dict, scaffold_dir: Path):
        """为每个 scaffold 创建 scaffold.yaml"""
        scaffold_yaml = {
            'version': '1.0.0',
            'id': preset['id'],
            'name': preset['name'],
            'description': preset['description'],
            'category': preset.get('category', 'language'),
            'tags': preset.get('tags', []),
            'files': 'files/',
            'variables': [
                {
                    'name': 'project_name',
                    'description': '项目名称',
                    'default': 'my-project',
                    'required': True
                },
                {
                    'name': 'author',
                    'description': '作者',
                    'default': '',
                    'required': False
                }
            ],
            'post_actions': [
                {
                    'type': 'script',
                    'path': 'scripts/init.sh',
                    'description': '初始化项目'
                }
            ]
        }

        scaffold_yaml_path = scaffold_dir / "scaffold.yaml"
        with open(scaffold_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(scaffold_yaml, f, default_flow_style=False, allow_unicode=True)

        self.logger.info(f"创建文件: {scaffold_yaml_path}")


class IndexUpdater:
    """索引更新器"""

    def __init__(self, config: MigrationConfig, logger: Logger):
        self.config = config
        self.logger = logger

    def update_index(self, presets_data: Dict) -> bool:
        """更新 presets/_index.yaml"""
        if self.config.dry_run:
            self.logger.dry_run(f"将创建文件: {self.config.presets_dir / '_index.yaml'}")
            return True

        try:
            index_yaml = {
                'version': '1.0.0',
                'description': 'agent-dev-control-kit 技术栈元数据索引',
                'presets': [
                    {
                        'id': preset['id'],
                        'name': preset['name'],
                        'description': preset['description'],
                        'scaffold': f"scaffolds/{preset['id']}",
                        'registry': 'registry/stacks.yaml'
                    }
                    for preset in presets_data.get('presets', [])
                ]
            }

            index_yaml_path = self.config.presets_dir / "_index.yaml"
            with open(index_yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(index_yaml, f, default_flow_style=False, allow_unicode=True)

            self.logger.info(f"创建文件: {index_yaml_path}")

            self._preserve_readme()

            return True

        except Exception as e:
            self.logger.error(f"更新索引失败: {e}")
            return False

    def _preserve_readme(self):
        """保留 presets/README.md"""
        readme_src = self.config.presets_dir / "README.md"
        if readme_src.exists():
            self.logger.verbose_log(f"README.md 已存在，保留: {readme_src}")


class TemplateProjectCleaner:
    """template-project 清理器"""

    def __init__(self, config: MigrationConfig, logger: Logger):
        self.config = config
        self.logger = logger

    def cleanup_template_project(self) -> bool:
        """清理重复的 template-project 目录"""
        if not self.config.template_project_dir.exists():
            self.logger.verbose_log("template-project/ 不存在，无需清理")
            return True

        if self.config.dry_run:
            self.logger.dry_run(f"将删除目录: {self.config.template_project_dir}")
            return True

        try:
            shutil.rmtree(self.config.template_project_dir)
            self.logger.info(f"删除重复目录: {self.config.template_project_dir}")
            return True
        except Exception as e:
            self.logger.error(f"清理 template-project 失败: {e}")
            return False


class BackupManager:
    """备份管理器"""

    def __init__(self, config: MigrationConfig, logger: Logger):
        self.config = config
        self.logger = logger

    def create_backup(self) -> bool:
        """创建备份"""
        if self.config.dry_run:
            self.logger.dry_run(f"将创建备份目录: {self.config.backup_dir}")
            return True

        try:
            self.config.backup_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建备份目录: {self.config.backup_dir}")

            dirs_to_backup = [
                ('presets', self.config.presets_dir),
                ('template-project', self.config.template_project_dir)
            ]

            for name, src_dir in dirs_to_backup:
                if src_dir.exists():
                    dst = self.config.backup_dir / name
                    shutil.copytree(src_dir, dst)
                    self.logger.info(f"备份: {src_dir} -> {dst}")

            return True

        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return False


class MigrationOrchestrator:
    """迁移编排器"""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.logger = Logger(config.verbose)

        self.validator = MigrationValidator(config, self.logger)
        self.backup_manager = BackupManager(config, self.logger)
        self.registry_builder = RegistryBuilder(config, self.logger)
        self.scaffold_migrator = ScaffoldMigrator(config, self.logger)
        self.index_updater = IndexUpdater(config, self.logger)
        self.cleaner = TemplateProjectCleaner(config, self.logger)

    def run(self) -> int:
        """执行迁移"""
        self.logger.info("=" * 60)
        self.logger.info("开始迁移: agent-dev-control-kit 三层架构重构")
        self.logger.info("=" * 60)

        if self.config.dry_run:
            self.logger.info("【DRY-RUN 模式】仅预览，不执行实际操作")

        ok, errors = self.validator.validate_prerequisites()
        if not ok:
            for err in errors:
                self.logger.error(err)
            return 1

        index_json_path = self.config.presets_dir / "_index.json"
        try:
            with open(index_json_path, 'r', encoding='utf-8') as f:
                presets_data = json.load(f)
            self.logger.info(f"加载配置: {index_json_path}")
        except Exception as e:
            self.logger.error(f"加载 _index.json 失败: {e}")
            return 1

        steps = [
            ("创建备份", lambda: self.backup_manager.create_backup()),
            ("构建 registry/", lambda: self.registry_builder.build_registry(presets_data)),
            ("迁移 scaffolds/", lambda: self.scaffold_migrator.migrate_scaffolds(presets_data)),
            ("更新索引", lambda: self.index_updater.update_index(presets_data)),
            ("清理重复目录", lambda: self.cleaner.cleanup_template_project())
        ]

        for step_name, step_func in steps:
            self.logger.info(f"\n步骤: {step_name}")
            if not step_func():
                self.logger.error(f"步骤失败: {step_name}")
                return 1

        self.logger.info("\n" + "=" * 60)
        self.logger.info("迁移完成")
        self.logger.info("=" * 60)

        if not self.config.dry_run:
            self.logger.info(f"备份位置: {self.config.backup_dir}")
            self.logger.info("请检查新结构后，手动删除备份目录")

        return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='agent-dev-control-kit 三层架构迁移脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python migrate-to-layered-structure.py --dry-run
  python migrate-to-layered-structure.py --verbose
  python migrate-to-layered-structure.py --force
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅预览，不执行实际操作'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='输出详细日志'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='强制覆盖已存在的目标文件'
    )

    parser.add_argument(
        '--base-path',
        type=str,
        default=None,
        help='基础路径（默认为脚本所在目录的上级目录）'
    )

    args = parser.parse_args()

    if args.base_path:
        base_path = Path(args.base_path).resolve()
    else:
        base_path = Path(__file__).parent.parent.resolve()

    if not base_path.exists():
        print(f"[ERROR] 基础路径不存在: {base_path}", file=sys.stderr)
        return 1

    config = MigrationConfig(
        base_path=base_path,
        dry_run=args.dry_run,
        verbose=args.verbose,
        force=args.force
    )

    orchestrator = MigrationOrchestrator(config)
    return orchestrator.run()


if __name__ == '__main__':
    sys.exit(main())