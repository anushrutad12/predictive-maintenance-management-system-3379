from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.docs_routes import router as docs_router

openapi_tags = [
    {
        "name": "Health",
        "description": "Health checks and service readiness endpoints.",
    },
    {
        "name": "Docs",
        "description": "Documentation-style navigation and page content APIs backing the Architecture/User Stories UI.",
    },
]

app = FastAPI(
    title="Predictive Maintenance Backend API",
    description=(
        "Backend API for the Predictive Maintenance Management System. "
        "This service includes minimal docs/navigation endpoints used by the Angular documentation-style UI."
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(docs_router)


@app.get(
    "/",
    tags=["Health"],
    operation_id="health_check",
    summary="Health check",
    description="Basic health check endpoint used by deployment and local development.",
)
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}
