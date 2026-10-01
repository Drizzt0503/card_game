from dataclasses import dataclass, field
from .weapon import Weapon


@dataclass
class Hero:
    hp: int = 30
    max_hp: int = 30
    armor: int = 0
    temporary_attack: int = 0
    weapon: Weapon | None = None
    hero_power_used: bool = False
    hero_attack_used: bool = False
    statuses: set[str] = field(default_factory=set)

    @property
    def attack(self) -> int:
        return (self.weapon.attack if self.weapon else 0) + self.temporary_attack

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        absorbed = min(self.armor, amount)
        self.armor -= absorbed
        self.hp = max(0, self.hp - (amount - absorbed))
