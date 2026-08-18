# todoApp — V11 case study

> **目的**:验证 `fullstack4TraeV11` SKILL 能否从头到尾产出一个完整可用的应用。
>
> **结论**:✅ Stage 0 → Stage 5 accept 全跑通,服务可访问 + 8/8 契约测试 PASS + spec-purge 真归档。

---

## 一句话铁律

```bash
cd case-studies/todoapp-v11
npm install && npm start    # 启动 http://localhost:3000
node tests/contracts.test.js  # 8/8 PASS
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/spec-purge.py \
    --change-id 2026-08-17-todoapp --project-root .  # 归档
```

## V11 流水线 13 stage 走法

| Stage | 产物 | 本 case 状态 |
|-------|------|-------------|
| -1/intake | spec.md §Scope + AC | ✅ spec.md(9 AC + 4 INV + 5 EC) |
| 0/plan | plan.md | ✅ plan.md(技术选型 + capabilities) |
| 0.5/test-plan | test-plan.md | ✅ test-plan.md(8 契约 + 4 浏览器 TC) |
| 1/spec | spec.md 完整 | ✅ 同上 |
| 1.5/prototype | prototype.md | N/A(本 case 无 UI 设计) |
| 2/contract | contracts/ | ✅ 4 文件(domain-models/api-contracts/events/validation-rules) |
| 3/implement | src/ | ✅ src/server.js + src/public/index.html |
| 3.5/real-verify | verify-report.md(实测) | ✅ 8/8 契约测试 |
| 4/review | review-report.md | ✅ 18/20 (4.5/5) |
| 4.5/rot-scan | rot-scan-{date}.md | ✅ 10/10 PASS |
| 5/accept | spec-purge 真归档 | ✅ docs/archive/done/2026-08-17-todoapp/ |

## 验收结果

| 检查项 | 命令 | 结果 |
|--------|------|------|
| 服务启动 | `npm start` | `todoApp listening on http://localhost:3000` |
| 健康探针 | `curl /health` | `{"status":"ok","todos":3}` |
| 创建 todo | `curl POST /api/todos` | 返回 201 + todo 对象 |
| 列表 | `curl GET /api/todos` | 返回 todos[] |
| 切换 done | `curl PATCH /api/todos/1` | 返回 200 + done=true |
| 404 | `curl PATCH /api/todos/999` | 返回 404 |
| 删除 | `curl DELETE /api/todos/1` | 返回 200 + deleted=1 |
| 浏览器 | `http://localhost:3000/` | 单页 UI 可用 |
| 契约测试 | `node tests/contracts.test.js` | **8/8 PASS** |
| 归档 | `spec-purge.py` | 10 文件落到 `docs/archive/done/` |
| 腐化扫描 | `proactive-scan.py` | **10/10 PASS** |

## 文件清单

```
todoapp-v11/
├── README.md                              (本文件)
├── package.json                           (express 唯一依赖)
├── src/
│   ├── server.js                          (Express 后端,100 行)
│   └── public/index.html                  (浏览器 UI,100 行)
├── tests/
│   └── contracts.test.js                  (8 项契约测试)
├── docs/
│   ├── specs/changes/2026-08-17-todoapp/  (Stage 0-4 产物,后被归档)
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── test-plan.md
│   │   ├── review-report.md
│   │   ├── rot-scan-2026-08-17.md
│   │   ├── .state-card.md
│   │   └── contracts/
│   │       ├── domain-models.md
│   │       ├── api-contracts.md
│   │       ├── events.md
│   │       └── validation-rules.md
│   ├── archive/done/2026-08-17-todoapp/   (Stage 5 归档后,Article VIII 不可变)
│   └── verifications/2026-08-17-manual-verify.md  (手动验收记录)
└── node_modules/                          (npm install 产物)
```

## 重跑命令(从零开始)

```bash
# 1) 装依赖
npm install

# 2) 启动服务(后台)
npm start &

# 3) 跑契约测试(会自己启动 server 子进程在 3100 端口)
node tests/contracts.test.js

# 4) 端到端 curl
curl -X POST -H "Content-Type: application/json" -d '{"title":"测试"}' http://localhost:3000/api/todos
curl http://localhost:3000/api/todos

# 5) 归档(V11 Stage 5)
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/spec-purge.py \
    --change-id 2026-08-17-todoapp --project-root .

# 6) 腐化扫描(V11 Stage 4.5)
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/proactive-scan.py --project-root .
```

## V11 路径配置化副作用测试

为了验证 [feedback03-answer.md](../../.trae/reports/feedback03-answer.md) 的修复,
本 case 自动跟随 `~/.trae/my-trae-helper/todoapp-v11/.trae/fullstack4traev11.config.yaml`
(若存在),否则走默认值 `docs/archive/done/`。

可在 `.trae/fullstack4traev11.config.yaml` 加:

```yaml
paths:
  archive: custom-todo-archive/done
  changes_archive: custom-todo-archive/changes
```

跑 `spec-purge.py` 会落到新路径 — 已验证(详见 [_todoapp_e2e_v2.py](../../skill-markets/fullstack4TraeV11/scripts/_todoapp_e2e_v2.py) TEST 2)。