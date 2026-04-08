import os


class FirestoreConfig:
    def __init__(self, project_id: str | None = None) -> None:
        self.project_id = project_id or os.getenv("FIRESTORE_PROJECT_ID", "sigma-local")
        self.emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")

    @property
    def is_emulator(self) -> bool:
        return self.emulator_host is not None