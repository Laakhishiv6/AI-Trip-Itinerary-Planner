import boto3
from decimal import Decimal
from .config import settings

TABLE_NAME = "travel_data"


def _get_resource():
    return boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def scan_all_places() -> list[dict]:
    """Full table scan — returns every item from travel_data."""
    table = _get_resource().Table(TABLE_NAME)
    items = []
    resp = table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return [_deserialize(i) for i in items]


def _deserialize(item: dict) -> dict:
    """Convert Decimal back to float so downstream code is clean."""
    return {
        k: float(v) if isinstance(v, Decimal) else v
        for k, v in item.items()
    }
