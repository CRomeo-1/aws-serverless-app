import json
import os
import random
import string
import time

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "short-links"))


def res(code, body=None, headers=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    return {"statusCode": code, "headers": h, "body": json.dumps(body) if body else ""}


def make_code(n=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(n))


def create_link(event):
    try:
        body = json.loads(event.get("body") or "{}")
    except ValueError:
        return res(400, {"error": "invalid json"})

    url = body.get("url", "")
    if not url.startswith(("http://", "https://")):
        return res(400, {"error": "url must start with http:// or https://"})

    code = make_code()
    table.put_item(Item={"code": code, "url": url, "clicks": 0, "created": int(time.time())})
    return res(201, {"code": code, "url": url})


def open_link(code):
    item = table.get_item(Key={"code": code}).get("Item")
    if not item:
        return res(404, {"error": "not found"})

    # count the visit
    table.update_item(
        Key={"code": code},
        UpdateExpression="ADD clicks :one",
        ExpressionAttributeValues={":one": 1},
    )
    return res(301, headers={"Location": item["url"]})


def get_stats(code):
    item = table.get_item(Key={"code": code}).get("Item")
    if not item:
        return res(404, {"error": "not found"})
    return res(200, {"code": code, "url": item["url"], "clicks": int(item["clicks"])})


def handler(event, context):
    route = event.get("routeKey")
    code = (event.get("pathParameters") or {}).get("code")

    if route == "POST /links":
        return create_link(event)
    elif route == "GET /{code}":
        return open_link(code)
    elif route == "GET /stats/{code}":
        return get_stats(code)

    return res(404, {"error": "route not found"})
