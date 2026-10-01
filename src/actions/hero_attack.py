from dataclasses import dataclass

from .action import Action


@dataclass(frozen=True)
class HeroAttackAction(Action):
    target: str  # "hero" or "minion:<index>"
