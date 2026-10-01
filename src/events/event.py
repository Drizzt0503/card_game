from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Event:
    event_type: str
    source_player_id: int | None = None
    target_player_id: int | None = None
    source_id: int | None = None
    target_id: int | None = None
    amount: int | None = None
    card_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
