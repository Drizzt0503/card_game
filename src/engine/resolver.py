from ..domain.game_state import GameState
from ..effects.effect import Effect
from ..events.event import Event
from ..triggers.trigger import TriggerEngine


def remove_dead_minions(state: GameState) -> list[str]:
    events: list[str] = []
    for player in state.players:
        dead = [minion for minion in player.board if not minion.alive]
        for minion in dead:
            events.append(f"{minion.name} dies")
        player.board[:] = [minion for minion in player.board if minion.alive]
    return events


def remove_dead_minions_with_events(state: GameState) -> list[Event]:
    events: list[Event] = []
    for player in state.players:
        dead = [minion for minion in player.board if not minion.alive]
        for minion in dead:
            events.append(Event(
                "minion_died", source_player_id=player.player_id,
                source_id=minion.instance_id, card_id=minion.card_id,
                data={"minion": minion},
            ))
        player.board[:] = [minion for minion in player.board if minion.alive]
    return events


class EffectResolver:
    def __init__(self, trigger_engine: TriggerEngine | None = None):
        self.trigger_engine = trigger_engine or TriggerEngine()

    def resolve(self, state: GameState, effects: list[Effect]) -> list[Event]:
        queue = list(effects)
        events: list[Event] = []
        while queue:
            effect = queue.pop(0)
            emitted = effect.apply(state)
            events.extend(emitted)
            for event in emitted:
                queue.extend(self.trigger_engine.process(state, event))
            death_events = remove_dead_minions_with_events(state)
            events.extend(death_events)
            for event in death_events:
                queue.extend(self.trigger_engine.process(state, event))
        return events
