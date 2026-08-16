#!/usr/bin/env bash
# V11 Pre-stage Gate (HARDENED) — Stage Transition Validation
# HARDENING POINTS:
#   1. set -euo pipefail (fail-fast + pipe error propagation)
#   2. Mandatory environment variable validation (V11_GATE_ENFORCED)
#   3. Missing env vars = gate FAIL (exit 1) — cannot bypass
#   4. Real execution of stage-gate.py with --next-stage — no mock/stub PASS
#   5. State card existence check + transition verification
#
# V11.8.x 新协议(P0-2):用 --next-stage 校验 current_stage → next_stage
# 转换合法性,而非旧 --stage(只能校验一致性)。EXPECTED_NEXT_STAGE
# 由 orchestrator 提供时,真校验状态机转换。
#
# Exit codes(继承自 stage-gate.py):
#   0 = PASS
#   1 = state-card field FAIL
#   2 = transition FAIL

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

echo "==> [V11 Gate] Pre-stage hardened gate"
echo "    Gate ID: $GATE_ID"

cd "$PROJECT_ROOT"

# ---- Step 0: MANDATORY environment variable validation ----
echo ""
echo "    [0/4] Environment variable validation (HARDENED):"

VALIDATION_FAILED=0

if [ -z "${V11_GATE_ENFORCED:-}" ]; then
    echo "          x V11_GATE_ENFORCED is NOT SET - gate FAILS"
    echo "          Required: V11_GATE_ENFORCED=true (set by V11 orchestrator)"
    VALIDATION_FAILED=1
else
    echo "          ok V11_GATE_ENFORCED=${V11_GATE_ENFORCED}"
fi

if [ -z "${V11_GATE_STAGE:-}" ]; then
    echo "          x V11_GATE_STAGE is NOT SET - gate FAILS"
    echo "          Required: V11_GATE_STAGE=<stage> (e.g., 1/spec, 2/impl)"
    VALIDATION_FAILED=1
else
    echo "          ok V11_GATE_STAGE=${V11_GATE_STAGE}"
fi

if [ -z "${V11_GATE_CALLER:-}" ]; then
    echo "          x V11_GATE_CALLER is NOT SET - gate FAILS"
    echo "          Required: V11_GATE_CALLER=<caller-name> (e.g., stage-1-agent)"
    VALIDATION_FAILED=1
else
    echo "          ok V11_GATE_CALLER=${V11_GATE_CALLER}"
fi

if [ $VALIDATION_FAILED -ne 0 ]; then
    echo ""
    echo "    [GATE FAIL] Missing mandatory environment variables"
    echo "    Agent cannot bypass this gate without proper V11 orchestrator context."
    echo "    To fix: Ensure V11 orchestrator sets V11_GATE_ENFORCED/STAGE/CALLER."
    exit 1
fi

# ---- Step 1: State card existence check ----
echo ""
echo "    [1/4] State card existence check:"

STATE_CARD="${STATE_CARD_PATH:-}"
if [ -z "$STATE_CARD" ]; then
    STATE_CARD="$(find docs/specs/changes -name .state-card.md 2>/dev/null | head -1 || true)"
fi
if [ -z "$STATE_CARD" ] && [ -f "$PROJECT_ROOT/docs/specs/.state-card.md" ]; then
    STATE_CARD="$PROJECT_ROOT/docs/specs/.state-card.md"
fi

if [ ! -f "$STATE_CARD" ]; then
    echo "          x State card NOT FOUND: $STATE_CARD"
    echo "          Required for stage transition validation."
    exit 1
else
    echo "          ok State card exists: $STATE_CARD"
fi

# ---- Step 2: stage-gate.py script existence check ----
echo ""
echo "    [2/4] stage-gate.py script existence check:"

V11_SCRIPTS_DIR="${V11_SCRIPTS:-}"
STAGE_GATE_SCRIPT=""

# V11_SCRIPTS 解析优先级(P0-2 已实装的协议):
#   优先级 1:显式 $V11_SCRIPTS 环境变量
#   优先级 2:用户全局 ~/.trae-cn/skills/fullstack4TraeV11/scripts
#   优先级 3:当前仓库 scripts/(init-from-zero 跑的用户本地版)
if [ -n "$V11_SCRIPTS_DIR" ] && [ -f "$V11_SCRIPTS_DIR/stage-gate.py" ]; then
    STAGE_GATE_SCRIPT="$V11_SCRIPTS_DIR/stage-gate.py"
elif [ -f "$HOME/.trae-cn/skills/fullstack4TraeV11/scripts/stage-gate.py" ]; then
    V11_SCRIPTS_DIR="$HOME/.trae-cn/skills/fullstack4TraeV11/scripts"
    STAGE_GATE_SCRIPT="$V11_SCRIPTS_DIR/stage-gate.py"
elif [ -f "$(dirname "$0")/../../scripts/stage-gate.py" ]; then
    V11_SCRIPTS_DIR="$(cd "$(dirname "$0")/../.." && pwd)/scripts"
    STAGE_GATE_SCRIPT="$V11_SCRIPTS_DIR/stage-gate.py"
fi

if [ -z "$STAGE_GATE_SCRIPT" ] || [ ! -f "$STAGE_GATE_SCRIPT" ]; then
    echo "          x stage-gate.py NOT FOUND"
    echo "          Searched: \$V11_SCRIPTS, ~/.trae-cn/skills/, \$(script_dir)/../../scripts/"
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

# 调用 stage-gate.py(P0-2 协议:--next-stage 校验 transition;exit code 0=PASS / 1=field FAIL / 2=transition FAIL)
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

# ---- Step 4: Gate signature (SHA-256 hash) ----
echo ""
echo "    [4/4] Gate signature generation:"

GATE_RESULT="status=PASS,gate_id=$GATE_ID,stage=${V11_GATE_STAGE},caller=${V11_GATE_CALLER},next_stage=${EXPECTED_NEXT_STAGE:-none}"
SIGNATURE=$(echo -n "$GATE_RESULT" | sha256sum | cut -d' ' -f1)
echo "          Signature: $SIGNATURE"
echo "          Gate result: $GATE_RESULT"

echo ""
echo "==> [V11 Gate] Pre-stage PASSED"
echo "    Gate ID: $GATE_ID"
echo "    Signature: $SIGNATURE"