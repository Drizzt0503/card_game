from __future__ import annotations

from collections.abc import Callable

from ..domain.game_state import GameState
from ..events.event import Event
from ..targeting.selector import TargetSelector
from ..targeting.target import TargetRef
from .effect import Effect


class CompositeEffect(Effect):
    def __init__(self, effects: list[Effect]):
        self.effects = effects

    def apply(self, state: GameState) -> list[Event]:
        events: list[Event] = []
        for effect in self.effects:
            events.extend(effect.apply(state))
        return events


class AreaEffect(Effect):
    def __init__(self, source_player_id: int, selector: TargetSelector,
                 effect_factory: Callable[[TargetRef], Effect]):
        self.source_player_id = source_player_id
        self.selector = selector
        self.effect_factory = effect_factory

    def apply(self, state: GameState) -> list[Event]:
        events: list[Event] = []
        for target in list(self.selector.select(state, self.source_player_id)):
            events.extend(self.effect_factory(target).apply(state))
        return events
