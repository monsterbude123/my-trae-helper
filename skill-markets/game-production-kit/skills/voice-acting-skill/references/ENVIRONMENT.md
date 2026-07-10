# 运行环境准备指南

## 1. 基本依赖

```bash
pip install -e .
# 安装 click, gradio-client, httpx, pydantic
```

Python >= 3.11 必需。验证：

```bash
python -m pytest scripts/tests/ -v
# 35 passed 即环境正常
```

## 2. TTS 服务配置

三引擎至少启动一个才能合成。端口冲突时通过 `.env` 修改。

```bash
# 项目根目录的 .env 文件
COSYVOICE_URL=http://127.0.0.1:15000
OMNIVOICE_URL=http://localhost:7860
QWENTTS_URL=http://localhost:15001
```

### 2a. CosyVoice3（推荐，速度最快）

```powershell
cd D:\workspace\AIGC\ai-tts\CosyVoice
.venv\Scripts\python.exe webui.py --port 15000 --model_dir pretrained_models/Fun-CosyVoice3-0.5B
```

验证：

```bash
curl http://127.0.0.1:15000/gradio_api/queue/status
# 返回 JSON 即服务正常
```

已知问题：

| 症状 | 原因 | 解决 |
|------|------|------|
| webui 启动报 GPT_SoVITS 等无关错误 | 旧版 webui.py 兼容性 | 不影响，忽略 |
| CUDA warning | CUDA 检测未做严格断言 | 不影响，忽略 |
| 合成报 `AssertionError: <\|endofprompt\|> not detected` | 提示词格式不对 | 已自动处理，无需干预 |
| 合成报 `RuntimeError: Kernel size (4) can't be greater than input (3)` | 音频帧太短 | 已自动填充 prompt，无需干预 |

### 2b. Qwen3-TTS（本地运行）

```powershell
cd D:\workspace\AIGC\ai-tts\Qwen3-TTS
.venv\Scripts\qwen-tts-demo.exe Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --ip 0.0.0.0 --port 15001 --no-flash-attn
```

验证：

```bash
curl http://127.0.0.1:15001/health
# 返回 ok 即正常
```

注意事项：

- 首次加载需下载模型（约 3-5 分钟），之后自动缓存
- `--no-flash-attn` 在没有 flash-attn 的 Windows 上必需
- 速度比 CosyVoice3 慢（中长句约 2.6x），但音色自然度好

### 2c. OmniVoice

```powershell
# 通过 gradio_client 连接，HTTP + SSE
# 默认端口 7860
```

验证：

```bash
python -c "
from gradio_client import Client
c = Client('http://localhost:7860')
print(c.view_api())
"
# 返回 API 列表即正常
```

已知问题：

| 症状 | 原因 | 解决 |
|------|------|------|
| `'tuple' object has no attribute 'get'` | gradio_client 版本差异 | 已自动处理，无需干预 |
| `/gradio_api/file=...` 403 | Gradio 文件路径更新 | 同机使用本地文件路径绕过，已处理 |
| 任务状态 `🔄 执行中` 卡住 | 轮询超时 | 默认 300s 超时，长文本增加等待 |

## 3. 启动验证

一键检查三引擎连通性：

```bash
python -c "
import sys; from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from vaslib.synthesizer.cosyvoice_adapter import CosyVoiceAdapter
from vaslib.synthesizer.qwen_tts_adapter import QwenTtsAdapter
from vaslib.synthesizer.omnivoice_adapter import OmniVoiceAdapter
for name, cls in [('CosyVoice',CosyVoiceAdapter),('Qwen3-TTS',QwenTtsAdapter),('OmniVoice',OmniVoiceAdapter)]:
    a = cls()
    ok = a.health_check() if hasattr(a,'health_check') else True
    print(f'{name}: {\"✓\" if ok else \"✗\"}')
"
```

输出示例：

```
CosyVoice: ✓
Qwen3-TTS: ✓
OmniVoice: ✓
```

## 4. 完整管线测试

```bash
# 分析样例剧本（只走本地 pipeline，不需要 TTS 服务）
vas analyze assets/examples/demo-script.md -o output

# 合成（至少一个 TTS 服务在运行）
vas synthesize -o output --engine cosyvoice
# 或全部引擎
vas synthesize -o output --engine all
```

## 5. 常见问题速查

| 问题 | 原因 | 检查/修复 |
|------|------|-----------|
| `vas: command not found` | pip install 未执行 | `pip install -e .` |
| `ModuleNotFoundError: gradio_client` | 依赖缺失 | `pip install gradio-client` |
| 合成报错但 TTS 服务在运行 | URL 配置错误 | 检查 `.env` 端口号 |
| CLI 报 `No such option: --qwents-url` | CLI 版本过旧 | 重新 `pip install -e .` |
| OmniVoice 全部 403 | Gradio 版本不匹配 | 确认 OmniVoice webui 已启动且端口正确 |
