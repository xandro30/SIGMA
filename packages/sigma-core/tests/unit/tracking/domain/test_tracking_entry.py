"""Unit tests para TrackingEntry aggregate."""
import pytest
from sigma_core.tracking.domain.aggregates.tracking_entry import TrackingEntry
from sigma_core.tracking.domain.value_objects.ids import TrackingEntryId
from sigma_core.tracking.domain.value_objects.entry_type import EntryType
from sigma_core.shared_kernel.value_objects import CardId, SpaceId, Timestamp


def _make_entry(**kwargs) -> TrackingEntry:
    defaults = dict(
        id=TrackingEntryId.generate(),
        space_id=SpaceId.generate(),
        card_id=CardId.generate(),
        area_id=None,
        project_id=None,
        epic_id=None,
        entry_type=EntryType.WORK,
        description="Implemented feature X",
        minutes=50,
        logged_at=Timestamp.now(),
    )
    defaults.update(kwargs)
    return TrackingEntry(**defaults)


def test_entry_stores_all_fields():
    e = _make_entry(minutes=75, description="Deep work")
    assert e.minutes == 75
    assert e.description == "Deep work"
    assert e.entry_type == EntryType.WORK


def test_entry_is_immutable():
    e = _make_entry()
    with pytest.raises(Exception):
        e.minutes = 999  # type: ignore[misc]


def test_entry_type_work_value():
    assert EntryType.WORK.value == "work"


def test_entry_without_card_is_valid():
    e = _make_entry(card_id=None)
    assert e.card_id is None


def test_tracking_entry_id_generates_unique():
    id1 = TrackingEntryId.generate()
    id2 = TrackingEntryId.generate()
    assert id1 != id2
