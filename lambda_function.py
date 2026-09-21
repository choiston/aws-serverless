import json


def lambda_handler(event, context):
    response = {"rtn-value": "안녕하세요"}

    # Keep the requested JSON for direct Lambda invocations, while returning
    # the HTTP API proxy response format for API Gateway requests.
    if isinstance(event, dict) and "requestContext" in event:
        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(response, ensure_ascii=False),
        }

    return response
