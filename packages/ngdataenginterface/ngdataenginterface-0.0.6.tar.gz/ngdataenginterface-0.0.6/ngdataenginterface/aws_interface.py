import boto3
import json
import ast


class AWSManager:
    def __init__(self, region_name, aws_access_key_id, aws_secret_access_key):
        self.s3_client = boto3.client(
            "s3",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.s3_resource = boto3.resource(
            "s3",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.secretsmanager_client = boto3.client(
            "secretsmanager",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )


class AWSInterface(AWSManager):
    def get_object_aws(self, bucket_name, object_name):
        return self.s3_client.get_object(
            Bucket=bucket_name,
            Key=object_name,
        )["Body"].read()

    def put_object_aws(self, bucket_name, object_name, object):
        return self.s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=bytes(json.dumps(object).encode("UTF-8")),
        )

    @staticmethod
    def concat_multiple_data_events(events):
        mult_data = ""

        for event in events:
            mult_data += json.dumps(event) + "\n"

        return mult_data[:-1].encode("UTF-8")

    def put_multiple_objects_aws_single_file(self, bucket_name, object_name, objects):
        concat_mult_objects = self.concat_multiple_data_events(objects)

        return self.s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=concat_mult_objects,
        )

    def list_objects_key_aws(self, bucket_name, path):
        bucket_resource = self.s3_resource.Bucket(bucket_name)
        objects_key = []

        for object_summary in bucket_resource.objects.filter(Prefix=path):
            objects_key.append(object_summary.key)

        return objects_key

    def list_objects_url_aws(self, bucket_name, path):
        bucket_resource = self.s3_resource.Bucket(bucket_name)
        objects_url = []

        for object_summary in bucket_resource.objects.filter(Prefix=path):
            objects_url.append(
                f"s3://{object_summary.bucket_name}/{object_summary.key}"
            )

        return objects_url

    def delete_objects_aws(self, bucket_name, path):
        # Delete objects under a path
        bucket = self.s3_resource.Bucket(bucket_name)
        return bucket.objects.filter(Prefix=path).delete()  # todo alert error

    def get_secret_aws(self, secret_name: str):
        """
        Retrieve a secret value from AWS Secrets Manager.

        Args:
            secret_name (str): The name or ARN of the secret.

        Returns:
            dict: The secret value as a dictionary.

        Example:
            secret = get_secret("my-secret", "us-west-2")
        """

        # Retrieve the secret value from AWS Secrets Manager
        get_secret_value_response = self.secretsmanager_client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response["SecretString"]

        # Convert the secret string to a dictionary using ast.literal_eval
        return ast.literal_eval(secret)
