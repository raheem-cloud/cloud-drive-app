import os
import boto3
from botocore.exceptions import NoCredentialsError

USE_S3 = os.getenv("USE_S3", "False").lower() in ("true", "1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "")
LOCAL_STORAGE = os.path.join(os.getcwd(), "uploads")

os.makedirs(LOCAL_STORAGE, exist_ok=True)

def upload_file_blob(file_obj, key):
    if USE_S3 and S3_BUCKET:
        s3 = boto3.client("s3")
        s3.upload_fileobj(file_obj, S3_BUCKET, key)
        return True
    else:
        dest_path = os.path.join(LOCAL_STORAGE, key)
        file_obj.save(dest_path)
        return True

def get_file_blob_path(key):
    return os.path.join(LOCAL_STORAGE, key)
