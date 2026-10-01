from dataclasses import dataclass, field

from .card import CardInstance


@dataclass
class Hand:
    cards: list[CardInstance] = field(default_factory=list)

    def add(self, card: CardInstance) -> None:
        self.cards.append(card)

    def remove(self, index: int) -> CardInstance:
        return self.cards.pop(index)

    def __len__(self) -> int:
        return len(self.cards)
