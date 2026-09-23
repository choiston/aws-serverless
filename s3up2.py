#!/usr/bin/env python3
"""공개 S3 버킷의 객체를 AWS 계정 설정 없이 관리한다.

필요 패키지: python3 -m pip install boto3 (AWS CLI는 필요하지 않음)

예시:
    python3 s3up2.py upload ./photo.jpg images/photo.jpg
    python3 s3up2.py list --prefix images/
    python3 s3up2.py download images/photo.jpg ./photo.jpg
    python3 s3up2.py delete images/photo.jpg

모든 요청은 인증 없이 전송한다. 같은 키로 다시 업로드하면 기존 객체를 갱신한다.
"""

import argparse
import sys
from pathlib import Path


BUCKET = "public-crud-100kb-086015456585"
REGION = "ap-northeast-2"


def parse_args():
    parser = argparse.ArgumentParser(description="S3 버킷의 객체를 관리합니다.")
    commands = parser.add_subparsers(dest="command", required=True)

    upload = commands.add_parser("upload", aliases=["update"], help="파일 업로드 또는 갱신")
    upload.add_argument("file", type=Path, help="업로드할 로컬 파일")
    upload.add_argument("key", nargs="?", help="S3 객체 키 (생략 시 파일 이름)")

    listing = commands.add_parser("list", help="객체 목록 조회")
    listing.add_argument("--prefix", default="", help="조회할 객체 키 접두사")

    download = commands.add_parser("download", aliases=["read"], help="객체 다운로드")
    download.add_argument("key", help="다운로드할 S3 객체 키")
    download.add_argument("file", type=Path, help="저장할 로컬 파일 경로")

    delete = commands.add_parser("delete", help="객체 삭제")
    delete.add_argument("key", help="삭제할 S3 객체 키")

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        import boto3
        from boto3.exceptions import Boto3Error
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        print("boto3가 필요합니다: python3 -m pip install boto3", file=sys.stderr)
        return 1

    try:
        from botocore import UNSIGNED
        from botocore.config import Config

        s3 = boto3.client(
            "s3", region_name=REGION, config=Config(signature_version=UNSIGNED)
        )

        if args.command in ("upload", "update"):
            if not args.file.is_file():
                print(f"파일을 찾을 수 없습니다: {args.file}", file=sys.stderr)
                return 1
            key = args.key if args.key is not None else args.file.name
            s3.upload_file(str(args.file), BUCKET, key)
            print(f"업로드 완료: s3://{BUCKET}/{key}")

        elif args.command == "list":
            pages = s3.get_paginator("list_objects_v2").paginate(
                Bucket=BUCKET, Prefix=args.prefix
            )
            for page in pages:
                for obj in page.get("Contents", []):
                    print(f"{obj['Key']}\t{obj['Size']} bytes")

        elif args.command in ("download", "read"):
            args.file.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(BUCKET, args.key, str(args.file))
            print(f"다운로드 완료: {args.file}")

        elif args.command == "delete":
            s3.delete_object(Bucket=BUCKET, Key=args.key)
            print(f"삭제 완료: s3://{BUCKET}/{args.key}")

    except (Boto3Error, BotoCoreError, ClientError, OSError) as error:
        print(f"작업 실패: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
