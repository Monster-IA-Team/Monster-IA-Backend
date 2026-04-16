import aioboto3, logging, os
from botocore.exceptions import ClientError
from fastapi import UploadFile

from configuration.s3_config import (
    S3_CONFIG, 
    BUCKET_NAME, 
    S3_PUBLIC_ENDPOINT
)

logger = logging.getLogger(__name__)

session = aioboto3.Session()

class S3Service:
    def __init__(self):
        pass
           
    async def upload_file(self, name: str, file: UploadFile) -> str:
        async with session.client("s3", **S3_CONFIG) as s3_client:
            try:
                name = name.replace(" ", "_").strip()
            
                _, ext = os.path.splitext(file.filename)
                filename = f"{name}{ext}"

                await s3_client.upload_fileobj(
                    file.file,
                    BUCKET_NAME,
                    filename,
                    ExtraArgs={
                       "ContentType": file.content_type
                    }
                )
                
                return f"{S3_PUBLIC_ENDPOINT}/{BUCKET_NAME}/{filename}"
                
            except Exception as e:
                logger.error(f"Error uploading file to S3: {e}")
                raise e