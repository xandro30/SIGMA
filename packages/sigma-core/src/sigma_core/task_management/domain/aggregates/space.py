from dataclasses import dataclass, field

from sigma_core.task_management.domain.errors import (
    InvalidWorkflowError, StateNotFoundError, DuplicateStateError,
)
from sigma_core.task_management.domain.value_objects import (
    SpaceId, SpaceName, WorkflowStateId, Timestamp,
)


BEGIN_STATE_ID = WorkflowStateId("00000000-0000-4000-a000-000000000001")
FINISH_STATE_ID = WorkflowStateId("00000000-0000-4000-a000-000000000002")

RESERVED_NAMES = {"begin", "finish"}


@dataclass(frozen=True)
class Transition:
    from_id: WorkflowStateId
    to_id: WorkflowStateId


@dataclass
class WorkflowState:
    id: WorkflowStateId
    name: str
    order: int


@dataclass
class Space:
    id: SpaceId
    name: SpaceName
    workflow_states: list[WorkflowState] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)


    def _all_state_ids(self) -> set[WorkflowStateId]:
        ids = {s.id for s in self.workflow_states}
        ids.add(BEGIN_STATE_ID)
        ids.add(FINISH_STATE_ID)
        return ids

    def _get_state(self, state_id: WorkflowStateId) -> WorkflowState | None:
        return next((s for s in self.workflow_states if s.id == state_id), None)

    def _state_exists(self, state_id: WorkflowStateId) -> bool:
        return state_id in self._all_state_ids()

    def is_valid_transition(
        self,
        from_id: WorkflowStateId,
        to_id: WorkflowStateId,
    ) -> bool:
        if not self.transitions:
            return True

        return Transition(from_id=from_id, to_id=to_id) in self.transitions

    def add_state(self, state: WorkflowState) -> None:
        if state.name.lower() in RESERVED_NAMES:
            raise InvalidWorkflowError(
                f"'{state.name}' es un nombre reservado del sistema"
            )
        if self._get_state(state.id) is not None:
            raise DuplicateStateError(state.id)

        self.workflow_states.append(state)
        self.workflow_states.sort(key=lambda s: s.order)
        self.updated_at = Timestamp.now()

    def remove_state(self, state_id: WorkflowStateId) -> None:
        if state_id in (BEGIN_STATE_ID, FINISH_STATE_ID):
            raise InvalidWorkflowError("No se puede eliminar BEGIN ni FINISH")
        if self._get_state(state_id) is None:
            raise StateNotFoundError(state_id)

        self.workflow_states = [
            s for s in self.workflow_states if s.id != state_id
        ]
        self.transitions = [
            t for t in self.transitions
            if t.from_id != state_id and t.to_id != state_id
        ]
        self.updated_at = Timestamp.now()

    def add_transition(
        self,
        from_id: WorkflowStateId,
        to_id: WorkflowStateId,
    ) -> None:
        if not self._state_exists(from_id):
            raise StateNotFoundError(from_id)
        if not self._state_exists(to_id):
            raise StateNotFoundError(to_id)
        if to_id == BEGIN_STATE_ID:
            raise InvalidWorkflowError("Ningún estado puede transicionar a BEGIN")
        if from_id == FINISH_STATE_ID:
            raise InvalidWorkflowError("FINISH no puede tener transiciones salientes")

        transition = Transition(from_id=from_id, to_id=to_id)
        if transition not in self.transitions:
            self.transitions.append(transition)
            self.updated_at = Timestamp.now()

    def remove_transition(
        self,
        from_id: WorkflowStateId,
        to_id: WorkflowStateId,
    ) -> None:
        self.transitions = [
            t for t in self.transitions
            if not (t.from_id == from_id and t.to_id == to_id)
        ]
        self.updated_at = Timestamp.now()