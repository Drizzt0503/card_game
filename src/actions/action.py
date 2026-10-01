from dataclasses import dataclass

from ..targeting.target import TargetRef


class Action:
    """Marker base class for future agents and the CLI."""


@dataclass(frozen=True)
class PlayCardAction(Action):
    hand_index: int
    target: TargetRef | None = None


@dataclass(frozen=True)
class AttackAction(Action):
    attacker_index: int
    target: str  # "hero" or "minion:<index>"


@dataclass(frozen=True)
class EndTurnAction(Action):
    pass
