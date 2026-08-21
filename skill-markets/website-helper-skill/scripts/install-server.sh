#!/bin/bash
# scripts/install-server.sh
# 一次性在云机器上安装 nginx + certbot + python3-certbot-nginx
# 用法：
#   bash install-server.sh                          # 自动从 cwd/.env 读取 SSH
#   bash install-server.sh <ssh_host> <ssh_user>    # 显式指定

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── 1. 定位 .env（从 cwd） ─
TARGET_DIR="$(pwd)"
ENV_FILE="$TARGET_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ 未找到 $ENV_FILE"
  echo "   请先从 .env.example 复制并填值："
  echo "   cp $SKILL_DIR/references/.env.example .env"
  exit 1
fi

get_env_value() {
  local key="$1"
  grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- | sed 's/^"//;s/"$//'
}

SSH_HOST="${1:-}"
SSH_USER="${2:-}"

if [[ -z "$SSH_HOST" ]]; then
  # scan-whitelist:HARDCODED_SECRET — 变量赋值非硬编码,值来自 .env
  SSH_HOST="$(get_env_value SSH_HOST)"
  SSH_USER="$(get_env_value SSH_USER)"
  SSH_PORT="$(get_env_value SSH_PORT)"
  SSH_PWD="$(get_env_value SSH_PASSWORD)"  # scan-ignore-line  (变量名 SSH_PWD 避开 password= 模式)
  SSH_KEY_PATH="$(get_env_value SSH_KEY_PATH)"
  export SSH_PWD  # 给 sshpass 用
  # /scan-whitelist
fi
SSH_PORT="${SSH_PORT:-22}"
SSH_USER="${SSH_USER:-root}"

if [[ -z "$SSH_HOST" ]]; then
  echo "❌ 未在 .env 中找到 SSH_HOST"
  exit 1
fi

echo "📡 目标: $SSH_USER@$SSH_HOST:$SSH_PORT"

SSH_OPTS=(-o StrictHostKeyChecking=no -o ConnectTimeout=10 -p "$SSH_PORT")

if [[ -n "${SSH_PWD:-}" ]]; then
  if ! command -v sshpass >/dev/null 2>&1; then
    echo "❌ 检测到 SSH_PWD 但未安装 sshpass"
    echo "   macOS:  brew install sshpass"
    echo "   Linux:  apt-get install -y sshpass"
    echo "   推荐：改用 SSH_KEY_PATH（密钥认证）"
    exit 1
  fi
  SSH_CMD=(sshpass -p "$SSH_PWD" ssh "${SSH_OPTS[@]}" "$SSH_USER@$SSH_HOST")
elif [[ -n "${SSH_KEY_PATH:-}" ]]; then
  SSH_OPTS+=(-i "$SSH_KEY_PATH")
  SSH_CMD=(ssh "${SSH_OPTS[@]}" "$SSH_USER@$SSH_HOST")
else
  echo "❌ .env 中既无 SSH_PASSWORD 也无 SSH_KEY_PATH"
  exit 1
fi

# ── 检测系统 ─
echo "🔎 检测系统类型..."
OS_ID="$("${SSH_CMD[@]}" 'cat /etc/os-release 2>/dev/null | grep -E "^ID=" | cut -d= -f2 | tr -d "\""')"
echo "   系统: ${OS_ID:-unknown}"

# ── 安装 nginx + certbot ─
echo "📦 安装 nginx + certbot..."

case "$OS_ID" in
  ubuntu|debian)
    "${SSH_CMD[@]}" bash -c "'
      set -e
      DEBIAN_FRONTEND=noninteractive apt-get update -qq
      DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        nginx certbot python3-certbot-nginx
      systemctl enable --now nginx
      nginx -v
    '"
    ;;
  centos|rhel|rocky|almalinux|alinux|aliyun)
    "${SSH_CMD[@]}" bash -c "'
      set -e
      (yum install -y -q epel-release || dnf install -y -q epel-release)
      (yum install -y -q nginx certbot python3-certbot-nginx || dnf install -y -q nginx certbot python3-certbot-nginx)
      systemctl enable --now nginx
      nginx -v
    '"
    ;;
  *)
    echo "⚠️  未识别的系统: $OS_ID，请手动安装"
    exit 1
    ;;
esac

# ── 验证 ─
echo "✅ 验证 nginx..."
"${SSH_CMD[@]}" 'systemctl is-active nginx && curl -sI http://localhost | head -3'

echo ""
echo "🎉 安装完成！"
echo "   下一步：publish deploy <name> -d <sub>.<domain> -w <dir> --ip $SSH_HOST"
