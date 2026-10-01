from dataclasses import dataclass


@dataclass(frozen=True)
class CardDefinition:
    card_id: str
    name: str
    cost: int
    attack: int
    health: int
    tribe: str | None = None
    card_class: str = "NEUTRAL"
    rarity: str = "BASIC"
    card_type: str = "MINION"
    collectible: bool = True
    description_zh: str = "白板手下。"
    description_en: str = "Vanilla minion."
    effect_id: str | None = None
    target_rule: str = "no_target"
    initial_statuses: tuple[str, ...] = ()
    spell_power: int = 0
    aura_ids: tuple[str, ...] = ()
    trigger_ids: tuple[str, ...] = ()
    attack_trigger_ids: tuple[str, ...] = ()


@dataclass
class CardInstance:
    instance_id: int
    definition: CardDefinition

    @property
    def card_id(self) -> str:
        return self.definition.card_id

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def cost(self) -> int:
        return self.definition.cost
