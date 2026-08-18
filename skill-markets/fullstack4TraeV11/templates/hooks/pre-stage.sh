#!/usr/bin/env bash
# V12 Pre-stage Gate (HARDENED) — Stage Transition Validation
# HARDENING POINTS (V12 ONLY):
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. Mandatory environment variable validation (V12_GATE_ENFORCED)
#   3. Missing env vars = gate FAIL (exit 1) — cannot bypass
#   4. Real execution of stage-gate.py with --next-stage — no mock/stub PASS
#   5. State card existence check + transition verification
#   6. **V12.0.0**: 物理路径校验(process-layer-guard.sh) — 默认行为
#   7. **V12.0.0**: stage-gate.py --reset-to 强制 default(若 STATE_CARD_RESET_TO 设置)
#
# V12.0 唯一布局:fact/ + stage/{N}/ 物理隔离;每 stage 独立状态卡
# (stage/-1/intake/.state-card.md ~ stage/7/health/.state-card.md)
# current_stage 必为 V12 13 stage 斜杠命名。
#
# Exit codes(继承自 stage-gate.py):
#   0 = PASS
#   1 = state-card field FAIL
#   2 = transition FAIL
#   3 = process-layer-guard FAIL(V12)
#   4 = --reset-to FAIL(V12)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GATE_ID="pre-stage-$(date +%Y%m%d%H%M%S)"

# 跨平台 Python 探测(§4.1.3 协议: PATH → python3 → python → py)
PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_BIN="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_BIN="python"
    elif command -v py >/dev/null 2>&1; then
        PYTHON_BIN="py"
    else
        echo "    [GATE FAIL] python3/python/py 都找不到。请安装 Python 3 或设置 PYTHON_BIN 环境变量。"
        exit 1
    fi
fi

echo "==> [V12 Gate] Pre-stage hardened gate"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- V12 13 stage 斜杠命名列表(与 registry/state-machine.yaml 对齐) ----
VALID_STAGES=(
    "-1/intake"
    "0/plan"
    "0.5/test-plan"
    "1/spec"
    "1.5/prototype"
    "2/contract"
    "3/implement"
    "3.5/real-verify"
    "4/review"
    "4.5/rot-scan"
    "5/accept"
    "6/bug-fix"
    "7/health"
)

# ---- Step 0: MANDATORY environment variable validation ----
echo ""
echo "    [0/4] Environment variable validation (HARDENED):"

VALIDATION_FAILED=0

if [ -z "${V12_GATE_ENFORCED:-}" ]; then
    echo "          x V12_GATE_ENFORCED is NOT SET - gate FAILS"
    echo "          Required: V12_GATE_ENFORCED=true (set by V12 orchestrator)"
    VALIDATION_FAILED=1
else
    echo "          ok V12_GATE_ENFORCED=${V12_GATE_ENFORCED}"
fi

if [ -z "${V12_GATE_STAGE:-}" ]; then
    echo "          x V12_GATE_STAGE is NOT SET - gate FAILS"
    echo "          Required: V12_GATE_STAGE=<stage> (e.g., 1/spec, 3/implement)"
    VALIDATION_FAILED=1
else
    echo "          ok V12_GATE_STAGE=${V12_GATE_STAGE}"
fi

if [ -z "${V12_GATE_CALLER:-}" ]; then
    echo "          x V12_GATE_CALLER is NOT SET - gate FAILS"
    echo "          Required: V12_GATE_CALLER=<caller-name> (e.g., stage-1-agent)"
    VALIDATION_FAILED=1
else
    echo "          ok V12_GATE_CALLER=${V12_GATE_CALLER}"
fi

if [ $VALIDATION_FAILED -ne 0 ]; then
    echo ""
    echo "    [GATE FAIL] Missing mandatory environment variables"
    echo "    Agent cannot bypass this gate without proper V12 orchestrator context."
    echo "    To fix: Ensure V12 orchestrator sets V12_GATE_ENFORCED/STAGE/CALLER."
    exit 1
fi

# ---- Step 1: V12 多卡存在性 + current_stage 校验 ----
echo ""
echo "    [1/4] V12 state card existence + current_stage check:"

# V12 唯一布局: 每 stage 独立状态卡。V12 入口必为 stage/-1/intake/.state-card.md
INTAKE_CARD="$PROJECT_ROOT/stage/-1/intake/.state-card.md"
if [ ! -f "$INTAKE_CARD" ]; then
    echo "          x Intake state card NOT FOUND: $INTAKE_CARD"
    echo "          V12 物理布局要求: stage/-1/intake/.state-card.md 必须存在"
    exit 1
fi
echo "          ok Intake card exists: $INTAKE_CARD"

# 解析 STATE_CARD_PATH(若已设,使用;否则按 V12_GATE_STAGE 选对应 stage 卡)
STATE_CARD="${STATE_CARD_PATH:-}"
if [ -z "$STATE_CARD" ]; then
    # V12 唯一路径: stage/{stage_id}/.state-card.md
    # stage_id 形如 "3/implement" → "stage/3/implement/.state-card.md"
    STATE_CARD="$PROJECT_ROOT/stage/${V12_GATE_STAGE}/.state-card.md"
fi

if [ ! -f "$STATE_CARD" ]; then
    echo "          x V12 stage state card NOT FOUND: $STATE_CARD"
    echo "          V12 物理布局: stage/{N}/.state-card.md 每 stage 独立"
    exit 1
fi
echo "          ok V12 stage card exists: $STATE_CARD"

# current_stage ∈ V12 13 stage 列表(斜杠命名)
CURRENT_STAGE="${V12_GATE_STAGE}"
STAGE_VALID=0
for s in "${VALID_STAGES[@]}"; do
    if [ "$s" = "$CURRENT_STAGE" ]; then
        STAGE_VALID=1
        break
    fi
done
if [ $STAGE_VALID -ne 1 ]; then
    echo "          x current_stage='$CURRENT_STAGE' NOT IN V12 13 stage 列表"
    echo "          Required: ${VALID_STAGES[*]}"
    exit 1
fi
echo "          ok current_stage='$CURRENT_STAGE' ∈ V12 stage 列表"

# ---- Step 2: stage-gate.py script existence check ----
echo ""
echo "    [2/4] stage-gate.py script existence check:"

V12_SCRIPTS_DIR="${V12_SCRIPTS:-}"
STAGE_GATE_SCRIPT=""

# V12_SCRIPTS 解析优先级:
#   优先级 1:显式 $V12_SCRIPTS 环境变量
#   优先级 2:用户全局 ~/.trae-cn/skills/fullstack4TraeV11/scripts
#   优先级 3:当前仓库 scripts/(init-from-zero 跑的用户本地版)
if [ -n "$V12_SCRIPTS_DIR" ] && [ -f "$V12_SCRIPTS_DIR/stage-gate.py" ]; then
    STAGE_GATE_SCRIPT="$V12_SCRIPTS_DIR/stage-gate.py"
elif [ -f "$HOME/.trae-cn/skills/fullstack4TraeV11/scripts/stage-gate.py" ]; then
    V12_SCRIPTS_DIR="$HOME/.trae-cn/skills/fullstack4TraeV11/scripts"
    STAGE_GATE_SCRIPT="$V12_SCRIPTS_DIR/stage-gate.py"
elif [ -f "$(dirname "$0")/../../scripts/stage-gate.py" ]; then
    V12_SCRIPTS_DIR="$(cd "$(dirname "$0")/../.." && pwd)/scripts"
    STAGE_GATE_SCRIPT="$V12_SCRIPTS_DIR/stage-gate.py"
fi

if [ -z "$STAGE_GATE_SCRIPT" ] || [ ! -f "$STAGE_GATE_SCRIPT" ]; then
    echo "          x stage-gate.py NOT FOUND"
    echo "          Searched: \$V12_SCRIPTS, ~/.trae-cn/skills/, \$(script_dir)/../../scripts/"
    echo "          Required for real stage transition validation."
    exit 1
else
    echo "          ok stage-gate.py exists: $STAGE_GATE_SCRIPT"
fi

# ---- Step 3: Real execution -- stage-gate.py with --next-stage ----
echo ""
echo "    [3/4] Real execution (no mock/stub PASS):"

EXPECTED_NEXT_STAGE="${EXPECTED_NEXT_STAGE:-}"
NEXT_STAGE_ARG=""
if [ -n "$EXPECTED_NEXT_STAGE" ]; then
    NEXT_STAGE_ARG="--next-stage $EXPECTED_NEXT_STAGE"
    echo "          Mode: transition validation (--next-stage)"
else
    echo "          Mode: state-card field validation only"
fi

echo "          Running: $PYTHON_BIN $STAGE_GATE_SCRIPT --state-card $STATE_CARD --project-root $PROJECT_ROOT $NEXT_STAGE_ARG"

# 调用 stage-gate.py(--next-stage 校验 transition;exit code 0=PASS / 1=field FAIL / 2=transition FAIL)
set +e
"$PYTHON_BIN" "$STAGE_GATE_SCRIPT" \
    --state-card "$STATE_CARD" \
    --project-root "$PROJECT_ROOT" \
    $NEXT_STAGE_ARG
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo "          ok stage-gate.py PASS"
elif [ $EXIT_CODE -eq 2 ]; then
    echo "          x stage-gate.py transition FAIL (exit 2)"
    echo "    [GATE FAIL] Stage transition not allowed by state machine"
    exit $EXIT_CODE
else
    echo "          x stage-gate.py field FAIL (exit $EXIT_CODE)"
    echo "    [GATE FAIL] Stage transition not allowed (state-card validation failed)"
    exit $EXIT_CODE
fi

# ---- V12 Step 3.5: process-layer-guard.sh 物理路径校验 ----
# V12 默认行为:fact/ + stage/{N}/ 物理布局强校验
echo ""
echo "    [3.5/4] process-layer-guard.sh (V12 physical layout):"

# 探测 process-layer-guard.sh
PROCESS_LAYER_GUARD=""
if [ -n "$V12_SCRIPTS_DIR" ] && [ -f "$V12_SCRIPTS_DIR/templates/hooks/process-layer-guard.sh" ]; then
    PROCESS_LAYER_GUARD="$V12_SCRIPTS_DIR/templates/hooks/process-layer-guard.sh"
elif [ -f "$HOME/.trae-cn/skills/fullstack4TraeV11/templates/hooks/process-layer-guard.sh" ]; then
    PROCESS_LAYER_GUARD="$HOME/.trae-cn/skills/fullstack4TraeV11/templates/hooks/process-layer-guard.sh"
elif [ -f "$(dirname "$STAGE_GATE_SCRIPT")/../templates/hooks/process-layer-guard.sh" ]; then
    PROCESS_LAYER_GUARD="$(dirname "$STAGE_GATE_SCRIPT")/../templates/hooks/process-layer-guard.sh"
fi

if [ -z "$PROCESS_LAYER_GUARD" ] || [ ! -f "$PROCESS_LAYER_GUARD" ]; then
    echo "          x process-layer-guard.sh NOT FOUND — V12 物理布局强校验必须存在"
    echo "    [GATE FAIL] V12 物理路径校验脚本不可缺失"
    exit 3
fi
PROJECT_ROOT="$PROJECT_ROOT" bash "$PROCESS_LAYER_GUARD"
PLG_EXIT=$?
if [ $PLG_EXIT -ne 0 ]; then
    echo "          x process-layer-guard FAIL (exit $PLG_EXIT)"
    echo "    [GATE FAIL] V12 物理布局路径违规 — 见 templates/change-dir-layout-v12-preview.md §2"
    exit 3
fi
echo "          ok process-layer-guard PASS"

# ---- Step 4: Gate signature (SHA-256 hash) ----
echo ""
echo "    [4/4] Gate signature generation:"

GATE_RESULT="status=PASS,gate_id=$GATE_ID,stage=${V12_GATE_STAGE},caller=${V12_GATE_CALLER},next_stage=${EXPECTED_NEXT_STAGE:-none}"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

echo ""
echo "==> [V12 Gate] Pre-stage PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Signature: $SIGNATURE"