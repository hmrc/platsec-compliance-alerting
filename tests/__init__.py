from botocore.exceptions import ClientError


def client_error() -> ClientError:
    return ClientError(
        operation_name="AssumeRole", error_response={"Error": {"Code": "AccessDenied", "Message": "AccessDenied"}}
    )
