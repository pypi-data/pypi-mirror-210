from __future__ import annotations

import os
from typing import BinaryIO
from typing import TYPE_CHECKING


class FileSystemBackend:
    """An artifact backend for file systems.

    Example:
       .. code-block:: python

          import optuna
          from optuna_dashboard.artifact import upload_artifact
          from optuna_dashboard.artifact.file_system import FileSystemBackend

          artifact_backend = FileSystemBackend("./artifacts")

          def objective(trial: optuna.Trial) -> float:
              ... = trial.suggest_float("x", -10, 10)
              file_path = generate_example_png(...)
              upload_artifact(artifact_backend, trial, file_path)
              return ...
    """

    def __init__(self, base_path: str) -> None:
        self._base_path = base_path

    def open(self, artifact_id: str) -> BinaryIO:
        filepath = os.path.join(self._base_path, artifact_id)
        return open(filepath, "rb")

    def write(self, artifact_id: str, content_body: BinaryIO) -> None:
        filepath = os.path.join(self._base_path, artifact_id)
        with open(filepath, "wb") as f:
            f.write(content_body.read())

    def remove(self, artifact_id: str) -> None:
        filepath = os.path.join(self._base_path, artifact_id)
        os.remove(filepath)


if TYPE_CHECKING:
    # A mypy-runtime assertion to ensure that LocalArtifactBackend
    # implements all abstract methods in ArtifactBackendProtocol.
    from .protocol import ArtifactBackend

    _: ArtifactBackend = FileSystemBackend("")
