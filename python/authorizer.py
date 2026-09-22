import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AUTH_TOKEN must be provided via Lambda environment (see serverless.yaml).
# No default on purpose: if the variable is missing every request is denied.
VALID_TOKEN = os.environ.get("AUTH_TOKEN", "")


def authorize(event, context):
    """
    Lambda TOKEN Authorizer.

    Clients must send:
        Authorization: Bearer <token>

    Returns an IAM policy allowing or denying access to the API.
    """
    token = _extract_token(event.get("authorizationToken", ""))
    method_arn = event.get("methodArn", "")

    if not VALID_TOKEN:
        logger.error("AUTH_TOKEN environment variable is not set; denying all requests")
        return _policy("user", "Deny", method_arn)

    if token and token == VALID_TOKEN:
        return _policy("user", "Allow", method_arn)

    logger.info("Authorization denied for methodArn=%s", method_arn)
    return _policy("user", "Deny", method_arn)


def _extract_token(header_value: str) -> str:
    """Strip 'Bearer ' prefix if present and return the bare token."""
    if header_value.lower().startswith("bearer "):
        return header_value[7:].strip()
    return header_value.strip()


def _policy(principal_id: str, effect: str, method_arn: str) -> dict:
    """
    Build a minimal IAM policy document.
    Wildcard resource covers all methods/stages of the same API so one
    Authorizer response can be cached and reused across all routes.
    """
    # Convert  arn:…:api-id/stage/METHOD/resource  →  arn:…:api-id/*
    arn_parts = method_arn.split(":")
    if len(arn_parts) >= 6:
        api_part = arn_parts[5].split("/")[0]
        resource_arn = ":".join(arn_parts[:5]) + ":" + api_part + "/*"
    else:
        resource_arn = method_arn

    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource_arn,
                }
            ],
        },
        "context": {
            "authorized": effect == "Allow",
        },
    }
