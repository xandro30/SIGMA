from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sigma_core.metrics.application.use_cases.create_cycle_artifacts import (
    OnCycleClosedHandler,
)
from sigma_core.metrics.domain.errors import MetricsDomainError
from sigma_core.planning.domain.errors import PlanningDomainError
from sigma_core.shared_kernel.errors import SigmaDomainError
from sigma_core.shared_kernel.events import CycleClosed
from sigma_rest.config import get_cors_origins
from sigma_rest.dependencies import (
    get_cycle_snapshot_repo,
    get_cycle_summary_repo,
    get_event_bus,
    get_metrics_card_reader,
    get_metrics_cycle_reader,
    get_metrics_space_reader,
)
from sigma_rest.error_handlers import (
    domain_error_handler,
    metrics_domain_error_handler,
    planning_domain_error_handler,
)
from sigma_rest.routers import (
    areas,
    cards,
    cycles,
    day_templates,
    days,
    epics,
    metrics,
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

app.add_exception_handler(MetricsDomainError, metrics_domain_error_handler)
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
app.include_router(metrics.router, prefix="/v1")
app.include_router(planning_queries.router, prefix="/v1")


# ── Wire domain event handlers (lazy — runs at first request) ────
_event_handlers_wired = False


@app.on_event("startup")
async def _wire_event_handlers():
    global _event_handlers_wired
    if _event_handlers_wired:
        return
    bus = get_event_bus()
    bus.subscribe(
        CycleClosed,
        OnCycleClosedHandler(
            card_reader=get_metrics_card_reader(),
            space_reader=get_metrics_space_reader(),
            cycle_reader=get_metrics_cycle_reader(),
            summary_repo=get_cycle_summary_repo(),
            snapshot_repo=get_cycle_snapshot_repo(),
        ),
    )
    _event_handlers_wired = True


@app.get("/health")
async def health():
    return {"status": "ok"}