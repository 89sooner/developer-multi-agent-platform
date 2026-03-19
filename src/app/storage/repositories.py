from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class InMemoryStore:
    runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    traces: dict[str, dict[str, Any]] = field(default_factory=dict)
    feedback: dict[str, dict[str, Any]] = field(default_factory=dict)

    @staticmethod
    def now() -> str:
        return datetime.utcnow().isoformat() + "Z"


store = InMemoryStore()
