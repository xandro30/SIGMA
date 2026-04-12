"""Tests unit del MetricsCalculator."""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.metrics.domain.services.metrics_calculator import MetricsCalculator
from sigma_core.metrics.domain.value_objects import CardSnapshot
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId


MADRID = ZoneInfo("Europe/Madrid")


def _ts(day: int, hour: int = 12) -> Timestamp:
    return Timestamp(datetime(2026, 4, day, hour, 0, tzinfo=MADRID))


def _card(
    *,
    area_id: AreaId | None = None,
    project_id: ProjectId | None = None,
    epic_id: EpicId | None = None,
    size: CardSize | None = CardSize.M,
    actual_time: int = 0,
    created_day: int = 1,
    entered_day: int | None = 5,
    completed_day: int = 10,
) -> CardSnapshot:
    return CardSnapshot(
        card_id=CardId.generate(),
        area_id=area_id,
        project_id=project_id,
        epic_id=epic_id,
        size=size,
        actual_time_minutes=actual_time,
        created_at=_ts(created_day),
        entered_workflow_at=_ts(entered_day) if entered_day else None,
        completed_at=_ts(completed_day),
    )


SIZE_MAP = {"m": 120, "s": 60, "l": 240}
calculator = MetricsCalculator()


class TestCalculateBlockBasic:
    def test_caso_vacio(self):
        block = calculator._calculate_block([], SIZE_MAP)
        assert block.total_cards_completed == 0
        assert block.avg_cycle_time_minutes is None
        assert block.avg_lead_time_minutes is None
        assert block.consumed_minutes == 0
        assert block.calibration_entries == []

    def test_throughput_cuenta_todas(self):
        cards = [_card(), _card(), _card()]
        block = calculator._calculate_block(cards, SIZE_MAP)
        assert block.total_cards_completed == 3

    def test_cycle_time_media(self):
        # entered day 5 12:00, completed day 10 12:00 = 5 dias = 7200 min
        cards = [_card(entered_day=5, completed_day=10)]
        block = calculator._calculate_block(cards, SIZE_MAP)
        assert block.avg_cycle_time_minutes == pytest.approx(7200.0)

    def test_cycle_time_excluye_cards_sin_entered_workflow(self):
        cards = [
            _card(entered_day=5, completed_day=10),
            _card(entered_day=None, completed_day=10),
        ]
        block = calculator._calculate_block(cards, SIZE_MAP)
        # Solo la primera cuenta para cycle time
        assert block.avg_cycle_time_minutes == pytest.approx(7200.0)

    def test_lead_time_media(self):
        # created day 1 12:00, completed day 10 12:00 = 9 dias = 12960 min
        cards = [_card(created_day=1, completed_day=10)]
        block = calculator._calculate_block(cards, SIZE_MAP)
        assert block.avg_lead_time_minutes == pytest.approx(12960.0)

    def test_consumed_con_size_mapping(self):
        cards = [_card(size=CardSize.M), _card(size=CardSize.S)]
        block = calculator._calculate_block(cards, SIZE_MAP)
        assert block.consumed_minutes == 120 + 60

    def test_consumed_excluye_cards_sin_size(self):
        cards = [_card(size=None), _card(size=CardSize.M)]
        block = calculator._calculate_block(cards, SIZE_MAP)
        assert block.consumed_minutes == 120

    def test_consumed_sin_size_mapping_es_cero(self):
        block = calculator._calculate_block([_card()], None)
        assert block.consumed_minutes == 0

    def test_calibration_solo_con_size_y_actual_time(self):
        cards = [
            _card(size=CardSize.M, actual_time=95),
            _card(size=CardSize.S, actual_time=0),  # excluida
            _card(size=None, actual_time=50),  # excluida
        ]
        block = calculator._calculate_block(cards, SIZE_MAP)
        assert len(block.calibration_entries) == 1
        assert block.calibration_entries[0].estimated_minutes == 120
        assert block.calibration_entries[0].actual_minutes == 95


class TestCalculateHierarchy:
    def test_arbol_global_area_project_epic(self):
        area_a = AreaId.generate()
        project_x = ProjectId.generate()
        epic_1 = EpicId.generate()

        cards = [
            _card(area_id=area_a, project_id=project_x, epic_id=epic_1),
            _card(area_id=area_a, project_id=project_x, epic_id=None),
            _card(area_id=area_a, project_id=None),
            _card(area_id=None),  # solo global
        ]
        budgets = {area_a: 600}

        global_block, areas = calculator.calculate(cards, budgets, SIZE_MAP)

        # Global: 4 cards
        assert global_block.total_cards_completed == 4

        # Area A: 3 cards (excluye la sin area)
        assert area_a in areas
        assert areas[area_a].metrics.total_cards_completed == 3
        assert areas[area_a].budget_minutes == 600

        # Project X: 2 cards (excluye la sin project)
        assert project_x in areas[area_a].projects
        pm = areas[area_a].projects[project_x]
        assert pm.metrics.total_cards_completed == 2

        # Epic 1: 1 card
        assert epic_1 in pm.epics
        assert pm.epics[epic_1].total_cards_completed == 1

    def test_area_con_budget_sin_cards(self):
        area_a = AreaId.generate()
        area_b = AreaId.generate()

        cards = [_card(area_id=area_a)]
        budgets = {area_a: 600, area_b: 300}

        _, areas = calculator.calculate(cards, budgets, SIZE_MAP)

        assert area_b in areas
        assert areas[area_b].metrics.total_cards_completed == 0
        assert areas[area_b].budget_minutes == 300

    def test_area_sin_budget_con_cards(self):
        area_a = AreaId.generate()

        cards = [_card(area_id=area_a)]
        budgets = {}  # sin budget

        _, areas = calculator.calculate(cards, budgets, SIZE_MAP)

        assert area_a in areas
        assert areas[area_a].budget_minutes == 0
        assert areas[area_a].metrics.total_cards_completed == 1
