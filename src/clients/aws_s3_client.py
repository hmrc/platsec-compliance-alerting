from botocore.client import BaseClient


class AwsS3Client:
    def __init__(self, boto_s3: BaseClient):
        self._s3 = boto_s3
