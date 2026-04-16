from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from controllers import  (
    predict_controllers, 
    schedule_controllers, 
    quiz_controllers,
    image_controllers
)

from configuration.s3_config import init_bucket

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_bucket()
    yield

app = FastAPI(
    title="Monster IA API", 
    description="V1 of Monster IA API", 
    version="1.0",
    lifespan=lifespan
    )

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
    )

app.include_router(predict_controllers.router)
app.include_router(schedule_controllers.router)
app.include_router(quiz_controllers.router)
app.include_router(image_controllers.router)