"""RL integration layer for the card game.

The first version intentionally exposes the complete domain ``GameState``.
Observation encoding and a fixed action space can be added here later without
changing the game engine.
"""

from .environment import CardGameEnv, EnvStep

__all__ = ["CardGameEnv", "EnvStep"]
