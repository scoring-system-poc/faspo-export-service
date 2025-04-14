import fastapi

from .probe import router as probe_router
from .export import router as export_router


router = fastapi.APIRouter(
    prefix="/api/v1",
)

router.include_router(probe_router)
router.include_router(export_router)
