from dataclasses import dataclass

from ..cards.tokens import make_token
from ..domain.game_state import GameState
from ..domain.weapon import Weapon
from ..effects.effect import (
    DamageEffect, DrawEffect, EquipWeaponEffect, GainArmorEffect,
    HealEffect, RandomChoiceEffect, SummonEffect, TemporaryAttackEffect,
)
from ..targeting.target import TargetKind, TargetRef, TargetRule, TargetingService


@dataclass(frozen=True)
class HeroPowerDefinition:
    power_id: str
    name: str
    cost: int
    target_rule: TargetRule


HERO_POWERS = {
    "DRUID": HeroPowerDefinition("shapeshift", "Shapeshift", 2, TargetRule.NO_TARGET),
    "HUNTER": HeroPowerDefinition("steady_shot", "Steady Shot", 2, TargetRule.ENEMY_HERO),
    "MAGE": HeroPowerDefinition("fireblast", "Fireblast", 2, TargetRule.ANY_CHARACTER),
    "PALADIN": HeroPowerDefinition("reinforce", "Reinforce", 2, TargetRule.NO_TARGET),
    "PRIEST": HeroPowerDefinition("lesser_heal", "Lesser Heal", 2, TargetRule.FRIENDLY_CHARACTER),
    "ROGUE": HeroPowerDefinition("dagger_mastery", "Dagger Mastery", 2, TargetRule.NO_TARGET),
    "SHAMAN": HeroPowerDefinition("totemic_call", "Totemic Call", 2, TargetRule.NO_TARGET),
    "WARLOCK": HeroPowerDefinition("life_tap", "Life Tap", 2, TargetRule.NO_TARGET),
    "WARRIOR": HeroPowerDefinition("armor_up", "Armor Up!", 2, TargetRule.NO_TARGET),
}


def hero_power_for(player_class: str) -> HeroPowerDefinition:
    try:
        return HERO_POWERS[player_class]
    except KeyError:
        raise ValueError(f"No hero power for class: {player_class}") from None


def build_effects(state: GameState, player_id: int, target: TargetRef | None, rng):
    player = state.player(player_id)
    definition = hero_power_for(player.player_class)
    if definition.target_rule != TargetRule.NO_TARGET:
        if target is None or not TargetingService().is_legal_target(
            state, player_id, definition.target_rule, target
        ):
            raise ValueError("Hero power target is illegal")

    if definition.power_id == "shapeshift":
        return [TemporaryAttackEffect(player_id, 1), GainArmorEffect(player_id, 1)]
    if definition.power_id == "steady_shot":
        return [DamageEffect(target.player_id, 2, target_kind="hero", source_player_id=player_id)]
    if definition.power_id == "fireblast":
        return [DamageEffect(target.player_id, 1, target_kind=target.kind.value,
                             target_id=target.entity_id, source_player_id=player_id)]
    if definition.power_id == "reinforce":
        return [SummonEffect(player_id, make_token("silver_hand_recruit", _next_entity_id(state)))]
    if definition.power_id == "lesser_heal":
        return [HealEffect(target.player_id, 2, target.kind.value, target.entity_id)]
    if definition.power_id == "dagger_mastery":
        return [EquipWeaponEffect(player_id, Weapon("basic_dagger", "Dagger", 1, 2))]
    if definition.power_id == "totemic_call":
        base_id = _next_entity_id(state)
        tokens = [
            make_token("healing_totem", base_id),
            make_token("stoneclaw_totem", base_id + 1),
            make_token("searing_totem", base_id + 2),
            make_token("wrath_of_air_totem", base_id + 3),
        ]
        return [RandomChoiceEffect([SummonEffect(player_id, token) for token in tokens], rng)]
    if definition.power_id == "life_tap":
        return [DrawEffect(player_id), DamageEffect(player_id, 2, target_kind="hero", source_player_id=player_id)]
    if definition.power_id == "armor_up":
        return [GainArmorEffect(player_id, 2)]
    raise ValueError(f"Unsupported hero power: {definition.power_id}")


def _next_entity_id(state: GameState) -> int:
    ids = []
    for player in state.players:
        ids.extend(card.instance_id for card in player.hand.cards)
        ids.extend(minion.instance_id for minion in player.board)
    return max(ids, default=10000) + 1
