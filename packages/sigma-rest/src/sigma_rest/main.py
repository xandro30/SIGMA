from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sigma_core.planning.domain.errors import PlanningDomainError
from sigma_core.shared_kernel.errors import SigmaDomainError
from sigma_rest.config import get_cors_origins
from sigma_rest.error_handlers import (
    domain_error_handler,
    planning_domain_error_handler,
)
from sigma_rest.routers import (
    areas,
    cards,
    cycles,
    day_templates,
    days,
    epics,
    planning_queries,
    projects,
    spaces,
    week_templates,
    weeks,
)

app = FastAPI(
    title="SIGMA API",
    description="Sistema Inteligente de Gestión y Monitorización de Actividades",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(PlanningDomainError, planning_domain_error_handler)
app.add_exception_handler(SigmaDomainError, domain_error_handler)

app.include_router(spaces.router, prefix="/v1")
app.include_router(cards.router, prefix="/v1")
app.include_router(areas.router, prefix="/v1")
app.include_router(projects.router, prefix="/v1")
app.include_router(epics.router, prefix="/v1")
app.include_router(cycles.router, prefix="/v1")
app.include_router(days.router, prefix="/v1")
app.include_router(day_templates.router, prefix="/v1")
app.include_router(week_templates.router, prefix="/v1")
app.include_router(weeks.router, prefix="/v1")
app.include_router(planning_queries.router, prefix="/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}