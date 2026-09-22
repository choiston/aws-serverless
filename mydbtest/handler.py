import base64
import json
import logging
import os

import pymysql
from pymysql.cursors import DictCursor


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

ALLOWED_FIELDS = ("english_name", "korean_name", "market_code")


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body, ensure_ascii=False, default=str),
    }


def parse_body(event):
    raw_body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body).decode("utf-8")
    body = json.loads(raw_body)
    if not isinstance(body, dict):
        raise ValueError("JSON body must be an object")
    return body


def market_id_from(event):
    value = (event.get("pathParameters") or {}).get("id")
    if value is None:
        return None
    market_id = int(value)
    if market_id <= 0:
        raise ValueError("id must be a positive integer")
    return market_id


def connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "mockinv"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=False,
    )


def fetch_market(cursor, market_id):
    cursor.execute(
        "SELECT upbit_market_id, english_name, korean_name, market_code "
        "FROM upbit_market WHERE upbit_market_id = %s",
        (market_id,),
    )
    return cursor.fetchone()


def lambda_handler(event, context):
    method = event.get("httpMethod", "").upper()
    if method == "OPTIONS":
        return response(204, {})

    try:
        market_id = market_id_from(event)

        with connection() as conn:
            with conn.cursor() as cursor:
                if method == "GET" and market_id is None:
                    params = event.get("queryStringParameters") or {}
                    limit = min(max(int(params.get("limit", 100)), 1), 500)
                    offset = max(int(params.get("offset", 0)), 0)
                    cursor.execute(
                        "SELECT upbit_market_id, english_name, korean_name, market_code "
                        "FROM upbit_market ORDER BY upbit_market_id LIMIT %s OFFSET %s",
                        (limit, offset),
                    )
                    items = cursor.fetchall()
                    cursor.execute("SELECT COUNT(*) AS total FROM upbit_market")
                    return response(
                        200,
                        {"items": items, "total": cursor.fetchone()["total"], "limit": limit, "offset": offset},
                    )

                if method == "GET" and market_id is not None:
                    item = fetch_market(cursor, market_id)
                    return response(200, item) if item else response(404, {"message": "Market not found"})

                if method == "POST" and market_id is None:
                    body = parse_body(event)
                    values = {field: body.get(field) for field in ALLOWED_FIELDS}
                    if not values["market_code"]:
                        return response(400, {"message": "market_code is required"})
                    cursor.execute(
                        "INSERT INTO upbit_market (english_name, korean_name, market_code) VALUES (%s, %s, %s)",
                        (values["english_name"], values["korean_name"], values["market_code"]),
                    )
                    new_id = cursor.lastrowid
                    conn.commit()
                    return response(201, fetch_market(cursor, new_id))

                if method == "PUT" and market_id is not None:
                    body = parse_body(event)
                    updates = {field: body[field] for field in ALLOWED_FIELDS if field in body}
                    if not updates:
                        return response(400, {"message": "Provide at least one market field"})
                    assignments = ", ".join(f"{field} = %s" for field in updates)
                    cursor.execute(
                        f"UPDATE upbit_market SET {assignments} WHERE upbit_market_id = %s",
                        (*updates.values(), market_id),
                    )
                    if cursor.rowcount == 0 and fetch_market(cursor, market_id) is None:
                        conn.rollback()
                        return response(404, {"message": "Market not found"})
                    conn.commit()
                    return response(200, fetch_market(cursor, market_id))

                if method == "DELETE" and market_id is not None:
                    cursor.execute("DELETE FROM upbit_market WHERE upbit_market_id = %s", (market_id,))
                    if cursor.rowcount == 0:
                        conn.rollback()
                        return response(404, {"message": "Market not found"})
                    conn.commit()
                    return response(200, {"deleted": True, "upbit_market_id": market_id})

                return response(405, {"message": "Method not allowed"})
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return response(400, {"message": str(exc)})
    except Exception:
        LOGGER.exception("Request failed")
        return response(500, {"message": "Internal server error"})
