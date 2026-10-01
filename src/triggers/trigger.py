from abc import ABC, abstractmethod

from ..domain.game_state import GameState
from ..effects.effect import DrawEffect, Effect
from ..events.event import Event


class Trigger(ABC):
    @abstractmethod
    def create_effects(self, state: GameState, event: Event) -> list[Effect]:
        """Return follow-up effects when this trigger matches the event."""

    def matches(self, state: GameState, event: Event) -> bool:
        return False


class TriggerEngine:
    def process(self, state: GameState, event: Event) -> list[Effect]:
        effects: list[Effect] = []
        triggers = list(state.triggers)
        if event.event_type == "minion_summoned":
            triggers.append(BeastSummonedTrigger())
        if event.event_type == "healed":
            triggers.append(NorthshireClericTrigger())
        for trigger in triggers:
            if trigger.matches(state, event):
                effects.extend(trigger.create_effects(state, event))
        return effects


class BeastSummonedTrigger(Trigger):
    def matches(self, state: GameState, event: Event) -> bool:
        minion = event.data.get("minion")
        return event.event_type == "minion_summoned" and minion is not None and minion.tribe == "BEAST"

    def create_effects(self, state: GameState, event: Event) -> list[Effect]:
        player = state.player(event.source_player_id)
        count = sum(1 for minion in player.board if "draw_on_friendly_beast_summoned" in minion.trigger_ids)
        return [DrawEffect(player.player_id) for _ in range(count)]


class NorthshireClericTrigger(Trigger):
    def matches(self, state: GameState, event: Event) -> bool:
        return event.event_type == "healed" and event.data.get("target_kind") == "minion"

    def create_effects(self, state: GameState, event: Event) -> list[Effect]:
        player = state.player(event.target_player_id)
        count = sum(1 for minion in player.board
                    if "draw_on_friendly_minion_healed" in minion.trigger_ids)
        return [DrawEffect(player.player_id) for _ in range(count)]
