from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sigma_core.task_management.domain.errors import SigmaDomainError
from sigma_rest.error_handlers import domain_error_handler
from sigma_rest.routers import spaces, cards, areas, projects, epics

app = FastAPI(
    title="SIGMA API",
    description="Sistema Inteligente de Gestión y Monitorización de Actividades",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(SigmaDomainError, domain_error_handler)

app.include_router(spaces.router, prefix="/v1")
app.include_router(cards.router, prefix="/v1")
app.include_router(areas.router, prefix="/v1")
app.include_router(projects.router, prefix="/v1")
app.include_router(epics.router, prefix="/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}