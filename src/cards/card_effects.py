from ..domain.card import CardInstance
from ..domain.game_state import GameState
from ..effects.effect import (BuffEffect, DamageAllCharactersEffect,
                              DamageAllOtherCharactersEffect,
                              DamageAllMinionsEffect, DamageOtherEnemyCharactersEffect,
                              DamageAllEnemyMinionsEffect, DamageEffect,
                              DamageThenDrawIfKilledEffect, DestroyEffect, DestroyWeaponEffect,
                              DiscardRandomEffect, DrawEffect, EquipWeaponEffect, FreezeAllEnemyMinionsEffect,
                              FreezeEffect, RandomChoiceEffect, RandomEnemyDamageEffect,
                              GainArmorEffect, HealAllFriendlyCharactersEffect, HealEffect,
                              DrawPerDamagedFriendlyMinionEffect, GrantChargeEffect,
                              ModifyManaEffect, ModifyWeaponEffect, SetHealthEffect,
                              MultiplyHealthEffect, SetAttackEffect, StealMinionEffect,
                              CopyRandomHandCardEffect, ReturnAllMinionsEffect, ReturnToHandEffect,
                              CorruptEffect,
                              TransformMinionEffect,
                              SummonEffect)
from ..domain.weapon import Weapon
from ..targeting.target import TargetKind, TargetRef, TargetRule, TargetingService
from .tokens import make_token
from .effect_registry import EffectBuilderRegistry


EFFECT_BUILDERS = EffectBuilderRegistry()


def build_play_effects(state: GameState, player_id: int, card: CardInstance,
                       target: TargetRef | None, rng):
    if card.definition.card_type == "MINION" and card.definition.effect_id is not None:
        return [SummonEffect(player_id, card)] + _build_card_effects(
            state, player_id, card, target, rng
        )
    return _build_card_effects(state, player_id, card, target, rng)


def _build_card_effects(state: GameState, player_id: int, card: CardInstance,
                        target: TargetRef | None, rng):
    definition = card.definition
    rule = TargetRule(definition.target_rule)
    if rule != TargetRule.NO_TARGET:
        if target is None or not TargetingService().is_legal_target(state, player_id, rule, target):
            raise ValueError("卡牌目標不合法")

    registered = EFFECT_BUILDERS.get(definition.effect_id)
    if registered is not None:
        return registered(state, player_id, card, target, rng)

    if definition.effect_id is None:
        return [SummonEffect(player_id, card)]
    if definition.effect_id == "arcane_intellect":
        return [DrawEffect(player_id, 2)]
    if definition.effect_id == "the_coin":
        return [ModifyManaEffect(player_id, 1)]
    if definition.effect_id == "fireball":
        return [_damage_from_target(target, 6, player_id)]
    if definition.effect_id == "frostbolt":
        return [_damage_from_target(target, 3, player_id),
                FreezeEffect(target.player_id, target.entity_id, target.kind.value)]
    if definition.effect_id == "mirror_image":
        base_id = _next_entity_id(state)
        return [
            SummonEffect(player_id, make_token("mirror_image", base_id)),
            SummonEffect(player_id, make_token("mirror_image", base_id + 1)),
        ]
    if definition.effect_id == "innervate":
        return [ModifyManaEffect(player_id, 1)]
    if definition.effect_id == "wild_growth":
        return [ModifyManaEffect(player_id, 1, maximum=True)]
    if definition.effect_id == "healing_touch":
        return [HealEffect(target.player_id, 8, target.kind.value, target.entity_id)]
    if definition.effect_id == "claw":
        return [BuffEffect(player_id, "hero", attack=2, temporary=True), GainArmorEffect(player_id, 2)]
    if definition.effect_id == "fiery_war_axe":
        return [EquipWeaponEffect(player_id, Weapon("fiery_war_axe", "Fiery War Axe", 3, 2))]
    if definition.effect_id == "arcanite_reaper":
        return [EquipWeaponEffect(player_id, Weapon("arcanite_reaper", "Arcanite Reaper", 5, 2))]
    if definition.effect_id == "execute":
        return [DestroyEffect(target.player_id, target.entity_id)]
    if definition.effect_id == "shield_block":
        return [GainArmorEffect(player_id, 5), DrawEffect(player_id)]
    if definition.effect_id == "arcane_shot":
        return [_damage_from_target(target, 2, player_id)]
    if definition.effect_id == "hunters_mark":
        return [SetHealthEffect(target.player_id, target.entity_id, 1)]
    if definition.effect_id == "tracking":
        return [DrawEffect(player_id)]
    if definition.effect_id == "holy_smite":
        return [_damage_from_target(target, 2, player_id)]
    if definition.effect_id == "power_word_shield":
        return [BuffEffect(target.player_id, "minion", target.entity_id, health=2),
                DrawEffect(player_id)]
    if definition.effect_id == "shadow_word_pain":
        return [DestroyEffect(target.player_id, target.entity_id)]
    if definition.effect_id == "holy_nova":
        return [DamageAllEnemyMinionsEffect(player_id, 2),
                HealAllFriendlyCharactersEffect(player_id, 2)]
    if definition.effect_id == "blessing_of_might":
        return [BuffEffect(target.player_id, "minion", target.entity_id, attack=3)]
    if definition.effect_id == "holy_light":
        return [HealEffect(target.player_id, 6, target.kind.value, target.entity_id)]
    if definition.effect_id == "consecration":
        return [DamageAllEnemyMinionsEffect(player_id, 2),
                _damage_from_target(TargetRef(TargetKind.HERO, 1 - player_id), 2, player_id)]
    if definition.effect_id == "hammer_of_wrath":
        return [_damage_from_target(target, 3, player_id), DrawEffect(player_id)]
    if definition.effect_id == "hand_of_protection":
        return [BuffEffect(target.player_id, "minion", target.entity_id, status="divine_shield")]
    if definition.effect_id == "deadly_poison":
        return [ModifyWeaponEffect(player_id, 2)]
    if definition.effect_id == "eviscerate":
        return [_damage_from_target(target, 2, player_id)]
    if definition.effect_id == "backstab":
        return [_damage_from_target(target, 2, player_id)]
    if definition.effect_id == "sinister_strike":
        return [DamageEffect(1 - player_id, 3, target_kind="hero", source_player_id=player_id)]
    if definition.effect_id == "acidic_swamp_ooze":
        return [DestroyWeaponEffect(1 - player_id)]
    if definition.effect_id == "elven_archer":
        return [_damage_from_target(target, 1, player_id)]
    if definition.effect_id == "darkscale_healer":
        return [HealAllFriendlyCharactersEffect(player_id, 2)]
    if definition.effect_id == "dragonling_mechanic":
        return [SummonEffect(player_id, make_token("mechanical_dragonling", _next_entity_id(state)))]
    if definition.effect_id in {"gnomish_inventor", "novice_engineer"}:
        return [DrawEffect(player_id)]
    if definition.effect_id == "ironforge_rifleman":
        return [_damage_from_target(target, 1, player_id)]
    if definition.effect_id == "nightblade":
        return [DamageEffect(1 - player_id, 3, target_kind="hero", source_player_id=player_id)]
    if definition.effect_id == "murloc_tidehunter":
        return [SummonEffect(player_id, make_token("murloc_raider", _next_entity_id(state)))]
    if definition.effect_id == "razorfen_hunter":
        return [SummonEffect(player_id, make_token("boar", _next_entity_id(state)))]
    if definition.effect_id == "shattered_sun_cleric":
        return [BuffEffect(target.player_id, "minion", target.entity_id, attack=1, health=1)]
    if definition.effect_id == "stormpike_commando":
        return [_damage_from_target(target, 2, player_id)]
    if definition.effect_id == "voodoo_doctor":
        return [HealEffect(target.player_id, 2, target.kind.value, target.entity_id)]
    if definition.effect_id == "frostwolf_warlord":
        amount = max(0, len(state.player(player_id).board) - 1)
        return [BuffEffect(player_id, "minion", card.instance_id, attack=amount, health=amount)]
    if definition.effect_id == "lightning_bolt":
        return [_damage_from_target(target, 3, player_id)]
    if definition.effect_id == "rockbiter_weapon":
        return [BuffEffect(player_id, "hero", attack=3, temporary=True)]
    if definition.effect_id == "frost_shock":
        return [_damage_from_target(target, 1, player_id),
                FreezeEffect(target.player_id, target.entity_id, target.kind.value)]
    if definition.effect_id == "bloodlust":
        return [BuffEffect(player_id, "minion", minion.instance_id, attack=3)
                for minion in state.player(player_id).board]
    if definition.effect_id == "feral_spirit":
        base_id = _next_entity_id(state)
        return [SummonEffect(player_id, make_token("spirit_wolf", base_id)),
                SummonEffect(player_id, make_token("spirit_wolf", base_id + 1))]
    if definition.effect_id == "mortal_coil":
        return [DamageThenDrawIfKilledEffect(player_id, target.player_id,
                                             target.entity_id, 1)]
    if definition.effect_id == "shadow_bolt":
        return [_damage_from_target(target, 4, player_id)]
    if definition.effect_id == "drain_life":
        return [_damage_from_target(target, 2, player_id),
                HealEffect(player_id, 2, "hero")]
    if definition.effect_id == "hellfire":
        return [DamageAllCharactersEffect(player_id, 3)]
    if definition.effect_id == "soulfire":
        return [_damage_from_target(target, 4, player_id), DiscardRandomEffect(player_id, rng)]
    if definition.effect_id == "arcane_missiles":
        return [RandomEnemyDamageEffect(player_id, 1, 3, rng)]
    if definition.effect_id == "arcane_explosion":
        return [DamageAllEnemyMinionsEffect(player_id, 1)]
    if definition.effect_id == "frost_nova":
        return [FreezeAllEnemyMinionsEffect(player_id)]
    if definition.effect_id == "polymorph":
        return [TransformMinionEffect(target.player_id, target.entity_id,
                                      make_token("sheep", target.entity_id).definition)]
    if definition.effect_id == "flamestrike":
        return [DamageAllEnemyMinionsEffect(player_id, 4)]
    if definition.effect_id == "multi_shot":
        return [RandomEnemyDamageEffect(player_id, 3, 2, rng, minions_only=True)]
    if definition.effect_id == "kill_command":
        return [_damage_from_target(target, 3, player_id)]
    if definition.effect_id == "animal_companion":
        base_id = _next_entity_id(state)
        return [RandomChoiceEffect([
            SummonEffect(player_id, make_token("huffer", base_id)),
            SummonEffect(player_id, make_token("misha", base_id)),
            SummonEffect(player_id, make_token("leokk", base_id)),
        ], rng)]
    if definition.effect_id == "houndmaster":
        return [BuffEffect(target.player_id, "minion", target.entity_id,
                           attack=2, health=2, status="taunt")]
    if definition.effect_id == "sap":
        return [ReturnToHandEffect(player_id, target.player_id, target.entity_id)]
    if definition.effect_id == "shiv":
        return [_damage_from_target(target, 1, player_id), DrawEffect(player_id)]
    if definition.effect_id == "fan_of_knives":
        return [DamageAllEnemyMinionsEffect(player_id, 1), DrawEffect(player_id)]
    if definition.effect_id == "assassinate":
        return [DestroyEffect(target.player_id, target.entity_id)]
    if definition.effect_id == "sprint":
        return [DrawEffect(player_id, 4)]
    if definition.effect_id == "vanish":
        return [ReturnAllMinionsEffect(player_id)]
    if definition.effect_id == "corruption":
        return [CorruptEffect(target.player_id, target.entity_id)]
    if definition.effect_id == "ancestral_healing":
        return [HealEffect(target.player_id, 99, "minion", target.entity_id),
                BuffEffect(target.player_id, "minion", target.entity_id, status="taunt")]
    if definition.effect_id == "hex":
        return [TransformMinionEffect(target.player_id, target.entity_id,
                                      make_token("frog", target.entity_id).definition)]
    if definition.effect_id == "totemic_might":
        return [BuffEffect(player_id, "minion", minion.instance_id, health=2)
                for minion in state.player(player_id).board]
    if definition.effect_id == "windfury":
        return [BuffEffect(target.player_id, "minion", target.entity_id, status="windfury")]
    if definition.effect_id == "dread_infernal":
        return [DamageAllOtherCharactersEffect(player_id, card.instance_id, 1)]
    if definition.effect_id == "divine_spirit":
        return [MultiplyHealthEffect(target.player_id, target.entity_id, 2)]
    if definition.effect_id == "shadow_word_death":
        return [DestroyEffect(target.player_id, target.entity_id)]
    if definition.effect_id == "holy_fire":
        return [_damage_from_target(target, 5, player_id), HealEffect(player_id, 5, "hero")]
    if definition.effect_id == "mind_control":
        return [StealMinionEffect(player_id, target.player_id, target.entity_id)]
    if definition.effect_id == "mind_vision":
        return [CopyRandomHandCardEffect(player_id, 1 - player_id, rng)]
    if definition.effect_id == "blessing_of_kings":
        return [BuffEffect(target.player_id, "minion", target.entity_id, attack=4, health=4)]
    if definition.effect_id == "humility":
        return [SetAttackEffect(target.player_id, target.entity_id, 1)]
    if definition.effect_id == "guardian_of_kings":
        return [HealEffect(player_id, 6, "hero")]
    if definition.effect_id == "lights_justice":
        return [EquipWeaponEffect(player_id, Weapon("lights_justice", "Light's Justice", 1, 4))]
    if definition.effect_id == "truesilver_champion":
        return [EquipWeaponEffect(player_id, Weapon("truesilver_champion", "Truesilver Champion", 4, 2))]
    if definition.effect_id == "moonfire":
        return [_damage_from_target(target, 1, player_id)]
    if definition.effect_id == "mark_of_the_wild":
        return [BuffEffect(target.player_id, "minion", target.entity_id,
                           attack=2, health=2, status="taunt")]
    if definition.effect_id == "savage_roar":
        effects = [BuffEffect(player_id, "hero", attack=2, temporary=True)]
        effects.extend(BuffEffect(player_id, "minion", minion.instance_id, attack=2)
                       for minion in state.player(player_id).board)
        return effects
    if definition.effect_id == "swipe":
        return [_damage_from_target(target, 4, player_id),
                DamageOtherEnemyCharactersEffect(player_id, target, 1)]
    if definition.effect_id == "starfire":
        return [_damage_from_target(target, 5, player_id), DrawEffect(player_id)]
    if definition.effect_id == "ironbark_protector":
        return [SummonEffect(player_id, card)]
    if definition.effect_id == "charge":
        return [BuffEffect(target.player_id, "minion", target.entity_id, attack=2),
                GrantChargeEffect(target.player_id, target.entity_id)]
    if definition.effect_id == "heroic_strike":
        return [BuffEffect(player_id, "hero", attack=4, temporary=True)]
    if definition.effect_id == "whirlwind":
        return [DamageAllMinionsEffect(player_id, 1)]
    if definition.effect_id == "cleave":
        return [RandomEnemyDamageEffect(player_id, 2, 2, rng, minions_only=True)]
    if definition.effect_id == "battle_rage":
        return [DrawPerDamagedFriendlyMinionEffect(player_id)]
    raise ValueError(f"Unsupported card effect: {definition.effect_id}")


def _damage_from_target(target: TargetRef, amount: int, source_player_id: int):
    return DamageEffect(target.player_id, amount, target_kind=target.kind.value,
                        target_id=target.entity_id, source_player_id=source_player_id,
                        spell_damage=True)


def _next_entity_id(state: GameState) -> int:
    ids = []
    for player in state.players:
        ids.extend(card.instance_id for card in player.hand.cards)
        ids.extend(minion.instance_id for minion in player.board)
    return max(ids, default=10000) + 1


# Data-driven builders for effects shared by many cards. More specialized
# cards can register their own builder without growing the dispatch function.
EFFECT_BUILDERS.register("arcane_intellect", lambda state, player_id, card, target, rng: [DrawEffect(player_id, 2)])
EFFECT_BUILDERS.register("tracking", lambda state, player_id, card, target, rng: [DrawEffect(player_id)])
EFFECT_BUILDERS.register("gnomish_inventor", lambda state, player_id, card, target, rng: [DrawEffect(player_id)])
EFFECT_BUILDERS.register("novice_engineer", lambda state, player_id, card, target, rng: [DrawEffect(player_id)])
EFFECT_BUILDERS.register("shield_block", lambda state, player_id, card, target, rng: [GainArmorEffect(player_id, 5), DrawEffect(player_id)])
