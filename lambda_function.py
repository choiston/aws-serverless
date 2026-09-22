import json

STOCKS = [
    {
        "symbol": "005930",
        "name": "삼성전자",
        "market": "KOSPI",
        "price": 71200,
        "change": 0.85,
        "volume": 12345678,
    },
    {
        "symbol": "000660",
        "name": "SK하이닉스",
        "market": "KOSPI",
        "price": 182500,
        "change": -1.24,
        "volume": 3210456,
    },
    {
        "symbol": "035420",
        "name": "NAVER",
        "market": "KOSPI",
        "price": 168000,
        "change": 0.3,
        "volume": 812340,
    },
    {
        "symbol": "035720",
        "name": "카카오",
        "market": "KOSPI",
        "price": 41950,
        "change": -0.59,
        "volume": 2945120,
    },
    {
        "symbol": "005380",
        "name": "현대차",
        "market": "KOSPI",
        "price": 236000,
        "change": 1.72,
        "volume": 654210,
    },
    {
        "symbol": "247540",
        "name": "에코프로비엠",
        "market": "KOSDAQ",
        "price": 158700,
        "change": 2.91,
        "volume": 1120034,
    },
    {
        "symbol": "086520",
        "name": "에코프로",
        "market": "KOSDAQ",
        "price": 93400,
        "change": -2.1,
        "volume": 1530990,
    },
    {
        "symbol": "196170",
        "name": "알테오젠",
        "market": "KOSDAQ",
        "price": 312000,
        "change": 0.97,
        "volume": 402311,
    },
]


def lambda_handler(event, context):
    response = STOCKS

    # Keep the requested JSON for direct Lambda invocations, while returning
    # the HTTP API proxy response format for API Gateway requests.
    if isinstance(event, dict) and "requestContext" in event:
        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(response, ensure_ascii=False),
        }

    return response
