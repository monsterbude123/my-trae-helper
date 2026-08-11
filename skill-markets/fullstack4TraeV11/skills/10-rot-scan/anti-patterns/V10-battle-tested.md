# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 4.5 Rot Scan 从 V10 agents/rot-detector.md + process-rot-analysis.md + proactive-scan.py 蒸馏。

## V10 实战反例（3 条）

### 蒸馏 1：跳过 rot-detector 直接 Accept（Article XIV 违规）

**实战场景**（V10.4 蒸馏）:
- Stage 4 Review PASS → 直接 Accept
- 未跑 rot-detector → 上线后状态卡说谎 / 孤儿测试 / Bundle Staleness 累积

**V11 改进**: 铁律 1（rot-detector 必跑）+ 编排器 §1 不可跳过 -1/0/1/3.5/4.5。

### 蒸馏 2：fix-list.json 空（扫完不改）

**实战场景**（V10.4 蒸馏）:
- proactive-scan.py 跑完 → 输出了 5 项 FAIL
- fix-list.json 是空的（"等下次"） → Accept 时检查发现

**V11 改进**: 铁律 5（fix-list.json 必产出 + 不可空）+ 编排器 §5 门禁脚本调用规则。

### 蒸馏 3：rot-detector 自身腐烂（rot #15 配置腐烂）

**实战场景**（V10.8 蒸馏）:
- rot-detector 自身逻辑过时（如 Bundle Staleness 检测失效）
- self-diagnose.py 未跑 → rot-detector 自己腐烂了都不知道

**V11 改进**: 铁律 3（self-diagnose.py Meta 自我诊断）+ depends_on.scripts 含 self-diagnose.py。

## V10 实战蒸馏经验（3 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| rot-detector 不可跳 | Article XIV | 铁律 1 |
| fix-list.json 必产 | rot-detector.md Step 3 | 铁律 5 |
| rot-detector 自身腐烂检测 | process-rot-analysis.md rot #15 | 铁律 3 |

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 rot-detector.md | → `../../10-rot-scan/SKILL.md` 铁律 1-6 |
| V10 process-rot-analysis.md | → `../../10-rot-scan/references/rot-classification.md` |
| V10 proactive-scan.py | → V11 `scripts/proactive-scan.py`（重写） |
| V10 self-diagnose.py | → V11 `scripts/self-diagnose.py`（重写） |

## 关联引用

[SKILL.md](../SKILL.md) | [rot-classification.md](../references/rot-classification.md) | [scan-protocol.md](../references/scan-protocol.md)
