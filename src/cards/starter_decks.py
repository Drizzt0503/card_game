import random

from ..domain.card import CardInstance
from ..domain.deck import Deck
from .card_registry import CARD_DEFINITIONS

CLASSES = (
    "DRUID",
    "HUNTER",
    "MAGE",
    "PALADIN",
    "PRIEST",
    "ROGUE",
    "SHAMAN",
    "WARLOCK",
    "WARRIOR",
)


def max_copies(definition) -> int:
    return 1 if definition.rarity == "LEGENDARY" else 2


def build_random_deck(player_id: int, player_class: str, rng: random.Random) -> Deck:
    if player_class not in CLASSES:
        raise ValueError(f"Unknown class: {player_class}")

    pool = [
        definition
        for definition in CARD_DEFINITIONS
        if definition.collectible
        and definition.card_class in ("NEUTRAL", player_class)
    ]
    if not pool:
        raise ValueError(f"No cards available for class: {player_class}")

    cards = []
    counts = {definition.card_id: 0 for definition in pool}
    instance_id = player_id * 1000
    while len(cards) < 30:
        available = [
            definition for definition in pool
            if counts[definition.card_id] < max_copies(definition)
        ]
        if not available:
            raise ValueError("Card pool cannot build a 30-card deck")
        definition = rng.choice(available)
        cards.append(CardInstance(instance_id, definition))
        counts[definition.card_id] += 1
        instance_id += 1

    deck = Deck(cards)
    deck.shuffle(rng)
    return deck


def build_starter_deck(player_id: int, rng: random.Random) -> Deck:
    return build_random_deck(player_id, "MAGE", rng)
