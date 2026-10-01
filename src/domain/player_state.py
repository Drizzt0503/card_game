from dataclasses import dataclass, field

from .deck import Deck
from .hand import Hand
from .hero import Hero
from .minion import Minion


@dataclass
class PlayerState:
    player_id: int
    name: str
    hero: Hero
    deck: Deck
    player_class: str = "NEUTRAL"
    hand: Hand = field(default_factory=Hand)
    board: list[Minion] = field(default_factory=list)
    mana: int = 0
    max_mana: int = 0

    def draw(self) -> bool:
        card = self.deck.draw()
        if card is None:
            return False
        self.hand.add(card)
        return True

    @property
    def alive(self) -> bool:
        return self.hero.alive
