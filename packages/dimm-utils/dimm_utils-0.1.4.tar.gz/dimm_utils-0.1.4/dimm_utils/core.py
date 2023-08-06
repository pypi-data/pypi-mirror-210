import subprocess
import os
import boto3
from botocore import exceptions as botocore_exceptions


def singleton_function(func):
    instance = None

    def get_instance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = func(*args, **kwargs)
        return instance

    return get_instance


def authenticate_local():
    def get_pulumi_secret(secret: str):
        result = subprocess.run(
            ["pulumi", "config", "get", secret], capture_output=True
        )
        return result.stdout.decode().strip()

    # Retrieve the initial AWS credentials from Pulumi config secrets
    aws_region = get_pulumi_secret("region")
    aws_access_key_id = get_pulumi_secret("access_key_id")
    aws_secret_access_key = get_pulumi_secret("secret_access_key")
    role_arn = get_pulumi_secret("role_arn")

    os.environ["aws_region"] = aws_region
    os.environ["aws_access_key_id"] = aws_access_key_id
    os.environ["aws_secret_access_key"] = aws_secret_access_key
    os.environ["aws_role_arn"] = role_arn


@singleton_function
def authenticate(role_session_name: str) -> dict[str, str]:
    print("Getting AWS credentials...")
    # Retrieve the initial AWS credentials from Environment Variables
    aws_region = os.environ["aws_region"]
    aws_access_key_id = os.environ["aws_access_key_id"]
    aws_secret_access_key = os.environ["aws_secret_access_key"]
    role_arn = os.environ["aws_role_arn"]

    # Create a boto3 client with the initial credentials
    sts = boto3.client(
        "sts",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )

    # Assume an IAM role
    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name,
    )

    aws_access_key_id = response["Credentials"]["AccessKeyId"]
    aws_secret_access_key = response["Credentials"]["SecretAccessKey"]
    aws_session_token = response["Credentials"]["SessionToken"]

    credentials = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
        "aws_session_token": aws_session_token,
        "region_name": aws_region,
    }
    return credentials


def get_secret(client, secret_name: str) -> str:
    try:
        # Retrieve the secret value
        response = client.get_secret_value(SecretId=secret_name)

        # Parse the secret value as JSON
        return response["SecretString"]
    except botocore_exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"The secret {secret_name} was not found.")

            return f"The secret {secret_name} was not found."
        else:
            print(e)
            raise e


def store_secret_from_local(client, secret_name: str, secret_value: str):
    authenticate_local()
    # Create or update the secret
    try:
        secret = get_secret(client, secret_name)
        if secret == secret_value:
            print("Secret already exists")
            return
        elif secret == f"The secret {secret_name} was not found.":
            print(f"Creating secret {secret_name}")
            client.create_secret(
                Name=secret_name,
                SecretString=secret_value,
            )
    except client.exceptions.ResourceExistsException:
        client.update_secret(
            SecretId=secret_name,
            SecretString=secret_value,
        )
    except Exception as e:
        print(e)
        raise e


def get_bucket_object(client, bucket_name: str, key: str):
    response = client.get_object(Bucket=bucket_name, Key=key)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        return response.get("Body")
    else:
        print(f"Unsuccessful S3 get_object response. Status - {status}")


def upload_file_to_s3(client, bucket_name: str, key: str, file_path: str):
    try:
        # Check if the parent directory exists
        parent_dir = "/".join(key.split("/")[:-1])
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=parent_dir)
        parent_dir_exists = response.get("KeyCount", 0) > 0

        # Create the parent directories if they don't exist
        if not parent_dir_exists:
            client.put_object(Bucket=bucket_name, Key=parent_dir + "/")

        # Write the file to S3
        print(f"Writing to S3: {key}")

        # upload the file to the S3 bucket
        client.upload_file(file_path, bucket_name, key)

        print(f"Successfully uploaded {file_path} to S3")

        url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
        print(url)
        return url

    except botocore_exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Error uploading file to S3: {error_code} - {error_message}")
        return None


def main():
    print("This is a module, not a script.")
    pass
