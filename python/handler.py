import json

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
}


def hello(event, context):
    """AWS Lambda handler for a simple Hello World HTTP endpoint."""
    query_params = event.get("queryStringParameters") or {}
    name = query_params.get("name", "World")

    body = {"message": f"Hello, {name}!", "language": "Python"}

    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps(body),
    }
