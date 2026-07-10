"""
Vision Audit — Qwen3-VL 视觉验收脚本 (Python)

技能目录: .trae/skills/vision-audit/
读取 E2E 截图 → 调用本地 VL 模型 → 输出结构化审计报告

依赖: pip install httpx pillow
用法:
  python .trae/skills/vision-audit/scripts/vision-audit.py --dir frontend/debug/screenshots
  python .trae/skills/vision-audit/scripts/vision-audit.py --single frontend/debug/screenshots/route-01-HomeView.png
  python .trae/skills/vision-audit/scripts/vision-audit.py --dir frontend/test-results --failed-only
  python .trae/skills/vision-audit/scripts/vision-audit.py --describe <file>  # 线框图识别（带降级）
"""

import os
import sys
import json
import base64
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO

# ↓ Python 3.8+ stdlib (no extra deps)
import http.client
import urllib.parse

# 可选：Pillow 用于图片缩放
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ═══════════════════════════════════════
# 项目根目录探测
# ═══════════════════════════════════════

def find_project_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    for d in [script_dir] + list(script_dir.parents):
        if (d / '.trae').exists() or (d / '.git').exists():
            return d
    return script_dir.parents[3]  # fallback


PROJECT_ROOT = find_project_root()
SKILL_DIR = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════
# 配置加载
# ═══════════════════════════════════════

def load_env() -> dict:
    candidates = [
        PROJECT_ROOT / '.env.vision',
        SKILL_DIR / '.env.vision',
        Path.cwd() / '.env.vision',
    ]

    env_path = None
    for p in candidates:
        if p.exists():
            env_path = p
            break

    if not env_path:
        print(f'❌ 未找到 .env.vision 配置文件')
        print(f'   搜索路径: {[str(c) for c in candidates]}')
        print(f'   请从 {SKILL_DIR / ".env.vision.example"} 复制并配置')
        sys.exit(1)

    print(f'📋 配置: {env_path}')

    raw = env_path.read_text(encoding='utf-8')
    config = {}
    for line in raw.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        config[k] = v

    return {
        'api_base_url': config.get('VISION_API_BASE_URL', 'http://localhost:1234/v1'),
        'model_name': config.get('VISION_MODEL_NAME', 'qwen3-vl-8b-instruct'),
        'api_key': config.get('VISION_API_KEY', 'lm-studio'),
        'timeout': int(config.get('VISION_REQUEST_TIMEOUT', '30000')),
        'max_concurrency': int(config.get('VISION_MAX_CONCURRENCY', '2')),
        'worker_start_delay': int(config.get('VISION_WORKER_START_DELAY', '500')),
        'retries': int(config.get('VISION_MAX_RETRIES', '2')),
        'retry_delay': int(config.get('VISION_RETRY_DELAY_MS', '2000')),
        'screenshots_dir': config.get('VISION_SCREENSHOTS_DIR', 'frontend/debug/screenshots'),
        'report_dir': config.get('VISION_REPORT_DIR', 'frontend/debug/reports/vision'),
    }


# ═══════════════════════════════════════
# 图片处理
# ═══════════════════════════════════════

def image_to_base64(file_path: str, resize_long_edge: int = 0) -> str:
    """读取图片并转为 base64。如果指定 resize_long_edge，等比缩放最长边。"""
    if resize_long_edge > 0 and HAS_PIL:
        img = Image.open(file_path)
        w, h = img.size
        if max(w, h) > resize_long_edge:
            ratio = resize_long_edge / max(w, h)
            new_size = (int(w * ratio), int(h * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format='PNG', optimize=True)
            return base64.b64encode(buf.getvalue()).decode('ascii')

    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')


# ═══════════════════════════════════════
# VL 模型调用
# ═══════════════════════════════════════

AUDIT_PROMPT = """你是一个专业的 UI/UX 审计助手。请分析这张网页截图，按以下维度给出评估，输出 JSON 格式：

{
  "layout": "简洁描述页面布局结构（顶栏/侧栏/内容区/底栏），各区域尺寸是否合理",
  "content": "页面内容状态：正常渲染 / 空态占位 / 错误态 / 加载中，空态是否有引导文案",
  "style": "发现的样式问题：文字重叠、截断、颜色对比度不足、间距不一致等",
  "interactions": "可见按钮和交互元素是否可正常点击，是否有缺失的关键操作",
  "risk": "LOW | MEDIUM | HIGH",
  "verdict": "一句话总结页面状态"
}

规则：
- risk=LOW: 页面正常，或仅有可接受的空态
- risk=MEDIUM: 有轻微布局偏移、间距问题、非关键元素缺失
- risk=HIGH: 白屏、主要区域空白、样式严重错误、错误信息暴露
- 只输出 JSON，不要额外说明"""

# ── ─describe 模式专用 prompt：线框图识别 ──
WIREFRAME_PROMPT = """你是一个页面结构分析助手。请分析这张截图，用 ASCII 线框图描述页面布局。输出 JSON，无多余文字：

{
  "diagram": "用 ┌┐└┘├┤│┬┴┼─ 字符画页面布局线框图。标出每个区域的实际文字和按钮，禁止使用 [按钮] [输入框] 等占位符。区域结构至少包含：顶栏、左侧、中心、右侧、底栏、状态栏等可见区域",
  "zones": {
    "titlebar": "顶栏实际文字和按钮",
    "left_panel": "左侧面板内容",
    "center": "中心区域实际内容（对话/编辑/表格等）",
    "right_panel": "右侧面板内容",
    "bottom_panel": "底栏标签和内容",
    "statusbar": "状态栏信息"
  },
  "verdict": "一句话描述当前页面是什么内容、处于什么状态"
}"""


async def call_vl_model(config: dict, image_b64: str, prompt: str) -> dict:
    """发送图片到 Qwen3-VL API，返回解析后的 JSON。（调用方负责重试）"""
    import httpx

    url = f"{config['api_base_url']}/chat/completions"
    headers = {'Content-Type': 'application/json'}
    if config['api_key']:
        headers['Authorization'] = f'Bearer {config["api_key"]}'
    payload = {
        'model': config['model_name'],
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {'url': f'data:image/png;base64,{image_b64}'},
                    },
                    {'type': 'text', 'text': prompt},
                ],
            },
        ],
        'max_tokens': 4096,
        'temperature': 0.1,
        'stop': ['\n\n\n'],
    }

    async with httpx.AsyncClient(timeout=config['timeout'] / 1000.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError(f'API {resp.status_code}: {resp.text[:200]}')

        data = resp.json()
        raw = data.get('choices', [{}])[0].get('message', {}).get('content', '')

        # 剥离 thinking 内容
        import re
        content = re.sub(r'/think.*?/think', '', raw, flags=re.DOTALL)
        content = re.sub(r'<think.*?</think>', '', content, flags=re.DOTALL)
        content = content.strip() or raw

        return _parse_vl_response(content)


def _parse_vl_response(content: str) -> dict:
    clean = content.replace('```json\n', '').replace('\n```', '').strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    import re
    m = re.search(r'\{[\s\S]*\}', clean)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    return {
        'layout': '无法解析',
        'content': '模型返回格式异常',
        'style': content[:300],
        'interactions': '未评估',
        'risk': 'MEDIUM',
        'verdict': 'VL 模型返回解析失败，请检查模型配置',
    }


# ═══════════════════════════════════════
# 重试与并发辅助
# ═══════════════════════════════════════

async def call_vl_model_with_retry(config: dict, image_b64: str, prompt: str) -> dict:
    """带指数退避重试的 VL 调用。仅重试超时/5xx 错误，4xx 不重试。"""
    max_retries = config['retries']
    base_delay = config['retry_delay'] / 1000.0

    last_err = None
    for i in range(max_retries + 1):
        try:
            return await call_vl_model(config, image_b64, prompt)
        except Exception as e:
            last_err = e
            # 不重试 4xx
            if 'API 4' in str(e):
                raise
            if i < max_retries:
                delay = base_delay * (2 ** i)
                print(f'🔄 第{i + 1}次重试（{delay:.0f}s 后）')
                await asyncio.sleep(delay)
    raise last_err


# ═══════════════════════════════════════
# 截图收集
# ═══════════════════════════════════════

def resolve_path(rel: str) -> Path:
    p = PROJECT_ROOT / rel
    if p.exists():
        return p
    return Path.cwd() / rel


def gather_screenshots(dir_path: str, failed_only: bool = False) -> list:
    d = resolve_path(dir_path)
    if not d.exists():
        print(f'❌ 目录不存在: {d}')
        return []

    files = sorted(
        p for p in d.iterdir()
        if p.suffix.lower() == '.png'
        and (not failed_only or 'failed' in p.name)
    )
    return files


# ═══════════════════════════════════════
# 报告生成
# ═══════════════════════════════════════

def generate_markdown(summary: dict, findings: list, model: str) -> str:
    lines = [
        '# Vision Audit Report',
        '',
        f'> **生成时间**: {datetime.now(timezone.utc).isoformat()}',
        f'> **模型**: {model}',
        f'> **总计**: {summary["total"]} | 🟢 LOW: {summary["low"]} | 🟡 MEDIUM: {summary["medium"]} | 🔴 HIGH: {summary["high"]}',
        '',
        '---',
        '',
        '## 问题汇总',
        '',
    ]

    high = [f for f in findings if f['risk'] == 'HIGH']
    medium = [f for f in findings if f['risk'] == 'MEDIUM']
    low = [f for f in findings if f['risk'] == 'LOW']

    if high:
        lines.append(f'### 🔴 HIGH ({len(high)})')
        lines.append('')
        for f in high:
            d = f['dimensions']
            lines.append(f'#### {f["screenshot"]}')
            lines.append(f'- **布局**: {d["layout"]}')
            lines.append(f'- **内容**: {d["content"]}')
            lines.append(f'- **样式**: {d["style"]}')
            lines.append(f'- **交互**: {d["interactions"]}')
            lines.append(f'- **结论**: {f["verdict"]}')
            lines.append('')
    else:
        lines.append('✅ 无 HIGH 级别问题')
        lines.append('')

    if medium:
        lines.append(f'### 🟡 MEDIUM ({len(medium)})')
        lines.append('')
        for f in medium:
            d = f['dimensions']
            lines.append(f'#### {f["screenshot"]}')
            lines.append(f'- **布局**: {d["layout"]}')
            lines.append(f'- **内容**: {d["content"]}')
            lines.append(f'- **样式**: {d["style"]}')
            lines.append(f'- **结论**: {f["verdict"]}')
            lines.append('')

    lines.append(f'### 🟢 LOW ({len(low)})')
    lines.append('')
    for f in low:
        lines.append(f'- **{f["screenshot"]}**: {f["verdict"]}')

    return '\n'.join(lines)


def generate_json(summary: dict, findings: list, model: str) -> str:
    return json.dumps({
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'model': model,
        'summary': summary,
        'findings': [
            {
                'screenshot': f['screenshot'],
                'risk': f['risk'],
                'dimensions': f['dimensions'],
                'verdict': f['verdict'],
            }
            for f in findings
        ],
    }, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════
# --describe 模式：线框图识别（带降级）
# ═══════════════════════════════════════

async def run_describe_mode(args):
    """线框图识别模式。
    
    Tier 1: 尝试本地 VL 模型 → 输出 ASCII 线框图 JSON。
    Tier 2 (降级): VL 不可用 → 输出结构化指令，由 AI Agent 使用
                   read_media_file MCP 工具直接读取图片分析。
    """
    file_path = resolve_path(args.describe)
    if not file_path.exists():
        print(json.dumps({
            'status': 'error',
            'reason': f'文件不存在: {file_path}',
        }, ensure_ascii=False))
        sys.exit(1)

    image_b64 = image_to_base64(str(file_path), args.resize)

    # 尝试加载配置（不强制要求 .env.vision 存在 — 降级流程需要）
    try:
        config = load_env()
        vl_available = True
    except SystemExit:
        config = {
            'api_base_url': 'http://localhost:1234/v1',
            'model_name': 'qwen3-vl-8b-instruct',
            'api_key': 'lm-studio',
            'timeout': 30000,
            'retries': 1,
            'retry_delay': 2000,
        }
        vl_available = False
    except Exception:
        vl_available = False
        config = {}

    # Tier 1: 尝试本地 VL 模型
    if vl_available:
        try:
            result = await call_vl_model_with_retry(config, image_b64, WIREFRAME_PROMPT)
            # 提取 diagram / zones / verdict
            diagram = result.get('diagram', '')
            zones = result.get('zones', {})
            verdict = result.get('verdict', '')
            if isinstance(zones, str):
                try:
                    zones = json.loads(zones)
                except (json.JSONDecodeError, TypeError):
                    zones = {}
            if not isinstance(zones, dict):
                zones = {}

            output = {
                'status': 'ok',
                'source': 'local_vl',
                'model': config.get('model_name', 'unknown'),
                'diagram': diagram,
                'zones': zones,
                'verdict': verdict,
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return
        except Exception as e:
            vl_error = str(e)
    else:
        vl_error = 'VISION_API_KEY 未配置或 .env.vision 不存在'

    # Tier 2: 降级 — 输出指令让 AI Agent 用 read_media_file MCP 分析
    fallback_output = {
        'status': 'fallback',
        'reason': f'本地 VL 模型不可用: {vl_error}',
        'image_path': str(file_path.absolute()),
        'instruction': (
            '请使用 run_mcp 调用 mcp_Filesystem 的 read_media_file 工具读取此图片，'
            '然后根据下面的 prompt 分析截图内容，输出 ASCII 线框图。'
        ),
        'prompt': WIREFRAME_PROMPT.strip(),
        'mcp_call': {
            'server_name': 'mcp_Filesystem',
            'tool_name': 'read_media_file',
            'args': {
                'path': str(file_path.absolute()),
            },
        },
    }
    print(json.dumps(fallback_output, ensure_ascii=False, indent=2))
    # 降级不算错误，exit 0 让 Agent 继续处理 fallback 指令
    sys.exit(0)


# ═══════════════════════════════════════
# 主入口
# ═══════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(description='Vision Audit — Qwen3-VL UI/UX 视觉验收')
    parser.add_argument('--dir', help='截图目录')
    parser.add_argument('--single', help='单张截图路径')
    parser.add_argument('--describe', help='线框图识别模式：分析单张截图内容，输出 ASCII 线框图（VL 不可用时输出降级指令给 AI Agent）')
    parser.add_argument('--failed-only', action='store_true', help='仅分析失败截图')
    parser.add_argument('--prompt', help='自定义分析 prompt')
    parser.add_argument('--resize', type=int, default=0, help='缩放最长边（像素），0=不缩放')
    parser.add_argument('--concurrency', type=int, default=None, help='覆盖并发的最大数量')
    args = parser.parse_args()

    if not args.dir and not args.single and not args.describe:
        print('用法: python vision-audit.py --dir <directory> [--failed-only]')
        print('  或: python vision-audit.py --single <file> [--prompt "..."]')
        print('  或: python vision-audit.py --describe <file>  # 线框图识别，VL 不可用时输出降级指令')
        sys.exit(1)

    # ── describe 模式：线框图识别（带降级） ──
    if args.describe:
        await run_describe_mode(args)
        return

    config = load_env()
    if args.concurrency is not None:
        config['max_concurrency'] = args.concurrency

    print(f'🔍 Vision Audit — 模型: {config["model_name"]}')
    print(f'   服务地址: {config["api_base_url"]}')
    print(f'   项目根: {PROJECT_ROOT}')
    print(f'   并发: {config["max_concurrency"]} | 启动间隔: {config["worker_start_delay"]}ms | 重试: {config["retries"]}次/间隔{config["retry_delay"]}ms')

    # 检查 httpx
    try:
        import httpx  # noqa: F401
    except ImportError:
        print('❌ 缺少 httpx 依赖，请执行: pip install httpx')
        sys.exit(1)

    # 收集截图
    if args.single:
        files = [resolve_path(args.single)]
    else:
        files = gather_screenshots(args.dir, args.failed_only)

    if not files:
        print('❌ 未找到 PNG 截图')
        sys.exit(1)

    print(f'📸 待分析: {len(files)} 张截图')

    # 预热
    print('🔌 连接 VL 模型...')
    try:
        import httpx
        health_headers = {}
        if config['api_key']:
            health_headers['Authorization'] = f'Bearer {config["api_key"]}'
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f'{config["api_base_url"]}/models',
                headers=health_headers,
            )
            if r.status_code == 200:
                print('   ✅ 模型服务可用')
    except Exception:
        print('   ⚠️ 模型服务连接超时，继续尝试...')

    print()

    # 分析（交错启动 worker + 信号量限流 + 指数退避重试）
    prompt = args.prompt or AUDIT_PROMPT
    sem = asyncio.Semaphore(config['max_concurrency'])

    async def analyze_one(file_path: Path, worker_id: int):
        # 交错延迟：每个 worker 首次启动前等待 worker_id * start_delay
        if worker_id > 0:
            delay = worker_id * config['worker_start_delay'] / 1000.0
            await asyncio.sleep(delay)
        async with sem:
            name = file_path.name
            print(f'  📷 {name} ... ', end='', flush=True)

            try:
                image_b64 = image_to_base64(str(file_path), args.resize)
                result = await call_vl_model_with_retry(config, image_b64, prompt)

                finding = {
                    'screenshot': name,
                    'risk': result.get('risk', 'MEDIUM'),
                    'dimensions': {
                        'layout': result.get('layout', '未评估'),
                        'content': result.get('content', '未评估'),
                        'style': result.get('style', '未评估'),
                        'interactions': result.get('interactions', '未评估'),
                    },
                    'verdict': result.get('verdict', '无结论'),
                }

                emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}.get(finding['risk'], '⚪')
                print(f'{emoji} {finding["risk"]} — {finding["verdict"]}')
                return finding
            except Exception as e:
                print(f'❌ 失败: {e}')
                return {
                    'screenshot': name,
                    'risk': 'MEDIUM',
                    'dimensions': {
                        'layout': '分析失败', 'content': '分析失败',
                        'style': str(e), 'interactions': '未评估',
                    },
                    'verdict': f'VL 调用失败: {e}',
                }

    # 分配 worker_id，保证交错启动顺序
    tasks = [analyze_one(f, i % config['max_concurrency']) for i, f in enumerate(files)]
    findings = await asyncio.gather(*tasks)
    findings = list(findings)

    # 汇总
    summary = {
        'total': len(findings),
        'low': sum(1 for f in findings if f['risk'] == 'LOW'),
        'medium': sum(1 for f in findings if f['risk'] == 'MEDIUM'),
        'high': sum(1 for f in findings if f['risk'] == 'HIGH'),
    }

    print()
    print(f'📊 汇总: {summary["total"]} | 🟢 {summary["low"]} | 🟡 {summary["medium"]} | 🔴 {summary["high"]}')

    # 写报告
    report_dir = resolve_path(config['report_dir'])
    report_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    md_path = report_dir / f'vision-report-{ts}.md'
    json_path = report_dir / f'vision-report-{ts}.json'

    md_path.write_text(generate_markdown(summary, findings, config['model_name']), encoding='utf-8')
    json_path.write_text(generate_json(summary, findings, config['model_name']), encoding='utf-8')

    print(f'📄 报告: {md_path}')
    print(f'📄 JSON: {json_path}')

    if summary['high'] > 0:
        print(f'\n⚠️ 发现 {summary["high"]} 个 HIGH 级别问题，需人工复核')
        sys.exit(1)
    else:
        print('\n✅ Vision Audit 通过')
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
