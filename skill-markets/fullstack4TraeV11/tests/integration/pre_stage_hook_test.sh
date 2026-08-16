#!/usr/bin/env bash
# tests/integration/pre_stage_hook_test.sh
# P0-2 + P2-3 真反例固化:pre-stage.sh 强制调 stage-gate.py,覆盖 4 个核心场景。
#
# 用例(来自 [TODO-REPAIR]):
#   1. 状态卡合法 + 无 EXPECTED_NEXT_STAGE → exit 0
#   2. 状态卡 + 合法 next stage → exit 0
#   3. 状态卡 + 非法 next stage → exit 1 或 2(transition FAIL)
#   4. V11_SCRIPTS 不存在 → exit 1
#
# 关键约束:hook 内部用 `git rev-parse --show-toplevel` 探测 PROJECT_ROOT,
# 所以每个 case 必须在 tmp 中 `git init`,再把 state card 放在 tmp/docs/specs/。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V11_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK_PATH="$V11_ROOT/templates/hooks/pre-stage.sh"
STAGE_GATE_PATH="$V11_ROOT/scripts/stage-gate.py"

# logs/integration/ 落报告(用 POSIX 路径,Windows 下 bash 可访问)
LOG_DIR="$V11_ROOT/logs/integration"
mkdir -p "$LOG_DIR"
REPORT="$LOG_DIR/pre_stage_hook_test_$(date +%Y%m%d%H%M%S).log"
: > "$REPORT"

PASS_COUNT=0
FAIL_COUNT=0

# ----------- helper:写状态卡 fixture -----------
write_state_card() {
    local path="$1"
    local current_stage="$2"
    mkdir -p "$(dirname "$path")"
    cat > "$path" <<EOF
---
card_type: change
card_id: integration-test-card
version: "1.0.0"
current_stage: $current_stage
stage_status: working
stage_started_at: 2026-08-16T00:00:00
stage_ended_at: null
updated_at: 2026-08-16T00:00:00
updated_by: integration-test
health: "🟢 on-track"
artifacts: []
visual_evidence:
  status: unverified
  screenshots: []
  verified_at: null
gate_result:
  status: PENDING
  gate: null
  output: null
  verified_at: null
next_stage:
  id: null
  skill_name: null
  expected_inputs: []
  prerequisites: []
blocked_by: null
actor: integration-test
duration_minutes: 0
notes: ""
---
EOF
}

# ----------- helper:准备 project root(tmp + git init + state card) -----------
prepare_project() {
    local tmp_dir="$1"
    local current_stage="$2"
    mkdir -p "$tmp_dir/docs/specs"
    write_state_card "$tmp_dir/docs/specs/.state-card.md" "$current_stage"
    # git init:让 hook 的 git rev-parse 探测到 PROJECT_ROOT = tmp_dir
    git -C "$tmp_dir" init -q 2>/dev/null || true
    git -C "$tmp_dir" config user.email "test@example.com" 2>/dev/null || true
    git -C "$tmp_dir" config user.name "test" 2>/dev/null || true
    # 提交 state card 进 git,避免 .gitignore 干扰
    git -C "$tmp_dir" add -f docs/specs/.state-card.md 2>/dev/null || true
    git -C "$tmp_dir" commit -q -m "test state card" 2>/dev/null || true
}

# ----------- helper:跑单个 case -----------
run_case() {
    local case_no="$1"
    local case_name="$2"
    local expected_exit="$3"
    local current_stage="$4"
    local expected_next_stage="$5"
    local v11_scripts_override="$6"  # "valid" / "nonexistent"

    local tmp_dir
    tmp_dir="$(mktemp -d -t prestage.XXXXXX)"
    prepare_project "$tmp_dir" "$current_stage"

    {
        echo ""
        echo "============================================================"
        echo "[CASE $case_no] $case_name"
        echo "        expected_exit=$expected_exit"
        echo "        tmp_dir=$tmp_dir"
        echo "        current_stage=$current_stage"
        echo "        expected_next_stage=${expected_next_stage:-<none>}"
        echo "        v11_scripts_override=$v11_scripts_override"
        echo "============================================================"
    } | tee -a "$REPORT"

    # 环境变量
    if [ "$v11_scripts_override" = "nonexistent" ]; then
        # CASE 4:必须让所有 3 个 fallback 都失败
        #   1. V11_SCRIPTS env → 设 /nonexistent
        #   2. ~/.trae-cn/skills → 设 HOME=/nonexistent-home
        #   3. $(dirname $0)/../../scripts/ → hook 不在 repo 内(从 tmp 外的位置复制 hook 到 tmp/templates/hooks/)
        # 我们用方案:把 hook 复制到 tmp 内,让第 3 个 fallback 找不到
        mkdir -p "$tmp_dir/templates/hooks"
        cp "$HOOK_PATH" "$tmp_dir/templates/hooks/pre-stage.sh"
        chmod +x "$tmp_dir/templates/hooks/pre-stage.sh"
        export V11_SCRIPTS="/nonexistent"
        export HOME="/nonexistent-home"
        HOOK_TO_RUN="$tmp_dir/templates/hooks/pre-stage.sh"
    else
        # CASE 1-3:用 V11_ROOT/scripts 作为 V11_SCRIPTS(强制命中优先级 1)
        export V11_SCRIPTS="$V11_ROOT/scripts"
        HOOK_TO_RUN="$HOOK_PATH"
    fi

    export V11_GATE_ENFORCED=true
    export V11_GATE_STAGE="$current_stage"
    export V11_GATE_CALLER="test-caller-$case_no"
    export STATE_CARD_PATH="$tmp_dir/docs/specs/.state-card.md"
    export EXPECTED_NEXT_STAGE="$expected_next_stage"

    set +e
    bash "$HOOK_TO_RUN" 2>&1
    local real_exit=$?
    set -e

    echo "" | tee -a "$REPORT"
    echo "[CASE $case_no] real_exit=$real_exit (expected $expected_exit)" | tee -a "$REPORT"

    if [ "$real_exit" -eq "$expected_exit" ]; then
        echo "[CASE $case_no PASS]" | tee -a "$REPORT"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "[CASE $case_no FAIL]" | tee -a "$REPORT"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    unset V11_GATE_ENFORCED V11_GATE_STAGE V11_GATE_CALLER STATE_CARD_PATH EXPECTED_NEXT_STAGE V11_SCRIPTS HOME
    rm -rf "$tmp_dir"
}

# 静态校验:hook 存在 + 可执行
if [ ! -f "$HOOK_PATH" ]; then
    echo "pre-stage.sh NOT FOUND: $HOOK_PATH" | tee -a "$REPORT"
    exit 1
fi
if [ ! -f "$STAGE_GATE_PATH" ]; then
    echo "stage-gate.py NOT FOUND: $STAGE_GATE_PATH" | tee -a "$REPORT"
    exit 1
fi

# ====== CASE 1:状态卡合法 + 无 EXPECTED_NEXT_STAGE → exit 0 ======
run_case 1 "valid card, no EXPECTED_NEXT_STAGE" 0 "3/implement" "" "valid"

# ====== CASE 2:状态卡 + 合法 next stage (-1/intake → 0/plan)→ exit 0 ======
run_case 2 "valid card + legal next stage (0/plan)" 0 "-1/intake" "0/plan" "valid"

# ====== CASE 3:状态卡 + 非法 next stage (5/accept → -1/intake,回退不合法)→ exit 2 ======
run_case 3 "valid card + illegal next stage (5/accept → -1/intake)" 2 "5/accept" "-1/intake" "valid"

# ====== CASE 4:V11_SCRIPTS 不存在 → exit 1 ======
run_case 4 "V11_SCRIPTS not exist" 1 "3/implement" "" "nonexistent"

# ====== 汇总 ======
echo "" | tee -a "$REPORT"
echo "============================================================" | tee -a "$REPORT"
echo "[SUMMARY] PASS=$PASS_COUNT FAIL=$FAIL_COUNT" | tee -a "$REPORT"
echo "Report: $REPORT" | tee -a "$REPORT"
echo "============================================================" | tee -a "$REPORT"

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "[ALL PASS]"
    exit 0
else
    echo "[HAS FAIL]"
    exit 1
fi