from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers import predict_controllers, schedule_controllers, quiz_controllers


app = FastAPI(
    title="Monster IA API", 
    description="V1 of Monster IA API", 
    version="1.0"
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