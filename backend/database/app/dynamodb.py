import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from typing import Optional
from .config import settings

TABLE_NAME = "travel_data"


def get_table():
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    return dynamodb.Table(TABLE_NAME)


def create_table_if_not_exists():
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    existing = [t.name for t in dynamodb.tables.all()]
    if TABLE_NAME in existing:
        return dynamodb.Table(TABLE_NAME)

    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "city", "KeyType": "HASH"},
            {"AttributeName": "category_name", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "city", "AttributeType": "S"},
            {"AttributeName": "category_name", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table


def batch_write_places(places: list[dict]):
    from decimal import Decimal

    SKIP_FIELDS = {"city", "lat", "lon"}
    FLOAT_FIELDS = {"lat", "lon", "rating", "price"}

    table = get_table()
    chunk_size = 25
    written = 0
    for i in range(0, len(places), chunk_size):
        chunk = places[i : i + chunk_size]
        with table.batch_writer() as batch:
            for place in chunk:
                item = {
                    "city": place["city"].lower(),
                    "category_name": f"{place['category']}#{place['name']}",
                }
                for key, val in place.items():
                    if key in SKIP_FIELDS or val is None or val == "":
                        continue
                    if key in FLOAT_FIELDS:
                        item[key] = Decimal(str(val))
                    else:
                        item[key] = val
                if place.get("lat") is not None:
                    item["lat"] = Decimal(str(place["lat"]))
                if place.get("lon") is not None:
                    item["lon"] = Decimal(str(place["lon"]))
                batch.put_item(Item=item)
                written += 1
    return written


def query_by_city(city: str) -> list[dict]:
    table = get_table()
    response = table.query(
        KeyConditionExpression=Key("city").eq(city.lower())
    )
    return response.get("Items", [])


def query_by_city_and_category(city: str, category: str) -> list[dict]:
    table = get_table()
    response = table.query(
        KeyConditionExpression=(
            Key("city").eq(city.lower())
            & Key("category_name").begins_with(f"{category}#")
        )
    )
    return response.get("Items", [])


def _to_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except Exception:
        return None


def serialize_item(item: dict) -> dict:
    return {
        "city": item.get("city", ""),
        "category": item.get("category", ""),
        "name": item.get("name", ""),
        "country": item.get("country", ""),
        "lat": _to_float(item.get("lat")),
        "lon": _to_float(item.get("lon")),
        "address": item.get("address"),
        "formatted_address": item.get("formatted_address"),
        "website": item.get("website"),
        "source": item.get("source"),
    }
