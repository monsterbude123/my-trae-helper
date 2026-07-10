from __future__ import annotations
from pydantic import BaseModel


class TiltCorrection(BaseModel):
    original_estimate: float
    target_duration: float
    speed_adjustment: float
    reason: str


class Batch(BaseModel):
    id: str
    scene_id: str
    lines: list  # list[Line]
    estimated_duration_seconds: float
    target_duration_seconds: float
    tilt_correction: TiltCorrection | None


class BatchPlan(BaseModel):
    batches: list[Batch]
    total_batches: int
    average_lines_per_batch: float
    overflow_strategy: str
