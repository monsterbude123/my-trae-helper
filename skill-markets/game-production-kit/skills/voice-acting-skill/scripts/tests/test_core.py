"""
配音剧本注音工具 - 核心模块 pytest 测试
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vaslib.parser.script_parser import (
    parse_script,
    parse_time_range,
    parse_dialogue,
    extract_characters,
)
from vaslib.analyzer.voice_assigner import (
    assign_voices,
    match_qwen_voice,
    match_cosy_voice,
    match_omni_voice,
)
from vaslib.batcher.batch_manager import (
    create_batch_plan,
    estimate_line_duration,
    correct_tilt,
)
from vaslib.annotator.annotation_generator import (
    generate_all,
    generate_qwen_tts,
    generate_cosy_voice,
    generate_omni_voice,
)
from vaslib.config.voices import (
    resolve_polyphones,
    get_pinyin_overrides,
    POLYPHONE_DICT,
)
from vaslib.types.script import (
    Character,
    TimeRange,
    Line,
    ParsedScript,
    ScriptMeta,
    Scene,
)
from vaslib.types.analysis import (
    ScriptAnalysis,
    VoiceAssignment,
    QwenTtsVoiceConfig,
    CosyVoiceVoiceConfig,
    OmniVoiceVoiceConfig,
)

import pytest


# ============================================================================
# 测试数据
# ============================================================================

DEMO_SCRIPT = """### **貔貅系列 实验动画 01 (优化版)**

● 时长:约1m40s ● 人物以中国五大瑞兽为形象，**整体采用3D盲盒潮玩质感，色彩明快**： 貔貅:配音为渝普 (川渝耙耳朵性格外化) 老龟:配音为东北口音 (东北大爷看淡生死) 凤:配音为沪普 (精致傲娇的凡尔赛) 龙:配音北京口音 (痞气中二的京城老炮儿) 麒麟:配音为天津口音 (相声捧哏气氛组)

| 大致时间线 | 描述 | 内容、动作设计 | 台词 | 备注 |
| :---- | :---- | :---- | :---- | :---- |
| 00:00~00:05 | 黑场开始... | 他穿着皱巴巴的T恤... | 貔貅:"我叫貔貅。乃上古瑞兽,招财进宝,只进不出。我真的绝对有才/财!说好听点叫守财,说难听点 我三千六百年没拉过屎。" | 奠定无厘头基调。 |
| 00:05~00:15 | 闪回... | ①商务宴会... | 貔貅(OS):"当年在单位,好像我嘴太欠..." | 快速交代背景。 |
| 00:25~00:30 | 转场,老龟家... | 貔貅捂着肚子... | 老龟:"大半夜的你要干哈" 貔貅:"龟哥,我问你一个私密问题。" | 一急一慢。 |
| 01:37~01:40 | 结尾。 | 排版... | 麒麟:"所以你俩的恩怨,最后是用开塞露还是502解决?" 龙医生:"用丫的仇恨!" | 完美收尾。 |"""


# ============================================================================
# test_parse_time_range
# ============================================================================


class TestParseTimeRange:
    """解析 "MM:SS~MM:SS" 格式的时间范围"""

    def test_basic_range(self):
        """"00:00~00:05" → start=0, end=5"""
        result = parse_time_range("00:00~00:05")
        assert isinstance(result, TimeRange)
        assert result.start_seconds == 0
        assert result.end_seconds == 5

    def test_late_range(self):
        """01:37~01:40 → start=97, end=100"""
        result = parse_time_range("01:37~01:40")
        assert result.start_seconds == 97
        assert result.end_seconds == 100

    def test_mid_range(self):
        """00:05~00:15 → start=5, end=15"""
        result = parse_time_range("00:05~00:15")
        assert result.start_seconds == 5
        assert result.end_seconds == 15

    def test_escaped_tilde(self):
        """带反斜杠转义 "00:00\\~00:05" → start=0, end=5"""
        result = parse_time_range("00:00\\~00:05")
        assert result.start_seconds == 0
        assert result.end_seconds == 5


# ============================================================================
# test_extract_characters
# ============================================================================


class TestExtractCharacters:
    """解析人物元信息section"""

    META_TEXT = (
        "人物以中国五大瑞兽为形象，**整体采用3D盲盒潮玩质感，色彩明快**： "
        "貔貅:配音为渝普 (川渝耙耳朵性格外化) "
        "老龟:配音为东北口音 (东北大爷看淡生死) "
        "凤:配音为沪普 (精致傲娇的凡尔赛) "
        "龙:配音北京口音 (痞气中二的京城老炮儿) "
        "麒麟:配音为天津口音 (相声捧哏气氛组)"
    )

    def test_extract_five_characters(self):
        """从meta section提取5个角色"""
        chars = extract_characters(self.META_TEXT)
        assert len(chars) == 5

    def test_pixiu(self):
        """检查貔貅"""
        chars = extract_characters(self.META_TEXT)
        pixiu = next(c for c in chars if c.name == "貔貅")
        assert pixiu.id == "pixiu"
        assert pixiu.gender == "male"
        assert pixiu.dialect_hint == "渝普"

    def test_laogui(self):
        """检查老龟"""
        chars = extract_characters(self.META_TEXT)
        laogui = next(c for c in chars if c.name == "老龟")
        assert laogui.id == "laogui"
        assert laogui.gender == "male"
        assert laogui.dialect_hint == "东北口音"

    def test_feng(self):
        """检查凤"""
        chars = extract_characters(self.META_TEXT)
        feng = next(c for c in chars if c.name == "凤")
        assert feng.id == "feng"
        assert feng.gender == "female"
        assert feng.dialect_hint == "沪普"

    def test_long(self):
        """检查龙"""
        chars = extract_characters(self.META_TEXT)
        long = next(c for c in chars if c.name == "龙")
        assert long.id == "long"
        assert long.gender == "male"
        assert long.dialect_hint == "北京口音"

    def test_qilin(self):
        """检查麒麟"""
        chars = extract_characters(self.META_TEXT)
        qilin = next(c for c in chars if c.name == "麒麟")
        assert qilin.id == "qilin"
        assert qilin.gender == "male"
        assert qilin.dialect_hint == "天津口音"


# ============================================================================
# test_parse_dialogue
# ============================================================================


class TestParseDialogue:
    """解析台词单元格"""

    def test_multi_character_same_cell(self):
        """解析多角色同格台词"""
        cell = '老龟:"大半夜的你要干哈" 貔貅:"龟哥,我问你一个私密问题。"'
        lines = parse_dialogue(cell, "scene-3")
        assert len(lines) == 2

    def test_character_assignment(self):
        """检查行数和角色分配"""
        cell = '老龟:"大半夜的你要干哈" 貔貅:"龟哥,我问你一个私密问题。"'
        lines = parse_dialogue(cell, "scene-3")
        assert lines[0].character_id == "laogui"
        assert lines[0].text == "大半夜的你要干哈"
        assert lines[1].character_id == "pixiu"
        assert lines[1].text == "龟哥,我问你一个私密问题。"


# ============================================================================
# test_parse_script
# ============================================================================


class TestParseScript:
    """测试完整解析"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.parsed = parse_script(DEMO_SCRIPT)

    def test_title(self):
        """检查标题"""
        assert self.parsed.meta.title == "貔貅系列 实验动画 01 (优化版)"

    def test_total_duration(self):
        """检查total_duration_seconds = 100 (1m40s)"""
        assert self.parsed.meta.total_duration_seconds == 100

    def test_character_count(self):
        """检查有5个角色"""
        assert len(self.parsed.meta.characters) == 5

    def test_has_multiple_scenes(self):
        """检查有多个场景"""
        assert len(self.parsed.scenes) >= 3

    def test_each_scene_has_duration(self):
        """检查每个场景有时长"""
        for scene in self.parsed.scenes:
            assert scene.time_range.start_seconds >= 0
            assert scene.time_range.end_seconds > scene.time_range.start_seconds


# ============================================================================
# test_assign_voices
# ============================================================================


class TestAssignVoices:
    """测试音色分配"""

    @pytest.fixture(autouse=True)
    def setup(self):
        parsed = parse_script(DEMO_SCRIPT)
        self.analysis = assign_voices(parsed)

    def test_all_characters_have_three_engine_configs(self):
        """检查每个角色都有3引擎配置"""
        for va in self.analysis.voice_assignments:
            assert va.qwen_tts is not None
            assert va.cosyvoice is not None
            assert va.omnivoice is not None

    def test_pixiu_qwen_voice(self):
        """检查貔貅的方言映射正确"""
        pixiu_va = next(
            va for va in self.analysis.voice_assignments if va.character_id == "pixiu"
        )
        assert pixiu_va.qwen_tts.voice_id == "Sunny"

    def test_laogui_qwen_voice(self):
        """检查老龟的方言映射正确"""
        laogui_va = next(
            va for va in self.analysis.voice_assignments if va.character_id == "laogui"
        )
        assert laogui_va.qwen_tts.voice_id == "Ethan"

    def test_feng_qwen_voice(self):
        """检查凤的方言映射正确"""
        feng_va = next(
            va for va in self.analysis.voice_assignments if va.character_id == "feng"
        )
        assert feng_va.qwen_tts.voice_id == "Jada"

    def test_long_qwen_voice(self):
        """检查龙的方言映射正确"""
        long_va = next(
            va for va in self.analysis.voice_assignments if va.character_id == "long"
        )
        assert long_va.qwen_tts.voice_id == "Dylan"

    def test_qilin_qwen_voice(self):
        """检查麒麟的方言映射正确"""
        qilin_va = next(
            va for va in self.analysis.voice_assignments if va.character_id == "qilin"
        )
        assert qilin_va.qwen_tts.voice_id == "Dylan"


# ============================================================================
# test_batch_plan
# ============================================================================


class TestBatchPlan:
    """测试批次切分"""

    @pytest.fixture(autouse=True)
    def setup(self):
        parsed = parse_script(DEMO_SCRIPT)
        analysis = assign_voices(parsed)
        self.batch_plan = create_batch_plan(analysis)

    def test_has_batches(self):
        """检查有批次"""
        assert len(self.batch_plan.batches) > 0

    def test_batch_duration_within_limit(self):
        """检查每批次不超15秒"""
        for batch in self.batch_plan.batches:
            assert batch.estimated_duration_seconds <= 15.0, (
                f"Batch {batch.id} duration {batch.estimated_duration_seconds}s > 15s"
            )

    def test_tilt_correction_logic(self):
        """检查 tiltCorrection 逻辑"""
        for batch in self.batch_plan.batches:
            if batch.tilt_correction is not None:
                tc = batch.tilt_correction
                assert tc.original_estimate > 0
                assert tc.target_duration > 0
                assert tc.speed_adjustment > 0
                assert tc.reason != ""


# ============================================================================
# test_generate_all
# ============================================================================


class TestGenerateAll:
    """测试注音生成"""

    @pytest.fixture(autouse=True)
    def setup(self):
        parsed = parse_script(DEMO_SCRIPT)
        analysis = assign_voices(parsed)
        batch_plan = create_batch_plan(analysis)
        self.result = generate_all(batch_plan, analysis)

    def test_three_engines_have_output(self):
        """检查三引擎都有输出"""
        assert "qwen" in self.result
        assert "cosy" in self.result
        assert "omni" in self.result

    def test_qwen_has_lines(self):
        """检查 qwen 引擎有台词行数"""
        qwen = self.result["qwen"]
        total_lines = sum(len(b.lines) for b in qwen.batches)
        assert total_lines > 0

    def test_cosy_has_lines(self):
        """检查 cosy 引擎有台词行数"""
        cosy = self.result["cosy"]
        total_lines = sum(len(b.lines) for b in cosy.batches)
        assert total_lines > 0

    def test_omni_has_lines(self):
        """检查 omni 引擎有台词行数"""
        omni = self.result["omni"]
        total_lines = sum(len(b.lines) for b in omni.batches)
        assert total_lines > 0

    def test_each_line_has_voice_assignment(self):
        """检查每行都有音色分配"""
        for engine_key, annotation in self.result.items():
            for batch in annotation.batches:
                for line in batch.lines:
                    if engine_key == "qwen":
                        assert line.voice != ""
                    elif engine_key == "cosy":
                        assert line.spk_id != ""


# ============================================================================
# test_resolve_polyphones
# ============================================================================


class TestResolvePolyphones:
    """测试多音字解析"""

    def test_long_word_priority(self):
        """测试长词优先 (行长 > 银行)"""
        text = "行长比银行行长更重要"
        result = resolve_polyphones(text)
        assert "行长[háng zhǎng]" in result
        assert "银行[yín háng]" in result

    def test_basic_replacement(self):
        """测试基本替换"""
        text = "处理重要文件"
        result = resolve_polyphones(text)
        assert "处理[chǔ lǐ]" in result
        assert "重要[zhòng yào]" in result

    def test_no_polyphone_match(self):
        """不含多音字的文本不应被替换"""
        text = "这是一段普通文本"
        result = resolve_polyphones(text)
        assert result == text

    def test_partial_match_only(self):
        """只有匹配的词才被替换"""
        text = "北京重庆"
        result = resolve_polyphones(text)
        assert "北京" in result
        assert "重庆[chóng qìng]" in result
