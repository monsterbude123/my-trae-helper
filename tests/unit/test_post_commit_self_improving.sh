#!/bin/bash
# tests/unit/test_post_commit_self_improving.sh
# 反例固化: post-commit 在 SIA 不可用 / HOME 不可用 / 全部可用 三态下都不应阻断 commit
#
# 触发依据: AGENTS.md §2.4 + learning.md §5 路径 C
# 关联 trap: AP-5(假通过 Gate)— post-commit 写错会让 commit 失败
#
# 跑法: bash tests/unit/test_post_commit_self_improving.sh
# 期望: 全部 PASS,exit 0

set +e

cd "$(dirname "$0")/../.." || exit 1

POST_COMMIT=".husky/post-commit"
LOG_FILE="logs/post-commit-self-improve.log"

# 临时伪造 SIA(覆盖 PATH)
cat > /tmp/fake-sia.sh << 'EOF'
#!/bin/bash
echo "[fake-sia] called: $*"
exit 0
EOF
chmod +x /tmp/fake-sia.sh
export PATH="/tmp:$PATH"
cp /tmp/fake-sia.sh /usr/local/bin/self-improving-agent 2>/dev/null

PASS=0
FAIL=0
log() { echo "[$1] $2"; }
check() {
  if [ "$1" = "$2" ]; then log "PASS" "$3"; PASS=$((PASS+1));
  else log "FAIL" "$3 (got=$1 want=$2)"; FAIL=$((FAIL+1)); fi
}

# 状态 1: HOME 不存在
SELF_IMPROVING_HOME="/nonexistent" bash "$POST_COMMIT" > /dev/null 2>&1
check $? "0" "SIA 存在但 HOME 不存在 → skip 不阻断"

# 状态 2: HOME 存在 → SIA 真实调用
mkdir -p /tmp/sia-home-test
SELF_IMPROVING_HOME="/tmp/sia-home-test" bash "$POST_COMMIT" > /dev/null 2>&1
RC=$?
check $RC "0" "SIA 存在 + HOME 存在 → 真实调用不阻断"
grep -q "fake-sia.*called" "$LOG_FILE"
check $? "0" "SIA 真实被调用(参数链路完整)"

# 状态 3: SIA 不可用时静默 skip(改用一个空 PATH 但 SIA 已存在于 /usr/local/bin → SIA 探测成功,HOME 不存在则 skip)
# 这里改测:把 SIA 链接移除,确认 SIA 探测分支
rm -f /usr/local/bin/self-improving-agent
SELF_IMPROVING_HOME="/tmp/sia-home-test" bash "$POST_COMMIT" > /dev/null 2>&1
check $? "0" "SIA 不可用时静默 skip"

# bash 语法静态检查
bash -n "$POST_COMMIT"
check $? "0" "bash 语法静态检查"

echo
echo "===== 自验收总结 ====="
echo "PASS=$PASS FAIL=$FAIL"
[ $FAIL -eq 0 ] && exit 0 || exit 1
