# i2v_vision_call.py — 命令行与集成指南

> `scripts/i2v_vision_call.py` 的完整使用手册:CLI / Shell pipe / Python import / 环境配置 / 错误码。

## §1 一行最小调用

```bash
python skill-markets/aigc-smart-kit/scripts/i2v_vision_call.py \
    --image path/to/photo.jpg \
    --out image-report.json
```

不传 `--keywords` 时,vision 完全自主判断。

## §2 参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--image` | path/url | **必填** | 本地路径或 `http(s)://` URL |
| `--keywords` | str | 空 | 空格分隔关键词,例:`"电影感 温暖 镜头推近"` |
| `--out` | path / `-` | `-`(stdout) | 输出 JSON 路径;`-` 表示 stdout |
| `--model` | str | `MiniMax-M3` | 可换 `MiniMax-M2.7` / `M2.5` / 其它兼容模型 |
| `--max-tokens` | int | 2048 | 最大输出 token |
| `--log-level` | str | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

## §3 输出契约(image-report.json)

严格遵循 [image-schema.md](image-schema.md) v1.0。退出码:

| 退出码 | 含义 | analyzer_status |
|--------|------|-----------------|
| `0` | vision 正常返回 + 解析成功 | `"ok"` |
| `2` | vision 调用失败 / 输出非 JSON / 缺 Key / 图片不存在等降级态 | `"partial: <原因>"` |

## §4 Shell pipe 集成

```bash
# 1) 直接 pipe 给 jq 抽字段
python scripts/i2v_vision_call.py --image photo.jpg | jq '.subject.name'

# 2) pipe 给下游 i2v-h3-prompt 包装 prompt(配合 stdin 入口)
python scripts/i2v_vision_call.py --image photo.jpg --keywords "电影感" \
  | python scripts/i2v_h3_build.py --stdin --out prompt.txt

# 3) 批量处理(for 循环)
for img in reference/*.jpg; do
    python scripts/i2v_vision_call.py --image "$img" --out "reports/$(basename "$img" .jpg).json"
done
```

## §5 Python import 集成

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skill-markets" / "aigc-smart-kit" / "scripts"))

from i2v_vision_call import run_analyze

report = run_analyze(
    image="photo.jpg",
    keywords=["电影感", "温暖"],
    model="MiniMax-M3",
    max_tokens=2048,
)

# report["analyzer_status"] == "ok" → 正常
# report["analyzer_status"].startswith("partial") → 降级
if report.get("analyzer_status") == "ok":
    subject_name = report["subject"]["name"]
    camera = report["dynamic"]["recommended_camera_motion"]
    print(f"主体:{subject_name} | 运镜:{camera['type']}")
```

**注意**:import 时会立即触发 `.env` 自动加载;已存在的环境变量优先级更高(用 `setdefault`,不会覆盖)。

## §6 环境变量

`.env` 加载顺序(先匹配先加载,setdefault 不覆盖 shell):

1. `cwd/.env`
2. 脚本所在目录向上 4 层内的 `.env`
3. `<skill>/.env`(兼容早期)

```
# .env(项目根目录推荐写法)
MINIMAX_API_KEY=eyJ-your-key-here       # 国内 api.minimaxi.com
MINIMAX_GLOBAL_API_KEY=eyJ-your-key     # 国际 api.minimax.io(二选一)
MINIMAX_TIMEOUT=60                       # 秒,默认 60
MINIMAX_BASE_URL=https://api.minimaxi.com  # 显式覆盖(可选)
```

**安全**:
- API Key 只入 `os.environ`,从不打印 / 日志 / 异常消息(用 `_client.mask_key()` 仅留末 4 位)。
- 不要把 `.env` 提交进 git(`.gitignore` 默认排除,但需自查)。
- `cat / echo $MINIMAX_API_KEY` 会泄露;只在脚本里引用。

## §7 错误码速查

| 现象 | 退出码 | 根因 | 修复 |
|------|--------|------|------|
| `[FATAL] 未找到 API Key...` | 2 | 缺 `MINIMAX_API_KEY` / `_GLOBAL_API_KEY` | 按 §6 配置 .env |
| `[401] 鉴权失败` | 2 | Key 无效 / 过期 | 重新签发 Key |
| `[429] 触发限流` | 2 | 调用过快 | 降低并发 / 加 `MINIMAX_TIMEOUT` |
| `[5xx] 服务端错误`(3 次重试后) | 2 | 上游服务异常 | 等待 + 重试;或换模型 |
| `ConnectionError` / `Timeout` | 2 | 网络 / 防火墙 | 检查代理 + 端口 |
| 图片文件不存在 | 2 | 路径错 / 没权限 | 用 `ls` 确认 + `--image` 用绝对路径 |
| 模型输出非 JSON | 2 | 模型没遵循 prompt | 降低 `temperature`(已 0.4);或换模型 |
| 退出 0 + `analyzer_status="ok"` | 0 | 正常 | 读 report 字段即可 |

## §8 跨平台

脚本纯 Python 3.9+ stdlib + `requests`(项目已统一依赖)。跨 win / macOS / linux 无差异:
- 路径用 `pathlib.Path`,自动处理分隔符。
- `.env` 加载跨平台(无 shell 命令依赖)。
- HTTP 走 `requests`,不走 `curl`/`wsl`/`bash`。

## §9 性能参考

- 单图本地 5MB → base64 ≈ 6.7MB,M3 1M context 完全够。
- 端到端响应:典型 8~20s(vision 模型耗时主导)。
- 并发:不内置并发(避免 Key 限流);上游 Agent 用 `asyncio.to_thread` 串行调用,或显式 `concurrent.futures.ThreadPoolExecutor(max_workers=3)` 控制。

## §10 关联引用

- [SKILL.md §2](SKILL.md) — 协议总览
- [references/image-schema.md](image-schema.md) — 输出 JSON 字段语义
- [references/scene-vocabulary.md](scene-vocabulary.md) — vision 输出词约束
- [references/failure-modes.md §10](failure-modes.md) — vision API 调用失败的修复细节
- 共享 HTTP 客户端:[`minimax-multimodal/scripts/_client.py`](../../../../minimax-multimodal/scripts/_client.py)