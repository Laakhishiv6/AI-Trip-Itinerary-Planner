import boto3
from botocore.exceptions import ClientError
from typing import Optional
from .config import settings

TABLE_NAME = "users"
OTP_TABLE_NAME = "pending_otps"


def _get_resource():
    return boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def get_table():
    return _get_resource().Table(TABLE_NAME)


def create_table_if_not_exists():
    dynamodb = _get_resource()
    existing = [t.name for t in dynamodb.tables.all()]
    if TABLE_NAME in existing:
        return dynamodb.Table(TABLE_NAME)

    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "email", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table


def get_user(email: str) -> Optional[dict]:
    table = get_table()
    response = table.get_item(Key={"email": email.lower()})
    return response.get("Item")


def create_otp_table_if_not_exists():
    dynamodb = _get_resource()
    existing = [t.name for t in dynamodb.tables.all()]
    if OTP_TABLE_NAME in existing:
        return dynamodb.Table(OTP_TABLE_NAME)

    table = dynamodb.create_table(
        TableName=OTP_TABLE_NAME,
        KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()

    # Enable TTL on the 'expires_at' attribute
    dynamodb.meta.client.update_time_to_live(
        TableName=OTP_TABLE_NAME,
        TimeToLiveSpecification={"Enabled": True, "AttributeName": "expires_at"},
    )
    return table


def get_otp_table():
    return _get_resource().Table(OTP_TABLE_NAME)


def store_pending_otp(email: str, hashed_otp: str, hashed_password: str, full_name: str, expires_at: int):
    table = get_otp_table()
    table.put_item(Item={
        "email": email.lower(),
        "hashed_otp": hashed_otp,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "expires_at": expires_at,
    })


def get_pending_otp(email: str) -> Optional[dict]:
    table = get_otp_table()
    response = table.get_item(Key={"email": email.lower()})
    return response.get("Item")


def delete_pending_otp(email: str):
    table = get_otp_table()
    table.delete_item(Key={"email": email.lower()})


def create_user(email: str, hashed_password: str, full_name: str, created_at: str) -> dict:
    table = get_table()
    item = {
        "email": email.lower(),
        "hashed_password": hashed_password,
        "full_name": full_name,
        "created_at": created_at,
    }
    table.put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(email)",
    )
    return item
