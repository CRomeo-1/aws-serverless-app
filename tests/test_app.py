import json
import os
import sys

import boto3
from moto import mock_aws

os.environ["AWS_DEFAULT_REGION"] = "me-central-1"
os.environ["TABLE_NAME"] = "test-table"
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))


@mock_aws
def test_create_and_open():
    boto3.resource("dynamodb").create_table(
        TableName="test-table",
        KeySchema=[{"AttributeName": "code", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "code", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    import app

    r = app.handler({"routeKey": "POST /links", "body": json.dumps({"url": "https://google.com"})}, None)
    assert r["statusCode"] == 201
    code = json.loads(r["body"])["code"]

    r = app.handler({"routeKey": "GET /{code}", "pathParameters": {"code": code}}, None)
    assert r["statusCode"] == 301
    assert r["headers"]["Location"] == "https://google.com"

    r = app.handler({"routeKey": "GET /stats/{code}", "pathParameters": {"code": code}}, None)
    assert json.loads(r["body"])["clicks"] == 1

    r = app.handler({"routeKey": "POST /links", "body": json.dumps({"url": "hello"})}, None)
    assert r["statusCode"] == 400
