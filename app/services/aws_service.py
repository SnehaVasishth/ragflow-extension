import os
import mimetypes
import boto3

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("ZBRAIN_S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("ZBRAIN_S3_SECRET_KEY"),
    region_name=os.getenv("ZBRAIN_S3_REGION"),
)

def download_file_from_s3(path: str, key: str, bucket: str = os.getenv("ZBRAIN_S3_BUCKET_NAME")):
    if not path or not key:
        print("INVALID_ARGUMENTS")
        raise ValueError("INVALID_ARGUMENTS")
    try:
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        response = s3.get_object(Bucket=bucket, Key=key)
        data = response['Body'].read()
        with open(path, 'wb') as file:
            file.write(data)
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        raise RuntimeError(f"Error downloading file: {str(e)}")
