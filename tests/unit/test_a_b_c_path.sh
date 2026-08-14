#!/bin/bash
# tests/unit/test_a_b_c_path.sh
# 反例固化: A+B+C 三路径自验收
#
# 跑法: bash tests/unit/test_a_b_c_path.sh
# 期望: 全部 PASS,exit 0

set +e
cd "$(dirname "$0")/../.." || exit 1

# 探测 node 路径(WSL / Git Bash 兼容)
NODE_BIN="$(command -v node 2>/dev/null || true)"
if [ -z "$NODE_BIN" ] && command -v where.exe >/dev/null 2>&1; then
  WIN_NODE="$(where.exe node 2>/dev/null | head -n 1 | tr -d '\r' || true)"
  if [ -n "$WIN_NODE" ]; then
    if [[ "$WIN_NODE" =~ ^([A-Za-z]):\\(.*)$ ]]; then
      DRIVE_LOWER="$(echo "${BASH_REMATCH[1]}" | tr '[:upper:]' '[:lower:]')"
      REST="${BASH_REMATCH[2]//\\//}"
      NODE_BIN="/mnt/${DRIVE_LOWER}/${REST}"
    fi
  fi
fi
if [ -z "$NODE_BIN" ] && [ -f "/mnt/c/Program Files/nodejs/node.exe" ]; then
  NODE_BIN="/mnt/c/Program Files/nodejs/node.exe"
fi
if [ -z "$NODE_BIN" ]; then
  echo "FAIL: 找不到 node,跳过测试"
  exit 1
fi
echo "node=$NODE_BIN"

PASS=0
FAIL=0
log() { echo "[$1] $2"; }
check() {
  if [ "$1" = "$2" ]; then log "PASS" "$3"; PASS=$((PASS+1));
  else log "FAIL" "$3 (got=$1 want=$2)"; FAIL=$((FAIL+1)); fi
}

# 测试隔离:在仓库内创建临时测试目录
TEST_ROOT=".self-improving-agent-test-$$"
mkdir -p "$TEST_ROOT/.self-improving-agent/.learnings" "$TEST_ROOT/.self-improving-agent/logs"
cd "$TEST_ROOT"
TEST_ROOT_WIN="$(pwd | sed 's|^/mnt/\([a-z]\)/|\U\1:/|; s|/|\\|g')"
SIA_HOME_WIN="$TEST_ROOT_WIN\\.self-improving-agent"
echo "test root WIN: $TEST_ROOT_WIN"
echo "sia home WIN: $SIA_HOME_WIN"

SHIM="../scripts/self-improving-agent.mjs"
SIGNAL="../scripts/agent-signal-detect.mjs"

# helper: 用 node 直接读文件
read_learn_file() {
  local file="$1"
  local pattern="$2"
  "$NODE_BIN" -e "process.stdout.write(require('fs').existsSync(process.argv[1]) && require('fs').readFileSync(process.argv[1],'utf8').includes(process.argv[2]) ? '1' : '0')" \
    "$SIA_HOME_WIN\\.learnings\\$file" "$pattern"
}
read_hint_file() {
  local pattern="$1"
  "$NODE_BIN" -e "process.stdout.write(require('fs').existsSync(process.argv[1]) && require('fs').readFileSync(process.argv[1],'utf8').includes(process.argv[2]) ? '1' : '0')" \
    "$SIA_HOME_WIN\\logs\\agent-hints.jsonl" "$pattern"
}
hint_size() {
  "$NODE_BIN" -e "const fs=require('fs'); try{process.stdout.write(String(fs.statSync(process.argv[1]).size));}catch{process.stdout.write('0');}" \
    "$SIA_HOME_WIN\\logs\\agent-hints.jsonl"
}

# ─── A 路径: log 子命令 ─────────────

"$NODE_BIN" "$SHIM" --home "$SIA_HOME_WIN" log --type error --summary "test A1 error" --detail "from test" > /dev/null 2>&1
check $? "0" "A1: log --type error 退出码 0"
RESULT=$(read_learn_file "ERRORS.md" "test A1 error")
check "$RESULT" "1" "A1: ERR 写入 ERRORS.md"

"$NODE_BIN" "$SHIM" --home "$SIA_HOME_WIN" log --type feature --summary "test A2 feature" > /dev/null 2>&1
check $? "0" "A2: log --type feature 退出码 0"
RESULT=$(read_learn_file "FEATURE_REQUESTS.md" "test A2 feature")
check "$RESULT" "1" "A2: FEAT 写入 FEATURE_REQUESTS.md"

# ─── B 路径: scan-logs ─────────────────

# shim 扫描 <cwd>/logs/<file>,cwd 是仓库根(由 main 调用者决定,这里是 shim 自己的 cwd)
# 因为我们 cd 到 TEST_ROOT,cwd 是 TEST_ROOT,但 shim reflect 内部硬编码 join(cwd, 'logs', ...)
# 用 --home 把 HOME 设为 SIA_HOME_WIN,但 scan-logs 读 cwd/logs/
# 解决: 写日志到 TEST_ROOT/logs/test_warn.log
mkdir -p logs
echo "normal line" > logs/test_warn.log
echo "[post-commit] warn: fake warning for test" >> logs/test_warn.log
"$NODE_BIN" "$SHIM" --home "$SIA_HOME_WIN" reflect --since HEAD --auto --log logs/test_warn.log > /dev/null 2>&1
check $? "0" "B1: reflect 含 scan-logs 退出码 0"
RESULT=$(read_learn_file "ERRORS.md" "post_commit_warn")
check "$RESULT" "1" "B1: 日志 warn 写入 ERRORS.md"
rm -f logs/test_warn.log

# ─── C 路径: scan-hints ─────────

# shim scan-hints 默认读 <cwd>/logs/agent-hints.jsonl + <HOME>/logs/agent-hints.jsonl
# 我们 cwd 是 TEST_ROOT,HOME 是 TEST_ROOT/.self-improving-agent
# 所以写 hints 到 TEST_ROOT/logs/agent-hints.jsonl(让 cwd 路径命中)即可
echo '{"type":"error","summary":"test C1 error","priority":"high","area":"config"}' > logs/agent-hints.jsonl
"$NODE_BIN" "$SHIM" --home "$SIA_HOME_WIN" scan-hints > /dev/null 2>&1
check $? "0" "C1: scan-hints 退出码 0"
RESULT=$(read_learn_file "ERRORS.md" "test C1 error")
check "$RESULT" "1" "C1: hint 写入 ERRORS.md"

echo '{"type":"feature","summary":"test C2 feature","priority":"medium","area":"config"}' > logs/agent-hints.jsonl
"$NODE_BIN" "$SHIM" --home "$SIA_HOME_WIN" scan-hints > /dev/null 2>&1
check $? "0" "C2: scan-hints 再次退出码 0"
RESULT=$(read_learn_file "FEATURE_REQUESTS.md" "test C2 feature")
check "$RESULT" "1" "C2: feature hint 写入 FEATURE_REQUESTS.md"
rm -f logs/agent-hints.jsonl

# C3: signal-detect 默认写 <HOME>/logs/agent-hints.jsonl
"$NODE_BIN" "$SIGNAL" --home "$SIA_HOME_WIN" "你确定这样行吗" > /dev/null 2>&1
check $? "0" "C3: signal-detect 纠正信号退出码 0"
RESULT=$(read_hint_file "你确定这样行吗")
check "$RESULT" "1" "C3: 纠正信号写入 hints"

# C4: signal-detect 无信号
HINT_BEFORE=$(hint_size)
"$NODE_BIN" "$SIGNAL" --home "$SIA_HOME_WIN" "今天天气不错" > /dev/null 2>&1
HINT_AFTER=$(hint_size)
check "$HINT_BEFORE" "$HINT_AFTER" "C4: 无信号 → 不写 hint"

# 清理
cd ..
rm -rf "$TEST_ROOT"

echo
echo "===== A+B+C 自验收总结 ====="
echo "PASS=$PASS FAIL=$FAIL"
[ $FAIL -eq 0 ] && exit 0 || exit 1