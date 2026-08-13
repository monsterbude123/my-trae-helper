# 发布流程执行模板

## 发布信息

- **服务**: [service-name]
- **版本**: [vX.Y.Z / YYYY.MM.DD-rcN]
- **目标环境**: [staging / canary / production]
- **回滚目标**: [上一个稳定版本]
- **执行人**: [Agent / 人工]
- **开始时间**: [YYYY-MM-DD HH:MM]

## 1. 发布前自检（CP-1 — HIGH 必须）

### 预检清单

- [ ] 版本号合法（semver）
- [ ] CHANGELOG 完整（Added/Changed/Fixed/Removed）
- [ ] 依赖锁定（lockfile 已提交）
- [ ] 环境配置一致性（参考 config-sync-control）
- [ ] 资产就绪（参考 asset-management-control）
- [ ] 冒烟测试通过（至少 1 个核心路径）
- [ ] 上一版本监控基线已采集（error_rate / latency_p99）

### 自检命令

```bash
# 一键自检
bash scripts/release-preflight.sh <service> <version>
# 退出码 0 = PASS，1 = FAIL
```

## 2. 版本标记（CP-2 — HIGH 必须）

### 不可变标识

| 标识类型 | 值 |
|---------|-----|
| git tag | `vX.Y.Z` |
| git SHA | `8f3a2bc91d...` |
| image digest | `sha256:abc...` |
| artifact hash | `sha256:xyz...` |

### release 元数据

```json
{
  "service": "[service-name]",
  "version": "[vX.Y.Z]",
  "git_sha": "[sha]",
  "image": "registry/[service]:[vX.Y.Z]@sha256:[digest]",
  "released_at": "[ISO timestamp]",
  "released_by": "agent:release-bot",
  "strategy": "canary / blue-green / rolling / feature-flag",
  "rollback_to": "[prev version]"
}
```

写入位置：`release/<service>-<version>.json`

## 3. 灰度策略（CP-3 — HIGH）

### 策略选择

- [ ] **canary**（默认）：5% → 25% → 50% → 100%，每段监控 ≥30min
- [ ] **blue-green**：部署 green，验证后切流，blue 保留 1h
- [ ] **rolling**：按批次 25% 替换旧实例
- [ ] **feature-flag**：开关控制，发布≠上线

### 灰度阶段记录

| 阶段 | 流量 % | 起始时间 | 结束时间 | 监控结果 |
|------|--------|---------|---------|---------|
| Stage 1 | 5% | HH:MM | HH:MM | PASS/FAIL |
| Stage 2 | 25% | HH:MM | HH:MM | PASS/FAIL |
| Stage 3 | 50% | HH:MM | HH:MM | PASS/FAIL |
| Stage 4 | 100% | HH:MM | HH:MM | PASS/FAIL |

## 4. 监控与自动回滚（CP-4 — HIGH）

### 实时指标

| 指标 | 阈值 | 实测 | 状态 |
|------|------|------|------|
| error_rate | ≤ 1% | [%] | OK/BLOCK |
| latency_p99 | ≤ baseline × 1.5 | [ms] | OK/BLOCK |
| success_rate | ≥ 99% | [%] | OK/BLOCK |
| qps_drop | ≤ 30% | [%] | OK/BLOCK |
| cpu/memory | ≤ 85% | [%] | OK/BLOCK |

### 回滚决策

```bash
# 任一指标超阈值 → 触发回滚
bash scripts/release-rollback.sh <service> <prev_version>

# 自动回滚脚本伪代码
if error_rate > 0.01 OR latency_p99 > baseline * 1.5:
    rollback_to = prev_version
    notify_oncall()
    write_post_mortem_draft()
```

## 5. 收尾与复盘（CP-5 — MEDIUM）

### 全量成功

- [ ] release-notes 归档
- [ ] CHANGELOG 更新（已含）
- [ ] 旧版本容器清理（保留上一个）
- [ ] 监控基线更新
- [ ] 通知团队（频道/审批单）

### 回滚事件（必走复盘）

- [ ] 24h 内产出 `post-mortem/<service>-<version>-<date>.md`
- [ ] 复盘必含：时间线 / 触发原因 / 影响范围 / 回滚时长 / 改进项
- [ ] 改进项转 issue 进入 backlog
- [ ] release 元数据保留 ≥ 365 天

## 6. 执行记录

| 时间 | 阶段 | 操作 | 结果 | 备注 |
|------|------|------|------|------|
| HH:MM | preflight | 自检 | PASS/FAIL | — |
| HH:MM | tag | 标记版本 | SUCCESS/FAIL | — |
| HH:MM | canary 5% | 切流 | SUCCESS/FAIL | — |
| HH:MM | canary 25% | 切流 | SUCCESS/FAIL | — |
| HH:MM | canary 50% | 切流 | SUCCESS/FAIL | — |
| HH:MM | canary 100% | 切流 | SUCCESS/FAIL | — |
| HH:MM | rollback | 自动回滚 | TRIGGERED | error_rate=2.3% |
| HH:MM | done | 归档 | SUCCESS/FAIL | — |

## 7. 验证结果

- [ ] 所有预检项 PASS
- [ ] 所有灰度阶段监控通过
- [ ] release 元数据已写入
- [ ] 监控基线已更新
- [ ] oncall 已通知
- [ ] 回滚预案已就绪（即使是全量成功，也要验证）

## 8. 回滚预案（HIGH 必须 — 发布前就绪）

```bash
# 快速回滚命令
bash scripts/release-rollback.sh <service> <prev_version>

# 验证回滚后服务正常
curl -sf http://service/api/health
bash scripts/smoke-test.sh <service>
```

回滚时长目标：≤ 60 秒（自动触发）；≤ 5 分钟（人工触发）。