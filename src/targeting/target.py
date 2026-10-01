from dataclasses import dataclass
from enum import Enum

from ..domain.game_state import GameState


class TargetKind(str, Enum):
    HERO = "hero"
    MINION = "minion"


class TargetRule(str, Enum):
    NO_TARGET = "no_target"
    SELF_HERO = "self_hero"
    ENEMY_HERO = "enemy_hero"
    FRIENDLY_MINION = "friendly_minion"
    ENEMY_MINION = "enemy_minion"
    ANY_MINION = "any_minion"
    FRIENDLY_CHARACTER = "friendly_character"
    ENEMY_CHARACTER = "enemy_character"
    ANY_CHARACTER = "any_character"
    ALL_FRIENDLY_MINIONS = "all_friendly_minions"
    ALL_ENEMY_MINIONS = "all_enemy_minions"
    ALL_CHARACTERS = "all_characters"
    DAMAGED_ENEMY_MINION = "damaged_enemy_minion"
    ENEMY_MINION_ATTACK_LE_3 = "enemy_minion_attack_le_3"
    UNDAMAGED_ENEMY_MINION = "undamaged_enemy_minion"
    ENEMY_MINION_ATTACK_GE_5 = "enemy_minion_attack_ge_5"


@dataclass(frozen=True)
class TargetRef:
    kind: TargetKind
    player_id: int
    entity_id: int | None = None


class TargetingService:
    def legal_targets(
        self,
        state: GameState,
        source_player_id: int,
        rule: TargetRule,
    ) -> list[TargetRef]:
        source = state.player(source_player_id)
        enemy = state.player(1 - source_player_id)

        friendly_hero = TargetRef(TargetKind.HERO, source_player_id)
        enemy_hero = TargetRef(TargetKind.HERO, enemy.player_id)
        friendly_minions = [
            TargetRef(TargetKind.MINION, source_player_id, minion.instance_id)
            for minion in source.board
        ]
        enemy_minions = [
            TargetRef(TargetKind.MINION, enemy.player_id, minion.instance_id)
            for minion in enemy.board
        ]

        if rule == TargetRule.NO_TARGET:
            return []
        if rule == TargetRule.SELF_HERO:
            return [friendly_hero]
        if rule == TargetRule.ENEMY_HERO:
            return [enemy_hero]
        if rule == TargetRule.FRIENDLY_MINION:
            return friendly_minions
        if rule == TargetRule.ENEMY_MINION:
            return enemy_minions
        if rule == TargetRule.ANY_MINION:
            return friendly_minions + enemy_minions
        if rule == TargetRule.FRIENDLY_CHARACTER:
            return [friendly_hero] + friendly_minions
        if rule == TargetRule.ENEMY_CHARACTER:
            return [enemy_hero] + enemy_minions
        if rule == TargetRule.ANY_CHARACTER:
            return [friendly_hero, enemy_hero] + friendly_minions + enemy_minions
        if rule == TargetRule.ALL_FRIENDLY_MINIONS:
            return friendly_minions
        if rule == TargetRule.ALL_ENEMY_MINIONS:
            return enemy_minions
        if rule == TargetRule.ALL_CHARACTERS:
            return [friendly_hero, enemy_hero] + friendly_minions + enemy_minions
        if rule == TargetRule.DAMAGED_ENEMY_MINION:
            return [
                target for target in enemy_minions
                if next(m for m in enemy.board if m.instance_id == target.entity_id).hp
                < next(m for m in enemy.board if m.instance_id == target.entity_id).max_hp
            ]
        if rule == TargetRule.ENEMY_MINION_ATTACK_LE_3:
            return [
                target for target in enemy_minions
                if next(m for m in enemy.board if m.instance_id == target.entity_id).attack <= 3
            ]
        if rule == TargetRule.UNDAMAGED_ENEMY_MINION:
            return [
                target for target in enemy_minions
                if next(m for m in enemy.board if m.instance_id == target.entity_id).hp
                == next(m for m in enemy.board if m.instance_id == target.entity_id).max_hp
            ]
        if rule == TargetRule.ENEMY_MINION_ATTACK_GE_5:
            return [
                target for target in enemy_minions
                if next(m for m in enemy.board if m.instance_id == target.entity_id).attack >= 5
            ]
        raise ValueError(f"Unknown target rule: {rule}")

    def is_legal_target(
        self,
        state: GameState,
        source_player_id: int,
        rule: TargetRule,
        target: TargetRef,
    ) -> bool:
        return target in self.legal_targets(state, source_player_id, rule)
