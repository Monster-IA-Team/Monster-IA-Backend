from fastapi import APIRouter, File, UploadFile, Form
from services.s3_services import S3Service

router = APIRouter(
    prefix="/api/image",
    tags=["Image Upload"]
)

s3_service = S3Service()

@router.post("/upload")
async def upload_image(
    name: str = Form(...), 
    file: UploadFile = File(...)
):
    url = await s3_service.upload_file(name, file)
    return {"url": url}