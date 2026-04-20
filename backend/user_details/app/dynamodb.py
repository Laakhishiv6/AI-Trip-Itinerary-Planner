import boto3
from boto3.dynamodb.conditions import Key
from .config import settings

TRAVEL_TABLE = "travel_data"


def _get_table():
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    return dynamodb.Table(TRAVEL_TABLE)


def get_city_options(city: str) -> dict:
    """Return distinct activity tags and food types for a city from DynamoDB."""
    table = _get_table()
    city_lower = city.lower()

    attractions_resp = table.query(
        KeyConditionExpression=(
            Key("city").eq(city_lower) & Key("category_name").begins_with("attraction#")
        )
    )
    restaurants_resp = table.query(
        KeyConditionExpression=(
            Key("city").eq(city_lower) & Key("category_name").begins_with("restaurant#")
        )
    )

    tags: set[str] = set()
    for item in attractions_resp.get("Items", []):
        for tag in item.get("tags", []):
            tags.add(tag)

    food_types: set[str] = set()
    for item in restaurants_resp.get("Items", []):
        for ft in item.get("food_type", []):
            food_types.add(ft)

    return {
        "activity_tags": sorted(tags),
        "food_types": sorted(food_types),
    }
