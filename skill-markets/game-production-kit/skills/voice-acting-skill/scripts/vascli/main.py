"""
配音剧本注音工具 - CLI 入口

基于 click 的命令行界面，提供 analyze 和 synthesize 两个子命令。
"""

import json
import os
import sys
from pathlib import Path

import click

# 将项目根目录添加到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _load_dotenv(dotenv_path: str | Path) -> None:
    """轻量级 .env 文件加载器，不依赖 python-dotenv。"""
    path = Path(dotenv_path).resolve()
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("\"'")
        if not os.environ.get(key):
            os.environ[key] = val


# 自动从 .env 文件加载环境变量（支持项目根 .env）
_load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


from vaslib.parser import parse_script
from vaslib.analyzer import assign_voices
from vaslib.batcher import create_batch_plan
from vaslib.annotator.annotation_generator import generate_all
from vaslib.annotator.markdown_formatter import (
    format_all_markdown,
    format_qwen_tts_markdown,
    format_cosy_voice_markdown,
    format_omni_voice_markdown,
)


# ---------------------------------------------------------------------------
# 辅助函数：将 pydantic model 序列化为 JSON 可用的 dict
# ---------------------------------------------------------------------------

def _dump(model):
    """将 pydantic v2 model 转为 dict。"""
    return model.model_dump(mode="python")


def _write_json(filepath: str, data) -> None:
    """写入 JSON 文件，使用 indent=2 和 ensure_ascii=False。"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
def cli():
    """配音剧本注音工具 - 将剧本自动转换为三引擎 TTS 注音规则并执行配音。"""
    pass


# ---------------------------------------------------------------------------
# analyze 命令
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--output", "-o", default="output", show_default=True, help="输出目录")
def analyze(input, output):
    """分析剧本并生成三引擎注音配音剧本"""
    input_path = Path(input).resolve()
    output_dir = Path(output).resolve()

    click.echo(f"📖 读取剧本: {input_path}")

    markdown = input_path.read_text(encoding="utf-8")

    # 1. 解析剧本
    click.echo("🔍 解析剧本...")
    parsed = parse_script(markdown)
    click.echo(f"  ✓ 标题: {parsed.meta.title}")
    click.echo(f"  ✓ 角色: {', '.join(c.name for c in parsed.meta.characters)}")
    click.echo(f"  ✓ 场景: {len(parsed.scenes)} 段")
    click.echo(f"  ✓ 总时长: {parsed.meta.total_duration_seconds}s")

    # 2. 保存解析结果
    parsed_dir = output_dir / "parsed"
    _write_json(str(parsed_dir / "script.json"), _dump(parsed))

    # 3. 分配音色
    click.echo("🎤 分配音色...")
    analysis = assign_voices(parsed)
    for va in analysis.voice_assignments:
        char = next(
            (c for c in parsed.meta.characters if c.id == va.character_id),
            None,
        )
        if char:
            click.echo(
                f"  ✓ {char.name}: "
                f"Qwen={va.qwen_tts.voice_id}, "
                f"CosyVoice={va.cosyvoice.voice_id}, "
                f"OmniVoice={va.omnivoice.voice_design}"
            )

    # 4. 保存分析结果
    analyzed_dir = output_dir / "analyzed"
    _write_json(str(analyzed_dir / "script-analysis.json"), _dump(analysis))

    # 5. 切分批次
    click.echo("📦 切分批次...")
    batch_plan = create_batch_plan(analysis)
    click.echo(f"  ✓ 总批次: {batch_plan.total_batches}")
    click.echo(f"  ✓ 平均每批台词: {batch_plan.average_lines_per_batch}")
    for batch in batch_plan.batches:
        tilt_info = (
            f" [倾斜修正: x{batch.tilt_correction.speed_adjustment}]"
            if batch.tilt_correction
            else ""
        )
        click.echo(
            f"    {batch.id}: {len(batch.lines)}句, "
            f"估算{batch.estimated_duration_seconds}s{tilt_info}"
        )

    # 6. 保存批次计划
    _write_json(str(analyzed_dir / "batch-plan.json"), _dump(batch_plan))

    # 7. 生成注音剧本
    click.echo("📝 生成注音剧本...")
    annotations = generate_all(batch_plan, analysis)

    annotated_dir = output_dir / "annotated"

    # Qwen TTS
    _write_json(str(annotated_dir / "qwen-tts.json"), _dump(annotations["qwen"]))
    qwen_total = sum(len(b.lines) for b in annotations["qwen"].batches)
    click.echo(f"  ✓ Qwen TTS: {qwen_total} 句")

    # CosyVoice
    _write_json(str(annotated_dir / "cosyvoice.json"), _dump(annotations["cosy"]))
    cosy_total = sum(len(b.lines) for b in annotations["cosy"].batches)
    click.echo(f"  ✓ CosyVoice: {cosy_total} 句")

    # OmniVoice
    _write_json(str(annotated_dir / "omnivoice.json"), _dump(annotations["omni"]))
    omni_total = sum(len(b.lines) for b in annotations["omni"].batches)
    click.echo(f"  ✓ OmniVoice: {omni_total} 句")

    # 8. 生成 Markdown 审核报告
    click.echo("📄 生成 Markdown 审核报告...")

    qwen_md = format_qwen_tts_markdown(annotations["qwen"])
    (annotated_dir / "qwen-tts.md").write_text(qwen_md, encoding="utf-8")

    cosy_md = format_cosy_voice_markdown(annotations["cosy"])
    (annotated_dir / "cosyvoice.md").write_text(cosy_md, encoding="utf-8")

    omni_md = format_omni_voice_markdown(annotations["omni"])
    (annotated_dir / "omnivoice.md").write_text(omni_md, encoding="utf-8")

    all_md = format_all_markdown(
        annotations["qwen"], annotations["cosy"], annotations["omni"]
    )
    (annotated_dir / "all-engines.md").write_text(all_md, encoding="utf-8")

    click.echo("  ✓ Markdown 报告已生成")

    # 9. 完成
    click.echo(f"\n✅ 完成! 输出目录: {output_dir}")
    click.echo("  📁 parsed/script.json")
    click.echo("  📁 analyzed/script-analysis.json")
    click.echo("  📁 analyzed/batch-plan.json")
    click.echo("  📁 annotated/qwen-tts.json + .md")
    click.echo("  📁 annotated/cosyvoice.json + .md")
    click.echo("  📁 annotated/omnivoice.json + .md")
    click.echo("  📁 annotated/all-engines.md (三引擎合并报告)")


# ---------------------------------------------------------------------------
# synthesize 命令
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--cosyvoice-url", default="http://127.0.0.1:50000", envvar="COSYVOICE_URL", help="CosyVoice服务地址")
@click.option("--omnivoice-url", default="http://localhost:7860/", envvar="OMNIVOICE_URL", help="OmniVoice Gradio 服务地址")
@click.option("--qwents-url", default="", envvar="QWENTTS_URL", help="Qwen3-TTS Gradio 服务地址（留空用 DashScope）")
@click.option("--output", "-o", default="output", help="输出目录")
@click.option(
    "--engine",
    default="all",
    type=click.Choice(["all", "cosyvoice", "omnivoice", "qwents"]),
    help="指定引擎",
)
def synthesize(cosyvoice_url, omnivoice_url, qwents_url, output, engine):
    """使用TTS引擎执行配音合成"""
    output_dir = Path(output).resolve()
    annotated_dir = output_dir / "annotated"
    analyzed_dir = output_dir / "analyzed"

    analysis_path = analyzed_dir / "script-analysis.json"
    batch_plan_path = analyzed_dir / "batch-plan.json"
    cosy_annotation_path = annotated_dir / "cosyvoice.json"
    qwen_annotation_path = annotated_dir / "qwen-tts.json"

    # 检查前置文件是否存在
    if not analysis_path.exists() or not batch_plan_path.exists():
        click.echo("❌ 请先运行 analyze 命令生成注音剧本")
        raise SystemExit(1)

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    batch_plan = json.loads(batch_plan_path.read_text(encoding="utf-8"))
    cosy_annotation = (
        json.loads(cosy_annotation_path.read_text(encoding="utf-8"))
        if cosy_annotation_path.exists()
        else None
    )
    qwen_annotation = (
        json.loads(qwen_annotation_path.read_text(encoding="utf-8"))
        if qwen_annotation_path.exists()
        else None
    )

    audio_dir = output_dir / "audio"

    run_cosyvoice = engine in ("all", "cosyvoice")
    run_omnivoice = engine in ("all", "omnivoice")
    run_qwents = engine in ("all", "qwents")

    cosyvoice_results = {}
    qwents_results = {}
    omnivoice_result = {"merged_audio_path": None, "status": "pending", "error": None}

    # ---- CosyVoice ----
    if run_cosyvoice and cosy_annotation:
        click.echo("🎙️ CosyVoice 配音合成...")
        from vaslib.synthesizer import CosyVoiceAdapter

        project_root = Path(__file__).resolve().parent.parent.parent
        default_prompt_wav = str(project_root / "assets" / "voices" / "default_prompt.wav")
        if not os.path.isfile(default_prompt_wav):
            default_prompt_wav = None

        cosy_adapter = CosyVoiceAdapter(cosyvoice_url, default_prompt_wav=default_prompt_wav)

        click.echo("  连接 CosyVoice 服务...")
        if not cosy_adapter.health_check():
            click.echo(f"  ❌ CosyVoice 服务不可用: {cosyvoice_url}")
        else:
            click.echo("  ✓ 服务连接成功")
            cosy_adapter.connect()

            all_lines = []
            for batch in cosy_annotation.get("batches", []):
                all_lines.extend(batch.get("lines", []))

            click.echo(f"  合成 {len(all_lines)} 句台词...")
            cosy_audio_dir = str(audio_dir / "cosyvoice")

            def _on_progress(completed, total):
                click.echo(f"\r  进度: {completed}/{total}", nl=False)

            batch_result = cosy_adapter.synthesize_batch(
                all_lines, cosy_audio_dir, on_progress=_on_progress
            )
            click.echo("")

            click.echo(
                f"  ✓ 成功: {batch_result['success_count']}, "
                f"失败: {batch_result['failure_count']}"
            )
            for r in batch_result.get("results", []):
                lid = r.get("line_id", "")
                if lid:
                    cosyvoice_results[lid] = r

    # ---- Qwen3-TTS ----
    if run_qwents and qwen_annotation:
        click.echo("🎙️ Qwen3-TTS 配音合成...")
        from vaslib.synthesizer import QwenTtsAdapter

        qwen_url = qwents_url if qwents_url else None
        qwen_adapter = QwenTtsAdapter(url=qwen_url)

        if not qwen_adapter.health_check():
            click.echo(f"  ❌ Qwen3-TTS 不可用 (url={qwents_url or '无(使用DashScope)'})")
        else:
            click.echo("  ✓ 服务连接成功")
            qwen_adapter.connect()

            all_lines = []
            for batch in qwen_annotation.get("batches", []):
                all_lines.extend(batch.get("lines", []))

            click.echo(f"  合成 {len(all_lines)} 句台词...")
            qwen_audio_dir = str(audio_dir / "qwen")

            def _on_qwen_progress(completed, total):
                click.echo(f"\r  进度: {completed}/{total}", nl=False)

            batch_result = qwen_adapter.synthesize_batch(
                all_lines, qwen_audio_dir, on_progress=_on_qwen_progress
            )
            click.echo("")

            click.echo(
                f"  ✓ 成功: {batch_result['success_count']}, "
                f"失败: {batch_result['failure_count']}"
            )
            for r in batch_result.get("results", []):
                lid = r.get("line_id", "")
                if lid:
                    qwents_results[lid] = r

    # ---- OmniVoice ----
    if run_omnivoice:
        click.echo("🎙️ OmniVoice 配音合成...")
        from vaslib.synthesizer import OmniVoiceAdapter

        omni_adapter = OmniVoiceAdapter(url=omnivoice_url)

        click.echo(f"  连接 OmniVoice 服务 ({omnivoice_url})...")
        try:
            omni_adapter.connect()
            click.echo("  ✓ 服务连接成功")
            if omni_adapter.available_voices:
                click.echo(f"  ✓ 可用音色预设: {len(omni_adapter.available_voices)}")
        except Exception as exc:
            click.echo(f"  ❌ 连接失败: {exc}")
            omnivoice_result = {
                "merged_audio_path": None,
                "status": "failed",
                "error": str(exc)[:200],
            }
            return

        # 构建对话剧本
        script = omni_adapter.build_dialogue_script(batch_plan, analysis)
        click.echo(f"  📝 提交对话任务: {len(script.split(chr(10)))} 句")

        omni_audio_dir = str(audio_dir / "omnivoice")
        characters = (
            analysis.get("meta", {}).get("characters", [])
        )
        result = omni_adapter.submit_dialogue_tasks(
            script,
            characters,
            "zh",
            omni_audio_dir,
            {"speed": 1.0, "mergeOutput": True, "num_step": 32},
        )

        click.echo(
            f"  ✓ 成功: {result.get('success_count', 0)}, "
            f"失败: {result.get('failure_count', 0)}"
        )
        merged = result.get("merged_audio_path")
        if merged:
            click.echo(f"  📦 合并音频: {merged}")

        omnivoice_result = {
            "merged_audio_path": merged,
            "status": "success" if result.get("failure_count", 0) == 0 else "failed",
            "error": None,
        }

    # ---- 生成工程文件 ----
    click.echo("📊 生成工程文件...")
    from vaslib.synthesizer import build_timeline, build_voice_map, build_comparison_report

    timeline = build_timeline(batch_plan, analysis, cosyvoice_results, omnivoice_result.get("merged_audio_path"))
    voice_map = build_voice_map(analysis, batch_plan, cosy_annotation)
    comparison = build_comparison_report(batch_plan, analysis, cosyvoice_results, omnivoice_result)

    project_dir = output_dir / "project"
    _write_json(str(project_dir / "timeline.json"), timeline)
    _write_json(str(project_dir / "voice-map.json"), voice_map)
    _write_json(str(project_dir / "comparison.json"), comparison)

    click.echo("  ✓ timeline.json")
    click.echo("  ✓ voice-map.json")
    click.echo("  ✓ comparison.json")

    click.echo(f"\n✅ 配音工程完成! 输出目录: {output_dir}")
    click.echo("  📁 audio/cosyvoice/ - CosyVoice 逐句音频")
    click.echo("  📁 audio/omnivoice/ - OmniVoice 合并音频")
    click.echo("  📁 project/timeline.json - 时间轴")
    click.echo("  📁 project/voice-map.json - 音色映射")
    click.echo("  📁 project/comparison.json - 引擎对比报告")


if __name__ == "__main__":
    cli()
