"""Inventory API - Lambda + DynamoDB (API Gateway HTTP API, payload v2)."""
import json
import os
import uuid
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ.get("TABLE_NAME", "items"))


def _default(o):
    if isinstance(o, Decimal):
        return int(o) if o == o.to_integral_value() else float(o)
    raise TypeError


def resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=_default),
    }


def validate(raw):
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return None, "body bukan JSON yang valid"
    if not isinstance(data, dict):
        return None, "body harus berupa JSON object"
    name = data.get("name")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
        return None, "name wajib diisi (1-100 karakter)"
    quantity = data.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
        return None, "quantity harus integer >= 0"
    location = data.get("location")
    if location is not None and (not isinstance(location, str) or len(location) > 100):
        return None, "location maksimal 100 karakter"
    return {"name": name.strip(), "quantity": quantity, "location": location}, None


def create_item(event):
    clean, err = validate(event.get("body"))
    if err:
        return resp(400, {"error": err})
    clean["id"] = str(uuid.uuid4())
    table.put_item(Item=clean)
    return resp(201, clean)


def list_items(_event):
    result = table.scan()
    items = result.get("Items", [])
    while "LastEvaluatedKey" in result:
        result = table.scan(ExclusiveStartKey=result["LastEvaluatedKey"])
        items += result.get("Items", [])
    return resp(200, items)


def update_item(event):
    item_id = (event.get("pathParameters") or {}).get("id")
    clean, err = validate(event.get("body"))
    if err:
        return resp(400, {"error": err})
    try:
        table.update_item(
            Key={"id": item_id},
            UpdateExpression="SET #n = :n, quantity = :q, #l = :l",
            ExpressionAttributeNames={"#n": "name", "#l": "location"},
            ExpressionAttributeValues={
                ":n": clean["name"], ":q": clean["quantity"], ":l": clean["location"],
            },
            ConditionExpression="attribute_exists(id)",
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return resp(404, {"error": "item tidak ditemukan"})
        raise
    return resp(200, {"updated": item_id})


def delete_item(event):
    item_id = (event.get("pathParameters") or {}).get("id")
    try:
        table.delete_item(Key={"id": item_id}, ConditionExpression="attribute_exists(id)")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return resp(404, {"error": "item tidak ditemukan"})
        raise
    return resp(200, {"deleted": item_id})


ROUTES = {
    "POST /items": create_item,
    "GET /items": list_items,
    "PUT /items/{id}": update_item,
    "DELETE /items/{id}": delete_item,
    "GET /health": lambda _e: resp(200, {"status": "ok"}),
}


def lambda_handler(event, context):
    handler = ROUTES.get(event.get("routeKey"))
    if handler is None:
        return resp(404, {"error": "route tidak ditemukan"})
    try:
        return handler(event)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}")
        return resp(500, {"error": "terjadi kesalahan server"})
