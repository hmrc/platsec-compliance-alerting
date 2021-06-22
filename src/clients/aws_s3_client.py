from io import BytesIO
from json import loads
from typing import Any, Dict, List

from botocore.client import BaseClient

from src.clients import boto_try


class AwsS3Client:
    def __init__(self, boto_s3: BaseClient):
        self._s3 = boto_s3

    def read_object(self, bucket: str, key: str) -> List[Dict[str, Any]]:
        return boto_try(
            lambda: list(loads(self._read_object(bucket, key))), f"failed to read object '{key}' from bucket '{bucket}'"
        )

    def list_objects(self, bucket: str, prefix: str = "", max_keys: int = 1000) -> List[str]:
        return boto_try(
            lambda: self._list_objects(bucket, prefix, max_keys),
            f"failed to list objects{' with prefix ' + prefix if prefix else ''} from bucket '{bucket}'",
        )

    def _read_object(self, bucket: str, key: str) -> str:
        with BytesIO() as buffer:
            self._s3.download_fileobj(Bucket=bucket, Key=key, Fileobj=buffer)
            return buffer.getvalue().decode("utf-8")

    def _list_objects(self, bucket: str, prefix: str, max_keys: int) -> List[str]:
        def get_keys(response: Dict[str, Any]) -> List[str]:
            return [obj["Key"] for obj in response["Contents"]] if response.get("Contents") else []

        resp = self._s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=max_keys)
        keys = get_keys(resp)

        while resp["IsTruncated"]:
            resp = self._s3.list_objects_v2(
                Bucket=bucket, Prefix=prefix, MaxKeys=max_keys, ContinuationToken=resp["NextContinuationToken"]
            )
            keys.extend(get_keys(resp))

        return keys
