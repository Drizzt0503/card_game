from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain.game_state import GameState
from .target import TargetRef, TargetRule, TargetingService


class TargetSelector(ABC):
    @abstractmethod
    def select(self, state: GameState, source_player_id: int) -> list[TargetRef]:
        pass


class RuleSelector(TargetSelector):
    def __init__(self, rule: TargetRule):
        self.rule = rule

    def select(self, state: GameState, source_player_id: int) -> list[TargetRef]:
        return TargetingService().legal_targets(state, source_player_id, self.rule)


class EnemyMinionsSelector(RuleSelector):
    def __init__(self):
        super().__init__(TargetRule.ENEMY_MINION)


class EnemyCharactersSelector(RuleSelector):
    def __init__(self):
        super().__init__(TargetRule.ENEMY_CHARACTER)


class FriendlyCharactersSelector(RuleSelector):
    def __init__(self):
        super().__init__(TargetRule.FRIENDLY_CHARACTER)

