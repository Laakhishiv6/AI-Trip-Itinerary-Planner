from pydantic import BaseModel, field_validator
from datetime import date
from typing import Literal


VALID_BUDGET_OPTIONS = {"Budget", "Moderate", "Luxury"}
VALID_ACTIVITY_TAGS = {
    "Beaches", "Nightlife", "Culture", "Adventure",
    "Zoo", "Shopping", "Nature", "Wellness", "Photography",
}
VALID_FOOD_TYPES = {"Vegetarian", "Non-Vegetarian", "Vegan", "Halal", "No Preference"}


class TripPlanRequest(BaseModel):
    city: str
    start_date: date
    end_date: date
    num_travelers: int
    budget_preference: Literal["Budget", "Moderate", "Luxury"]
    activity_preferences: list[str]
    food_preferences: list[str]

    @field_validator("num_travelers")
    @classmethod
    def travelers_range(cls, v: int) -> int:
        if not (1 <= v <= 20):
            raise ValueError("num_travelers must be between 1 and 20")
        return v

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("end_date must be on or after start_date")
        return v

    @field_validator("activity_preferences")
    @classmethod
    def validate_activities(cls, v: list[str]) -> list[str]:
        invalid = set(v) - VALID_ACTIVITY_TAGS
        if invalid:
            raise ValueError(f"Invalid activity tags: {invalid}. Valid: {sorted(VALID_ACTIVITY_TAGS)}")
        return v

    @field_validator("food_preferences")
    @classmethod
    def validate_food(cls, v: list[str]) -> list[str]:
        invalid = set(v) - VALID_FOOD_TYPES
        if invalid:
            raise ValueError(f"Invalid food types: {invalid}. Valid: {sorted(VALID_FOOD_TYPES)}")
        return v


class TripPlanResponse(BaseModel):
    city: str
    start_date: date
    end_date: date
    num_days: int
    num_travelers: int
    budget_preference: str
    activity_preferences: list[str]
    food_preferences: list[str]
    available_activity_tags: list[str]
    available_food_types: list[str]


class BudgetOption(BaseModel):
    label: str
    description: str


class AvailableOptionsResponse(BaseModel):
    city: str
    activity_tags: list[str]
    food_types: list[str]
    budget_options: list[BudgetOption]
