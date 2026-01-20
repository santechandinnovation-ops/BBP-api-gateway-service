from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config.settings import settings
from app.middleware.rate_limit import limiter
from app.routes import health, auth_routes, user_routes, trip_routes, path_routes
from app.services.proxy import proxy

app = FastAPI(
    title=settings.APP_NAME,
    description="API Gateway for BBP Microservices",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

app.include_router(health.router)
app.include_router(auth_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(trip_routes.router, prefix="/api")
app.include_router(path_routes.router, prefix="/api")

@app.on_event("shutdown")
async def shutdown_event():
    await proxy.close()

@app.get("/")
async def root():
    return {
        "service": "BBP API Gateway",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth",
            "users": "/api/users",
            "trips": "/api/trips",
            "paths": "/api/paths"
        }
    }
