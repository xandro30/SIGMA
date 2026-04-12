from __future__ import annotations

import urllib.parse
import uuid
from dataclasses import dataclass


# ── Identifier helpers ────────────────────────────────────────────


def _validate_uuid4(value: str, class_name: str) -> None:
    try:
        parsed = uuid.UUID(value, version=4)
        if str(parsed) != value:
            raise ValueError()
    except ValueError:
        raise ValueError(f"{class_name} inválido: {value!r} — debe ser un UUID v4")


# ── Identifiers propios del BC ────────────────────────────────────


@dataclass(frozen=True)
class WorkflowStateId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "WorkflowStateId")

    @classmethod
    def generate(cls) -> WorkflowStateId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class ProjectId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "ProjectId")

    @classmethod
    def generate(cls) -> ProjectId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class EpicId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "EpicId")

    @classmethod
    def generate(cls) -> EpicId:
        return cls(str(uuid.uuid4()))


# ── Strings con invariantes ───────────────────────────────────────


@dataclass(frozen=True)
class CardTitle:
    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("CardTitle no puede estar vacío")
        if len(stripped) > 255:
            raise ValueError("CardTitle no puede superar 255 caracteres")
        object.__setattr__(self, "value", stripped)


@dataclass(frozen=True)
class SpaceName:
    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("SpaceName no puede estar vacío")
        if len(stripped) > 100:
            raise ValueError("SpaceName no puede superar 100 caracteres")
        object.__setattr__(self, "value", stripped)


# ── Url ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Url:
    value: str

    def __post_init__(self) -> None:
        try:
            result = urllib.parse.urlparse(self.value)
            if result.scheme not in ("http", "https") or not result.netloc:
                raise ValueError()
        except Exception:
            raise ValueError(f"URL inválida: {self.value!r}")


# ── ChecklistItem ─────────────────────────────────────────────────


@dataclass(frozen=True)
class ChecklistItem:
    text: str
    done: bool = False

    def __post_init__(self) -> None:
        stripped = self.text.strip()
        if not stripped:
            raise ValueError("ChecklistItem.text no puede estar vacío")
        if len(stripped) > 500:
            raise ValueError("ChecklistItem.text no puede superar 500 caracteres")
        object.__setattr__(self, "text", stripped)

    def complete(self) -> ChecklistItem:
        return ChecklistItem(text=self.text, done=True)

    def reopen(self) -> ChecklistItem:
        return ChecklistItem(text=self.text, done=False)
