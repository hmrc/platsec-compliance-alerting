from unittest import TestCase
from moto import mock_aws

import boto3

from src.clients.aws_s3_client import AwsS3Client
from src.data.exceptions import AwsClientException

bucket = "test-bucket"
keys = [f"key_{index}" for index in range(10)]
obj = '[{"key": "val1"}, {"key": "val2"}]'


@mock_aws
class TestAwsS3Client(TestCase):
    def setUp(self) -> None:
        self.client = AwsS3Client(boto3.client("s3", region_name="us-east-1"))
        self.client._s3.create_bucket(Bucket=bucket)
        for key in keys:
            self.client._s3.put_object(Bucket=bucket, Key=key, Body=obj)

    def test_read_object(self) -> None:
        self.assertEqual([{"key": "val1"}, {"key": "val2"}], self.client.read_object(bucket, keys[0]))

    def test_read_object_failure(self) -> None:
        with self.assertRaisesRegex(AwsClientException, "unexpected-bucket"):
            self.client.read_object("unexpected-bucket", keys[0])

        with self.assertRaisesRegex(AwsClientException, "unexpected-key"):
            self.client.read_object(bucket, "unexpected-key")

    def test_read_invalid_object(self) -> None:
        self.client._s3.put_object(Bucket=bucket, Key="invalid-json", Body='{"key": "value"')

        with self.assertRaisesRegex(AwsClientException, "invalid-json"):
            self.client.read_object(bucket, "invalid-json")

    def test_list_objects(self) -> None:
        self.assertEqual(keys, self.client.list_objects(bucket, max_keys=5))

    def test_list_prefixed_objects(self) -> None:
        self.assertEqual([], self.client.list_objects(bucket, prefix="unexpected-prefix"))
        self.assertEqual(["key_4"], self.client.list_objects(bucket, prefix="key_4"))

    def test_list_objects_failure(self) -> None:
        with self.assertRaisesRegex(AwsClientException, "not-a-bucket"):
            self.client.list_objects("not-a-bucket")

        with self.assertRaisesRegex(AwsClientException, "unexpected-prefix"):
            self.client.list_objects("not-a-bucket", prefix="unexpected-prefix")
