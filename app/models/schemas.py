from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

TravelType = Literal[
    "business",
    "leisure",
    "adventure",
    "family",
    "backpacking",
]

TravelMode = Literal["air", "car", "train", "cruise"]
ClimateProfile = Literal["tropical", "cold", "desert", "temperate"]


class TravelerProfile(BaseModel):
    name: Optional[str] = None
    age_group: Literal["child", "teen", "adult", "senior"] = "adult"
    has_special_needs: bool = False
    notes: Optional[str] = None


class TripParameters(BaseModel):
    origin_climate: ClimateProfile
    destination_climate: ClimateProfile
    duration_days: int = Field(..., gt=0)
    season: Literal["spring", "summer", "fall", "winter"]
    travel_type: TravelType
    travel_mode: TravelMode
    traveler_demographics: List[TravelerProfile] = Field(default_factory=list)
    travel_start: Optional[date] = None


class ChecklistItem(BaseModel):
    name: str
    category: str
    score: float
    rationale: List[str]
    priority: Literal["critical", "high", "medium", "nice-to-have"]


class ChecklistResponse(BaseModel):
    destination: str
    trip_type: TravelType
    travel_mode: TravelMode
    climate: ClimateProfile
    items: List[ChecklistItem]
