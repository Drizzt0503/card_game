from abc import ABC, abstractmethod

from ..domain.card import CardInstance
from ..domain.game_state import GameState
from ..domain.minion import Minion
from ..domain.weapon import Weapon
from ..events.event import Event
from ..targeting.target import TargetKind, TargetRef


class Effect(ABC):
    @abstractmethod
    def apply(self, state: GameState) -> list[Event]:
        """Modify state and return facts about the modification."""


class SummonEffect(Effect):
    def __init__(self, player_id: int, card: CardInstance):
        self.player_id = player_id
        self.card = card

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.player_id)
        if len(player.board) >= 7:
            return []
        minion = Minion.from_card(self.card)
        has_tundra_rhino = any("grant_beast_charge" in m.aura_ids for m in player.board)
        minion.can_attack = "charge" in minion.statuses or (
            has_tundra_rhino and minion.tribe == "BEAST"
        ) or any(
            "grant_small_minion_charge" in m.aura_ids and minion.attack <= 3
            for m in player.board
        )
        minion.attacks_remaining = 2 if "windfury" in minion.statuses else 1
        player.board.append(minion)
        return [Event(
            event_type="minion_summoned",
            source_player_id=self.player_id,
            source_id=minion.instance_id,
            card_id=minion.card_id,
            data={"minion": minion},
        )]


class DamageEffect(Effect):
    def __init__(
        self,
        target_player_id: int,
        amount: int,
        *,
        target_kind: str,
        target_id: int | None = None,
        source_player_id: int | None = None,
        source_id: int | None = None,
        spell_damage: bool = False,
    ):
        self.target_player_id = target_player_id
        self.amount = amount
        self.target_kind = target_kind
        self.target_id = target_id
        self.source_player_id = source_player_id
        self.source_id = source_id
        self.spell_damage = spell_damage

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.target_player_id)
        amount = self.amount
        if self.spell_damage and self.source_player_id is not None:
            amount += sum(
                1 for minion in state.player(self.source_player_id).board
                if minion.spell_power
            )
        if self.target_kind == "hero":
            if "divine_shield" in player.hero.statuses:
                player.hero.statuses.remove("divine_shield")
            else:
                player.hero.take_damage(amount)
        elif self.target_kind == "minion":
            minion = next(
                (m for m in player.board if m.instance_id == self.target_id),
                None,
            )
            if minion is None:
                return []
            if "divine_shield" in minion.statuses:
                minion.statuses.remove("divine_shield")
            else:
                minion.take_damage(amount)
        else:
            raise ValueError(f"Unknown damage target kind: {self.target_kind}")
        return [Event(
            event_type="damage_dealt",
            source_player_id=self.source_player_id,
            target_player_id=self.target_player_id,
            source_id=self.source_id,
            target_id=self.target_id,
            amount=amount,
            data={"target_kind": self.target_kind},
        )]


class DrawEffect(Effect):
    def __init__(self, player_id: int, amount: int = 1):
        self.player_id = player_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.player_id)
        events = []
        for _ in range(self.amount):
            card = player.deck.draw()
            if card is None:
                break
            player.hand.add(card)
            events.append(Event(
                event_type="card_drawn",
                target_player_id=self.player_id,
                card_id=card.card_id,
            ))
        return events


class HealEffect(Effect):
    def __init__(self, target_player_id: int, amount: int, target_kind: str, target_id: int | None = None):
        self.target_player_id = target_player_id
        self.amount = amount
        self.target_kind = target_kind
        self.target_id = target_id

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.target_player_id)
        if self.target_kind == "hero":
            before = player.hero.hp
            player.hero.hp = min(player.hero.max_hp, player.hero.hp + self.amount)
            healed = player.hero.hp - before
        elif self.target_kind == "minion":
            minion = next((m for m in player.board if m.instance_id == self.target_id), None)
            if minion is None:
                return []
            before = minion.hp
            minion.hp = min(minion.max_hp, minion.hp + self.amount)
            healed = minion.hp - before
        else:
            raise ValueError(f"Unknown heal target kind: {self.target_kind}")
        return [Event("healed", target_player_id=self.target_player_id,
                      target_id=self.target_id, amount=healed,
                      data={"target_kind": self.target_kind})]


class GainArmorEffect(Effect):
    def __init__(self, player_id: int, amount: int):
        self.player_id = player_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        state.player(self.player_id).hero.armor += self.amount
        return [Event("armor_gained", target_player_id=self.player_id, amount=self.amount)]


class TemporaryAttackEffect(Effect):
    def __init__(self, player_id: int, amount: int):
        self.player_id = player_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        state.player(self.player_id).hero.temporary_attack += self.amount
        return [Event("temporary_attack_gained", target_player_id=self.player_id, amount=self.amount)]


class EquipWeaponEffect(Effect):
    def __init__(self, player_id: int, weapon: Weapon):
        self.player_id = player_id
        self.weapon = weapon

    def apply(self, state: GameState) -> list[Event]:
        hero = state.player(self.player_id).hero
        hero.weapon = self.weapon
        hero.hero_attack_used = False
        return [Event("weapon_equipped", target_player_id=self.player_id,
                      amount=self.weapon.attack,
                      data={"weapon_id": self.weapon.weapon_id})]


class ModifyWeaponEffect(Effect):
    def __init__(self, player_id: int, attack: int):
        self.player_id = player_id
        self.attack = attack

    def apply(self, state: GameState) -> list[Event]:
        weapon = state.player(self.player_id).hero.weapon
        if weapon is None:
            return []
        weapon.attack += self.attack
        return [Event("weapon_modified", target_player_id=self.player_id,
                      amount=self.attack)]


class DestroyWeaponEffect(Effect):
    def __init__(self, player_id: int):
        self.player_id = player_id

    def apply(self, state: GameState) -> list[Event]:
        hero = state.player(self.player_id).hero
        if hero.weapon is None:
            return []
        weapon_id = hero.weapon.weapon_id
        hero.weapon = None
        return [Event("weapon_destroyed", target_player_id=self.player_id,
                      data={"weapon_id": weapon_id})]


class DamageAllCharactersEffect(Effect):
    def __init__(self, source_player_id: int, amount: int):
        self.source_player_id = source_player_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        for player in state.players:
            DamageEffect(
                player.player_id, self.amount, target_kind="hero",
                source_player_id=self.source_player_id, spell_damage=True,
            ).apply(state)
            for minion in list(player.board):
                DamageEffect(
                    player.player_id, self.amount, target_kind="minion",
                    target_id=minion.instance_id,
                    source_player_id=self.source_player_id, spell_damage=True,
                ).apply(state)
        return [Event("damage_all_characters", source_player_id=self.source_player_id,
                      amount=self.amount)]


class DamageAllOtherCharactersEffect(Effect):
    def __init__(self, source_player_id: int, source_minion_id: int, amount: int):
        self.source_player_id = source_player_id
        self.source_minion_id = source_minion_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        for player in state.players:
            DamageEffect(player.player_id, self.amount, target_kind="hero",
                         source_player_id=self.source_player_id,
                         spell_damage=True).apply(state)
            for minion in list(player.board):
                if player.player_id == self.source_player_id and minion.instance_id == self.source_minion_id:
                    continue
                DamageEffect(player.player_id, self.amount, target_kind="minion",
                             target_id=minion.instance_id,
                             source_player_id=self.source_player_id,
                             spell_damage=True).apply(state)
        return [Event("damage_all_other_characters", source_player_id=self.source_player_id,
                      amount=self.amount)]


class DamageAllMinionsEffect(Effect):
    def __init__(self, source_player_id: int, amount: int):
        self.source_player_id = source_player_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        for player in state.players:
            for minion in list(player.board):
                DamageEffect(player.player_id, self.amount, target_kind="minion",
                             target_id=minion.instance_id,
                             source_player_id=self.source_player_id).apply(state)
        return [Event("damage_all_minions", source_player_id=self.source_player_id,
                      amount=self.amount)]


class DamageOtherEnemyCharactersEffect(Effect):
    def __init__(self, source_player_id: int, primary_target: TargetRef, amount: int):
        self.source_player_id = source_player_id
        self.primary_target = primary_target
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        enemy = state.player(1 - self.source_player_id)
        events: list[Event] = []
        targets = [TargetRef(TargetKind.HERO, enemy.player_id)] + [
            TargetRef(TargetKind.MINION, enemy.player_id, m.instance_id)
            for m in enemy.board
        ]
        for target in targets:
            if target == self.primary_target:
                continue
            events.extend(DamageEffect(
                target.player_id, self.amount, target_kind=target.kind.value,
                target_id=target.entity_id, source_player_id=self.source_player_id,
                spell_damage=True,
            ).apply(state))
        return events


class DrawPerDamagedFriendlyMinionEffect(Effect):
    def __init__(self, player_id: int):
        self.player_id = player_id

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.player_id)
        amount = sum(1 for m in player.board if m.hp < m.max_hp)
        if player.hero.hp < player.hero.max_hp:
            amount += 1
        return DrawEffect(self.player_id, amount).apply(state)


class GrantChargeEffect(Effect):
    def __init__(self, player_id: int, target_id: int):
        self.player_id = player_id
        self.target_id = target_id

    def apply(self, state: GameState) -> list[Event]:
        minion = next((m for m in state.player(self.player_id).board
                       if m.instance_id == self.target_id), None)
        if minion is None:
            return []
        minion.statuses.add("charge")
        minion.can_attack = True
        minion.attacks_remaining = 2 if "windfury" in minion.statuses else 1
        return [Event("charge_granted", target_player_id=self.player_id,
                      target_id=self.target_id)]


class SetAttackEffect(Effect):
    def __init__(self, target_player_id: int, target_id: int, attack: int):
        self.target_player_id = target_player_id
        self.target_id = target_id
        self.attack = attack

    def apply(self, state: GameState) -> list[Event]:
        minion = next((m for m in state.player(self.target_player_id).board
                       if m.instance_id == self.target_id), None)
        if minion is None:
            return []
        minion._base_attack = self.attack
        minion.attack = self.attack + minion.buff_attack + minion.aura_attack
        return [Event("attack_set", target_player_id=self.target_player_id,
                      target_id=self.target_id, amount=self.attack)]


class MultiplyHealthEffect(Effect):
    def __init__(self, target_player_id: int, target_id: int, multiplier: int):
        self.target_player_id = target_player_id
        self.target_id = target_id
        self.multiplier = multiplier

    def apply(self, state: GameState) -> list[Event]:
        minion = next((m for m in state.player(self.target_player_id).board
                       if m.instance_id == self.target_id), None)
        if minion is None:
            return []
        old_health = minion.max_hp
        minion._base_max_hp *= self.multiplier
        minion.max_hp = minion._base_max_hp + minion.buff_health + minion.aura_health
        minion.hp += old_health
        return [Event("health_multiplied", target_player_id=self.target_player_id,
                      target_id=self.target_id, amount=self.multiplier)]


class StealMinionEffect(Effect):
    def __init__(self, source_player_id: int, target_player_id: int, target_id: int):
        self.source_player_id = source_player_id
        self.target_player_id = target_player_id
        self.target_id = target_id

    def apply(self, state: GameState) -> list[Event]:
        source = state.player(self.source_player_id)
        enemy = state.player(self.target_player_id)
        if len(source.board) >= 7:
            return []
        for index, minion in enumerate(enemy.board):
            if minion.instance_id == self.target_id:
                source.board.append(enemy.board.pop(index))
                return [Event("minion_stolen", source_player_id=self.source_player_id,
                              target_id=self.target_id)]
        return []


class CopyRandomHandCardEffect(Effect):
    def __init__(self, source_player_id: int, target_player_id: int, rng):
        self.source_player_id = source_player_id
        self.target_player_id = target_player_id
        self.rng = rng

    def apply(self, state: GameState) -> list[Event]:
        enemy_hand = state.player(self.target_player_id).hand.cards
        if not enemy_hand:
            return []
        card = self.rng.choice(enemy_hand)
        source = state.player(self.source_player_id)
        source.hand.add(CardInstance(card.instance_id + 100000, card.definition))
        return [Event("card_copied", target_player_id=self.source_player_id,
                      card_id=card.card_id)]


class ReturnToHandEffect(Effect):
    def __init__(self, source_player_id: int, target_player_id: int, target_id: int):
        self.source_player_id = source_player_id
        self.target_player_id = target_player_id
        self.target_id = target_id

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.target_player_id)
        for index, minion in enumerate(player.board):
            if minion.instance_id == self.target_id:
                from ..cards.card_registry import CARD_REGISTRY
                from ..cards.tokens import TOKEN_DEFINITIONS
                definition = CARD_REGISTRY.get(minion.card_id) or TOKEN_DEFINITIONS.get(minion.card_id)
                if definition is None:
                    return []
                player.board.pop(index)
                player.hand.add(CardInstance(minion.instance_id, definition))
                return [Event("minion_returned", source_player_id=self.source_player_id,
                              target_player_id=self.target_player_id, target_id=self.target_id)]
        return []


class ReturnAllMinionsEffect(Effect):
    def __init__(self, source_player_id: int):
        self.source_player_id = source_player_id

    def apply(self, state: GameState) -> list[Event]:
        events: list[Event] = []
        for player in state.players:
            for minion in list(player.board):
                events.extend(ReturnToHandEffect(
                    self.source_player_id, player.player_id, minion.instance_id
                ).apply(state))
        return events


class CorruptEffect(Effect):
    def __init__(self, target_player_id: int, target_id: int):
        self.target_player_id = target_player_id
        self.target_id = target_id

    def apply(self, state: GameState) -> list[Event]:
        minion = next((m for m in state.player(self.target_player_id).board
                       if m.instance_id == self.target_id), None)
        if minion is None:
            return []
        minion.statuses.add("corrupted")
        return [Event("corrupted", target_player_id=self.target_player_id,
                      target_id=self.target_id)]


class DamageThenDrawIfKilledEffect(Effect):
    def __init__(self, source_player_id: int, target_player_id: int, target_id: int, amount: int):
        self.source_player_id = source_player_id
        self.target_player_id = target_player_id
        self.target_id = target_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        minion = next((m for m in state.player(self.target_player_id).board
                       if m.instance_id == self.target_id), None)
        if minion is None:
            return []
        minion.take_damage(self.amount)
        events = [Event("damage_dealt", source_player_id=self.source_player_id,
                        target_player_id=self.target_player_id, target_id=self.target_id,
                        amount=self.amount, data={"target_kind": "minion"})]
        if not minion.alive:
            events.extend(DrawEffect(self.source_player_id).apply(state))
        return events


class DiscardRandomEffect(Effect):
    def __init__(self, player_id: int, rng):
        self.player_id = player_id
        self.rng = rng

    def apply(self, state: GameState) -> list[Event]:
        hand = state.player(self.player_id).hand.cards
        if not hand:
            return []
        card = self.rng.choice(hand)
        hand.remove(card)
        return [Event("card_discarded", target_player_id=self.player_id,
                      card_id=card.card_id)]


class RandomEnemyDamageEffect(Effect):
    def __init__(self, source_player_id: int, amount: int, hits: int, rng,
                 minions_only: bool = False):
        self.source_player_id = source_player_id
        self.amount = amount
        self.hits = hits
        self.rng = rng
        self.minions_only = minions_only

    def apply(self, state: GameState) -> list[Event]:
        enemy = state.player(1 - self.source_player_id)
        targets = [("minion", m.instance_id) for m in enemy.board]
        if not self.minions_only:
            targets.append(("hero", None))
        events = []
        for _ in range(self.hits):
            if not targets:
                break
            kind, target_id = self.rng.choice(targets)
            events.extend(DamageEffect(
                enemy.player_id, self.amount, target_kind=kind,
                target_id=target_id, source_player_id=self.source_player_id,
                spell_damage=True,
            ).apply(state))
            targets = [(k, i) for k, i in targets
                       if k == "hero" or next((m for m in enemy.board if m.instance_id == i), None)]
        return events


class FreezeAllEnemyMinionsEffect(Effect):
    def __init__(self, source_player_id: int):
        self.source_player_id = source_player_id

    def apply(self, state: GameState) -> list[Event]:
        enemy = state.player(1 - self.source_player_id)
        for minion in enemy.board:
            minion.statuses.add("frozen")
            minion.can_attack = False
        return [Event("freeze_all_enemy_minions", source_player_id=self.source_player_id)]


class TransformMinionEffect(Effect):
    def __init__(self, target_player_id: int, target_id: int, card):
        self.target_player_id = target_player_id
        self.target_id = target_id
        self.card = card

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.target_player_id)
        for index, minion in enumerate(player.board):
            if minion.instance_id == self.target_id:
                player.board[index] = Minion.from_card(
                    CardInstance(minion.instance_id, self.card)
                )
                return [Event("minion_transformed", target_player_id=self.target_player_id,
                              target_id=self.target_id)]
        return []


class RandomChoiceEffect(Effect):
    def __init__(self, choices: list[Effect], rng):
        if not choices:
            raise ValueError("RandomChoiceEffect requires at least one choice")
        self.choices = choices
        self.rng = rng

    def apply(self, state: GameState) -> list[Event]:
        return self.rng.choice(self.choices).apply(state)


class FreezeEffect(Effect):
    def __init__(self, target_player_id: int, target_id: int | None, target_kind: str = "minion"):
        self.target_player_id = target_player_id
        self.target_id = target_id
        self.target_kind = target_kind

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.target_player_id)
        if self.target_kind == "hero":
            player.hero.statuses.add("frozen")
        else:
            minion = next((m for m in player.board if m.instance_id == self.target_id), None)
            if minion is None:
                return []
            minion.statuses.add("frozen")
            minion.can_attack = False
        return [Event("frozen", target_player_id=self.target_player_id, target_id=self.target_id)]


class BuffEffect(Effect):
    def __init__(self, target_player_id: int, target_kind: str, target_id: int | None = None,
                 attack: int = 0, health: int = 0, status: str | None = None,
                 temporary: bool = False):
        self.target_player_id = target_player_id
        self.target_kind = target_kind
        self.target_id = target_id
        self.attack = attack
        self.health = health
        self.status = status
        self.temporary = temporary

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.target_player_id)
        if self.target_kind == "hero":
            target = player.hero
            target.temporary_attack += self.attack
            if self.health:
                target.max_hp += self.health
                target.hp += self.health
        else:
            target = next((m for m in player.board if m.instance_id == self.target_id), None)
            if target is None:
                return []
            target.buff_attack += self.attack
            target.attack += self.attack
            if self.health:
                target.buff_health += self.health
                target.max_hp += self.health
                target.hp += self.health
            if self.status:
                target.statuses.add(self.status)
        return [Event("buffed", target_player_id=self.target_player_id,
                      target_id=self.target_id, data={"temporary": self.temporary})]


class ModifyManaEffect(Effect):
    def __init__(self, player_id: int, amount: int, maximum: bool = False):
        self.player_id = player_id
        self.amount = amount
        self.maximum = maximum

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.player_id)
        if self.maximum:
            player.max_mana = min(10, player.max_mana + self.amount)
            player.mana = min(player.max_mana, player.mana + self.amount)
        else:
            player.mana += self.amount
        return [Event("mana_modified", target_player_id=self.player_id, amount=self.amount)]


class DestroyEffect(Effect):
    def __init__(self, target_player_id: int, target_id: int):
        self.target_player_id = target_player_id
        self.target_id = target_id

    def apply(self, state: GameState) -> list[Event]:
        minion = next((m for m in state.player(self.target_player_id).board
                       if m.instance_id == self.target_id), None)
        if minion is None:
            return []
        minion.hp = 0
        return [Event("destroyed", target_player_id=self.target_player_id, target_id=self.target_id)]


class SetHealthEffect(Effect):
    def __init__(self, target_player_id: int, target_id: int, health: int):
        self.target_player_id = target_player_id
        self.target_id = target_id
        self.health = health

    def apply(self, state: GameState) -> list[Event]:
        minion = next((m for m in state.player(self.target_player_id).board
                       if m.instance_id == self.target_id), None)
        if minion is None:
            return []
        minion._base_max_hp = self.health
        minion.max_hp = self.health
        minion.hp = min(minion.hp, self.health)
        return [Event("health_set", target_player_id=self.target_player_id,
                      target_id=self.target_id, amount=self.health)]


class DamageAllEnemyMinionsEffect(Effect):
    def __init__(self, source_player_id: int, amount: int):
        self.source_player_id = source_player_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        enemy = state.player(1 - self.source_player_id)
        for minion in enemy.board:
            minion.take_damage(self.amount)
        return [Event("damage_all_enemy_minions", source_player_id=self.source_player_id,
                      amount=self.amount)]


class HealAllFriendlyCharactersEffect(Effect):
    def __init__(self, player_id: int, amount: int):
        self.player_id = player_id
        self.amount = amount

    def apply(self, state: GameState) -> list[Event]:
        player = state.player(self.player_id)
        player.hero.hp = min(player.hero.max_hp, player.hero.hp + self.amount)
        for minion in player.board:
            minion.hp = min(minion.max_hp, minion.hp + self.amount)
        return [Event("heal_all_friendly_characters", target_player_id=self.player_id,
                      amount=self.amount)]
