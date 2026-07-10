from __future__ import annotations
from pydantic import BaseModel

from .script import ScriptMeta, Scene


class QwenTtsVoiceConfig(BaseModel):
    voice_id: str
    emotion_style: str
    language_type: str


class CosyVoiceVoiceConfig(BaseModel):
    voice_id: str
    instruct_template: str
    ref_audio_path: str | None


class OmniVoiceVoiceConfig(BaseModel):
    voice_design: str
    ref_audio_path: str | None
    phoneme_overrides: dict[str, str]


class VoiceAssignment(BaseModel):
    character_id: str
    qwen_tts: QwenTtsVoiceConfig
    cosyvoice: CosyVoiceVoiceConfig
    omnivoice: OmniVoiceVoiceConfig


class ScriptAnalysis(BaseModel):
    meta: ScriptMeta
    scenes: list[Scene]
    voice_assignments: list[VoiceAssignment]


class DialectHint(BaseModel):
    pass


class DialectMapping(BaseModel):
    qwen_tts_voice_id: str
    cosyvoice_instruct: str
    omnivoice_design: str
