from datetime import date, datetime
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from .config import settings


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return vectors.tolist()


def embed_one(text: str) -> list[float]:
    return embed_texts([text])[0]


def build_document(place: dict) -> str:
    """
    Constructs a rich natural-language sentence for a place so the
    embedding captures all searchable attributes.
    """
    parts = [
        place.get("name", ""),
        f"in {place.get('city', '').title()}, {place.get('country', '')}",
    ]

    category = place.get("category", "")
    if category:
        parts.append(f"— a {category}")

    cuisine = place.get("cuisine")
    if cuisine:
        parts.append(f"serving {cuisine} cuisine")

    rating = place.get("rating")
    if rating:
        parts.append(f"rated {rating}")

    price = place.get("price")
    currency = place.get("currency", "")
    if price:
        parts.append(f"price {price} {currency}".strip())

    address = place.get("formatted_address") or place.get("address")
    if address:
        parts.append(f"located at {address}")

    opening_hours = place.get("opening_hours")
    if opening_hours:
        parts.append(f"open {opening_hours}")

    return " ".join(p for p in parts if p)


# Maps budget labels to descriptive phrases that align with place descriptions
_BUDGET_PHRASES = {
    "Budget": "budget-friendly affordable cheap hostels street food",
    "Moderate": "mid-range comfortable local restaurants",
    "Luxury": "luxury premium high-end fine dining",
}


def build_user_query(plan: dict) -> str:
    """
    Converts a TripPlanRequest-shaped dict into a natural-language query
    that sits in the same embedding space as build_document() output.

    Accepts both string dates ("2026-05-01") and date objects.
    No cross-service imports — works from a plain dict.
    """
    city = plan.get("city", "").title()
    budget = plan.get("budget_preference", "")
    activities: list[str] = plan.get("activity_preferences") or []
    food: list[str] = plan.get("food_preferences") or []
    num_travelers: int | None = plan.get("num_travelers")
    start_date = plan.get("start_date")
    end_date = plan.get("end_date")

    parts: list[str] = []

    if city:
        parts.append(f"places in {city}")

    if activities:
        parts.append(f"for {', '.join(a.lower() for a in activities)}")

    if food and "No Preference" not in food:
        parts.append(f"with {', '.join(f.lower() for f in food)} food")

    budget_phrase = _BUDGET_PHRASES.get(budget)
    if budget_phrase:
        parts.append(budget_phrase)

    if num_travelers == 1:
        parts.append("suitable for a solo traveler")
    elif num_travelers and num_travelers > 1:
        parts.append(f"suitable for a group of {num_travelers}")

    num_days = _trip_duration(start_date, end_date)
    if num_days:
        parts.append(f"{num_days}-day trip")

    return " ".join(parts)


def embed_user_plan(plan: dict) -> list[float]:
    """Convenience wrapper: build query text from plan dict and embed it."""
    return embed_one(build_user_query(plan))


def _trip_duration(start, end) -> int | None:
    """Return number of days between two dates (str or date objects). Returns None on error."""
    try:
        def _parse(d) -> date:
            return datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d

        s, e = _parse(start), _parse(end)
        days = (e - s).days + 1
        return days if days > 0 else None
    except Exception:
        return None
