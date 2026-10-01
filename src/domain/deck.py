import random
from dataclasses import dataclass, field

from .card import CardInstance


@dataclass
class Deck:
    cards: list[CardInstance] = field(default_factory=list)

    def shuffle(self, rng: random.Random) -> None:
        rng.shuffle(self.cards)

    def draw(self) -> CardInstance | None:
        return self.cards.pop(0) if self.cards else None

    def __len__(self) -> int:
        return len(self.cards)
