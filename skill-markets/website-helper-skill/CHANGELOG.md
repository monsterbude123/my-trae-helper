# Changelog — website-helper-skill

## v0.3.0 (2026-08-20)

### Architecture — 4-layer decomposition

* **Layer 1 (IO)** — `publish/docker/{compose,probe,install}.py` — typed wrappers
  around `ssh.exec_command("docker …")` / `docker-compose` / `certbot`. 2-way
  composable for any compose project (zentao / wordpress / nextcloud / gitlab).
* **Layer 2 (Actions)** — `publish/actions/{dns,nginx,ssl}.py` — one action per
  concern, returns `Step` dataclass, never raises. Trivially sub-agent-friendly.
* **Layer 3 (Pipeline)** — `publish/pipeline.py` — `Step` dataclass + `Pipeline`
  with listener fan-out, short-circuit on hard failure, structured timing.
* **Layer 4 (Router)** — `publish/cli.py` — typer commands only; `publish/commands/`
  houses per-command bodies (config / cert / list).

### File moves

* `cli.py` 443 → **191 lines** (-57%) — now router-only
* new `cli_helpers.py` — promoted `_get_dns_provider` to testable module
* new `commands/{config,cert,list}.py` — extracted non-deploy command bodies

### Tests

* `tests/test_pipeline_and_docker.py` — 26 cases covering Layer 1 + Layer 3
* uses `FakeSsh` to script `exec_command` responses without a real docker daemon
* **45 passed total** (was 19 in v0.2)

### Backwards compatibility

* `publish deploy` (CLI surface) unchanged; users see the same options
* `publish deploy --proxy` (added v0.2) unchanged
* `SshClient` API unchanged — all new helpers compose on top of it

---

## v0.2.0 (2026-08-20)

### New Features

- **VR-009 反代模式**：`publish deploy --proxy --upstream URL` 落地反向代理部署
  - 新增 `publish/nginx/config.py::generate_proxy_server_block()` — 含 WebSocket
    upgrade header、`client_max_body_size 100M`、proxy buffering 优化
  - `cli.deploy` 增加 mutex 校验：`--webroot` 与 `--proxy` 互斥
- **VR-010 vhost 路径自动探测**：`publish/nginx/vhost_probe.py::detect_vhost_target()`
  - 支持宝塔 / cPanel / OpenLiteSpeed / Debian 原生 / RHEL 5 种布局
  - 解决 2026-08-20 实战最大翻车点：**写到错目录 nginx 静默吞配置 → 138B 404**
- **VR-011 certbot 自动降级**：`publish/certs/cert_manager.py::request_cert()`
  - 检测 `certbot_nginx` 插件存在性，缺失时自动用 `--standalone` fallback
  - 自动启停 nginx + iptables 锁 80 端口以完成 HTTP-01 challenge
- **VR-007 upstream URL 校验**：`publish/utils/validators.py::validate_upstream()`
- **VR-008 .env 引号剥离**：`publish/config/store.py::_parse_env_file()`
  - 修 2026-08-20 PowerShell 写 `"C:\..."` 给 paramiko 报 `OSError [Errno 22]` 的根因

### Bug Fixes

- `validate_webroot` 强校验现在仅在 **未指定 `--proxy`** 时触发（脱离 `typer.Option(..., required)` 强制）

### Tests

- `tests/test_proxy_and_env.py` — 19 cases 覆盖三态（PASS / BLOCK / 边界）

### Docs

- `SKILL.md §4.5` 增加反代模式说明
- 仓库内 sink [README.md + distill-2026-08-20.md](skill-markets/website-helper-skill/) — 蒸馏原始踩坑
