# 6 层排查（Six-Layer Diagnosis）

> Stage 6 Bug Fix Step 3 必走。V10 debugger-methodology.md 蒸馏。

---

## 6 层定义

| 层 | 范围 | 典型工具 |
|----|------|---------|
| **网络层** | DNS / TLS / 代理 / 防火墙 | curl, dig, openssl, mitmproxy |
| **接入层** | API gateway / 路由 / 限流 / CDN | nginx logs, gateway dashboard |
| **应用层** | 业务逻辑 / 中间件 / 状态 / 配置 | app logs, debugger, strace |
| **数据层** | DB schema / 索引 / 事务 / 缓存 | SQL logs, EXPLAIN, redis-cli |
| **集成层** | 第三方服务 / SDK / webhook / queue | 3rd party dashboard, mq console |
| **客户端层** | UI / 缓存 / localStorage / service worker | 浏览器 DevTools, console, Application |

---

## 排查流程

```
Step 3.1: 网络层（先排除最外层）
  └─ curl -v https://api.example.com/health
  └─ DNS 解析 → TLS 握手 → TCP 连接

Step 3.2: 接入层
  └─ API gateway 日志
  └─ 限流 / 路由 / 鉴权

Step 3.3: 应用层（最常见）
  └─ 业务逻辑错误
  └─ 中间件顺序
  └─ 状态机错误

Step 3.4: 数据层
  └─ DB schema 漂移
  └─ 索引缺失
  └─ 事务隔离级别

Step 3.5: 集成层
  └─ 第三方 API 响应
  └─ SDK 版本

Step 3.6: 客户端层
  └─ localStorage 缓存陈旧
  └─ Service Worker
  └─ 浏览器版本
```

## 采集 vs 解析二分（V10.11 蒸馏）

**问题**: 看到错误信息就解析，可能忽略上游采集失败。

**正解**: 区分"采集到错误" vs "解析失败"：
- 采集失败（无数据）→ 网络 / 接入 / 数据层
- 解析失败（有数据但格式错）→ 应用 / 集成层

---

## 反例

### 反例 A：只查应用层就下结论

```
debugger: 看应用代码 → "业务逻辑错" → 改  # ❌ 可能实际是网络层
正确: 6 层逐层排除 → GitNexus impact
```

### 反例 B：忽略客户端缓存

```
debugger: 服务端返回正确数据 → 用户看到错误  # ❌ 客户端缓存陈旧
正确: 检查 localStorage / Service Worker / Browser Cache
```

---

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md)
- [five-step-flow.md](five-step-flow.md)
- V10 debugger-methodology.md: `V10 来源` (已蒸馏到本文档)
