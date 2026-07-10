from __future__ import annotations
from pydantic import BaseModel


class SynthesisResult(BaseModel):
    line_id: str
    audio_path: str
    duration_seconds: float
    sample_rate: int = 0
    format: str = ""
    metadata: dict = {}


class SynthesisError(BaseModel):
    line_id: str
    message: str
    cause: str


class BatchSynthesisResult(BaseModel):
    batch_id: str
    results: list[SynthesisResult]
    total_duration_seconds: float
    success_count: int
    failure_count: int
    errors: list[SynthesisError]


class TTSAdapterConfig(BaseModel):
    cosyvoice_url: str
    omnivoice_url: str = "http://localhost:7860/"
    output_dir: str
    concurrency: int


class ProjectClip(BaseModel):
    line_id: str
    batch_id: str
    scene_id: str
    character_id: str
    text: str
    audio_path: str
    start_time_seconds: float
    duration_seconds: float
    fade_in_seconds: float
    fade_out_seconds: float


class ProjectTrack(BaseModel):
    engine: str
    clips: list[ProjectClip]


class ProjectTimeline(BaseModel):
    project_id: str
    created_at: str
    total_duration_seconds: float
    tracks: list[ProjectTrack]


class VoiceMapCharacter(BaseModel):
    character_id: str
    character_name: str
    cosyvoice: dict
    omnivoice: dict
    line_ids: list[str]


class VoiceMap(BaseModel):
    characters: list[VoiceMapCharacter]


class EngineSummary(BaseModel):
    engine: str
    success_rate: float
    average_duration_seconds: float
    average_latency_ms: float
    total_cost: float


class LineComparison(BaseModel):
    line_id: str
    text: str
    character_name: str
    engines: dict
    best_match: str
    best_match_reason: str


class ComparisonRecommendation(BaseModel):
    character_id: str
    character_name: str
    recommended_engine: str
    reason: str


class ComparisonReport(BaseModel):
    project_id: str
    generated_at: str
    summary: dict
    line_comparisons: list[LineComparison]
    recommendations: list[ComparisonRecommendation]
