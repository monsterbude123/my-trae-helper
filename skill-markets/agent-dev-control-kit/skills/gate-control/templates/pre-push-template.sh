#!/bin/bash

# L2 推送前门禁脚本
# 用法: .husky/pre-push

set -e

echo "=== L2 推送前门禁 ==="

# 1. 执行 L1 门禁
echo "[1/4] 执行 L1 门禁..."
npm run lint && npm run typecheck && npm run test:unit
if [ $? -ne 0 ]; then
    echo "❌ L1 门禁失败"
    exit 1
fi
echo "✅ L1 门禁通过"

# 2. 集成测试
echo "[2/4] 集成测试..."
npm run test:integration
if [ $? -ne 0 ]; then
    echo "❌ 集成测试失败"
    exit 1
fi
echo "✅ 集成测试通过"

# 3. 覆盖率检查
echo "[3/4] 覆盖率检查..."
npm run test:coverage
if [ $? -ne 0 ]; then
    echo "⚠️ 覆盖率未达标"
    exit 1
fi
echo "✅ 覆盖率达标"

# 4. 构建检查
echo "[4/4] 构建检查..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi
echo "✅ 构建成功"

echo ""
echo "=== L2 门禁全部通过 ==="