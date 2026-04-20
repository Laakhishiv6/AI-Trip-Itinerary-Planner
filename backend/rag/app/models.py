from datetime import date
from pydantic import BaseModel
from typing import Optional, Literal


class IndexResponse(BaseModel):
    message: str
    total_fetched: int
    total_upserted: int


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    city: Optional[str] = None
    category: Optional[str] = None


class TripPlanSearchRequest(BaseModel):
    """Same shape as user_details TripPlanRequest — used to drive RAG search."""
    city: str
    start_date: date
    end_date: date
    num_travelers: int
    budget_preference: Literal["Budget", "Moderate", "Luxury"]
    activity_preferences: list[str]
    food_preferences: list[str]
    top_k: int = 10
    category: Optional[str] = None


class PlaceResult(BaseModel):
    score: float
    name: str
    city: str
    country: str
    category: str
    rating: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    cuisine: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[PlaceResult]
