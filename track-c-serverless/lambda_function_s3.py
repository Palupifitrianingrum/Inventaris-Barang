"""Inventory API - Lambda + S3 (API Gateway HTTP API, payload v2).

Satu item = satu objek JSON di S3: items/<uuid>.json
"""
import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError

BUCKET = os.environ["BUCKET_NAME"]
PREFIX = "items/"
s3 = boto3.client("s3")


def resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def key_of(item_id):
    return f"{PREFIX}{item_id}.json"


def valid_id(item_id):
    try:
        uuid.UUID(str(item_id))
        return True
    except ValueError:
        return False


def exists(item_id):
    try:
        s3.head_object(Bucket=BUCKET, Key=key_of(item_id))
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def save(item):
    s3.put_object(
        Bucket=BUCKET,
        Key=key_of(item["id"]),
        Body=json.dumps(item).encode("utf-8"),
        ContentType="application/json",
    )


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
    save(clean)
    return resp(201, clean)


def list_items(_event):
    items = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            body = s3.get_object(Bucket=BUCKET, Key=obj["Key"])["Body"].read()
            items.append(json.loads(body))
    return resp(200, items)


def update_item(event):
    item_id = (event.get("pathParameters") or {}).get("id")
    clean, err = validate(event.get("body"))
    if err:
        return resp(400, {"error": err})
    if not valid_id(item_id) or not exists(item_id):
        return resp(404, {"error": "item tidak ditemukan"})
    clean["id"] = item_id
    save(clean)
    return resp(200, {"updated": item_id})


def delete_item(event):
    item_id = (event.get("pathParameters") or {}).get("id")
    if not valid_id(item_id) or not exists(item_id):
        return resp(404, {"error": "item tidak ditemukan"})
    s3.delete_object(Bucket=BUCKET, Key=key_of(item_id))
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
