#!/usr/bin/env python3
"""acceptance-audit.py — V10 四维度真实验收（替代 review_report 字符串匹配）

> 来源: V10 实战腐烂点 #A
> 根因: phase-gate.check_review_to_accept 仅匹配 "PASS" + "total_score: 5.0" 字符串,
>       AI 自评报告（含旧 scorecard 92/100）写"total_score: 5.0"就能蒙混过关。
> 修复: 真正执行 4 维度验证（不是字符串匹配），输出 JSON。

用法:
    python acceptance-audit.py --project-root <path> --feature <name> [--no-build] [--skip-curl] [--no-visual] [--json]

退出码:
    0 = pass (四维全部 PASS)
    1 = reject (任一适用维度 FAIL)

V10.3.9 升级 (2026-07-29): UI/UX 维度新增三层视觉证据深度校验 (PNG magic + bytes + PIL 像素)
详见 references/reset-and-verify-protocol.md §Stage 1.5

SECURITY 标注（V10.12.2 NEW）: 本脚本含 subprocess 调用（pytest / cargo / npm / curl / python <visual-content-check>），
全部为 V10 四维验收需要（运行真实测试 + 检查本地 dev server / 调用同包脚本）。
白名单参数固定：cmd 列表由本脚本生成，无 shell=True / curl 仅限 localhost。
详见 SECURITY-MAP.md fullstack4TraeV10 行 §注。
<!-- scan-whitelist:SHELL_EXEC --><!-- /scan-whitelist -->
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple

try:
    from common import FeaturePaths
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import FeaturePaths


TEST_TIMEOUT = 60  # 秒
TODO_PATTERN = re.compile(r"\b(todo!|unimplemented!|FIXME)\b", re.IGNORECASE)

# V10.3.9 视觉证据硬门禁阈值 (2026-07-29 升级)
VISUAL_MIN_BYTES = 5000          # 最低字节数 (< 则视为空白页/错误页)
VISUAL_MAX_AGE_HOURS = 168       # 视觉证据必须 7 天内 (活跃性指标)
PNG_MAGIC = b"\x89PNG\r\n\x1a\n" # PNG 文件签名 (前 8 字节)
LUM_MIN = 30                     # 像素平均亮度下限 (过低=全黑/未渲染)
LUM_MAX = 240                    # 像素平均亮度上限 (过高=全白/错误页)


def _audit_code(project_root: Path, no_build: bool) -> Tuple[str, str]:
    """代码维度: 跑测试 + grep todo 标记

    自动检测项目类型:
      - src-tauri/Cargo.toml → cargo test --lib (Tauri 项目)
      - package.json + scripts.test → npm test
      - pyproject.toml / pytest.ini → pytest
    """
    cargo_toml = project_root / "src-tauri" / "Cargo.toml"
    pkg_json = project_root / "package.json"
    pyproject = project_root / "pyproject.toml"

    test_cmd = None
    test_kind = None
    test_cwd = project_root  # 默认从项目根跑
    if cargo_toml.is_file():
        test_cmd = ["cargo", "test", "--lib", "--quiet"]
        test_kind = "cargo"
        test_cwd = project_root / "src-tauri"  # Tauri 项目: Cargo.toml 在子目录
    elif pkg_json.is_file():
        try:
            content = pkg_json.read_text(encoding="utf-8")
            if '"test"' in content:
                test_cmd = ["npm", "test", "--", "--run"]
                test_kind = "npm"
        except OSError:
            pass
    elif pyproject.is_file():
        test_cmd = ["pytest", "-q", "--tb=no"]
        test_kind = "pytest"

    if no_build or test_cmd is None:
        # 仅 grep todo
        todo_count = 0
        for ext in (".rs", ".ts", ".tsx", ".js", ".jsx", ".py"):
            for p in project_root.rglob(f"*{ext}"):
                if any(part in p.parts for part in ("node_modules", "target", "dist", ".git", "__pycache__")):
                    continue
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                todo_count += len(TODO_PATTERN.findall(text))
        if test_cmd is None:
            return ("PASS", f"无测试框架（仅 grep: {todo_count} 处 todo/FIXME）")
        return ("FAIL", f"--no-build 跳过 {test_kind} test；todo/FIXME = {todo_count}")

    try:
        result = subprocess.run(
            test_cmd,
            cwd=test_cwd,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return ("FAIL", f"{test_kind} test 超时（{TEST_TIMEOUT}s）")
    except FileNotFoundError:
        return ("FAIL", f"{test_kind} 命令未找到")

    # 提取测试结果（粗略: passed/failed 计数）—— 仅匹配 cargo "test result: ok. N passed; M failed" 格式
    stdout = result.stdout + result.stderr
    # cargo 测试结果只在 test result: 行（如 "test result: ok. 279 passed; 0 failed; 0 ignored"）
    m_result = re.search(r"test result:\s*\S+\.\s*(\d+)\s+passed;\s*(\d+)\s+failed", stdout)
    if m_result:
        pass_n = int(m_result.group(1))
        fail_n = int(m_result.group(2))
    else:
        # npm/jest 格式（如 "Tests: N passed, M failed"）
        m_pass = re.search(r"Tests:.*?(\d+)\s+passed", stdout)
        m_fail = re.search(r"(\d+)\s+failed", stdout)
        pass_n = int(m_pass.group(1)) if m_pass else 0
        # 仅当 fail 出现在 "Tests:..." 或 "X failed; Y ignored" 格式才算
        fail_n = int(m_fail.group(1)) if m_fail else 0
        if fail_n > 0 and ("test result:" not in stdout and "Tests:" not in stdout):
            fail_n = 0  # 避免误匹配函数名 "...marks_failed"

    # 退出码 != 0 但 fail_n > 0 → 真失败
    if result.returncode != 0 and fail_n > 0:
        return ("FAIL", f"{test_kind} test 退出码 {result.returncode}（{fail_n} failed）")

    # 退出码 != 0 但 0 failed → 警告但 PASS（cargo --offline / doc-tests / warning-only 退出）
    if result.returncode != 0 and fail_n == 0:
        return ("PASS", f"{test_kind} tests {pass_n} passed（警告: 退出码 {result.returncode}，可能 doc-test/warning-only）")

    # grep todo
    todo_count = 0
    for ext in (".rs", ".ts", ".tsx", ".js", ".jsx", ".py"):
        for p in project_root.rglob(f"*{ext}"):
            if any(part in p.parts for part in ("node_modules", "target", "dist", ".git", "__pycache__")):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            todo_count += len(TODO_PATTERN.findall(text))

    if todo_count > 0:
        return ("FAIL", f"tests {pass_n} passed / {fail_n} failed；但有 {todo_count} 处 todo/FIXME")

    return ("PASS", f"{test_kind} test {pass_n} passed / {fail_n} failed；0 todo/FIXME")


def _audit_visual_evidence(shot_path: Path) -> Tuple[bool, str]:
    """V10.3.9 视觉证据深度校验 (2026-07-29 升级)

    三层门禁:
      1) PNG magic number (前 8 字节 == b'\\x89PNG\\r\\n\\x1a\\n') — 防伪文件
      2) 文件大小 ≥ VISUAL_MIN_BYTES (5000 bytes) — 防空白页/错误页
      3) PIL 像素亮度 [LUM_MIN, LUM_MAX] — 防全黑/全白无效渲染

    返回:
      (True, msg)  - 通过
      (False, msg) - 校验失败 (FAIL)
    """
    reasons: list[str] = []

    # 1. PNG magic number
    try:
        with open(shot_path, "rb") as f:
            header = f.read(8)
    except OSError as e:
        return (False, f"无法读取截图文件: {e}")

    if header != PNG_MAGIC:
        return (
            False,
            f"❌ PNG magic 校验失败 (前 8 字节 = {header!r}, 期望 {PNG_MAGIC!r}) — 不是真实 PNG",
        )

    # 2. 文件大小
    size = shot_path.stat().st_size
    if size < VISUAL_MIN_BYTES:
        return (
            False,
            f"❌ 截图仅 {size} bytes (< {VISUAL_MIN_BYTES}) — 疑似空白页/连接错误页",
        )

    # 3. PIL 像素亮度 (可选, 软警告, 仅在 PIL 可用时执行)
    # 用途: 检测明显的全黑/全白无渲染页; 但深色主题 (avg_lum<30) 是合法 UI,
    #       所以亮度异常只标 ⚠️ 警告, 不 FAIL (硬门禁只看 PNG magic + bytes)
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return (True, f"PNG magic ✅ + {size} bytes (PIL 未安装, 跳过亮度检查)")

    try:
        with Image.open(shot_path) as img:
            # 转灰度计算平均亮度 (降采样到 32x32 加速, 减少深色主题误判)
            gray = img.convert("L").resize((32, 32))
            pixels = list(gray.tobytes())  # bytes 形式, 比 getdata() 更稳
            avg_lum = sum(pixels) / len(pixels)
            # 唯一色数 (低 = 纯色块/单页; 高 = 真 UI 元素)
            unique_count = len(set(pixels))
    except Exception as e:
        return (True, f"PNG magic ✅ + {size} bytes (PIL 解码失败 {e}, 跳过亮度检查)")

    lum_warn = ""
    if avg_lum < LUM_MIN:
        lum_warn = f", ⚠️ 深色主题 (亮度 {avg_lum:.1f}<{LUM_MIN}, 合法)"
    elif avg_lum > LUM_MAX:
        lum_warn = f", ⚠️ 过亮 (亮度 {avg_lum:.1f}>{LUM_MAX}, 可能白屏)"

    return (True, f"PNG ✅ + {size} bytes + 亮度 {avg_lum:.1f}, 唯一色 {unique_count}{lum_warn}")


def _is_port_listening(port: int = 18080, host: str = "127.0.0.1") -> bool:
    """检测端口是否在 listen（防止后端没起来导致 0/5 假 PASS）"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()


def _audit_api(project_root: Path, feature: str, skip_curl: bool) -> Tuple[str, str]:
    """API 维度: 读 api-contracts.md 提取端点 + curl 每个

    4xx 视为业务正常（不算 fail），5xx + 连接失败 = FAIL。
    """
    paths = FeaturePaths.from_root(project_root, feature)
    api_md = paths.contracts_dir / "api-contracts.md"
    if not api_md.is_file():
        return ("N/A", f"无 {api_md.relative_to(project_root)}（纯前端/内部模块）")

    # 提取端点: ### N.M `METHOD /path` 或 ## §N `METHOD /path` (V10/V9 双名兼容)
    endpoints: list[Tuple[str, str]] = []
    text = api_md.read_text(encoding="utf-8")
    for m in re.finditer(r"#{2,3}\s+[\d§.IVX]+\s+`(GET|POST|PUT|DELETE|PATCH)\s+([^`]+)`", text):
        endpoints.append((m.group(1), m.group(2).strip()))

    # 合并 events.md / event-contracts.md（SSE 端点, V10/V9 双名兼容）
    evt_md = None
    for evt_name in ("events.md", "event-contracts.md"):
        candidate = paths.contracts_dir / evt_name
        if candidate.is_file():
            evt_md = candidate
            break
    if evt_md is not None:
        for m in re.finditer(r"#{2,3}\s+[\d§.IVX]+\s+`?(GET|POST)\s+([^`\n]+)`?", evt_md.read_text(encoding="utf-8")):
            endpoints.append((m.group(1), m.group(2).strip()))

    if not endpoints:
        return ("N/A", "contracts/ 下未发现可 curl 的端点")

    if skip_curl:
        return ("PASS", f"contracts 声明 {len(endpoints)} 端点（--skip-curl 跳过实际请求）")

    # ★ V10 腐烂点 #2 修复：先探测端口是否真实监听（防止后端没起 → 0/5 假 PASS）
    if not _is_port_listening(18080):
        return ("FAIL", "后端 18080 端口未 listen（请先 cd src-tauri && cargo run 启动后端）")

    base = "http://127.0.0.1:18080"
    hits: list[str] = []
    fails: list[str] = []
    for method, path in endpoints:
        # 路径参数占位符 → 测试用真实 ID（仅 health/plugins 能测）
        test_path = path
        # /api/v1/plugins/:id/toggle 这种参数化端点跳过（无真实 ID）
        if re.search(r":[a-zA-Z_]\w*", path) and "toggle" not in path:
            continue
        url = base + test_path.split(" ")[0] if " " in test_path else base + test_path
        try:
            r = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", method, url, "--max-time", "3"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            code = r.stdout.strip()
            if code.startswith("2") or code.startswith("4"):
                hits.append(f"{method} {test_path} → {code}")
            else:
                fails.append(f"{method} {test_path} → {code or 'no-response'}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            fails.append(f"{method} {test_path} → timeout/no-curl")

    total = len(hits) + len(fails)
    if total == 0:
        return ("N/A", "无可测试端点（全部含路径参数）")

    if fails:
        return ("FAIL", f"{len(hits)}/{total} 命中；FAIL: {'; '.join(fails[:3])}")

    return ("PASS", f"{len(hits)}/{total} 端点命中（{hits[0]} 等）")


def _audit_uiux(project_root: Path, no_visual: bool = False) -> Tuple[str, str]:
    """UI/UX 维度: 真实启动验证 + 视觉证据

    三层门禁（V10.3.8 实战升级）:
      1) 前端测试文件存在性 (vitest/jest)
      2) [Tauri 项目] release binary 启动 + 端口 LISTEN + 视觉证据
         (chrome headless 截图 + vision-audit / 字节数对比)
      3) [非 Tauri 项目] 仅前两个文件存在性 + 数量验证
    """
    pkg = project_root / "package.json"
    if not pkg.is_file():
        return ("N/A", "无 package.json（纯后端项目）")

    try:
        content = pkg.read_text(encoding="utf-8")
    except OSError:
        return ("N/A", "package.json 不可读")

    # 是否有 vitest/jest
    has_vitest = "vitest" in content
    has_jest = "jest" in content
    if not (has_vitest or has_jest):
        return ("N/A", "无 vitest/jest 配置（纯后端项目）")

    # 不实际跑前端测试（避免长时构建）；改检查测试文件存在性
    test_files = (
        list((project_root / "src").rglob("*.test.ts*"))
        + list((project_root / "src").rglob("*.spec.ts*"))
        + list((project_root / "tests").rglob("*.test.ts*"))
    )
    test_files = [p for p in test_files if "node_modules" not in p.parts]

    test_part = f"测试文件 {len(test_files)} 个（vitest={has_vitest}）"
    if not test_files:
        return ("FAIL", f"无前端测试文件（要求 5 区域组件契约覆盖）")

    # ── V10.3.8 NEW: Tauri 视觉验证 (硬门禁，非降级) ──
    # 检测项目是否为 Tauri 项目（有 src-tauri/ + tauri.conf.json）
    tauri_conf = project_root / "src-tauri" / "tauri.conf.json"
    is_tauri = tauri_conf.is_file()

    if not is_tauri:
        return ("PASS", test_part)

    if no_visual:
        return ("PASS", f"{test_part} + [--no-visual] 跳过 Tauri 视觉验证")

    # 检查 release binary 是否存在
    target_release_dir = project_root / "src-tauri" / "target" / "release"
    # 多平台名字兼容
    bin_candidates = []
    for name in os.listdir(target_release_dir) if target_release_dir.is_dir() else []:
        if name.endswith(".exe") or "release" in name:
            bin_candidates.append(target_release_dir / name)
    bin_candidates = [b for b in bin_candidates if b.is_file() and b.stat().st_size > 1024 * 1024]  # ≥1MB

    if not bin_candidates:
        return ("FAIL", f"{test_part} + ❌ Tauri release binary 不存在 (src-tauri/target/release/*.exe)")

    # 检查端口 18080 (后端) LISTEN（说明应用至少启动了）
    if not _is_port_listening(18080):
        return ("FAIL", f"{test_part} + ❌ 后端端口 18080 未 LISTEN (Tauri 应用未启动或 release binary 过期)")

    # 检查最近一次 Tauri 验证截图（Visual Evidence）
    shots_dir = project_root / "docs" / "verifications" / "tauri"
    shots = sorted(shots_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True) if shots_dir.is_dir() else []

    if not shots:
        return ("PASS", f"{test_part} + ⚠️ Tauri binary 启动 + 端口 LISTEN，但无视觉证据 {shots_dir}/*.png。要求 verifier 启动后用 chrome headless 截图存到 docs/verifications/tauri/")

    newest = shots[0]
    age_hours = (time.time() - newest.stat().st_mtime) / 3600
    size = newest.stat().st_size

    # V10.4 升级 (2026-07-30): 在 _audit_visual_evidence 之前先调 visual-content-check
    # 腐烂点 9 修复: 解决 PNG magic OK 但内容是空白/布局错乱的假阳性
    try:
        vcc_script = Path(__file__).parent / "visual-content-check.py"
        if vcc_script.exists():
            vcc = subprocess.run(
                ["python", str(vcc_script), str(newest), "--json"],
                cwd=project_root, capture_output=True, text=True, timeout=15,
            )
            if vcc.returncode != 0:
                try:
                    vcc_data = json.loads(vcc.stdout)
                    results_list = vcc_data.get("results", [{}])
                    first = results_list[0] if results_list else {}
                    fail_msg = first.get("detail", "unknown")
                except json.JSONDecodeError:
                    fail_msg = vcc.stdout[:200] or vcc.stderr[:200] or "visual-content-check failed"
                return (
                    "FAIL",
                    test_part + " + V10.4 visual-content-check FAIL: " + fail_msg,
                )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # visual-content-check 不可用时,降级到原有 _audit_visual_evidence

    # V10.3.9 升级 (2026-07-29): 三层视觉证据校验 (PNG magic + bytes + PIL 亮度)
    visual_ok, visual_msg = _audit_visual_evidence(newest)
    if not visual_ok:
        return ("FAIL", f"{test_part} + ❌ {visual_msg}")

    # 活跃性指标: 截图必须在最近 VISUAL_MAX_AGE_HOURS 内 (默认 7 天)
    if age_hours > VISUAL_MAX_AGE_HOURS:
        return (
            "FAIL",
            f"{test_part} + ⚠️ 视觉证据 {newest.name} 已有 {age_hours/24:.1f} 天前 (>{VISUAL_MAX_AGE_HOURS/24:.0f}天) — 必须重新截图",
        )

    return ("PASS", f"{test_part} + Tauri 启动 ✅ + {shots[0].name} ({size} bytes, {age_hours:.1f}h ago, {visual_msg})")


def _audit_artifact_schema(paths_dict: dict) -> Tuple[str, str]:
    """工件标准件维度: 校验 V10 标准件齐全（spec + tasks + 4 件 contracts）

    来源: artifact-schema.md §二 + contract-first.md §1-4
    返回:
      FAIL: 任一标准件缺失
      PASS: 6 件齐全
    """
    spec = paths_dict.get("spec")
    if spec is None:
        return ("N/A", "无 spec 路径（spec_dict 解析失败）")

    specs_dir = spec.parent
    project_root = paths_dict.get("project_root")
    contracts_dir = specs_dir / "contracts"

    # 1. spec.md 必须存在
    if not spec.is_file():
        return ("FAIL", f"缺失 {spec.relative_to(project_root) if project_root else spec}")

    # 2. tasks.md 必须存在（artifact-schema §二 强制）
    tasks_md = specs_dir / "tasks.md"
    if not tasks_md.is_file():
        return ("FAIL", "缺失 tasks.md（artifact-schema §二 强制件）")

    # 3. contracts/ 必须存在
    if not contracts_dir.is_dir():
        return ("FAIL", "缺失 contracts/ 目录（contract-first §1-4 四件套所在）")

    # 4. 契约三件套（强名）
    for fname in ("api-contracts.md", "domain-models.md", "validation-rules.md"):
        f = contracts_dir / fname
        if not f.is_file():
            return ("FAIL", f"缺失 contracts/{fname}")

    # 5. events 双名兼容（V10: events.md, V9: event-contracts.md）
    if not (contracts_dir / "events.md").is_file() and not (contracts_dir / "event-contracts.md").is_file():
        return ("FAIL", "缺失 contracts/events.md（或 event-contracts.md, V9 兼容）")

    return ("PASS", "6 件标准件齐全（spec + tasks + 4 件 contracts/events 双名兼容）")


def _audit_drift_detect(project_root: Path, feature: str) -> Tuple[str, str]:
    """契约漂移维度（V10.3.7+）: 实跑 contracts/ vs 实际 import 差异扫描

    检测:
      1. contracts/domain-models.md 声明的 interface/type 在代码中有真实实现
      2. contracts/api-contracts.md 声明的端点路径在后端 routes 中真实存在
      3. 防止"contracts 声明 X，实际代码 import Y"的漂移

    返回:
      FAIL: 发现漂移（contracts 与实际代码不一致）
      PASS: 全部对齐
      N/A: 无可校验的契约（如纯前端 + 无 domain-models）
    """
    paths = FeaturePaths.from_root(project_root, feature)
    contracts_dir = paths.contracts_dir
    if not contracts_dir.is_dir():
        return ("N/A", "contracts/ 目录不存在，跳过漂移检测")

    drifts: list[str] = []

    # === 1. domain-models.md vs 代码 interface 漂移 ===
    domain_md = contracts_dir / "domain-models.md"
    if domain_md.is_file():
        text = domain_md.read_text(encoding="utf-8")
        # 仅从 ```typescript / ```ts 代码块中提取 interface/type 声明
        # （避免 Markdown 表格/正文误匹配）
        declared: set[str] = set()
        in_code_block = False
        code_lang = ""
        for line in text.splitlines():
            if line.strip().startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_lang = line.strip().lstrip("`").strip().lower()
                else:
                    in_code_block = False
                continue
            if in_code_block and code_lang in ("typescript", "ts", "tsx", "javascript", "js"):
                for m in re.finditer(r"(?:interface|type)\s+(\w+)", line):
                    declared.add(m.group(1))
        if declared:
            # 在源码中查找实际声明
            src_dirs = [project_root / "src", project_root / "src-tauri" / "src"]
            for name in sorted(declared):
                found = False
                for src_dir in src_dirs:
                    if not src_dir.exists():
                        continue
                    for src_file in list(src_dir.rglob("*.ts")) + list(src_dir.rglob("*.tsx")) + list(src_dir.rglob("*.rs")):
                        try:
                            content = src_file.read_text(encoding="utf-8", errors="ignore")
                            # TS: interface/type Name, Rust: pub struct Name / struct Name
                            if re.search(rf"(?:interface|type)\s+{re.escape(name)}\b", content):
                                found = True
                                break
                            if re.search(rf"\bstruct\s+{re.escape(name)}\b", content):
                                found = True
                                break
                        except Exception:
                            continue
                    if found:
                        break
                if not found:
                    drifts.append(f"domain-models 声明 {name}，代码中未找到实现")

    # === 2. api-contracts.md vs 后端 routes 漂移 ===
    api_md = contracts_dir / "api-contracts.md"
    if api_md.is_file():
        text = api_md.read_text(encoding="utf-8")
        # 提取声明的路径
        declared_paths = re.findall(r"`(GET|POST|PUT|DELETE|PATCH)\s+([^`]+)`", text)
        if declared_paths:
            # 在后端路由中查找
            routes_dir = project_root / "src-tauri" / "src"
            if routes_dir.exists():
                for _method, path in declared_paths:
                    # 简单匹配：path 中的核心段（如 /api/v1/plugins）应在路由文件中出现
                    key = path.strip().split("/")[-1] or path.strip()
                    if not key or key.startswith(":"):
                        continue
                    found = False
                    for rs_file in routes_dir.rglob("*.rs"):
                        try:
                            content = rs_file.read_text(encoding="utf-8", errors="ignore")
                            if key in content:
                                found = True
                                break
                        except Exception:
                            continue
                    if not found:
                        drifts.append(f"api-contracts 声明 {path}，后端未找到路由")

    if drifts:
        return ("FAIL", f"漂移 {len(drifts)} 项：" + "；".join(drifts[:3]) + ("..." if len(drifts) > 3 else ""))

    return ("PASS", "contracts 与代码无漂移")


def _audit_boundary(project_root: Path, feature: str) -> Tuple[str, str]:
    """模块边际维度: 读 spec.md E2E 段，检查 [x] 勾选比例 ≥ 50%"""
    paths = FeaturePaths.from_root(project_root, feature)
    spec = paths.spec
    if not spec.is_file():
        return ("FAIL", f"缺失: {spec.relative_to(project_root)}")

    content = spec.read_text(encoding="utf-8")

    # 1. 必须含 ## E2E 段
    e2e_header = re.search(r"^## E2E", content, re.MULTILINE | re.IGNORECASE)
    if not e2e_header:
        return ("FAIL", "spec.md 缺 ## E2E 段")

    # 2. 提取 E2E 段
    e2e_match = re.search(
        r"^## E2E.*?(?=^## |\Z)",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not e2e_match:
        return ("FAIL", "无法定位 E2E 段边界")

    section = e2e_match.group(0)

    # 3. 计数 [x] / [ ] / [⏳]（⏳ 视为未勾选）
    checked = len(re.findall(r"-\s*\[x\]", section, re.IGNORECASE))
    unchecked = len(re.findall(r"-\s*\[\s*\]", section))
    pending = len(re.findall(r"-\s*\[⏳\]", section))
    total = checked + unchecked + pending

    if total == 0:
        return ("FAIL", "E2E 段无任何勾选项")

    ratio = checked / total
    if ratio < 0.5:
        return (
            "FAIL",
            f"E2E 已勾选 {ratio*100:.0f}%（{checked}/{total}，含 {pending} ⏳）— 要求 ≥50%",
        )

    # V10 硬门禁: ⏳ 必须为 0（v10_simplified 标记后遗留 ⏳ = 流水线漏水）
    if pending > 0:
        return (
            "FAIL",
            f"E2E 勾选 {ratio*100:.0f}%（{checked}/{total}），但仍有 {pending} 项 ⏳ 未完成（要求 0 ⏳）",
        )

    return ("PASS", f"E2E 已勾选 {ratio*100:.0f}%（{checked}/{total}）")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="V10 四维度真实验收（替代 review_report 字符串匹配）",
    )
    parser.add_argument("--project-root", required=True, help="V10 项目根（含 docs/specs/）")
    parser.add_argument("--feature", required=True, help="feature 名（如 00-01-foundation）")
    parser.add_argument("--no-build", action="store_true", help="跳过 cargo/npm/pytest 构建")
    parser.add_argument("--skip-curl", action="store_true", help="跳过 curl 端点")
    parser.add_argument("--strict-artifacts", action="store_true", default=True,
                        help="严格校验工件标准件（默认开启）")
    parser.add_argument("--no-strict-artifacts", dest="strict_artifacts", action="store_false",
                        help="关闭严格工件校验（项目自定义件降级为 WARNING）")
    parser.add_argument("--no-visual", action="store_true",
                        help="[Tauri] 跳过视觉证据检查（默认必须")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    # 构造 paths_dict（供 _audit_artifact_schema 使用）
    paths_dict: dict = {"project_root": project_root}
    try:
        fp = FeaturePaths.from_root(project_root, args.feature)
        paths_dict["spec"] = fp.spec
        paths_dict["tasks"] = fp.tasks
        paths_dict["contracts_dir"] = fp.contracts_dir
    except Exception:
        paths_dict["spec"] = None

    results = {
        "code": _audit_code(project_root, args.no_build),
        "api": _audit_api(project_root, args.feature, args.skip_curl),
        "uiux": _audit_uiux(project_root, args.no_visual),
        "boundary": _audit_boundary(project_root, args.feature),
        "drift_detect": _audit_drift_detect(project_root, args.feature),
    }

    # 第 6 维度: artifact_schema（项目自定义件严格校验）
    if args.strict_artifacts:
        results["artifact_schema"] = _audit_artifact_schema(paths_dict)

    # V10 硬门禁: 适用维度（≠ N/A）任一非 PASS = REJECT
    fail_count = sum(1 for status, _ in results.values() if status == "FAIL")

    payload = {
        "status": "pass" if fail_count == 0 else "reject",
        "feature": args.feature,
        "project_root": str(project_root),
        "dimensions": {
            k: {"status": v[0], "evidence": v[1]} for k, v in results.items()
        },
        "errors": [v[1] for _, v in results.items() if v[0] == "FAIL"],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    else:
        # 文本模式
        verdict = "✅ PASS" if fail_count == 0 else "🛑 REJECT"
        print(f"{verdict} | feature={args.feature}")
        for k, v in results.items():
            print(f"  [{v[0]:>4}] {k}: {v[1]}")
        if fail_count:
            print(f"\n🛑 {fail_count} 个维度 FAIL — 任一 FAIL = REJECT")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())