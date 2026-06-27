from aiogram import Router

from .start import router as start_router
from .menu import router as menu_router
from .services import router as services_router
from .ppt import router as ppt_router
from .documents import router as documents_router
from .payment import router as payment_router
from .admin import router as admin_router
from .ai_helper import router as ai_helper_router
from .resume import router as resume_router


def setup_routers() -> Router:
    """Setup all routers."""
    main_router = Router()
    main_router.include_router(start_router)
    main_router.include_router(admin_router)
    main_router.include_router(resume_router)
    main_router.include_router(ppt_router)
    main_router.include_router(documents_router)
    main_router.include_router(payment_router)
    main_router.include_router(ai_helper_router)
    main_router.include_router(services_router)
    main_router.include_router(menu_router)
    return main_router
