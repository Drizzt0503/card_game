from dataclasses import dataclass

from ..targeting.target import TargetRef
from .action import Action


@dataclass(frozen=True)
class HeroPowerAction(Action):
    target: TargetRef | None = None
