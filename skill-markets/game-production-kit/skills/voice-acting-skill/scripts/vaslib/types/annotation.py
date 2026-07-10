from __future__ import annotations
from pydantic import BaseModel


class QwenTtsLine(BaseModel):
    line_id: str
    text: str
    annotated_text: str
    voice: str
    speed: float
    language_type: str


class QwenTtsBatch(BaseModel):
    batch_id: str
    lines: list[QwenTtsLine]


class QwenTtsAnnotation(BaseModel):
    engine: str = "qwen-tts"
    model: str
    batches: list[QwenTtsBatch]


class CosyVoiceLine(BaseModel):
    line_id: str
    tts_text: str
    spk_id: str
    instruct_text: str
    ref_audio_path: str | None
    ref_text: str | None
    speed: float
    stream: bool


class CosyVoiceBatch(BaseModel):
    batch_id: str
    lines: list[CosyVoiceLine]


class CosyVoiceAnnotation(BaseModel):
    engine: str = "cosyvoice"
    model: str
    mode: str
    batches: list[CosyVoiceBatch]


class OmniVoiceLine(BaseModel):
    line_id: str
    text: str
    language: str
    pinyin_overrides: dict[str, str]
    instruct: str
    ref_audio_path: str | None
    ref_text: str | None


class OmniVoiceBatch(BaseModel):
    batch_id: str
    lines: list[OmniVoiceLine]


class OmniVoiceAnnotation(BaseModel):
    engine: str = "omnivoice"
    model: str
    batches: list[OmniVoiceBatch]


EngineAnnotation = QwenTtsAnnotation | CosyVoiceAnnotation | OmniVoiceAnnotation
