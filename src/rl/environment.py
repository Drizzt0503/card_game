"""A minimal environment wrapper around the existing game engine.

This module is deliberately small.  It does not hide information, encode the
state, or define an action space yet.  An agent receives the complete
``GameState`` and passes one of the existing ``Action`` objects to ``step``.
"""

from dataclasses import dataclass
import random
from typing import Any

from ..actions.action import Action
from ..domain.game_state import GameState
from ..engine.game_engine import GameEngine
from ..session.game_session import new_game


@dataclass(frozen=True)
class EnvStep:
    """Result of applying one action in the environment."""

    state: GameState
    reward: float
    done: bool
    info: dict[str, Any]


class CardGameEnv:
    """Minimal RL-style wrapper for one card-game episode.

    By default, ``reset`` creates a new game using ``new_game``.  For tests or
    self-play experiments, callers can provide an existing ``GameState`` and
    optionally its matching ``GameEngine``.

    The environment is intentionally single-step and full-state for now:

    ``GameState -> agent chooses existing Action -> GameEngine.apply_action``

    No observation conversion or action encoding is performed yet.
    """

    def __init__(
        self,
        seed: int | None = None,
        player_classes: tuple[str, str] = ("MAGE", "MAGE"),
        reward_player_id: int = 0,
    ) -> None:
        if reward_player_id not in (0, 1):
            raise ValueError("reward_player_id must be 0 or 1")
        self.seed = seed
        self.player_classes = player_classes
        self.reward_player_id = reward_player_id
        self.state: GameState | None = None
        self.engine: GameEngine | None = None
        self.done = False

    def reset(
        self,
        seed: int | None = None,
        *,
        state: GameState | None = None,
        engine: GameEngine | None = None,
    ) -> GameState:
        """Start an episode and return the complete initial ``GameState``.

        Passing ``state`` is useful when a caller wants to construct a custom
        scenario.  Such a state is assumed to already be initialized; the
        environment will not draw opening hands or start a turn again.
        """

        if state is not None:
            self.state = state
            self.engine = engine or GameEngine(random.Random(seed))
        else:
            episode_seed = self.seed if seed is None else seed
            self.state, self.engine = new_game(
                seed=episode_seed,
                player_classes=self.player_classes,
            )

        self.done = self.state.game_over
        return self.state

    def step(self, action: Action) -> EnvStep:
        """Apply one existing game ``Action`` and return the updated state.

        Invalid actions are allowed to raise the engine's ``InvalidAction``
        exception.  This keeps the first environment version transparent and
        makes illegal-action handling an explicit future RL-layer decision.
        """

        if self.state is None or self.engine is None:
            raise RuntimeError("Call reset() before step()")
        if self.done:
            raise RuntimeError("The episode is already done; call reset()")

        acting_player_id = self.state.current_player_id
        logs = self.engine.apply_action(self.state, action)
        self.done = self.state.game_over
        reward = self._reward()
        info: dict[str, Any] = {
            "logs": logs,
            "acting_player_id": acting_player_id,
            "current_player_id": self.state.current_player_id,
        }
        if self.done:
            info["winner_id"] = self.state.winner_id

        return EnvStep(self.state, reward, self.done, info)

    def _reward(self) -> float:
        if not self.done or self.state is None:
            return 0.0
        if self.state.winner_id == self.reward_player_id:
            return 1.0
        return -1.0
