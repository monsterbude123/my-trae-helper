#!/usr/bin/env python3
"""
init-control-kit.py - 初始化 Agent 开发控制体系（支持技术栈选型）

功能：
- 检查必要目录和文件
- 生成初始配置文件
- 创建标准目录结构
- 验证环境依赖
- 加载和应用技术栈脚手架（用户级 > 项目级 > 内置）

使用：
    python init-control-kit.py [OPTIONS]

选项：
    --target PATH           目标目录（默认：当前目录）
    --force                 强制覆盖已有配置
    --check-only            仅检查不创建
    --verbose               详细输出模式

    --stack ID              技术栈选型 (nodejs / python / go / java-maven / ...)
    --scaffold, -s PATH     指定脚手架目录（如 nodejs, rust-react, nextjs-fullstack）
    --list-stacks           列出所有可用选型
    --add-stack PATH        从本地路径添加新选型到用户级目录
    --interactive, -i       交互式选择选型
    --auto-detect           自动检测已有项目的技术栈
    --scaffolds-dir PATH    自定义脚手架目录（默认使用内置）
    --user-scaffolds-dir PATH 用户级脚手架目录（默认 ~/.agent-dev-control-kit/scaffolds）

依赖：
    - Python 3.8+
    - colorama（可选，用于彩色输出）
    - PyYAML（可选，用于读取 scaffold.yaml / registry/stacks.yaml）
"""

import os
import sys
import json
import shutil
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

try:
    from colorama import init as colorama_init, Fore, Style
    HAS_COLORAMA = True
    colorama_init()
except ImportError:
    HAS_COLORAMA = False
    Fore = Style = type('Dummy', (), {'__getattr__': lambda s, n: ''})()

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_ARGS_ERROR = 2
EXIT_CONFIG_ERROR = 3
EXIT_USER_INTERRUPT = 10

DEFAULT_USER_SCAFFOLDS_DIR = Path.home() / '.agent-dev-control-kit' / 'scaffolds'

FALLBACK_DETECTION_RULES: Dict[str, List[str]] = {
    'nodejs': ['package.json'],
    'python': ['pyproject.toml', 'requirements.txt', 'setup.py', 'Pipfile'],
    'go': ['go.mod', 'go.sum'],
    'java-maven': ['pom.xml'],
    'java-gradle': ['build.gradle', 'settings.gradle'],
}


def find_scaffold(stack_id: str, scaffold_dir: Optional[Path] = None) -> Optional[Path]:
    """
    三层优先级查找脚手架目录：
    1. 用户指定目录（--scaffold 参数）
    2. 用户级 ~/.agent-dev-control-kit/scaffolds/<id>/
    3. 项目级 ./scaffolds/<id>/
    4. 内置 scaffolds/<id>/

    返回：脚手架目录路径，未找到返回 None
    """
    builtin_scaffolds = Path(__file__).resolve().parent.parent / 'scaffolds'
    
    search_paths = []
    
    if scaffold_dir:
        explicit_path = Path(scaffold_dir)
        if explicit_path.is_dir():
            if explicit_path.name == stack_id or (explicit_path / 'scaffold.yaml').exists():
                return explicit_path
            explicit_subdir = explicit_path / stack_id
            if explicit_subdir.is_dir():
                return explicit_subdir
    
    user_scaffolds = DEFAULT_USER_SCAFFOLDS_DIR / stack_id
    if user_scaffolds.is_dir():
        search_paths.append(user_scaffolds)
    
    project_scaffolds = Path.cwd() / 'scaffolds' / stack_id
    if project_scaffolds.is_dir():
        search_paths.append(project_scaffolds)
    
    builtin_path = builtin_scaffolds / stack_id
    if builtin_path.is_dir():
        search_paths.append(builtin_path)
    
    for path in search_paths:
        if (path / 'scaffold.yaml').exists() or (path / 'files').is_dir():
            return path
    
    return None


def load_scaffold_metadata(scaffold_path: Path) -> Dict[str, Any]:
    """
    从 scaffold.yaml 读取脚手架元数据。
    若无 scaffold.yaml，返回最小元数据。
    """
    scaffold_yaml = scaffold_path / 'scaffold.yaml'
    
    if scaffold_yaml.exists():
        if not HAS_YAML:
            print(f"⚠️  PyYAML 未安装，无法读取 {scaffold_yaml}")
            return {'id': scaffold_path.name, 'name': scaffold_path.name}
        try:
            with scaffold_yaml.open('r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  解析 {scaffold_yaml} 失败: {e}")
            metadata = {}
    else:
        metadata = {}
    
    metadata.setdefault('id', scaffold_path.name)
    metadata.setdefault('name', metadata.get('id'))
    metadata.setdefault('description', '')
    metadata.setdefault('variables', {})
    metadata.setdefault('detection', {})
    
    if not isinstance(metadata.get('detection'), dict):
        metadata['detection'] = {'files': list(metadata.get('detection', []))}
    
    metadata['_scaffold_path'] = str(scaffold_path)
    metadata['_has_files'] = (scaffold_path / 'files').is_dir()
    
    return metadata


def copy_scaffold_files(files_dir: Path, target_dir: Path, force: bool, verbose: bool) -> Tuple[int, int]:
    """
    复制脚手架 files/ 目录内容到目标目录。
    返回：(copied_count, skipped_count)
    """
    if not files_dir.exists() or not files_dir.is_dir():
        return (0, 0)
    
    copied = 0
    skipped = 0
    
    for src_file in files_dir.rglob('*'):
        if not src_file.is_file():
            continue
        rel_path = src_file.relative_to(files_dir)
        dest_path = target_dir / rel_path
        
        if dest_path.exists() and not force:
            skipped += 1
            if verbose:
                print(f"  ⏭  已存在，跳过: {rel_path}")
            continue
        
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_path)
            copied += 1
            mark = '✅' if not dest_path.exists() else '🔄'
            print(f"  {mark} Created: {rel_path}")
        except Exception as e:
            print(f"  🛑 复制失败 {rel_path}: {e}")
    
    return (copied, skipped)


def render_templates(target_dir: Path, metadata: Dict[str, Any], verbose: bool = False) -> int:
    """
    渲染目标目录中的模板变量（如 {{PROJECT_NAME}}）。
    返回：渲染文件数
    """
    variables = metadata.get('variables', {})
    if not variables:
        return 0
    
    variables.setdefault('PROJECT_NAME', target_dir.name)
    variables.setdefault('PROJECT_ID', target_dir.name.lower().replace('-', '_'))
    variables.setdefault('TIMESTAMP', datetime.now().strftime('%Y-%m-%d'))
    
    rendered = 0
    
    for file_path in target_dir.rglob('*'):
        if not file_path.is_file():
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, IOError):
            continue
        
        new_content = content
        for var_name, var_value in variables.items():
            pattern = '{{' + var_name + '}}'
            if pattern in new_content:
                new_content = new_content.replace(pattern, str(var_value))
        
        if new_content != content:
            try:
                file_path.write_text(new_content, encoding='utf-8')
                rendered += 1
                if verbose:
                    print(f"  🔧 渲染变量: {file_path.relative_to(target_dir)}")
            except Exception as e:
                print(f"  ⚠️  渲染失败 {file_path}: {e}")
    
    return rendered


def apply_stack_preset(stack_id: str, target_dir: Path,
                       scaffold_dir: Optional[Path] = None,
                       force: bool = False, verbose: bool = False) -> bool:
    """
    根据选型应用脚手架到目标目录。

    步骤：
    1. 查找脚手架（三层优先级）
    2. 读取 scaffold.yaml 获取元数据
    3. 复制 files/ 目录内容
    4. 渲染模板变量
    5. 注入必需的脚本（绝不使用 echo-skip 占位）
    """
    scaffold_path = find_scaffold(stack_id, scaffold_dir)

    if not scaffold_path:
        print(f"🛑 未找到脚手架 '{stack_id}'")
        print("  搜索路径：")
        print(f"    - 用户级: {DEFAULT_USER_SCAFFOLDS_DIR / stack_id}")
        print(f"    - 项目级: {Path.cwd() / 'scaffolds' / stack_id}")
        builtin_scaffolds = Path(__file__).resolve().parent.parent / 'scaffolds'
        print(f"    - 内置:   {builtin_scaffolds / stack_id}")
        return False

    print(f"📦 使用脚手架: {scaffold_path}")

    metadata = load_scaffold_metadata(scaffold_path)
    print(f"📋 选型名称: {metadata.get('name', stack_id)}")
    if metadata.get('description'):
        print(f"   {metadata['description']}")

    files_dir = scaffold_path / 'files'
    if not files_dir.exists() or not files_dir.is_dir():
        print(f"⚠️  脚手架无 files/ 目录: {scaffold_path}")
        return True

    print(f"\n📁 复制脚手架文件...")
    copied, skipped = copy_scaffold_files(files_dir, target_dir, force, verbose)

    print(f"\n🔧 渲染模板变量...")
    rendered = render_templates(target_dir, metadata, verbose)

    print(f"\n📋 检查必需脚本清单...")
    injected = ensure_required_scripts(target_dir, metadata, force=force, verbose=verbose)

    print(f"\n📊 脚手架应用摘要:")
    print(f"   - 复制文件: {copied}")
    print(f"   - 跳过文件: {skipped}")
    print(f"   - 渲染变量: {rendered}")
    print(f"   - 注入脚本: {injected}")

    return True


# Patterns that mark a script body as an echo-skip placeholder
_ECHO_SKIP_RE = re.compile(
    r"^\s*echo\s+['\"]?(?:skip|not\s+config|skipping|no\s+\w+\s+configured)",
    re.IGNORECASE,
)


def _is_echo_skip(body: str) -> bool:
    """True if the script body is a no-op echo placeholder."""
    if not body:
        return True
    s = body.strip()
    if s in (':', 'true', 'false'):
        return True
    return bool(_ECHO_SKIP_RE.match(s))


# Real (non-skip) implementations for placeholder injection
_NODEJS_PLACEHOLDERS = {
    'lint':          "eslint src/ tests/",
    'typecheck':     "node --check src/index.js",
    'test:unit':     "node --test tests/unit",
    'test':          "node --test tests/unit tests/integration",
    'test:integration': "node --test tests/integration",
    'test:coverage': "node --test --experimental-test-coverage tests/",
    'build':         "node src/index.js --version",
}

_PYTHON_REQUIRED_FILES_HINTS = {
    'pyproject.toml': "Add [build-system] + [project.scripts] sections.",
    'ruff.toml':      "Configure ruff linter rules.",
    'mypy.ini':       "Configure mypy strict mode for src/.",
}


def _ensure_nodejs_scripts(target_dir: Path, required: Dict[str, List[str]], force: bool, verbose: bool) -> int:
    """Inject missing required scripts into package.json without echo-skip bodies."""
    pkg = target_dir / 'package.json'
    if not pkg.exists():
        print("    ⚠️  package.json missing — skipping npm script injection")
        return 0
    try:
        with pkg.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"    🛑 parse package.json failed: {e}")
        return 0

    scripts = data.setdefault('scripts', {})
    injected = 0

    for phase in ('pre_commit', 'pre_push'):
        for name in (required.get(phase) or []):
            if name in scripts and not _is_echo_skip(scripts[name]):
                continue
            placeholder = _NODEJS_PLACEHOLDERS.get(name)
            if placeholder is None:
                print(f"    ⚠️  no safe placeholder for required script '{name}' — leave manual")
                continue
            old = scripts.get(name)
            if old is not None and _is_echo_skip(old):
                print(f"    🔁 replace echo-skip: scripts.{name} -> {placeholder!r}")
            else:
                print(f"    ➕ inject required script: scripts.{name} -> {placeholder!r}")
                if verbose:
                    print(f"          (was missing)")
            scripts[name] = placeholder
            injected += 1

    if injected > 0:
        with pkg.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
    return injected


def _ensure_python_files(target_dir: Path, required_files: List[str], verbose: bool) -> int:
    """Ensure required Python project files exist (with safe starter content, never echo-skip)."""
    injected = 0
    for fname in required_files:
        path = target_dir / fname
        if path.exists():
            continue
        hint = _PYTHON_REQUIRED_FILES_HINTS.get(fname, '')
        print(f"    ➕ create stub: {fname}  ({hint})")
        if fname == 'pyproject.toml':
            path.write_text(
                '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n\n'
                '[project]\nname = "placeholder"\nversion = "0.0.0"\nrequires-python = ">=3.10"\n\n'
                '[tool.ruff]\nline-length = 100\ntarget-version = "py310"\n\n'
                '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n',
                encoding='utf-8',
            )
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {fname} — placeholder, replace with real config\n", encoding='utf-8')
        injected += 1
    return injected


def ensure_required_scripts(target_dir: Path, metadata: Dict[str, Any], force: bool = False, verbose: bool = False) -> int:
    """
    确保 target_dir 中所有必需的脚本 / 文件存在；缺失则注入合理占位（绝不用 echo 跳过）。

    Returns: number of injected/fixed items.
    """
    required = metadata.get('required_scripts') or {}
    if not isinstance(required, dict):
        return 0

    injected = 0
    sid = (metadata.get('id') or '').lower()

    if sid == 'nodejs':
        injected += _ensure_nodejs_scripts(target_dir, required, force=force, verbose=verbose)
    elif sid == 'python':
        required_files = (metadata.get('required_files') or [])
        injected += _ensure_python_files(target_dir, required_files, verbose=verbose)
    elif sid in ('go', 'java-maven'):
        # Toolchain-based: report missing required files but don't inject.
        for f in (metadata.get('required_files') or []):
            if not (target_dir / f).exists():
                print(f"    ⚠️  required file missing: {f} (user must create)")

    if injected == 0:
        print("    ✓ all required scripts already present (no echo-skip detected)")
    return injected


def load_preset(preset_dir: Path, source_label: str) -> Optional[Dict]:
    """从单个 scaffold 目录加载选型定义。"""
    if not preset_dir.is_dir():
        return None
    
    scaffold_yaml = preset_dir / 'scaffold.yaml'
    preset: Optional[Dict] = None
    
    if scaffold_yaml.exists():
        if not HAS_YAML:
            return None
        try:
            with scaffold_yaml.open('r', encoding='utf-8') as f:
                preset = yaml.safe_load(f) or {}
        except Exception:
            return None
    else:
        preset_id = preset_dir.name
        preset = {
            'id': preset_id,
            'name': preset_id,
            'description': f'Auto-discovered scaffold: {preset_id}',
        }
    
    preset.setdefault('id', preset_dir.name)
    preset.setdefault('name', preset['id'])
    preset.setdefault('description', '')
    preset.setdefault('detection', {})
    
    if not isinstance(preset['detection'], dict):
        preset['detection'] = {'files': list(preset['detection'])}
    
    preset['_source'] = str(preset_dir)
    preset['_source_label'] = source_label
    preset['_has_template'] = (preset_dir / 'files').is_dir()
    
    return preset


def _load_presets_from_registry(scaffolds_root: Path, source_label: str) -> Dict[str, Dict]:
    """从 registry/stacks.yaml 加载选型注册表。"""
    presets: Dict[str, Dict] = {}
    
    registry_file = scaffolds_root / 'registry' / 'stacks.yaml'
    if registry_file.exists():
        if not HAS_YAML:
            print(f"⚠️  PyYAML 未安装，跳过 {registry_file}")
            return presets
        try:
            with registry_file.open('r', encoding='utf-8') as f:
                registry = yaml.safe_load(f) or {}
            stacks = registry.get('stacks', [])
            for entry in stacks:
                stack_id = entry.get('id') or entry.get('name')
                if not stack_id:
                    continue
                scaffold_dir = scaffolds_root / stack_id
                preset = load_preset(scaffold_dir, source_label)
                if preset:
                    for k in ('name', 'description', 'category', 'tags'):
                        if entry.get(k) is not None:
                            preset[k] = entry[k]
                    presets[preset['id']] = preset
            return presets
        except Exception as e:
            print(f"⚠️  解析 {registry_file} 失败，回退到目录扫描: {e}")
    
    for preset_dir in scaffolds_root.iterdir():
        if not preset_dir.is_dir():
            continue
        if preset_dir.name.startswith('_') or preset_dir.name.startswith('.'):
            continue
        if preset_dir.name == 'registry':
            continue
        preset = load_preset(preset_dir, source_label)
        if preset:
            presets[preset['id']] = preset
    
    return presets


def load_presets(scaffolds_dir: Optional[Path] = None,
                 user_scaffolds_dir: Optional[Path] = None) -> Dict[str, Dict]:
    """加载所有可用选型，优先级：用户级 > 项目级 > 内置。"""
    presets: Dict[str, Dict] = {}
    
    builtin_dir = Path(__file__).resolve().parent.parent / 'scaffolds'
    builtin = _load_presets_from_registry(builtin_dir, 'built-in')
    presets.update(builtin)
    
    if scaffolds_dir:
        custom = _load_presets_from_registry(Path(scaffolds_dir), 'project')
        presets.update(custom)
    
    if user_scaffolds_dir:
        user_dir = Path(user_scaffolds_dir).expanduser()
        user = _load_presets_from_registry(user_dir, 'user')
        presets.update(user)
    
    return presets


def list_stacks(presets: Dict[str, Dict]) -> None:
    """打印所有可用选型。"""
    if not presets:
        print("⚠️  未发现任何选型")
        return
    
    print("\n=== Available Tech Stacks ===\n")
    for preset_id, preset in presets.items():
        source_label = preset.get('_source_label', 'built-in')
        icon = '🔧 User' if source_label == 'user' else (
            '📁 Project' if source_label == 'project' else '📦 Built-in'
        )
        print(f"{icon} {preset.get('name', preset_id)} ({preset_id})")
        if preset.get('description'):
            print(f"    {preset['description']}")
        toolchain = preset.get('toolchain') or {}
        if isinstance(toolchain, dict):
            runtime = toolchain.get('runtime')
            runtime_version = toolchain.get('runtime_version')
            if runtime:
                version = f" {runtime_version}" if runtime_version else ''
                print(f"    Runtime: {runtime}{version}")
        detection = preset.get('detection') or {}
        if isinstance(detection, dict) and detection.get('files'):
            print(f"    Detection: {', '.join(detection['files'])}")
        elif isinstance(detection, list) and detection:
            print(f"    Detection: {', '.join(detection)}")
        template_mark = '✓ files/' if preset.get('_has_template') else '✗ no files'
        print(f"    [{template_mark}]")
        print()


def custom_stack_interactive() -> Optional[str]:
    """交互式添加新选型。"""
    print("\n=== Add Custom Stack ===")
    try:
        src = input("Source scaffold directory path (or 'cancel'): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    if not src or src.lower() in ('cancel', 'q', 'quit'):
        return None
    target = add_custom_stack(src, DEFAULT_USER_SCAFFOLDS_DIR)
    return target


def interactive_select(presets: Dict[str, Dict]) -> Optional[str]:
    """交互式选择选型。"""
    if not presets:
        print("⚠️  没有可选的选型")
        return None
    
    print("\n=== Select Your Tech Stack ===\n")
    ids = list(presets.keys())
    choices = [f"{presets[i].get('name', i)} ({i})" for i in ids]
    
    print("Available options:")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    print(f"  {len(choices) + 1}. Custom (add new)")
    print(f"  {len(choices) + 2}. Skip (no scaffold)")
    
    last = len(choices) + 1
    skip_idx = len(choices) + 1
    
    while True:
        try:
            raw = input(f"\nYour choice [1-{skip_idx + 1}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n用户中断")
            return None
        if not raw:
            print("Invalid input")
            continue
        try:
            idx = int(raw) - 1
        except ValueError:
            print("Invalid input")
            continue
        
        if 0 <= idx < len(choices):
            return ids[idx]
        elif idx == last:
            new_id = custom_stack_interactive()
            if new_id:
                return new_id
            return interactive_select(presets)
        elif idx == skip_idx:
            return None
        else:
            print("Invalid selection")


def _resolve_detection_files(preset: Dict) -> List[str]:
    """从 preset 中提取检测文件列表。"""
    detection = preset.get('detection') or {}
    files: List[str] = []
    if isinstance(detection, dict):
        files = list(detection.get('files') or [])
    elif isinstance(detection, list):
        files = list(detection)
    if not files:
        files = FALLBACK_DETECTION_RULES.get(preset.get('id', ''), [])
    return files


def detect_stack(target_dir: Path, presets: Dict[str, Dict]) -> Optional[str]:
    """根据目标目录中的文件自动检测技术栈。"""
    target = Path(target_dir).resolve()
    if not target.exists() or not target.is_dir():
        print(f"⚠️  检测目录不存在: {target}")
        return None
    
    detected: List[str] = []
    for preset_id, preset in presets.items():
        for fname in _resolve_detection_files(preset):
            if (target / fname).exists():
                detected.append(preset_id)
                break
    
    if len(detected) == 1:
        print(f"✅ 自动检测到技术栈: {detected[0]}")
        return detected[0]
    elif len(detected) > 1:
        print(f"⚠️  检测到多个技术栈: {', '.join(detected)}")
        print("请使用 --stack 明确指定，或使用 --interactive 手动选择")
        return None
    else:
        print("ℹ️  未检测到已知技术栈")
        return None


def add_custom_stack(source_path: str, user_scaffolds_dir: Optional[Path]) -> Optional[str]:
    """从本地路径添加新选型到用户级目录。"""
    src = Path(source_path).expanduser().resolve()
    if not src.exists() or not src.is_dir():
        print(f"🛑 源路径无效: {source_path}")
        return None
    
    target_root = Path(user_scaffolds_dir).expanduser() if user_scaffolds_dir else DEFAULT_USER_SCAFFOLDS_DIR
    target_root.mkdir(parents=True, exist_ok=True)
    
    preset_id = src.name
    dest = target_root / preset_id
    
    if dest.exists():
        print(f"⚠️  目标已存在: {dest}")
        try:
            ans = input("覆盖？[y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if ans != 'y':
            print("已取消")
            return None
        shutil.rmtree(dest)
    
    try:
        shutil.copytree(src, dest)
        print(f"✅ 已添加选型 '{preset_id}' 到 {target_root}")
        return preset_id
    except Exception as e:
        print(f"🛑 添加失败: {e}")
        return None


class ControlKitInitializer:
    """Agent 开发控制体系初始化器"""
    
    REQUIRED_DIRS = [
        '.agents/skills',
        'guards',
        'gates',
        'hooks',
        'scripts',
        'tests/unit',
        'tests/integration',
        'tests/e2e',
    ]
    
    REQUIRED_FILES = {
        'guard-config.yaml': 'guards/guard-config.yaml',
        'gate-config.json': 'gates/gate-config.json',
        'hooks-config.json': 'hooks/hooks-config.json',
    }
    
    def __init__(self, target_path: Path, force: bool = False, verbose: bool = False):
        self.target = target_path.resolve()
        self.force = force
        self.verbose = verbose
        self.created_dirs: List[Path] = []
        self.created_files: List[Path] = []
        self.existing_items: List[str] = []
        self.errors: List[str] = []
    
    def log(self, message: str, level: str = 'INFO') -> None:
        """输出日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if level == 'SUCCESS':
            prefix = f'{Fore.GREEN}✅{Style.RESET_ALL}' if HAS_COLORAMA else '✅'
        elif level == 'WARNING':
            prefix = f'{Fore.YELLOW}⚠️{Style.RESET_ALL}' if HAS_COLORAMA else '⚠️'
        elif level == 'ERROR':
            prefix = f'{Fore.RED}🛑{Style.RESET_ALL}' if HAS_COLORAMA else '🛑'
        else:
            prefix = f'{Fore.CYAN}ℹ️{Style.RESET_ALL}' if HAS_COLORAMA else 'ℹ️'
        
        print(f"{prefix} [{timestamp}] {message}")
    
    def check_environment(self) -> bool:
        """检查环境依赖"""
        self.log("检查环境依赖...")
        
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.errors.append(f"Python 版本过低: {sys.version}，需要 Python 3.8+")
            return False
        
        if self.verbose:
            self.log(f"Python 版本: {sys.version}")
        
        if not HAS_COLORAMA:
            self.log("colorama 未安装，将使用纯文本输出", 'WARNING')
        if not HAS_YAML:
            self.log("PyYAML 未安装，无法读取 scaffold.yaml / registry/stacks.yaml", 'WARNING')
        
        return True
    
    def check_target_directory(self) -> bool:
        """检查目标目录"""
        if not self.target.exists():
            self.log(f"目标目录不存在: {self.target}", 'ERROR')
            self.errors.append(f"目标目录不存在: {self.target}")
            return False
        
        if not self.target.is_dir():
            self.log(f"目标路径不是目录: {self.target}", 'ERROR')
            self.errors.append(f"目标路径不是目录: {self.target}")
            return False
        
        if self.verbose:
            self.log(f"目标目录: {self.target}")
        
        return True
    
    def create_directory_structure(self, check_only: bool = False) -> bool:
        """创建目录结构"""
        self.log("检查目录结构...")
        
        success = True
        for dir_path in self.REQUIRED_DIRS:
            full_path = self.target / dir_path
            
            if full_path.exists():
                self.existing_items.append(str(full_path))
                if self.verbose:
                    self.log(f"目录已存在: {dir_path}")
            else:
                if check_only:
                    self.log(f"目录缺失: {dir_path}", 'WARNING')
                else:
                    try:
                        full_path.mkdir(parents=True, exist_ok=True)
                        self.created_dirs.append(full_path)
                        self.log(f"创建目录: {dir_path}", 'SUCCESS')
                    except Exception as e:
                        self.errors.append(f"创建目录失败 {dir_path}: {str(e)}")
                        self.log(f"创建目录失败: {dir_path} - {str(e)}", 'ERROR')
                        success = False
        
        return success
    
    def generate_guard_config(self) -> str:
        """生成 guard-config.yaml 内容"""
        return """# Guard Configuration
# Agent 开发控制体系 - Guard 配置文件

version: "1.0.0"
last_updated: "2025-08-13"

guards:
  - name: api-contract-guard
    enabled: true
    severity: HIGH
    checks:
      - endpoint_schema
      - version_management
      - breaking_change_detection

  - name: architecture-guard
    enabled: true
    severity: HIGH
    checks:
      - layer_boundary
      - circular_dependency
      - module_responsibility

  - name: test-coverage-guard
    enabled: true
    severity: HIGH
    config:
      line_coverage_threshold: 80
      branch_coverage_threshold: 70
      new_code_threshold: 90

  - name: security-guard
    enabled: true
    severity: CRITICAL
    checks:
      - secret_detection
      - injection_prevention
      - dependency_vulnerability

  - name: performance-guard
    enabled: true
    severity: MEDIUM
    checks:
      - n_plus_one_detection
      - memory_peak
      - response_time

whitelist:
  - id: WL-001
    target:
      type: path
      pattern: "tests/**"
    reason: "测试代码，豁免部分检查"
    expires: null

report:
  format: json
  output_path: reports/guards/
"""
    
    def generate_gate_config(self) -> str:
        """生成 gate-config.json 内容"""
        config = {
            "version": "1.0.0",
            "last_updated": "2025-08-13",
            "gates": {
                "L1": {
                    "name": "基础检查",
                    "checks": ["directory_structure", "config_files"],
                    "auto_pass": False
                },
                "L2": {
                    "name": "功能完整性检查",
                    "checks": ["guards_pass", "test_coverage_60"],
                    "auto_pass": False
                },
                "L3": {
                    "name": "质量门禁检查",
                    "checks": ["guards_pass", "test_coverage_80", "no_block"],
                    "auto_pass": False
                },
                "L4": {
                    "name": "发布前完整检查",
                    "checks": ["guards_pass", "test_coverage_80", "no_block", "performance_baseline", "security_scan", "doc_sync"],
                    "auto_pass": False
                }
            }
        }
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def generate_hooks_config(self) -> str:
        """生成 hooks-config.json 内容"""
        config = {
            "version": "1.0.0",
            "last_updated": "2025-08-13",
            "hooks": {
                "pre-commit": {
                    "enabled": True,
                    "guards": ["security-guard", "api-contract-guard"],
                    "fail_on": "BLOCK"
                },
                "pre-push": {
                    "enabled": True,
                    "guards": ["architecture-guard", "test-coverage-guard"],
                    "fail_on": "BLOCK"
                },
                "pre-merge": {
                    "enabled": True,
                    "guards": ["all"],
                    "fail_on": "WARN"
                }
            }
        }
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def create_config_files(self, check_only: bool = False) -> bool:
        """创建配置文件"""
        self.log("检查配置文件...")
        
        configs = {
            'guards/guard-config.yaml': self.generate_guard_config(),
            'gates/gate-config.json': self.generate_gate_config(),
            'hooks/hooks-config.json': self.generate_hooks_config(),
        }
        
        success = True
        for file_path, content in configs.items():
            full_path = self.target / file_path
            
            if full_path.exists():
                if self.force:
                    if check_only:
                        self.log(f"配置文件将被覆盖: {file_path}", 'WARNING')
                    else:
                        try:
                            backup_path = full_path.with_suffix(f'.backup-{datetime.now().strftime("%Y%m%d%H%M%S")}')
                            shutil.copy2(full_path, backup_path)
                            full_path.write_text(content, encoding='utf-8')
                            self.log(f"覆盖配置文件: {file_path} (备份: {backup_path.name})", 'SUCCESS')
                        except Exception as e:
                            self.errors.append(f"覆盖配置文件失败 {file_path}: {str(e)}")
                            self.log(f"覆盖配置文件失败: {file_path} - {str(e)}", 'ERROR')
                            success = False
                else:
                    self.existing_items.append(str(full_path))
                    if self.verbose:
                        self.log(f"配置文件已存在: {file_path}")
            else:
                if check_only:
                    self.log(f"配置文件缺失: {file_path}", 'WARNING')
                else:
                    try:
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(content, encoding='utf-8')
                        self.created_files.append(full_path)
                        self.log(f"创建配置文件: {file_path}", 'SUCCESS')
                    except Exception as e:
                        self.errors.append(f"创建配置文件失败 {file_path}: {str(e)}")
                        self.log(f"创建配置文件失败: {file_path} - {str(e)}", 'ERROR')
                        success = False
        
        return success
    
    def generate_summary(self) -> Dict:
        """生成执行摘要"""
        return {
            "status": "success" if not self.errors else "error",
            "target": str(self.target),
            "created": {
                "directories": len(self.created_dirs),
                "files": len(self.created_files)
            },
            "existing": len(self.existing_items),
            "errors": len(self.errors),
            "error_details": self.errors
        }
    
    def run(self, check_only: bool = False, stack_id: Optional[str] = None,
            scaffold_dir: Optional[Path] = None) -> int:
        """执行初始化流程"""
        self.log(f"开始初始化 Agent 开发控制体系...")
        self.log(f"目标目录: {self.target}")
        
        if not self.check_environment():
            return EXIT_ERROR
        
        if not self.check_target_directory():
            return EXIT_CONFIG_ERROR
        
        steps = [
            ("检查目录结构", lambda: self.create_directory_structure(check_only)),
            ("检查配置文件", lambda: self.create_config_files(check_only)),
        ]
        
        for step_name, step_func in steps:
            self.log(f"执行: {step_name}")
            if not step_func():
                self.log(f"{step_name} 失败", 'ERROR')
        
        if stack_id and not check_only:
            self.log(f"应用技术栈选型: {stack_id}")
            if not apply_stack_preset(stack_id, self.target, scaffold_dir, self.force, self.verbose):
                self.log("应用选型脚手架失败", 'ERROR')
        
        summary = self.generate_summary()
        
        print("\n" + "=" * 60)
        self.log("初始化摘要", 'INFO')
        print("=" * 60)
        print(f"目标目录: {summary['target']}")
        print(f"创建目录: {summary['created']['directories']}")
        print(f"创建文件: {summary['created']['files']}")
        print(f"已存在项: {summary['existing']}")
        print(f"错误数量: {summary['errors']}")
        
        if summary['errors'] > 0:
            print("\n错误详情:")
            for error in summary['error_details']:
                print(f"  - {error}")
        
        print("=" * 60)
        
        if not check_only and not self.errors:
            self._print_next_steps(stack_id)
        
        if summary['status'] == 'success':
            self.log("初始化完成", 'SUCCESS')
            return EXIT_SUCCESS
        else:
            self.log("初始化失败", 'ERROR')
            return EXIT_ERROR
    
    def _print_next_steps(self, stack_id: Optional[str]) -> None:
        """完成后打印下一步建议"""
        print("\n📌 下一步建议:")
        if stack_id:
            print(f"  • 已应用选型 {stack_id}，可执行:")
            print("  • 查看生成的文件: ls -la")
        else:
            print("  • 使用 --list-stacks 查看可用技术栈选型")
            print("  • 使用 --stack <id> 指定选型重新初始化（配合 --force）")
            print("  • 使用 --interactive 进入交互式选型")
        print("  • 启动 guards/gates 流程（参见 gates/ 与 guards/ 目录）")
        print()


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='初始化 Agent 开发控制体系（支持技术栈选型）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 在当前目录初始化
    python init-control-kit.py

    # 在指定目录初始化
    python init-control-kit.py --target /path/to/project

    # 强制覆盖已有配置
    python init-control-kit.py --force

    # 仅检查不创建
    python init-control-kit.py --check-only

    # 列出所有可用技术栈选型
    python init-control-kit.py --list-stacks

    # 指定技术栈初始化
    python init-control-kit.py --stack nodejs --target ./my-app

    # 指定脚手架目录
    python init-control-kit.py --stack nextjs -s /path/to/scaffolds

    # 交互式选择技术栈
    python init-control-kit.py --interactive

    # 自动检测已有项目的技术栈
    python init-control-kit.py --auto-detect --target ./existing-app

    # 添加自定义选型
    python init-control-kit.py --add-stack /path/to/my-scaffold
        """
    )
    
    parser.add_argument(
        '--target',
        type=Path,
        default=Path.cwd(),
        help='目标目录（默认：当前目录）'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制覆盖已有配置'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='仅检查不创建'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出模式'
    )
    
    parser.add_argument(
        '--stack',
        choices=['nodejs', 'python', 'go', 'java-maven'],
        help='技术栈选型（仅作为内置快捷选项）'
    )
    
    parser.add_argument(
        '--scaffold', '-s',
        type=Path,
        help='指定脚手架目录（如 nodejs, rust-react, nextjs-fullstack）'
    )
    
    parser.add_argument(
        '--list-stacks',
        action='store_true',
        help='列出所有可用的选型'
    )
    
    parser.add_argument(
        '--add-stack',
        help='从本地路径添加新选型到用户级目录'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='交互式选择选型'
    )
    
    parser.add_argument(
        '--auto-detect',
        action='store_true',
        help='自动检测已有项目的技术栈'
    )
    
    parser.add_argument(
        '--scaffolds-dir',
        type=Path,
        help='自定义脚手架目录'
    )
    
    parser.add_argument(
        '--user-scaffolds-dir',
        type=Path,
        default=DEFAULT_USER_SCAFFOLDS_DIR,
        help=f'用户级脚手架目录（默认 {DEFAULT_USER_SCAFFOLDS_DIR}）'
    )
    
    return parser.parse_args()


def resolve_stack_id(args: argparse.Namespace, presets: Dict[str, Dict]) -> Optional[str]:
    """根据 args 优先级解析最终选型 id。"""
    if args.stack:
        if args.stack not in presets:
            print(f"🛑 选型 '{args.stack}' 不存在。可用选型：")
            list_stacks(presets)
            return None
        return args.stack
    
    if args.interactive:
        return interactive_select(presets)
    
    if args.auto_detect:
        return detect_stack(args.target, presets)
    
    return None


def main() -> int:
    """主函数"""
    try:
        args = parse_args()
        
        presets = load_presets(
            scaffolds_dir=args.scaffolds_dir,
            user_scaffolds_dir=args.user_scaffolds_dir,
        )
        
        if args.list_stacks:
            list_stacks(presets)
            return EXIT_SUCCESS
        
        if args.add_stack:
            new_id = add_custom_stack(args.add_stack, args.user_scaffolds_dir)
            return EXIT_SUCCESS if new_id else EXIT_ERROR
        
        stack_id: Optional[str] = None
        if args.stack or args.interactive or args.auto_detect:
            stack_id = resolve_stack_id(args, presets)
            if args.stack and not stack_id:
                return EXIT_ARGS_ERROR
        
        initializer = ControlKitInitializer(
            target_path=args.target,
            force=args.force,
            verbose=args.verbose
        )
        
        return initializer.run(
            check_only=args.check_only,
            stack_id=stack_id,
            scaffold_dir=args.scaffold,
        )
    
    except KeyboardInterrupt:
        print("\n用户中断执行")
        return EXIT_USER_INTERRUPT
    except Exception as e:
        print(f"未预期的错误: {str(e)}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())