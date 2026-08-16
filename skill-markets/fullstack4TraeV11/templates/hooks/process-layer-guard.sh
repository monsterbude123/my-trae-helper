#!/usr/bin/env bash
# V11.8.6 NEW: process-layer-guard.sh — V12 物理布局路径校验 hook
#
# 触发时机: pre-commit(检查暂存区 .md 文件路径) 或 pre-stage.sh(检查本次 stage 写入)
# 退出码: 0=PASS / 1=FAIL
#
# 校验规则(对齐 templates/change-dir-layout-v12-preview.md §2):
#   1. docs/specs/changes/{id}/ 根目录禁止任何 .md(必须落 fact/ 或 stage/{N}/)
#   2. fact/ 禁止 process 层命名(*-notes / handoff* / diagnosis / fix-* / v[0-9]*)
#   3. stage/{N}/ 禁止 fact 层命名(spec.md / plan.md / contracts/)
#
# 跨平台: macOS / Linux / Git Bash on Windows

set -euo pipefail

# Git Bash 在 Windows 下默认 nullglob 关闭,空 glob 当字面量处理 → 加 shopt -s nullglob
shopt -s nullglob 2>/dev/null || true

PROJECT_ROOT="${PROJECT_ROOT:-.}"
CHANGES_DIR="$PROJECT_ROOT/docs/specs/changes"

if [ ! -d "$CHANGES_DIR" ]; then
    echo "✅ process-layer-guard PASS ($CHANGES_DIR 不存在,跳过)"
    exit 0
fi

errors=0

# 遍历 docs/specs/changes/{id}/ 子目录(排除 _v12-preview-template 与 archive)
for change_dir in "$CHANGES_DIR"/*/; do
    change_dir="${change_dir%/}"
    change_id="$(basename "$change_dir")"

    # 排除 _v12-preview-template 模板目录(自身就是模板)
    if [ "$change_id" = "_v12-preview-template" ]; then
        continue
    fi

    # 仅校验 v12-preview 项目(即有 fact/ + stage/ 两个目录的项目)
    is_v12_preview=false
    if [ -d "$change_dir/fact" ] && [ -d "$change_dir/stage" ]; then
        is_v12_preview=true
    fi

    # Rule 1: docs/specs/changes/{id}/ 根目录禁止任何 .md(README 除外)
    # 仅对 v12-preview 项目启用(V11-default 项目允许根 .md)
    if [ "$is_v12_preview" = "true" ]; then
        for f in "$change_dir"/*.md; do
            if [ -f "$f" ]; then
                fname="$(basename "$f")"
                echo "❌ FAIL [$change_id] $fname 落在 docs/specs/changes/$change_id/ 根目录"
                echo "    必须落 fact/ 或 stage/{N}/ —— 见 templates/change-dir-layout-v12-preview.md §0"
                errors=$((errors+1))
            fi
        done
    fi

    # Rule 2: fact/ 禁止 process 层命名
    if [ -d "$change_dir/fact" ]; then
        for f in "$change_dir/fact"/*; do
            if [ ! -f "$f" ]; then continue; fi
            fname="$(basename "$f")"
            # 放行 README / spec / plan / test-plan / prototype / contracts / .state-card
            case "$fname" in
                README.md|spec.md|plan.md|test-plan.md|prototype.md|.state-card.md)
                    continue ;;
            esac
            # 禁止 *-notes.md / *handoff*.md / diagnosis-* / fix-* / v[0-9]*
            if echo "$fname" | grep -qE '(notes\.md|handoff.*\.md|diagnosis-|^fix-|^v[0-9])'; then
                echo "❌ FAIL [$change_id] fact/$fname 是 process 层命名"
                echo "    必移至 stage/{N}/ —— 见 templates/change-dir-layout-v12-preview.md §2"
                errors=$((errors+1))
            fi
        done
        # contracts/ 子目录允许,但其内文件必须是契约 4 件套
        if [ -d "$change_dir/fact/contracts" ]; then
            for f in "$change_dir/fact/contracts"/*.md; do
                if [ ! -f "$f" ]; then continue; fi
                fname="$(basename "$f")"
                case "$fname" in
                    domain-models.md|api-contracts.md|events.md|validation-rules.md)
                        continue ;;
                esac
                echo "❌ FAIL [$change_id] fact/contracts/$fname 不在契约 4 件套内"
                echo "    必移至 stage/2-contract/ —— 见 references/stage-physical-isolation.md §1"
                errors=$((errors+1))
            done
        fi
    fi

    # Rule 3: stage/{N}/ 禁止 fact 层命名
    if [ -d "$change_dir/stage" ]; then
        for stage_sub in "$change_dir/stage"/*/; do
            stage_sub="${stage_sub%/}"
            stage_name="$(basename "$stage_sub")"
            for f in "$stage_sub"/*.md; do
                if [ ! -f "$f" ]; then continue; fi
                fname="$(basename "$f")"
                # 禁止 spec.md / plan.md / contracts/
                case "$fname" in
                    spec.md|plan.md|README.md)
                        echo "❌ FAIL [$change_id] stage/$stage_name/$fname 是 fact 层命名"
                        echo "    必移至 fact/ —— 见 templates/change-dir-layout-v12-preview.md §2"
                        errors=$((errors+1))
                        continue ;;
                esac
                if [ -d "$stage_sub/contracts" ]; then
                    echo "❌ FAIL [$change_id] stage/$stage_name/contracts/ 禁止(fact 层命名)"
                    echo "    必移至 fact/contracts/ —— 见 templates/change-dir-layout-v12-preview.md §2"
                    errors=$((errors+1))
                fi
            done
        done
    fi
done

if [ "$errors" -gt 0 ]; then
    echo "❌ process-layer-guard FAIL: $errors 处路径违规"
    echo "   详见 templates/change-dir-layout-v12-preview.md §2"
    exit 1
fi

echo "✅ process-layer-guard PASS (v12-preview 项目路径校验全通过)"
exit 0