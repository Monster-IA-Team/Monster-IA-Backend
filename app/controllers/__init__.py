from .predict_controllers import router as predict_router
from .schedule_controllers import router as schedule_router
from .quiz_controllers import router as quiz_router
from .image_controllers import router as image_router
from .auth_controller import router as auth_router
from .monster_controller import router as monster_router
from .admin_controller import router as admin_router

predict_controllers = predict_router
schedule_controllers = schedule_router
quiz_controllers = quiz_router
image_controllers = image_router
auth_controller = auth_router
monster_controller = monster_router
admin_controller = admin_router
