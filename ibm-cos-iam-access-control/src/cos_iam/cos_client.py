"""Thin wrapper around ibm_boto3 that authenticates through IBM Cloud IAM."""
import ibm_boto3
from ibm_botocore.client import Config, ClientError


def make_cos_client(api_key: str, instance_crn: str, endpoint: str):
    return ibm_boto3.client(
        "s3",
        ibm_api_key_id=api_key,
        ibm_service_instance_id=instance_crn,
        config=Config(signature_version="oauth"),
        endpoint_url=endpoint,
    )


def can_list(client, bucket: str) -> bool:
    try:
        client.list_objects_v2(Bucket=bucket, MaxKeys=1)
        return True
    except ClientError as e:
        _log_denied(e)
        return False


def can_upload(client, bucket: str, key: str = "iam-access-test.txt") -> bool:
    try:
        client.put_object(Bucket=bucket, Key=key, Body=b"access control test")
        return True
    except ClientError as e:
        _log_denied(e)
        return False


def can_delete(client, bucket: str, key: str = "iam-access-test.txt") -> bool:
    try:
        client.delete_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        _log_denied(e)
        return False


def _log_denied(err: ClientError) -> None:
    code = err.response.get("Error", {}).get("Code", "Unknown")
    print(f"    -> denied ({code})")
