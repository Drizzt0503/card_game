from abc import ABC, abstractmethod

from ..actions.action import Action
from ..domain.game_state import GameState


class AIAgent(ABC):
    """Common interface for rule-based and future RL agents."""

    @abstractmethod
    def choose_action(self, state: GameState) -> Action:
        """Choose one legal action candidate for the current state."""
