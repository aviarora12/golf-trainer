import boto3
import os
from botocore.exceptions import NoCredentialsError


class S3Service:

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        self.bucket = os.getenv('AWS_S3_BUCKET', 'swingcheck-videos')

    def upload_file(self, file_obj, s3_key: str) -> str:
        """Upload file to S3. Returns URL."""
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket,
                s3_key,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            url = f"https://{self.bucket}.s3.amazonaws.com/{s3_key}"
            return url
        except NoCredentialsError:
            raise Exception("AWS credentials not found")

    def download_file(self, s3_key: str, local_path: str) -> None:
        """Download file from S3."""
        try:
            self.s3_client.download_file(self.bucket, s3_key, local_path)
        except NoCredentialsError:
            raise Exception("AWS credentials not found")

    def delete_file(self, s3_key: str) -> None:
        """Delete file from S3."""
        self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)


s3_service = S3Service()
