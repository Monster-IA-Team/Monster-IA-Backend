import os, aioboto3, logging, json

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

S3_CONFIG = {
    "endpoint_url": os.getenv("S3_ENDPOINT"),
    "aws_access_key_id": os.getenv("S3_ACCESS_LOGIN"),
    "aws_secret_access_key": os.getenv("S3_SECRET_PASSWORD"),
    "region_name": os.getenv("S3_REGION"),
}

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

S3_PUBLIC_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT")

session = aioboto3.Session()

async def init_bucket():
    if not BUCKET_NAME or not BUCKET_NAME.strip():
        logger.error("Bucket name is not set in environment variables.")
        return 
    
    async with session.client("s3", **S3_CONFIG) as s3_client:
        try:
            await s3_client.head_bucket(Bucket=BUCKET_NAME)
            logger.info(f"Bucket '{BUCKET_NAME}' already exists.")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                logger.info(f"Creating bucket: {BUCKET_NAME}")
                await s3_client.create_bucket(Bucket=BUCKET_NAME)

                policy = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
                    }]
                }
                
                await s3_client.put_bucket_policy(
                    Bucket=BUCKET_NAME,
                    Policy=json.dumps(policy)
                )
                
                logger.info(f"Set public read policy for bucket: {BUCKET_NAME}")
            else:
                logger.error(f"Error checking S3 bucket: {e}")