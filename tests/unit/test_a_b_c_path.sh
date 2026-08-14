#!/bin/bash
# tests/unit/test_a_b_c_path.sh
# 反例固化: A+B+C 三路径自验收
#
# 跑法: bash tests/unit/test_a_b_c_path.sh
# 期望: 全部 PASS,exit 0
#
# 关键: 测试在临时目录跑(让 shim 的 process.cwd() 指向测试目录)
#       因为 shim 默认写 cwd/.self-improving-agent/,WSL→Windows native node 互操作只对当前 cwd 可见

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
mkdir -p "$TEST_ROOT/logs"
cd "$TEST_ROOT"
echo "test root: $(pwd)"

SHIM="../scripts/self-improving-agent.mjs"
SIGNAL="../scripts/agent-signal-detect.mjs"

# ─── A 路径: log 子命令(主 agent 显式调用) ─────────────

# A1: log --type error
"$NODE_BIN" "$SHIM" log --type error --summary "test A1 error" --detail "from test" > /dev/null 2>&1
check $? "0" "A1: log --type error 退出码 0"
grep -q "test A1 error" .self-improving-agent/.learnings/ERRORS.md
check $? "0" "A1: ERR 写入 ERRORS.md"

# A2: log --type feature
"$NODE_BIN" "$SHIM" log --type feature --summary "test A2 feature" > /dev/null 2>&1
check $? "0" "A2: log --type feature 退出码 0"
grep -q "test A2 feature" .self-improving-agent/.learnings/FEATURE_REQUESTS.md
check $? "0" "A2: FEAT 写入 FEATURE_REQUESTS.md"

# ─── B 路径: scan-logs(钩子日志 warn) ─────────────────

# B1: 写一个临时 log 含 warn 行
echo "normal line" > logs/test_warn.log
echo "[post-commit] warn: fake warning for test" >> logs/test_warn.log
"$NODE_BIN" "$SHIM" reflect --since HEAD --auto --log logs/test_warn.log > /dev/null 2>&1
check $? "0" "B1: reflect 含 scan-logs 退出码 0"
grep -q "post_commit_warn" .self-improving-agent/.learnings/ERRORS.md
check $? "0" "B1: 日志 warn 写入 ERRORS.md"

# ─── C 路径: scan-hints(主 agent 写 hint 文件) ─────────

# C1: 写一条 error hint 到 logs/agent-hints.jsonl
echo '{"type":"error","summary":"test C1 error","priority":"high","area":"config"}' > logs/agent-hints.jsonl
"$NODE_BIN" "$SHIM" scan-hints > /dev/null 2>&1
check $? "0" "C1: scan-hints 退出码 0"
grep -q "test C1 error" .self-improving-agent/.learnings/ERRORS.md
check $? "0" "C1: hint 写入 ERRORS.md"

# C2: 写一条 feature hint
echo '{"type":"feature","summary":"test C2 feature","priority":"medium","area":"config"}' > logs/agent-hints.jsonl
"$NODE_BIN" "$SHIM" scan-hints > /dev/null 2>&1
check $? "0" "C2: scan-hints 再次退出码 0"
grep -q "test C2 feature" .self-improving-agent/.learnings/FEATURE_REQUESTS.md
check $? "0" "C2: feature hint 写入 FEATURE_REQUESTS.md"

# C3: 信号检测脚本(默认写到 ./logs/agent-hints.jsonl)
"$NODE_BIN" "$SIGNAL" "你确定这样行吗" > /dev/null 2>&1
check $? "0" "C3: signal-detect 纠正信号退出码 0"
[ -f logs/agent-hints.jsonl ] && grep -q "你确定这样行吗" logs/agent-hints.jsonl
check $? "0" "C3: 纠正信号写入 hints"

# C4: 信号检测无信号
HINT_BEFORE=$(wc -c < logs/agent-hints.jsonl 2>/dev/null || echo 0)
"$NODE_BIN" "$SIGNAL" "今天天气不错" > /dev/null 2>&1
HINT_AFTER=$(wc -c < logs/agent-hints.jsonl 2>/dev/null || echo 0)
check "$HINT_BEFORE" "$HINT_AFTER" "C4: 无信号 → 不写 hint"

# 清理
cd ..
rm -rf "$TEST_ROOT"

echo
echo "===== A+B+C 自验收总结 ====="
echo "PASS=$PASS FAIL=$FAIL"
[ $FAIL -eq 0 ] && exit 0 || exit 1
