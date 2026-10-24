"""Input/output contracts of the prediction engine (also documented in shared/schemas/)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class FridgeIn(BaseModel):
    id: str
    cls: str = Field("ILR", description="Unit type: ILR or DOMESTIC")


class ReadingIn(BaseModel):
    fridge_id: str
    tick: int = Field(..., description="10-minute reading index from the start of the series")
    minute: int
    temp_c: float | None = Field(None, description="Air temperature in °C; null for a missing reading")


class ScoreRequest(BaseModel):
    fridges: list[FridgeIn]
    readings: list[ReadingIn]


class ScoreResponse(BaseModel):
    thresholds: dict[str, float]
    rows: list[dict] = Field(..., description="One scored row per reading; see shared/schemas/scored_reading.json")


class RawReading(BaseModel):
    fridge_id: str
    timestamp: str = Field(..., description="ISO 8601")
    temp_c: float | None = None


class ValidateRequest(BaseModel):
    readings: list[RawReading]
