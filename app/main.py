from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.concurrency import run_in_threadpool

from controllers import  (
    predict_controllers, 
    schedule_controllers, 
    quiz_controllers,
    image_controllers,
    auth_controller,
    monster_controller
)

from configuration.s3_config import init_bucket

from seed.seed_data import SeedData

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_bucket()
    
    seeder = SeedData()
    await run_in_threadpool(seeder.seed_data)
    
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
app.include_router(auth_controller.router)
app.include_router(monster_controller.router)