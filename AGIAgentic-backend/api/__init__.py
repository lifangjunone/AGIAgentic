
from fastapi import APIRouter

from api.mcp_api import router as mcp_router
from api.llm_api import router as llm_router
from api.tool_api import router as tool_router
from api.health_api import router as health_router


router = APIRouter()
router.include_router(mcp_router)
router.include_router(llm_router)
router.include_router(tool_router)
router.include_router(health_router)

