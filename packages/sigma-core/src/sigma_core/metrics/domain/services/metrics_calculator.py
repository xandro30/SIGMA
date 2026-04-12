"""MetricsCalculator — servicio puro de dominio.

Sin I/O, sin estado. Recibe datos (cards, budgets, size_mapping) y devuelve
el arbol jerarquico completo de metricas precalculadas.
"""
from __future__ import annotations

from collections import defaultdict

from sigma_core.metrics.domain.value_objects import (
    AreaMetrics,
    CalibrationEntry,
    CardSnapshot,
    MetricsBlock,
    ProjectMetrics,
)
from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId


class MetricsCalculator:
    """Calcula metricas jerarquicas sobre un conjunto de cards completadas.

    Uso:
    - Handler de ``CycleClosed``: calcula y persiste en ``CycleSummary``.
    - Query on-demand (ciclo activo): calcula al vuelo sin persistir.
    """

    def calculate(
        self,
        cards: list[CardSnapshot],
        area_budgets: dict[AreaId, int],
        size_mapping: dict[str, int] | None,
    ) -> tuple[MetricsBlock, dict[AreaId, AreaMetrics]]:
        """Retorna (global_metrics, areas_dict) con el arbol completo."""
        global_block = self._calculate_block(cards, size_mapping)

        # Agrupar cards por area
        by_area: dict[AreaId, list[CardSnapshot]] = defaultdict(list)
        for card in cards:
            if card.area_id is not None:
                by_area[card.area_id].append(card)

        areas: dict[AreaId, AreaMetrics] = {}
        # Incluir areas con budget aunque no tengan cards
        all_area_ids = set(by_area.keys()) | set(area_budgets.keys())
        for area_id in all_area_ids:
            area_cards = by_area.get(area_id, [])
            area_block = self._calculate_block(area_cards, size_mapping)
            budget = area_budgets.get(area_id, 0)

            # Agrupar cards de esta area por project
            by_project: dict[ProjectId, list[CardSnapshot]] = defaultdict(list)
            for card in area_cards:
                if card.project_id is not None:
                    by_project[card.project_id].append(card)

            projects: dict[ProjectId, ProjectMetrics] = {}
            for project_id, project_cards in by_project.items():
                project_block = self._calculate_block(
                    project_cards, size_mapping
                )

                # Agrupar cards de este project por epic
                by_epic: dict[EpicId, list[CardSnapshot]] = defaultdict(list)
                for card in project_cards:
                    if card.epic_id is not None:
                        by_epic[card.epic_id].append(card)

                epics: dict[EpicId, MetricsBlock] = {}
                for epic_id, epic_cards in by_epic.items():
                    epics[epic_id] = self._calculate_block(
                        epic_cards, size_mapping
                    )

                projects[project_id] = ProjectMetrics(
                    project_id=project_id,
                    metrics=project_block,
                    epics=epics,
                )

            areas[area_id] = AreaMetrics(
                area_id=area_id,
                budget_minutes=budget,
                metrics=area_block,
                projects=projects,
            )

        return global_block, areas

    def _calculate_block(
        self,
        cards: list[CardSnapshot],
        size_mapping: dict[str, int] | None,
    ) -> MetricsBlock:
        """Calcula un MetricsBlock sobre un subconjunto de cards."""
        total = len(cards)

        # Cycle time: completed_at - entered_workflow_at
        cycle_times: list[float] = []
        for c in cards:
            if c.entered_workflow_at is not None and c.completed_at is not None:
                delta = (
                    c.completed_at.value - c.entered_workflow_at.value
                ).total_seconds() / 60.0
                cycle_times.append(delta)
        avg_ct = (
            sum(cycle_times) / len(cycle_times) if cycle_times else None
        )

        # Lead time: completed_at - created_at
        lead_times: list[float] = []
        for c in cards:
            delta = (
                c.completed_at.value - c.created_at.value
            ).total_seconds() / 60.0
            lead_times.append(delta)
        avg_lt = sum(lead_times) / len(lead_times) if lead_times else None

        # Consumed: sum of size_mapping[card.size]
        consumed = 0
        if size_mapping is not None:
            for c in cards:
                if c.size is not None and c.size.value in size_mapping:
                    consumed += size_mapping[c.size.value]

        # Calibration: estimated vs actual
        calibration: list[CalibrationEntry] = []
        if size_mapping is not None:
            for c in cards:
                if (
                    c.size is not None
                    and c.size.value in size_mapping
                    and c.actual_time_minutes > 0
                ):
                    calibration.append(
                        CalibrationEntry(
                            card_id=c.card_id,
                            estimated_minutes=size_mapping[c.size.value],
                            actual_minutes=c.actual_time_minutes,
                        )
                    )

        return MetricsBlock(
            total_cards_completed=total,
            avg_cycle_time_minutes=avg_ct,
            avg_lead_time_minutes=avg_lt,
            consumed_minutes=consumed,
            calibration_entries=calibration,
        )
