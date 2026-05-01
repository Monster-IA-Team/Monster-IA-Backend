from fastapi import APIRouter, Depends, File, UploadFile, Form
from services.s3_services import S3Service
from dependencies.auth import auth_handler

router = APIRouter(
    prefix="/api/image",
    tags=["Image Upload"],
    dependencies=[Depends(auth_handler.get_current_user)]
)

s3_service = S3Service()

@router.post("/upload")
async def upload_image(
    name: str = Form(...), 
    folder: str = Form("images"), 
    file: UploadFile = File(...)
):

    url = await s3_service.upload_file(
        file=file,
        name=name,
        folder=folder
    )
    
    return {"url": url}