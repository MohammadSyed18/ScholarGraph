"""Revision-checked JSON snapshots with atomic publication on POSIX systems."""

from contextlib import contextmanager
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import tempfile
from .graph import EvidenceGraph


class RevisionConflict(ValueError):
    pass


class GraphStore:
    def __init__(self, path):
        self.path = Path(path)

    @contextmanager
    def _lock(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(self.path.suffix + ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def load(self):
        if not self.path.exists():
            return 0, EvidenceGraph()
        data = json.loads(self.path.read_text())
        if (
            data.get("version") != 1
            or type(data.get("revision")) is not int
            or data["revision"] < 1
        ):
            raise ValueError("invalid graph snapshot")
        return data["revision"], EvidenceGraph.from_data(data["graph"])

    def update(self, expected_revision, operation):
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("invalid revision")
        with self._lock():
            revision, graph = self.load()
            if revision != expected_revision:
                raise RevisionConflict("graph changed; reload before editing")
            candidate = deepcopy(graph)
            operation(candidate)
            # Revalidate references and confidence rather than trusting mutable dictionaries.
            checked = EvidenceGraph.from_data(candidate.export())
            payload = {
                "version": 1,
                "revision": revision + 1,
                "graph": checked.export(),
            }
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(
                    "w", dir=self.path.parent, delete=False
                ) as handle:
                    temporary = Path(handle.name)
                    json.dump(payload, handle, indent=2, allow_nan=False)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, self.path)
            finally:
                if temporary:
                    temporary.unlink(missing_ok=True)
            return revision + 1, checked
