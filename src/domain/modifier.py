from dataclasses import dataclass
from enum import Enum


class ModifierLayer(str, Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    AURA = "aura"


@dataclass(frozen=True)
class StatModifier:
    attack: int = 0
    health: int = 0
    spell_power: int = 0
    layer: ModifierLayer = ModifierLayer.PERMANENT
    source_id: str | None = None
