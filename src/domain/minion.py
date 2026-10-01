from dataclasses import dataclass, field


@dataclass
class Minion:
    instance_id: int
    card_id: str
    name: str
    attack: int
    hp: int
    max_hp: int
    can_attack: bool = False
    statuses: set[str] = field(default_factory=set)
    buff_attack: int = 0
    buff_health: int = 0
    aura_attack: int = 0
    aura_health: int = 0
    tribe: str | None = None
    spell_power: int = 0
    aura_ids: tuple[str, ...] = ()
    trigger_ids: tuple[str, ...] = ()
    attack_trigger_ids: tuple[str, ...] = ()
    attacks_remaining: int = 1

    def __post_init__(self) -> None:
        self._base_attack = self.attack
        self._base_max_hp = self.max_hp

    @classmethod
    def from_card(cls, card, can_attack: bool = False) -> "Minion":
        return cls(card.instance_id, card.card_id, card.name, card.definition.attack,
                   card.definition.health, card.definition.health, can_attack,
                   set(card.definition.initial_statuses), tribe=card.definition.tribe,
                   spell_power=card.definition.spell_power,
                   aura_ids=card.definition.aura_ids,
                   trigger_ids=card.definition.trigger_ids,
                   attack_trigger_ids=card.definition.attack_trigger_ids)

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
