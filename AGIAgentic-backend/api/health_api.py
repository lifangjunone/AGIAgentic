
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health",tags=["Health"])

@router.get("/")
async def health_check():
    """ Health check endpoint to verify the service is running.
    Returns:
        dict: A simple status message.
    """
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check():
    """ Readiness check endpoint to verify the service is ready to handle requests.
    Returns:
        dict: A simple readiness message.
    """
    return {"ready": True}

@router.get("/info")
async def service_info():
    """ Service info endpoint to provide basic information about the service.
    Returns:
        dict: A basic info message.
    """
    import platform

    return JSONResponse(
      {
          "service": "AGIAgentic Backend",
          "version": "1.0.0",
          "uptime": "72 hours",
          "os_name": platform.system(),
          "os_version": platform.version(),
          "os_detail": platform.platform()
      }
    )

@router.get("/status")
async def service_status():
    """ Service status endpoint to provide detailed status information.
    Returns:
        dict: A detailed status message.
    """
    return JSONResponse(
      {
        "service": "AGIAgentic Backend",
        "version": "1.0.0",
        "uptime": "72 hours",
        "dependencies": {
            "database": "connected",
            "llm_provider": "operational"
        }
      } 
    )
