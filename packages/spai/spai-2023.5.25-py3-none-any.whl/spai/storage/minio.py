from minio import Minio
import os

client = Minio(
    endpoint=os.environ["S3_ENDPOINT"],
    access_key=os.environ["ACCESS_KEY_ID"],
    secret_key=os.environ["SECRET_ACCESS_KEY"],
    secure=True,
    region=os.environ["S3_REGION"],
)

bucket = os.environ["S3_BUCKET"]

if not client.bucket_exists(bucket):
    client.make_bucket(bucket)
    print(f"{bucket} created")
