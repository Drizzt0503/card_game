import random

from ..cards.starter_decks import build_random_deck
from ..domain.game_state import GameState
from ..domain.hero import Hero
from ..domain.player_state import PlayerState
from ..engine.game_engine import GameEngine
from ..cards.card_registry import CARD_REGISTRY
from ..domain.card import CardInstance


def new_game(
    seed: int | None = None,
    player_classes: tuple[str, str] = ("MAGE", "MAGE"),
) -> tuple[GameState, GameEngine]:
    rng = random.Random(seed)
    players = [
        PlayerState(0, "Player 1", Hero(), build_random_deck(0, player_classes[0], rng), player_classes[0]),
        PlayerState(1, "Player 2", Hero(), build_random_deck(1, player_classes[1], rng), player_classes[1]),
    ]
    state = GameState(players)
    engine = GameEngine(rng)
    state.current_player_id = rng.randrange(2)
    engine.start(state)
    second_player_id = 1 - state.current_player_id
    players[second_player_id].hand.add(
        CardInstance(second_player_id * 100000 + 99999, CARD_REGISTRY["the_coin"])
    )
    return state, engine
