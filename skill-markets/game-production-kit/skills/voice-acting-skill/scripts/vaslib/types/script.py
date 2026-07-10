from __future__ import annotations
from pydantic import BaseModel
from typing import Literal


LineType = Literal["dialogue", "narration", "action", "emotion_hint"]


class TimeRange(BaseModel):
    start_seconds: float
    end_seconds: float


class Character(BaseModel):
    id: str
    name: str
    gender: Literal["male", "female", "other"]
    age: Literal["child", "young", "middle", "elderly"]
    personality: str
    dialect_hint: str


class Line(BaseModel):
    id: str
    type: LineType
    character_id: str | None
    text: str
    raw_text: str
    emotion_hint: str
    pause_before: float
    pause_after: float


class Scene(BaseModel):
    id: str
    scene_number: int
    time_range: TimeRange
    location: str
    time_of_day: str
    description: str
    lines: list[Line]


class ScriptMeta(BaseModel):
    title: str
    characters: list[Character]
    total_duration_seconds: float


class ParsedScript(BaseModel):
    meta: ScriptMeta
    scenes: list[Scene]
