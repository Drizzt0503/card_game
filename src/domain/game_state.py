from dataclasses import dataclass
from typing import Any

from .player_state import PlayerState


@dataclass
class GameState:
    players: list[PlayerState]
    current_player_id: int = 0
    turn_number: int = 1
    phase: str = "ACTION"
    winner_id: int | None = None
    triggers: list[Any] = None

    def __post_init__(self) -> None:
        if self.triggers is None:
            self.triggers = []

    def player(self, player_id: int) -> PlayerState:
        return self.players[player_id]

    @property
    def current_player(self) -> PlayerState:
        return self.player(self.current_player_id)

    @property
    def opponent(self) -> PlayerState:
        return self.player(1 - self.current_player_id)

    @property
    def game_over(self) -> bool:
        return self.winner_id is not None
