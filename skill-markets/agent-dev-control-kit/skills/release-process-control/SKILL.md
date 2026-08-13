---
name: release-process-control
description: 发布流程控制技能。规范预发布、灰度、监控、回滚全流程，确保线上变更可控、可回滚、可审计。当用户提到"发布"、"上线"、"灰度"、"canary"、"回滚"、"deploy"、"release"、"rollback"时主动加载。
version: 1.0.0
requires:
  skills: [execution-control]
  optional: [config-sync-control, asset-management-control]
---

# Release Process Control

## 触发词

- 发布 / 上线 / 灰度 / canary / 回滚 / rollback / deploy / release / rollout / 预发布

## 功能说明

发布流程控制技能为线上变更提供完整的发布-灰度-监控-回滚闭环，覆盖**发布前自检、版本标记、灰度策略、监控阈值、自动回滚、事后复盘**六大环节。确保任何发布都可控、可回滚、可追溯。

## 适用场景

| 场景 | 典型动作 | 典型风险 |
|------|---------|---------|
| 业务服务发布 | 蓝绿/金丝雀/滚动 | 流量切错、数据不一致 |
| 模型/算法上线 | A/B 测试 + 监控对比 | 效果下降、无降级方案 |
| 静态资源发布 | CDN 灰度 | 缓存命中率暴跌、404 |
| 数据库迁移 | 在线 DDL + 双写 | 迁移失败、回滚超时 |
| 前端发版 | feature flag + 灰度 | 兼容性、白屏 |

## 输入规范

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `service` | string | 服务名 | `api-gateway`, `web-app`, `ml-model-v3` |
| `version` | string | 版本号（semver） | `v2.4.1`, `2026.08.13-rc1` |
| `environment` | string | 目标环境 | `staging`, `canary`, `production` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `strategy` | string | `canary` | 发布策略：`blue-green` / `canary` / `rolling` / `feature-flag` |
| `canary_percent` | integer | `5` | 灰度初始流量百分比 |
| `rollout_window` | string | `30m` | 灰度持续时间 |
| `rollback_threshold` | object | — | 自动回滚阈值（error_rate / latency_p99） |
| `dry_run` | boolean | `false` | 仅预演不真正发布 |

## 核心流程

```
发布请求 → 预检（pre-flight） → 版本标记 → 灰度（canary）→ 监控观察 → 全量 or 自动回滚 → 收尾归档
```

## 5 个关键控制点

### CP-1 发布前自检（HIGH — 失败即阻断）

- 版本号合法性：必须符合 semver 或既定版本规则
- ChangeLog / ReleaseNotes 完整性：必含 `Added/Changed/Fixed/Removed`
- 依赖锁定：lockfile 已提交、关键依赖有 SBOM
- 环境配置一致性：参考 `config-sync-control`
- 资产就绪：参考 `asset-management-control`
- 冒烟测试通过：核心 API/页面/路径至少 1 个绿用例

### CP-2 版本标记与不可变（HIGH）

- 每次发布必须产生**不可变版本标识**（git tag / image digest / artifact hash）
- 禁止用 `latest` / `vN` 这种浮动标签作为生产引用
- 版本元数据写入 `release/<service>-<version>.json`：

```json
{
  "service": "api-gateway",
  "version": "v2.4.1",
  "git_sha": "8f3a2bc91d",
  "image": "registry/api-gateway:v2.4.1@sha256:abc...",
  "released_at": "2026-08-13T10:30:00Z",
  "released_by": "agent:release-bot",
  "strategy": "canary",
  "rollback_to": "v2.4.0"
}
```

### CP-3 灰度策略（HIGH）

- 默认 `canary`：先 5% 流量，监控稳定后逐步 25% → 50% → 100%
- 每个灰度阶段必须满足观察窗口（默认 30 分钟）+ 阈值通过
- `blue-green`：新版本独立部署，验证通过后切换负载均衡
- `rolling`：按批次替换旧实例，每批 25%，间隔 5 分钟
- `feature-flag`：开关粒度控制，发布不等于上线

### CP-4 监控与自动回滚（HIGH）

发布期间实时采集以下指标（任一超阈值自动回滚）：

| 指标 | 阈值（默认） | 说明 |
|------|------------|------|
| `error_rate` | > 1% | 5xx 比例 |
| `latency_p99` | > baseline × 1.5 | 99 分位延迟 |
| `success_rate` | < 99% | 业务成功率 |
| `qps_drop` | > 30% | 流量异常下跌 |
| `cpu/memory` | > 85% | 资源过载 |

自动回滚决策点：

```
if error_rate > threshold OR latency_p99 > baseline * 1.5:
    rollback_to = previous_version
    trigger_rollback()
    notify_oncall()
```

### CP-5 收尾与复盘（MEDIUM）

- 全量发布成功后：归档 release-notes、更新 CHANGELOG、清理临时资源
- 失败/回滚后：写入 `post-mortem/<service>-<version>-<date>.md`
- 复盘必含：时间线 / 触发原因 / 影响范围 / 回滚时长 / 改进项
- release 元数据保留 ≥ 365 天用于审计

## 输出规范

### 成功输出

```json
{
  "status": "success",
  "data": {
    "release_id": "rel_20260813_103000",
    "service": "api-gateway",
    "version": "v2.4.1",
    "strategy": "canary",
    "stages": [
      {"stage": "5%",  "duration": "30m", "result": "PASS"},
      {"stage": "25%", "duration": "30m", "result": "PASS"},
      {"stage": "50%", "duration": "30m", "result": "PASS"},
      {"stage": "100%","duration": "—",    "result": "PASS"}
    ],
    "rollback_to": "v2.4.0",
    "total_duration": "1h32m"
  }
}
```

### 回滚输出

```json
{
  "status": "rolled_back",
  "data": {
    "release_id": "rel_20260813_103000",
    "service": "api-gateway",
    "rolled_back_from": "v2.4.1",
    "rolled_back_to": "v2.4.0",
    "reason": "error_rate 2.3% > threshold 1%",
    "rollback_duration": "45s",
    "affected_users_estimate": 1200
  }
}
```

### 失败输出（预检未过）

```json
{
  "status": "error",
  "error": {
    "code": "E101",
    "message": "Pre-flight check failed",
    "phase": "preflight",
    "context": "smoke test failed: GET /api/health returned 503"
  }
}
```

## 验收标准

1. **可回滚**：任意发布都必须在 60 秒内可回滚到上一稳定版
2. **可灰度**：默认采用 canary，灰度期间任一阶段失败自动停止
3. **可审计**：release 元数据、监控快照、回滚决策全部留痕
4. **可追溯**：版本号 ↔ git SHA ↔ image digest ↔ 配置 ↔ 资产 五者一一对应
5. **零强推**：禁止跳过自检直接 `kubectl apply` / `deploy` 到生产
6. **复盘必走**：所有回滚事件必须在 24 小时内产出 post-mortem

## 错误处理

### 错误分级

| 级别 | 代码前缀 | 处理方式 |
|------|---------|---------|
| CRITICAL | E1xx | 立即停止发布，触发自动回滚 |
| ERROR | E2xx | 当前阶段失败，保留在灰度状态等待决策 |
| WARNING | E3xx | 记录告警，标记为需人工 review |
| INFO | E4xx | 记录信息，不影响流程 |

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|---------|
| E101 | 自检未过 | 修复后重试，禁止强制跳过 |
| E102 | 版本号非法 | 检查 semver 规则 |
| E201 | 灰度失败 | 自动回滚，写 post-mortem |
| E202 | 回滚失败 | 触发 oncall 人工介入 |
| E301 | 监控数据缺失 | 补齐监控后再发布 |

## 示例用法

### 示例 1：canary 发布

```markdown
**用户请求**：发布 api-gateway v2.4.1 到生产环境

**执行过程**：
1. 预检：版本号合法、CHANGELOG 完整、smoke 通过 → PASS
2. 版本标记：tag=v2.4.1, image=sha256:abc..., rollback_to=v2.4.0
3. 灰度：5% 流量 30min → error_rate=0.3% PASS
4. 灰度：25% → 50% → 100%，每段监控阈值
5. 收尾：归档 release-notes，清理旧版本容器
6. 返回：release_id=rel_20260813_103000, total_duration=1h32m
```

### 示例 2：自动回滚

```markdown
**用户请求**：发布 v2.5.0 到生产环境

**执行过程**：
1. 预检通过
2. 灰度 5%：error_rate=2.3%（超阈值 1%）
3. 自动回滚到 v2.4.0
4. 通知 oncall
5. 生成 post-mortem 草稿
6. 返回：status=rolled_back, reason=error_rate 2.3%
```

### 示例 3：blue-green 发布

```markdown
**用户请求**：以 blue-green 策略发布 web-app v3.0.0

**执行过程**：
1. 部署 green 环境（独立实例集）
2. 健康检查 + 冒烟测试
3. 切换负载均衡器 100% 到 green
4. 保留 blue 环境 1 小时（应急回滚）
5. 1 小时后清理 blue
6. 返回：strategy=blue-green, total_duration=25m
```

## 示例代码

### Python：发布编排（伪代码）

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable

class Stage(Enum):
    PREFLIGHT = "preflight"
    TAG = "tag"
    CANARY_5 = "canary_5"
    CANARY_25 = "canary_25"
    CANARY_50 = "canary_50"
    CANARY_100 = "canary_100"
    DONE = "done"
    ROLLBACK = "rollback"

@dataclass
class ReleaseConfig:
    service: str
    version: str
    rollback_to: str
    strategy: str = "canary"
    canary_stages: list[int] = None  # 默认 [5, 25, 50, 100]
    window_minutes: int = 30
    error_rate_threshold: float = 0.01
    latency_p99_factor: float = 1.5

def release(config: ReleaseConfig, deploy_fn: Callable, monitor_fn: Callable) -> dict:
    stages = config.canary_stages or [5, 25, 50, 100]
    log = []

    # CP-1 预检
    preflight = deploy_fn.preflight(config)
    log.append({"stage": Stage.PREFLIGHT.value, "result": preflight["status"]})
    if preflight["status"] != "PASS":
        return {"status": "error", "error": {"code": "E101", "message": "preflight failed"}}

    # CP-2 版本标记
    tag = deploy_fn.tag(config.version, config.rollback_to)
    log.append({"stage": Stage.TAG.value, "result": "PASS"})

    # CP-3 灰度
    for percent in stages:
        deploy_fn.shift_traffic(config.service, percent)
        metrics = monitor_fn.wait(config.service, percent, window_minutes=config.window_minutes)

        # CP-4 监控 + 自动回滚
        if metrics.error_rate > config.error_rate_threshold \
           or metrics.latency_p99 > metrics.baseline_p99 * config.latency_p99_factor:
            deploy_fn.rollback(config.service, config.rollback_to)
            return {
                "status": "rolled_back",
                "data": {
                    "rolled_back_from": config.version,
                    "rolled_back_to": config.rollback_to,
                    "reason": f"error_rate={metrics.error_rate} at {percent}%",
                    "stages": log
                }
            }
        log.append({"stage": f"canary_{percent}", "result": "PASS"})

    # CP-5 收尾
    deploy_fn.archive_release_notes(config.service, config.version)
    return {"status": "success", "data": {"service": config.service, "version": config.version, "stages": log}}
```

### Bash：预检脚本

```bash
#!/usr/bin/env bash
# release-preflight.sh — 发布前自检
set -euo pipefail

SERVICE=${1:?"service required"}
VERSION=${2:?"version required"}

FAIL=0

# 1. 版本号合法性
if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-rc[0-9]+)?$ ]]; then
  echo "[FAIL] E102 invalid version: $VERSION"; FAIL=1
fi

# 2. CHANGELOG 完整性
if ! grep -q "## \[$VERSION\]" CHANGELOG.md; then
  echo "[FAIL] CHANGELOG missing entry for $VERSION"; FAIL=1
fi

# 3. 依赖锁定
if [[ ! -f package-lock.json ]] && [[ ! -f pnpm-lock.yaml ]] && [[ ! -f go.sum ]]; then
  echo "[FAIL] no lockfile found"; FAIL=1
fi

# 4. 冒烟测试（核心路径）
if ! curl -sf "http://localhost:3000/api/health" > /dev/null; then
  echo "[FAIL] E101 smoke test failed: /api/health not 2xx"; FAIL=1
fi

# 5. 与上一版本对比变更集
PREV=$(git tag --sort=-version:refname | grep -v "^$VERSION$" | head -1)
if [[ -z "$PREV" ]]; then
  echo "[WARN] no previous version tag found"
fi

exit $FAIL
```

## 依赖说明

### 必需依赖

- CI/CD 平台（GitHub Actions / GitLab CI / Argo）
- 容器镜像仓库（Harbor / ECR / GCR）
- 监控/告警系统（Prometheus + AlertManager / Datadog）

### 可选依赖

- 灰度流量调度（Istio / Nginx + Lua / Load Balancer）
- 变更管理平台（Atlassian Jira / 飞书审批）

## 注意事项

1. **永远不跳过预检**：即使"只改一行"，也要走完整 preflight
2. **永远准备 rollback**：发布开始前必须验证回滚路径可用
3. **永远不直接 latest**：生产引用必须用具体版本号或 digest
4. **灰度期间不离场**：发布期间必须有 oncall 待命
5. **复盘不拖延**：回滚事件 24h 内必须产出 post-mortem
6. **跨环境一致**：staging 与 production 的发布流程必须一致（避免 staging 通过 prod 翻车）

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | 2026-08-13 | 初始版本（补齐 5 大 Execution Skill 之一） |