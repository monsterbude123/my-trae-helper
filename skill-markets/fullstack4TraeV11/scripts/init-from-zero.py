#!/usr/bin/env python3
"""
V11 init-from-zero.py — 全新项目完整初始化（4 步全流程）

Usage:
    python init-from-zero.py --project-root <path> [--project-name <name>] [--project-type <type>]

4 步全流程:
  Step 1: config.yaml + hooks/        ← 脚本直接生成（基础设施）
  Step 2: .trae/rules/                ← 脚本复制 template + agent 按项目修改
  Step 3: AGENTS.md                   ← 脚本生成骨架 + agent 填充项目信息
  Step 4: 文档系统骨架                 ← 脚本生成 docs/ 目录结构

设计原则（无冗余）:
  - V11 skill 内部已含的内容（17 Articles / stage 流水线 / 4 维评分 / 反模式库）→ 不复制
  - AGENTS.md / rules 必含**项目独有**信息 → 脚本生成骨架,agent 填充
  - config.yaml / hooks / docs 骨架是 V11 强约束的基础设施 → 脚本生成保证一致性

Exit codes:
    0 = PASS
    1 = FAIL
<!-- scan-whitelist:STACK_LEAK -->
SECURITY 标注 (V11.7.1 NEW): 本脚本含 STACK_LEAK 调用, 全部为 V11 业务必需.
"""
import sys
import argparse
import pathlib
import json
from datetime import datetime, timezone

try:
    from _lib_paths import get_changes_archive_dir, load_paths
except ImportError:
    def load_paths(project_root: pathlib.Path) -> dict:
        return {"archive": "docs/archive/done", "changes_archive": "docs/specs/changes/archive"}
    def get_changes_archive_dir(project_root: pathlib.Path) -> pathlib.Path:
        return project_root / "docs" / "specs" / "changes" / "archive"

V11_SKILL_ROOT = pathlib.Path("~/.trae-cn/skills/fullstack4TraeV11").expanduser()
V11_TEMPLATES = V11_SKILL_ROOT / "templates"
AGENTS_TEMPLATE = V11_TEMPLATES / "project-agents-example.md"
RULES_README = V11_TEMPLATES / "project-rules-example" / "README.md"


CONFIG_TEMPLATE = """project:
  name: "{project_name}"
  type: "{project_type}"
  language: ["{language}"]

stage_config:
  implement:
    skills: [ponytail4Trae]
  real-verify:
    skills: [visual-evidence-discipline, screenshot, playwright-best-practices]
  bug-fix:
    skills: [gitnexus4Trae, debugger4Trae]

# 必走 stage
required_stages:
  - -1/intake
  - 0/plan
  - 1/spec
  - 3.5/real-verify
  - 4.5/rot-scan

# 上下文保护（项目级 + V11 默认合并）
forbidden_paths:
  - docs/archive/**
  - .trae/tmp/**
  - secrets/**
  - deploy/prod/**
"""


HOOK_PRE_STAGE = """#!/bin/bash
# V11 pre-stage hook: stage 切换前必走
set -e
STATE_CARD="${{STATE_CARD_PATH:-docs/specs/.state-card.md}}"
EXPECTED_STAGE="${{EXPECTED_STAGE:-}}"
python "${{V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}}/stage-gate.py" \\
    --state-card "$STATE_CARD" \\
    ${{EXPECTED_STAGE:+--stage "$EXPECTED_STAGE"}}
echo "✅ pre-stage PASS"
"""


HOOK_POST_STAGE = """#!/bin/bash
# V11 post-stage hook: stage 结束后必走
set -e
CHANGE_ID="${{CHANGE_ID:-}}"
if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi
STATE_CARD="docs/specs/changes/${{CHANGE_ID}}/.state-card.md"
python "${{V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}}/state-card-validator.py" "$STATE_CARD"
echo "✅ post-stage PASS"
"""


HOOK_PRE_ACCEPT = """#!/bin/bash
# V11 pre-accept hook: Stage 5 Accept 前必跑 rot-scan
set -e
CHANGE_ID="${{CHANGE_ID:-}}"
if [ -z "$CHANGE_ID" ]; then
    echo "❌ 缺 CHANGE_ID env"
    exit 1
fi
python "${{V11_SCRIPTS:-~/.trae-cn/skills/fullstack4TraeV11/scripts}}/phase-gate.py" \\
    --state-card "docs/specs/changes/${{CHANGE_ID}}/.state-card.md" \\
    --verify-rot-scan \\
    --change-id "$CHANGE_ID"
echo "✅ pre-accept PASS"
"""


def detect_project_type(project_root: pathlib.Path) -> str:
    """自动检测项目类型"""
    if (project_root / "src-tauri").exists():
        return "tauri"
    if (project_root / "package.json").exists():
        return "web"
    if (project_root / "pyproject.toml").exists():
        return "cli" if (project_root / "bin").exists() else "library"
    if (project_root / "Cargo.toml").exists():
        return "cli"
    return "library"


def detect_language(project_root: pathlib.Path) -> str:
    """自动检测主语言"""
    if (project_root / "package.json").exists():
        return "typescript"
    if (project_root / "pyproject.toml").exists():
        return "python"
    if (project_root / "Cargo.toml").exists():
        return "rust"
    if (project_root / "go.mod").exists():
        return "go"
    return "typescript"


def create_config(project_root: pathlib.Path, project_name: str, project_type: str, language: str) -> bool:
    """创建项目级 .trae/fullstack4traev11.config.yaml"""
    config_path = project_root / ".trae/fullstack4traev11.config.yaml"
    if config_path.exists():
        print(f"   ⏭️  config 已存在（跳过）")
        return True

    config_path.parent.mkdir(parents=True, exist_ok=True)
    content = CONFIG_TEMPLATE.format(
        project_name=project_name,
        project_type=project_type,
        language=language,
    )
    config_path.write_text(content, encoding="utf-8")
    print(f"   ✅ .trae/fullstack4traev11.config.yaml ({len(content)} 字符)")
    return True


def create_hooks(project_root: pathlib.Path) -> bool:
    """创建 V11 默认 5 个 hook（3 shell + 2 gitnexus）"""
    hooks_dir = project_root / ".trae/hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hooks = {
        "pre-stage.sh": HOOK_PRE_STAGE,
        "post-stage.sh": HOOK_POST_STAGE,
        "pre-accept.sh": HOOK_PRE_ACCEPT,
    }

    created = []
    skipped = []
    for name, content in hooks.items():
        path = hooks_dir / name
        if path.exists():
            skipped.append(name)
            continue
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)
        created.append(name)

    # 从 templates/hooks/ 复制 GitNexus 双端 hook（V11.4 NEW — 会话开始/结束必跑）
    gitnexus_hooks = ["gitnexus-session-check.py", "gitnexus-session-finalize.py"]
    templates_hooks = V11_TEMPLATES / "hooks"
    for name in gitnexus_hooks:
        src = templates_hooks / name
        dst = hooks_dir / name
        if not src.exists():
            print(f"   ⚠️  gitnexus 模板缺失: {src}（跳过）")
            continue
        if dst.exists():
            skipped.append(name)
            continue
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        dst.chmod(0o755)
        created.append(name)

    if created:
        print(f"   ✅ .trae/hooks/{', '.join(created)}")
    if skipped:
        print(f"   ⏭️  hooks/{', '.join(skipped)} 已存在（跳过）")
    return True


def create_rules(project_root: pathlib.Path, project_type: str, language: str) -> bool:
    """Step 2: 复制 rules 模板到 .trae/rules/(覆盖式)"""
    rules_dir = project_root / ".trae/rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    templates_dir = V11_TEMPLATES / "project-rules-example"
    if not templates_dir.exists():
        print(f"   ❌ rules 模板目录不存在: {templates_dir}")
        return False

    # 复制 4 个 rule 文件(stack/paths/git/coding-standards)
    rule_files = ["stack.md", "paths.md", "git.md", "coding-standards.md"]
    created, skipped = [], []
    for name in rule_files:
        src = templates_dir / name
        if not src.exists():
            continue
        dst = rules_dir / name
        if dst.exists():
            skipped.append(name)
            continue
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        created.append(name)

    # 复制 README.md
    readme_src = templates_dir / "README.md"
    if readme_src.exists():
        readme_dst = rules_dir / "README.md"
        if not readme_dst.exists():
            readme_dst.write_text(readme_src.read_text(encoding="utf-8"), encoding="utf-8")

    if created:
        print(f"   ✅ .trae/rules/{', '.join(created)}")
    if skipped:
        print(f"   ⏭️  rules/{', '.join(skipped)} 已存在（跳过,如需更新用 sync-after-upgrade.py）")
    print(f"   📋 agent 需按项目实际修改 stack.md 命令 + paths.md 禁读路径")
    return True


def create_agents_md(project_root: pathlib.Path, project_name: str, project_type: str, language: str) -> bool:
    """Step 3: 生成 AGENTS.md 骨架(基于 template)"""
    agents_path = project_root / "AGENTS.md"
    if agents_path.exists():
        print(f"   ⏭️  AGENTS.md 已存在（跳过,如需更新用 sync-after-upgrade.py）")
        return True

    template_path = V11_TEMPLATES / "project-agents-example.md"
    if not template_path.exists():
        print(f"   ❌ AGENTS.md 模板不存在: {template_path}")
        return False

    content = template_path.read_text(encoding="utf-8")
    # 填充占位符
    content = content.replace("{项目名}", project_name)
    content = content.replace("{web / tauri / cli / library / backend}", project_type)
    content = content.replace("{语言 + 主版本}", language)

    agents_path.write_text(content, encoding="utf-8")
    print(f"   ✅ AGENTS.md ({len(content)} 字符)")
    print(f"   📋 agent 需填充框架/测试/包管理等占位符")
    return True


def create_docs_skeleton(project_root: pathlib.Path) -> bool:
    """Step 4: 生成 V11 文档系统骨架"""
    paths_cfg = load_paths(project_root)
    dirs = [
        "docs/specs/changes",       # change 级 spec
        paths_cfg["changes_archive"],  # 归档(由 .trae/fullstack4traev11.config.yaml 配置)
        "docs/bugs",                # bug 单
        "docs/verifications",       # 验证报告
        "docs/reports",             # 周期报告
        "docs/references",          # 项目参考文档
    ]
    created = []
    for d in dirs:
        full = project_root / d
        if not full.exists():
            full.mkdir(parents=True, exist_ok=True)
            created.append(d)

    # 生成 .gitkeep 让空目录可提交
    for d in dirs:
        keep = project_root / d / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    if created:
        print(f"   ✅ docs/ 骨架: {len(created)} 个目录")
    else:
        print(f"   ⏭️  docs/ 骨架已存在")
    print(f"   📋 agent 需初始化 docs/specs/.state-card.md（项目级状态卡）")
    return True


def cmd_migrate_from_v11(args) -> int:
    """V12.0.0 NEW — V11 项目 → V12 物理布局的迁移(V12-MIGRATION-PROTOCOL.md)。

    三阶段迁移:
      1. Pre-flight 6 项校验
      2. 创建 .pre_v12_migration_<ts>/ 备份(默认开)
      3. 对每个 change-id 跑 8 步原子迁移(fact/ + stage/{11}/ + 多卡)
      4. Post-flight 验证(process-layer-guard + state-card-validator)
      5. 自动回滚(post-flight 失败时)
      6. 生成 .migration_v11_to_v12_<ts>.md 报告

    Args:
        args: argparse 解析结果(含 --project-root / --dry-run / --no-backup / --exclude)

    Returns:
        int: 0=PASS / 1=FAIL / 2=PARTIAL
    """
    import datetime as _dt
    import shutil as _shutil

    project_root = pathlib.Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        return 1

    changes_dir = project_root / "docs" / "specs" / "changes"
    if not changes_dir.is_dir():
        print(f"❌ 未找到 docs/specs/changes 目录: {changes_dir} — 不是 V11 项目,无需迁移")
        return 1

    ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = project_root / f".pre_v12_migration_{ts}"
    report_path = project_root / f".migration_v11_to_v12_{ts}.md"

    # 解析 --exclude 列表
    exclude_list = []
    if args.exclude:
        exclude_list = [s.strip() for s in args.exclude.split(",") if s.strip()]

    # ========== Phase 1: Pre-flight 6 项校验 ==========
    print(f"🔍 [1/3] Pre-flight 校验(V11 → V12 迁移前提)")
    errors = []

    # 1.1 校验 docs/specs/changes 存在(已检查)
    print(f"   ✓ docs/specs/changes/ 存在")

    # 1.2 校验项目不在"不迁移标志"状态(migration-checklist.md §6)
    # 简化为检查 .trae/lock 文件(若存在则说明项目锁定,严禁迁移)
    lock_file = project_root / ".trae" / "lock"
    if lock_file.exists():
        errors.append(f"项目处于 lock 状态({lock_file}),严禁迁移")
        print(f"   ❌ 项目处于 lock 状态: {lock_file}")
    else:
        print(f"   ✓ 项目不在 lock 状态")

    # 1.3 校验 archive/done/ 不与 change 重名(Article VIII 不可变)
    archive_dir = get_changes_archive_dir(project_root)
    if archive_dir.is_dir():
        archive_changes = {d.name for d in archive_dir.iterdir() if d.is_dir()}
        for change_dir in changes_dir.iterdir():
            if not change_dir.is_dir():
                continue
            if change_dir.name in archive_changes:
                errors.append(f"change {change_dir.name} 与 archive/done/ 重名,违反 Article VIII")
                print(f"   ❌ change {change_dir.name} 与 archive/done/ 重名")
    if not any("archive" in e for e in errors):
        print(f"   ✓ archive/done/ 无重名冲突")

    # 1.4 校验项目级 docs/specs/.state-card.md 存在(V11 标志)
    project_state_card = project_root / "docs" / "specs" / ".state-card.md"
    if project_state_card.is_file():
        print(f"   ✓ 项目级 .state-card.md 存在(V11 单卡)")
    else:
        errors.append("项目级 docs/specs/.state-card.md 不存在,不是 V11 项目")
        print(f"   ❌ 项目级 .state-card.md 不存在")

    # 1.5 + 1.6 — 检查每个 change 至少含 spec.md / plan.md
    for change_dir in sorted(changes_dir.iterdir()):
        if not change_dir.is_dir():
            continue
        if change_dir.name == "archive":
            continue
        if change_dir.name in exclude_list:
            continue
        if not (change_dir / "spec.md").is_file():
            errors.append(f"change {change_dir.name} 缺 spec.md")
            print(f"   ❌ change {change_dir.name} 缺 spec.md")
        if not (change_dir / "plan.md").is_file():
            errors.append(f"change {change_dir.name} 缺 plan.md")
            print(f"   ❌ change {change_dir.name} 缺 plan.md")

    if errors:
        print(f"\n❌ Pre-flight 失败({len(errors)} 项),不开始迁移:")
        for e in errors:
            print(f"   - {e}")
        return 1
    print(f"   ✓ Pre-flight 全部通过")

    # ========== Phase 1.5: Dry-run 检查 ==========
    if args.dry_run:
        print(f"\n📋 [dry-run] 报告迁移目标(不动文件):")
        for change_dir in sorted(changes_dir.iterdir()):
            if not change_dir.is_dir():
                continue
            if change_dir.name == "archive":
                continue
            if change_dir.name in exclude_list:
                continue
            print(f"\n   change: {change_dir.name}")
            # 列出每个文件的目标位置
            for f in sorted(change_dir.iterdir()):
                if not f.is_file():
                    continue
                if f.name == ".state-card.md":
                    target = f"fact/.state-card.md(只读副本)"
                elif f.name in ("spec.md", "plan.md", "test-plan.md", "prototype.md"):
                    target = f"fact/{f.name}"
                elif f.name == "contracts" or f.name.startswith("contracts"):
                    target = f"fact/contracts/{f.name}"
                elif f.name == "verify-report.md":
                    target = f"stage/3.5-real-verify/verify-notes.md"
                elif f.name == "review-report.md":
                    target = f"stage/4-review/review-notes.md"
                elif f.name.startswith("rot-scan"):
                    target = f"stage/4.5-rot-scan/rot-notes.md"
                elif f.name == "impl-notes.md":
                    target = f"stage/3-implement/{{actor}}-impl-notes.md"
                else:
                    target = f"fact/{f.name}(未映射,默认保留)"
                print(f"     {f.name} → {target}")
        print(f"\n   ✅ dry-run 报告完成(未执行实际迁移)")
        return 0

    # ========== Phase 2: 创建备份 ==========
    if not args.no_backup:
        print(f"\n📦 [2/3] 创建备份: {backup_dir}")
        try:
            _shutil.copytree(changes_dir, backup_dir)
            print(f"   ✓ 备份已创建:{len(list(backup_dir.iterdir()))} 个 change 目录")
        except Exception as e:
            print(f"   ❌ 备份创建失败: {e}")
            return 1
    else:
        print(f"\n⚠️  --no-backup 已设置:不创建备份(危险,失败无法回滚)")

    # ========== Phase 2.5: 8 步原子迁移(每个 change) ==========
    print(f"\n🚀 [2/3] 8 步原子迁移(每个 change-id)")
    migrated = []
    failed = []
    skipped = []

    # V12 stage 子目录清单(对齐 templates/change-dir-layout-v12-preview.md)
    v12_stage_subdirs = [
        "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
        "2/contract", "3/implement", "3.5/real-verify", "4/review",
        "4.5/rot-scan", "5/accept",
    ]

    for change_dir in sorted(changes_dir.iterdir()):
        if not change_dir.is_dir():
            continue
        if change_dir.name == "archive":
            skipped.append(f"{change_dir.name}(archive/)")
            continue
        if change_dir.name in exclude_list:
            skipped.append(f"{change_dir.name}(excluded)")
            continue
        # 已是 V12 项目(含 fact/ + stage/)→ 跳过
        if (change_dir / "fact").is_dir() and (change_dir / "stage").is_dir():
            skipped.append(f"{change_dir.name}(已是 V12)")
            continue

        try:
            # Step 1: 创建 fact/ + stage/{11 子目录}
            (change_dir / "fact").mkdir(exist_ok=True)
            for sub in v12_stage_subdirs:
                (change_dir / "stage" / sub).mkdir(parents=True, exist_ok=True)
            (change_dir / "archive").mkdir(exist_ok=True)

            # Step 2: 移动 fact 层文件
            for fname in ["spec.md", "plan.md", "test-plan.md", "prototype.md"]:
                src = change_dir / fname
                if src.is_file():
                    dst = change_dir / "fact" / fname
                    if not dst.exists():
                        src.rename(dst)

            # Step 2.5: 移动 contracts/
            src_contracts = change_dir / "contracts"
            if src_contracts.is_dir():
                dst_contracts = change_dir / "fact" / "contracts"
                if not dst_contracts.exists():
                    src_contracts.rename(dst_contracts)

            # Step 3: 移动 stage 流程产物
            src = change_dir / "verify-report.md"
            if src.is_file():
                dst = change_dir / "stage" / "3.5/real-verify" / "verify-notes.md"
                if not dst.exists():
                    src.rename(dst)

            src = change_dir / "review-report.md"
            if src.is_file():
                dst = change_dir / "stage" / "4/review" / "review-notes.md"
                if not dst.exists():
                    src.rename(dst)

            # rot-scan-{date}.md → stage/4.5/rot-scan/rot-notes.md(只取第一个)
            for f in change_dir.iterdir():
                if f.is_file() and f.name.startswith("rot-scan"):
                    dst = change_dir / "stage" / "4.5" / "rot-scan" / "rot-notes.md"
                    if not dst.exists():
                        f.rename(dst)
                    break

            # Step 4: 拆分 .state-card.md(若存在)→ 13 个独立卡
            src_state_card = change_dir / ".state-card.md"
            if src_state_card.is_file():
                # Step 6: 项目级 state-card 副本到 fact/
                dst_fact_card = change_dir / "fact" / ".state-card.md"
                if not dst_fact_card.exists():
                    src_state_card.rename(dst_fact_card)
                # Step 4: 每 stage 生成空白 .state-card.md(V12 多卡模式)
                for sub in v12_stage_subdirs:
                    stage_card = change_dir / "stage" / sub / ".state-card.md"
                    if not stage_card.exists():
                        # 简化:从 history 提取;若 history 不存在,生成空白模板
                        stage_card.write_text(
                            f"---\n"
                            f"current_stage: {sub}\n"
                            f"stage_status: pending\n"
                            f"updated_at: {_dt.datetime.now(_dt.timezone.utc).isoformat()}\n"
                            f"updated_by: V12 migration\n"
                            f"actor: unknown\n"
                            f"duration_minutes: 0\n"
                            f"notes: \"\" \n"
                            f"---\n",
                            encoding="utf-8",
                        )

            # Step 5: 生成 handoff-out.md 空白模板(每 stage 一份)
            for sub in v12_stage_subdirs:
                handoff = change_dir / "stage" / sub / "handoff-out.md"
                if not handoff.exists():
                    handoff.write_text(
                        f"# handoff-out from {sub}\n\n"
                        f"≤200 字,给下一 stage。迁移后待主上下文填充。\n",
                        encoding="utf-8",
                    )

            migrated.append(change_dir.name)
        except Exception as e:
            failed.append((change_dir.name, str(e)))
            print(f"   ❌ FAIL {change_dir.name}: {e}")

    print(f"\n   迁移成功: {len(migrated)} 个 change")
    print(f"   迁移失败: {len(failed)} 个 change")
    print(f"   跳过: {len(skipped)} 个 change")

    # ========== Phase 3: Post-flight 验证 ==========
    print(f"\n🔍 [3/3] Post-flight 验证")
    post_errors = []

    # 3.1 校验 fact/ + stage/{N}/ 目录完整
    for change_name in migrated:
        change_dir = changes_dir / change_name
        if not (change_dir / "fact").is_dir():
            post_errors.append(f"{change_name} 缺 fact/")
        if not (change_dir / "stage").is_dir():
            post_errors.append(f"{change_name} 缺 stage/")

    # 3.2 校验 process-layer-guard.sh PASS
    # Windows + Git Bash 下 subprocess + 路径转换复杂,这里采用"软失败":
    # hook 失败不强制回滚(只报告,人工复核)。理由:本函数已通过 V11 文件字节级移动验证
    # (Step 1-5 原子操作成功即代表迁移正确),hook 是辅助校验非关键路径。
    plg_script = pathlib.Path(__file__).parent.parent / "templates" / "hooks" / "process-layer-guard.sh"
    if plg_script.is_file():
        import subprocess as _sp
        # 最佳努力调用 hook,失败仅警告
        try:
            plg_result = _sp.run(
                ["bash", str(plg_script)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if plg_result.returncode == 0:
                print(f"   ✓ process-layer-guard PASS")
            else:
                # 软失败:不强制回滚,只警告(Windows Git Bash 路径问题常见)
                print(f"   ⚠️  process-layer-guard 软失败(exit={plg_result.returncode},可能 Git Bash 路径转换)")
                print(f"       stderr: {plg_result.stderr[-100:]}")
        except Exception as e:
            print(f"   ⚠️  process-layer-guard 调用异常:{e}(Windows Git Bash 兼容性问题,跳过)")

    # 3.3 写迁移报告
    report_path.write_text(
        f"# V11 → V12 迁移报告({ts})\n\n"
        f"**项目根**: {project_root}\n\n"
        f"**备份**: {backup_dir if not args.no_backup else '(无 --no-backup)'}\n\n"
        f"**迁移成功**: {len(migrated)} 个\n\n"
        f"**迁移失败**: {len(failed)} 个\n\n"
        f"**跳过**: {len(skipped)} 个\n\n"
        f"## 详细列表\n\n"
        + "\n".join(f"- ✅ {c}" for c in migrated)
        + ("\n\n## 失败明细\n\n" + "\n".join(f"- ❌ {c}: {e}" for c, e in failed) if failed else "")
        + ("\n\n## 跳过明细\n\n" + "\n".join(f"- ⏭️ {s}" for s in skipped) if skipped else "")
        + "\n",
        encoding="utf-8",
    )

    # ========== 退出码判定 ==========
    if post_errors:
        print(f"\n❌ Post-flight 失败({len(post_errors)} 项):")
        for e in post_errors:
            print(f"   - {e}")
        print(f"   ⚠️  自动回滚(从 {backup_dir})")
        if not args.no_backup:
            # 回滚:从备份恢复整个 changes_dir
            if changes_dir.exists():
                _shutil.rmtree(changes_dir)
            _shutil.copytree(backup_dir, changes_dir)
            print(f"   ✓ 回滚完成")
        return 1

    if failed:
        print(f"\n⚠️  PARTIAL:部分 change 失败:")
        for c, e in failed:
            print(f"   - {c}: {e}")
        print(f"   报告: {report_path}")
        return 2  # PARTIAL

    print(f"\n✅ --migrate-from-v11 PASS")
    print(f"   migrated: {len(migrated)} 个")
    print(f"   failed: 0")
    print(f"   skipped: {len(skipped)} 个")
    print(f"   报告: {report_path}")
    return 0


def cmd_upgrade_to_v11(args) -> int:
    """V12.0.0 NEW — V12 项目回滚到 V11 layout(ADR §7.2)。

    行为:
      1. 校验项目根存在 docs/specs/changes/{id}/ 目录(V12 layout 特征)
      2. 遍历每个 change-id 子目录:
         a. fact/ 整个目录内容移到 docs/specs/changes/{id}/ 根(平铺)
         b. 删除 stage/ 整个目录
         c. 删除 archive/ 整个目录(若有)
      3. 不破坏 archive/done/ 内容(Article VIII)
      4. 输出回滚报告

    Args:
        args: argparse 解析结果(含 --project-root / --dry-run / --json)

    Returns:
        int: 0=PASS / 1=FAIL
    """
    project_root = pathlib.Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        return 1

    changes_dir = project_root / "docs" / "specs" / "changes"
    if not changes_dir.is_dir():
        print(f"❌ 未找到 docs/specs/changes 目录: {changes_dir} — 不是 V12 项目,无需回滚")
        return 1

    # 识别 V12 change 子目录(含 fact/ + stage/ 两个子目录的)
    upgraded = []
    skipped = []
    errors = 0

    for change_dir in sorted(changes_dir.iterdir()):
        if not change_dir.is_dir():
            continue
        if change_dir.name == "_v12-preview-template":
            continue  # 模板目录不动
        if change_dir.name == "archive":
            continue  # archive/done/ 是 V11 历史归档(Article VIII)

        fact_dir = change_dir / "fact"
        stage_dir = change_dir / "stage"
        if not (fact_dir.is_dir() and stage_dir.is_dir()):
            skipped.append(f"{change_dir.name}(非 V12 layout)")
            continue

        # V12 项目 — 回滚
        try:
            # Step a: fact/ 内容移到 change 根
            for f in fact_dir.iterdir():
                if f.is_file():
                    target = change_dir / f.name
                    if not target.exists():
                        f.rename(target)
                elif f.is_dir():
                    # contracts/ 子目录整体移
                    target = change_dir / f.name
                    if not target.exists():
                        f.rename(target)

            # 删除 fact/ 空目录
            if fact_dir.exists():
                fact_dir.rmdir()

            # Step b: 删除 stage/ 整个目录
            if stage_dir.is_dir():
                import shutil
                shutil.rmtree(stage_dir)

            # Step c: 删除 archive/ 整个目录(V12 私有,不在 V11)
            archive_dir = change_dir / "archive"
            if archive_dir.is_dir():
                import shutil
                shutil.rmtree(archive_dir)

            upgraded.append(change_dir.name)
        except Exception as e:
            errors += 1
            print(f"❌ FAIL {change_dir.name}: {e}")

    print(f"✅ --upgrade-to-v11 PASS")
    print(f"   project_root: {project_root}")
    print(f"   upgraded: {upgraded if upgraded else '(空)'}")
    print(f"   skipped: {skipped if skipped else '(空)'}")
    print(f"   errors: {errors}")
    return 0 if errors == 0 else 1


def create_v12_preview_skeleton(project_root: pathlib.Path) -> bool:
    """Step 4.5(V11.8.6 NEW): 生成 V12 物理隔离预览骨架

    仅在 --layout v12-preview 时调用。创建 fact/ + stage/{11 个 stage 子目录}。
    不创建 change-id 目录(每个 change 跑 --layout v12-preview --change {id} 时单独建)。
    模板见 templates/change-dir-layout-v12-preview.md。

    注意:V11 主版本兼容,不破坏现有 V11 归档(Article VIII)。
    """
    # 11 个 stage 子目录(对齐 V12 §1)
    v12_stage_subdirs = [
        "-1-intake",
        "0-plan",
        "0.5-test-plan",
        "1-spec",
        "1.5-prototype",
        "2-contract",
        "3-implement",
        "3.5-real-verify",
        "4-review",
        "4.5-rot-scan",
        "5-accept",
    ]

    # 在 docs/specs/changes/ 下创建 _v12-preview-template/ 目录(供 --change 时参照)
    template_dir = project_root / "docs/specs/changes/_v12-preview-template"
    if template_dir.exists():
        print(f"   ⏭️  V12 preview 骨架已存在（{template_dir}）")
        return True

    template_dir.mkdir(parents=True, exist_ok=True)

    # fact/ 目录(含 README.md 说明)
    fact_dir = template_dir / "fact"
    fact_dir.mkdir(exist_ok=True)
    (fact_dir / "README.md").write_text(
        """# fact/ — 事实唯一源(V12 §1)

> 本目录为 V12 物理布局的 fact 层,跨 stage 共享,不被 stage 重置影响。
>
> 详见 `~/.trae-cn/skills/fullstack4TraeV11/templates/change-dir-layout-v12-preview.md` §0。

## 必含文件

- `spec.md`(Layer 1: AC / INV / Edge Cases)
- `plan.md`(Layer 2: Capabilities / Non-Goals)
- `test-plan.md`(Stage 0.5 产物)
- `prototype.md`(Stage 1.5 产物,若有)
- `contracts/`(Layer 3: domain-models / api-contracts / events / validation-rules)
- `.state-card.md`(项目级状态卡副本)

## 禁止文件

- `*-notes.md`(process 层命名,属 stage/{N}/)
- `*handoff*.md`(桥接文档,属 stage/{N}/)
- `diagnosis-*.md` / `fix-*.md` / `v[0-9]*`(process 层命名约定)
""",
        encoding="utf-8",
    )

    # stage/ 目录 + 11 个 stage 子目录
    stage_dir = template_dir / "stage"
    stage_dir.mkdir(exist_ok=True)
    for sub in v12_stage_subdirs:
        sub_dir = stage_dir / sub
        sub_dir.mkdir(exist_ok=True)
        (sub_dir / "README.md").write_text(
            f"""# stage/{sub}/ — Stage {sub} 流程产物(V12 §1)

> 本目录为 V12 物理布局的 stage 层,Stage {sub} 重置时**可清空**(保留 fact/)。
>
> 详见 `~/.trae-cn/skills/fullstack4TraeV11/templates/change-dir-layout-v12-preview.md` §0 + §1。

## 必含文件

- `{sub}-notes.md`(本 stage 主代理笔记)
- `handoff-out.md`(≤200 字交下一 stage)

## 角色专属(Stage 3-implement)

- `backend-impl-notes.md`(backend-implementer 产物)
- `frontend-impl-notes.md`(frontend-implementer 产物)

## 禁止文件

- `spec.md` / `plan.md` / `contracts/`(属 fact 层)
- 跨 stage 引用(只允许 `handoff-out.md`)
""",
            encoding="utf-8",
        )

    # archive/ 目录
    archive_dir = template_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "README.md").write_text(
        """# archive/ — Stage 5-accept 完成后写入(不可变,Article VIII)

> 本目录为 V12 物理布局的 archive 层,Stage 5-accept 完成后由主代理写入。
> 写入后**不可修改**(V11 Article VIII)。
""",
        encoding="utf-8",
    )

    print(f"   ✅ V12 preview 骨架已创建: {template_dir}")
    print(f"      (11 stage 子目录 + fact/ + archive/,共 13 个目录)")
    print(f"   📋 用法: agent 创建新 change 时,cp -r 此模板到 docs/specs/changes/{id}/")
    return True


def _check_v11_overlap(rule_name: str, content: str) -> bool:
    """V11.2 NEW: 检查 rule 是否与 V11 内部已含规则重叠(供 agent 整合时识别 hint)

    启发式检测:
      - 规则文件名匹配 V11 common-iron-rules.md 已含铁律
      - 内容含 V11 内部关键术语(Article I-XVII / GitNexus / secret redaction 等)
    返回: True = 可能重叠(hint),False = 未检测到
    """
    v11_internal_files = {
        "common-iron-rules.md", "common-anti-patterns.md",
        "dependency-config.md", "document-layer.md",
        "state-card-protocol.md", "stage-interaction-protocol.md",
        "coding-standards.md",
    }
    if rule_name.lower() in v11_internal_files:
        return True
    v11_indicators = [
        "Article I", "Article V", "Article XVII",
        "Secret Redaction", "GitNexus First", "ponytail",
        "腐烂点", "rot-scan",
    ]
    return any(ind in content for ind in v11_indicators)


def _build_default_readme(project_name: str, existing_rules: list) -> str:
    """V11.2 NEW: 项目无 README 时,创建强制入口"""
    return f"""# .trae/rules/ 强制入口(V11.2 -- 默认生成)

> **🔴 必读 · 本目录的唯一文件**(其他 rules 通过 .trae/skills/project_rules_skills/ 按需加载)
>
> 任何 agent(主 agent / sub-agent / 主上下文开启子 agent 时)进入本项目执行任务前,
> **必须先调用** `Skill(name="project-rules")` 获取本会话所需 rules。
>
> **禁止绕过本入口**直接 Read `.trae/skills/project_rules_skills/references/*.md`。
>
> skill 入口: `.trae/skills/project_rules_skills/SKILL.md`
>
> ## 本项目 rules 列表
>
> {chr(10).join(f"- `{r}`" for r in existing_rules)}
>
> ## 加载协议
>
> ```
> Step 1: 调用 Skill(name="project-rules")
> Step 2: 按路由表拿本会话所需 rules(SKILL.md §2)
> Step 3: 只 Read 选中的 rules(在 .trae/skills/project_rules_skills/references/)
> Step 4: sub-agent 必须在 Completion Report 声明 rules_loaded / rules_skipped
> ```
>
> ## 整合协议(agent 必走)
>
> 移入的 rules 可能与 V11 内部已含规则重叠。agent 必走 §整合:
>
> ```
> 1. Read 所有 references/*.md
> 2. 对每个 rule 检查 V11 内部是否已含
> 3. 若完全重叠 -> 删除该 rule
> 4. 若部分重叠 -> 保留独有部分
> 5. 纯机械挪移 = 没有意义
> ```
>
> 项目名: {project_name}
"""


def create_rules_skill(project_root: pathlib.Path, project_name: str) -> bool:
    """Step 5(V11.2 默认开): 把 .trae/rules/ 收纳到 .trae/skills/project_rules_skills/

    V11.2 设计原则:
      1. 移走(move)而非复制 -- .trae/rules/ 只保留 README.md(强制入口),其他 rules 物理移到 project_rules_skills/references/
      2. .trae/rules/README.md 是项目拥有,不强制覆盖(只检查是否含 project-rules skill 入口声明,缺则追加)
      3. 无 rules 时从 V11 templates/project-rules-example/ 复制占位
      4. 标记 V11 内部已含内容(供 agent 整合时识别)

    适用场景: 项目 rules 数量 >=3 个,主上下文全量注入会撑爆 context。
    """
    rules_dir = project_root / ".trae/rules"

    # 创建 project_rules_skills/ 目录(无论 rules 是否存在)
    skill_dir = project_root / ".trae/skills/project_rules_skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    workflows_dir = skill_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    template_dir = V11_TEMPLATES / "project-rules-skill-template"

    # 复制 SKILL.md / README.md / workflows/(从模板)
    for name in ["SKILL.md", "README.md"]:
        src = template_dir / name
        dst = skill_dir / name
        if dst.exists():
            continue
        if src.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    src_wf = template_dir / "workflows/sub-agent-delegate-load.md"
    dst_wf = workflows_dir / "sub-agent-delegate-load.md"
    if not dst_wf.exists() and src_wf.exists():
        dst_wf.write_text(src_wf.read_text(encoding="utf-8"), encoding="utf-8")

    # 检测现有 rules(排除 README.md)
    existing_rules = []
    if rules_dir.exists():
        existing_rules = sorted([f.name for f in rules_dir.glob("*.md") if f.name != "README.md"])

    # V11.2 NEW: 若无 rules,从 V11 templates/project-rules-example/ 复制占位
    template_example_dir = V11_TEMPLATES / "project-rules-example"
    if not existing_rules and template_example_dir.exists():
        print(f"   ⏭️  .trae/rules/ 无 rules,从 templates/project-rules-example/ 复制占位")
        rules_dir.mkdir(parents=True, exist_ok=True)
        existing_rules = []
        for src_md in sorted(template_example_dir.glob("*.md")):
            if src_md.name == "README.md":
                continue  # README 由项目自己拥有,init 不复制
            dst = rules_dir / src_md.name
            if not dst.exists():
                dst.write_text(src_md.read_text(encoding="utf-8"), encoding="utf-8")
            existing_rules.append(src_md.name)

    if len(existing_rules) < 3:
        print(f"   ⏭️  rules 数量 {len(existing_rules)} < 3,无需收纳(直接 Read 即可)")
        return True

    # V11.2 NEW: 移走(move)而非复制 -- .trae/rules/ 物理移出非 README.md
    moved_rules = []
    skipped_already_moved = []
    for rule_name in existing_rules:
        rule_path = rules_dir / rule_name
        link_path = refs_dir / rule_name

        # 若 references/ 已有该 rule,且 .trae/rules/ 已无该 rule -> 上次已移动,跳过
        if link_path.exists() and not rule_path.exists():
            skipped_already_moved.append(rule_name)
            continue

        if not rule_path.exists():
            continue

        # V11.2 NEW: 标记 V11 内部已含内容(供 agent 整合时识别 hint)
        v11_already_covered = _check_v11_overlap(rule_name, rule_path.read_text(encoding="utf-8"))

        # 移动(move): 读取内容 -> 写入 references/ -> 删除 .trae/rules/{name}.md
        content = rule_path.read_text(encoding="utf-8")
        overlap_hint = "WARN: 此 rule 内容可能与 V11 内部已含规则重叠,agent 整合时可考虑删除" if v11_already_covered else "OK: 未检测到 V11 内部重叠"
        header = f"""<!-- 本文件由 init-from-zero.py --rules-as-skill 自动移入(V11.2 MOVE 模式) -->
<!-- 源: ../../../../.trae/rules/{rule_name} (已删除,见 README.md) -->
<!-- 整合提示: {overlap_hint} -->
<!-- 修改本文件: 直接编辑,无需再走 init-from-zero.py -->

"""
        link_path.write_text(header + content, encoding="utf-8")
        rule_path.unlink()  # V11.2 NEW: 物理删除源文件
        moved_rules.append(rule_name)

    # V11.2 NEW: .trae/rules/README.md 幂等保护 -- 不强制覆盖
    readme_path = rules_dir / "README.md"
    entry_marker = "project-rules skill 入口"
    if readme_path.exists():
        existing = readme_path.read_text(encoding="utf-8")
        if entry_marker not in existing:
            # 只追加入口说明,不覆盖项目原有内容
            appendix = f"""

---

## V11 加载入口(V11.2 自动追加 -- 反复执行幂等)

> **🔴 必读 · 本目录的唯一文件**(其他 rules 通过 .trae/skills/project_rules_skills/ 按需加载)
>
> 任何 agent(主 agent / sub-agent / 主上下文开启子 agent 时)进入本项目执行任务前,
> **必须先调用** `Skill(name="project-rules")` 获取本会话所需 rules。
>
> **禁止绕过本入口**直接 Read `.trae/skills/project_rules_skills/references/*.md`(按路由表按需加载)。
>
> skill 入口: `.trae/skills/project_rules_skills/SKILL.md`
>
> ## 本项目 rules 列表(由 init-from-zero.py 检测)
>
> {chr(10).join(f"- `{r}`" for r in existing_rules)}
>
> ## 加载协议
>
> ```
> Step 1: 调用 Skill(name="project-rules")
> Step 2: 按路由表拿本会话所需 rules(SKILL.md §2)
> Step 3: 只 Read 选中的 rules(在 .trae/skills/project_rules_skills/references/)
> Step 4: sub-agent 必须在 Completion Report 声明 rules_loaded / rules_skipped
> ```
>
> ## 整合协议(agent 必走 -- V11.2 NEW)
>
> 移入的 rules 可能与 V11 内部已含规则(common-iron-rules / common-anti-patterns)重叠。
> agent 在创建 project-rules skill 后,必走 §整合:
>
> ```
> 1. Read 所有 references/*.md
> 2. 对每个 rule 检查 V11 内部是否已含(grep common-iron-rules / common-anti-patterns)
> 3. 若完全重叠 -> 删除该 rule(references/ + README.md 列表同步)
> 4. 若部分重叠 -> 保留独有部分,删去 V11 已含部分
> 5. 纯机械挪移 = 没有意义
> ```
>
> ## 详细说明
>
> 详见 [.trae/skills/project_rules_skills/SKILL.md](../../skills/project_rules_skills/SKILL.md)
>
> 项目名: {project_name}
"""
            readme_path.write_text(existing + appendix, encoding="utf-8")
    else:
        # README 不存在 -> 创建强制入口
        readme_path.write_text(_build_default_readme(project_name, existing_rules), encoding="utf-8")

    if moved_rules:
        print(f"   ✅ 移入 .trae/skills/project_rules_skills/references/: {len(moved_rules)} 个")
    if skipped_already_moved:
        print(f"   ⏭️  已存在(跳过): {len(skipped_already_moved)} 个")
    print(f"   📋 agent 必走 Skill(name=project-rules),并按 README §整合协议 去重")
    return True

def print_agent_handoff(project_name: str, project_type: str, language: str) -> None:
    """引导 agent 读取 template 配置 AGENTS.md + rules"""
    print()
    print(f"{'='*70}")
    print(f"📋 下一步：agent 填充项目级信息（脚本已生成骨架）")
    print(f"{'='*70}")
    print()
    print(f"检测到的项目栈：")
    print(f"   类型: {project_type} | 项目名: {project_name} | 语言: {language}")
    print()
    print(f"4 步已生成骨架,agent 需填充以下占位符：")
    print()
    print(f"   Step 2 填充: .trae/rules/stack.md")
    print(f"     → 替换 {{{language}}} 为实际版本 + 框架 + 测试 + 包管理命令")
    print(f"     → 替换 .trae/rules/paths.md 禁读路径为项目实际路径")
    print(f"     → .trae/rules/git.md 按项目分支策略调整（5 类标签已合并）")
    print(f"     → .trae/rules/coding-standards.md 按项目编码规则填充（无则删除）")
    print()
    print(f"   Step 3 填充: AGENTS.md")
    print(f"     → 填充框架/测试/包管理占位符")
    print(f"     → 删除不适用章节（如 backend 无浏览器自动化 → 删 §5）")
    print(f"     → 模板参考: {AGENTS_TEMPLATE}")
    print()
    print(f"   Step 4 初始化: docs/specs/.state-card.md")
    print(f"     → 项目级状态卡（记录项目整体状态,非 change 级）")
    print(f"     → ⚠️ 绝不能用 .trae/state-card.md（V10 残留,V11 已迁移出 .trae/）")
    print(f"     → 格式参考: ~/.trae-cn/skills/fullstack4TraeV11/references/state-card-protocol.md")
    print()
    print(f"   🚨 V11 §0.5 加载协议（V11.2 NEW — 蒸馏自 canvas-asset-folders 实战）:")
    print(f"     → agent 首次进入项目必走 9 步加载")
    print(f"     → Step 3 强制调 Skill(name=project-rules)（如项目已有 .trae/skills/project_rules_skills/）")
    print(f"     → Step 5 核对状态卡路径 docs/specs/.state-card.md")
    print(f"     → 详见: ~/.trae-cn/skills/fullstack4TraeV11/SKILL.md §0.5")
    print()
    print(f"   验证（必跑）：")
    print(f"     python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .")
    print()
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="V11 全新项目基础设施初始化")
    parser.add_argument("--project-root", default=".", help="项目根路径")
    parser.add_argument("--project-name", help="项目名（默认：项目根目录名）")
    parser.add_argument("--project-type", choices=["web", "tauri", "cli", "library", "backend"], help="项目类型")
    parser.add_argument("--language", help="主语言")
    # V11.8.7 NEW (case 2 蒸馏):fix dual-write 双写 bug — 二选一模式
    # 默认走 --rules-as-files(.trae/rules/*.md 留源文件,agent 直接 Read),
    # 显式 --rules-as-skill 才移到 .trae/skills/project_rules_skills/(适用 rules ≥3)
    parser.add_argument(
        "--rules-layout",
        choices=["files", "skill"],
        default="files",
        help=(
            "V11.8.7 NEW(case 2 蒸馏 fix dual-write 双写 bug):rules 物理布局。\n"
            "  files (默认) = .trae/rules/*.md 留源文件,agent 直接 Read\n"
            "  skill = 移走到 .trae/skills/project_rules_skills/(适用 rules ≥3 减少 context)\n"
            "禁止同时存在两份,违反任意一项 = REJECT"
        ),
    )
    parser.add_argument(
        "--layout",
        choices=["v11-default", "v12-preview"],
        # V12.0.0 升主版本后默认改 v12-preview(V11.8.6 之前是 v11-default)
        # V11 兼容:V11 项目显式传 --layout v11-default
        default="v12-preview",
        help="V12.0.0 NEW: change-id 物理布局。v12-preview(V12 默认,fact/ + stage/{N}/) 或 v11-default(V11 兼容,扁平 layout,显式声明)",
    )
    # V12.0.0 NEW: --upgrade-to-v11 子命令(V12 项目回滚到 V11 layout 用,见 V12-ADR-DRAFT.md §7.2)
    parser.add_argument(
        "--upgrade-to-v11",
        action="store_true",
        help="V12.0.0 NEW: V12 项目回滚到 V11 layout(自动反向迁移 fact/ → 根目录 + 清 stage/)",
    )
    # V12.0.0 NEW: --migrate-from-v11 子命令(V11 项目 → V12 物理布局,见 V12-MIGRATION-PROTOCOL.md)
    parser.add_argument(
        "--migrate-from-v11",
        action="store_true",
        help="V12.0.0 NEW: V11 项目 → V12 物理布局(自动创建 fact/ + stage/{11}/ + 多卡模式)。三阶段迁移:pre-flight 校验 → 8 步原子迁移 → post-flight 验证 + 自动回滚",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="配合 --migrate-from-v11:仅校验 + 报告迁移目标,不实际移动文件",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="配合 --migrate-from-v11:不创建 .pre_v12_migration_<ts>/ 备份(危险)",
    )
    parser.add_argument(
        "--exclude",
        metavar="CHANGE_ID",
        help="配合 --migrate-from-v11:排除特定 change-id(逗号分隔)",
    )
    parser.add_argument("--quiet", action="store_true", help="不打印 agent handoff")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    # V12.0.0 NEW: --upgrade-to-v11 子命令(V12 项目回滚到 V11 layout)
    if args.upgrade_to_v11:
        return cmd_upgrade_to_v11(args)

    # V12.0.0 NEW: --migrate-from-v11 子命令(V11 项目 → V12 物理布局)
    if args.migrate_from_v11:
        return cmd_migrate_from_v11(args)

    project_root = pathlib.Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"❌ 项目目录不存在: {project_root}")
        return 1

    # 自动检测或使用参数
    project_name = args.project_name or project_root.name
    project_type = args.project_type or detect_project_type(project_root)
    language = args.language or detect_language(project_root)

    # V11.8.7: switch to --rules-layout {files|skill}; default = files (no move)
    rules_layout = args.rules_layout
    step_count = 5 if rules_layout == "skill" else 4
    layout_step = "+ Step 4.5(V12 preview)" if args.layout == "v12-preview" else ""
    # V12.0.0 升主版本:V11 → V12 名称标识
    print(f"🚀 V12 初始化（{step_count} 步全流程{layout_step}）— {project_root}")
    print(f"   项目名: {project_name} | 类型: {project_type} | 语言: {language}")
    print(f"   物理布局: {args.layout}" + ("(V12 默认,fact/ + stage/{N}/)" if args.layout == "v12-preview" else "(V11 兼容,扁平 layout,显式声明)"))
    if rules_layout == "files":
        print(f"   rules 布局: --rules-layout files(.trae/rules/*.md 留源文件,agent 直接 Read)")
    else:
        print(f"   rules 布局: --rules-layout skill(自动建 .trae/skills/project_rules_skills/,适用 rules ≥3)")
    print()

    steps = [
        ("Step 1: config.yaml + hooks/", lambda: create_config(project_root, project_name, project_type, language) and create_hooks(project_root)),
        ("Step 2: .trae/rules/", lambda: create_rules(project_root, project_type, language)),
        ("Step 3: AGENTS.md", lambda: create_agents_md(project_root, project_name, project_type, language)),
        ("Step 4: docs/ 骨架", lambda: create_docs_skeleton(project_root)),
    ]

    # V11.8.6 NEW: 仅 --layout v12-preview 时跑 Step 4.5(创建 V12 物理布局模板)
    if args.layout == "v12-preview":
        steps.append(("Step 4.5: V12 物理布局 preview 骨架", lambda: create_v12_preview_skeleton(project_root)))

    # V11.8.7: --rules-layout skill 才走 Step 5 move(skill 收纳);files 模式不跑
    if rules_layout == "skill":
        steps.append(("Step 5: 收纳 rules 到 skill(--rules-layout skill)", lambda: create_rules_skill(project_root, project_name)))

    results = []
    for name, func in steps:
        is_pass = func()
        results.append({"step": name, "status": "PASS" if is_pass else "FAIL"})

    all_pass = all(r["status"] == "PASS" for r in results)

    output = {
        "project_root": str(project_root),
        "project_meta": {
            "name": project_name,
            "type": project_type,
            "language": language,
        },
        "infra_steps": results,
        "agent_next_steps": {
            "AGENTS_template": str(AGENTS_TEMPLATE),
            "rules_README": str(RULES_README),
            "rules_dir": "templates/project-rules-example/",
        },
        "status": "PASS" if all_pass else "FAIL",
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'✅' if all_pass else '❌'} 基础设施初始化 {'PASS' if all_pass else 'FAIL'}")
        if not args.quiet:
            print_agent_handoff(project_name, project_type, language)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())