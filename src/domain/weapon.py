from dataclasses import dataclass


@dataclass
class Weapon:
    weapon_id: str
    name: str
    attack: int
    durability: int

    def lose_durability(self, amount: int = 1) -> None:
        self.durability = max(0, self.durability - amount)

    @property
    def destroyed(self) -> bool:
        return self.durability <= 0
