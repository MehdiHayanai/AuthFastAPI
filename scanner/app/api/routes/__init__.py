from app.api.routes.v1 import auth, users
from fastapi import APIRouter

router = APIRouter()
router.include_router(auth.router)
router.include_router(users.router)
