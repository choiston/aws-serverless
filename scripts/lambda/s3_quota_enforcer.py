"""
S3 버킷 용량 제한 강제 Lambda
- 트리거: s3:ObjectCreated:* (public-crud-100kb 버킷)
- 규칙:
  1) 업로드된 객체 하나가 MAX_BUCKET_BYTES(100KB)를 넘으면 삭제
  2) 업로드 후 버킷 전체 용량이 MAX_BUCKET_BYTES를 넘으면 방금 올린 객체 삭제
  3) 멀티파트 업로드(파일 하나를 여러 파트로 나눠 올림)는 허용하지 않음 -> 삭제
"""
import os
import urllib.parse

import boto3

s3 = boto3.client("s3")
MAX_BUCKET_BYTES = int(os.environ.get("MAX_BUCKET_BYTES", "102400"))  # 100 KB


def bucket_total_bytes(bucket: str) -> int:
    total = 0
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            total += obj["Size"]
    return total


def reject(bucket: str, key: str, reason: str) -> None:
    s3.delete_object(Bucket=bucket, Key=key)
    print(f"REJECTED s3://{bucket}/{key} - {reason}")


def lambda_handler(event, context):
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        size = record["s3"]["object"].get("size", 0)
        event_name = record.get("eventName", "")

        if "CompleteMultipartUpload" in event_name:
            reject(bucket, key, "multipart upload is not allowed (one file per single PUT)")
            continue

        if size > MAX_BUCKET_BYTES:
            reject(bucket, key, f"object size {size}B > limit {MAX_BUCKET_BYTES}B")
            continue

        total = bucket_total_bytes(bucket)
        if total > MAX_BUCKET_BYTES:
            reject(bucket, key, f"bucket total {total}B > limit {MAX_BUCKET_BYTES}B")
            continue

        print(f"ACCEPTED s3://{bucket}/{key} size={size}B bucket_total={total}B")

    return {"ok": True}
