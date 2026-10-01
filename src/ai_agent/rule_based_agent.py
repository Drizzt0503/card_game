import random

from ..actions.action import Action, AttackAction, EndTurnAction, PlayCardAction
from ..actions.hero_attack import HeroAttackAction
from ..actions.hero_power import HeroPowerAction
from ..cards.card_effects import build_play_effects
from ..heroes.hero_powers import build_effects, hero_power_for
from ..targeting.target import TargetRule, TargetingService
from .base import AIAgent
from .card_knowledge import AREA_CLEAR_CARDS, DAMAGE_BY_CARD, HERO_POWER_DAMAGE, REMOVAL_WEAPONS


class RuleBasedAgent(AIAgent):
    """Simple baseline agent; its state input can later become an Observation."""

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.targeting = TargetingService()

    def choose_action(self, state) -> Action:
        player = state.current_player

        affordable_cards = []
        for index, card in enumerate(player.hand.cards):
            if card.cost > player.mana:
                continue
            if card.definition.card_type == "MINION" and len(player.board) >= 7:
                continue
            target = self._card_target(state, index)
            try:
                build_play_effects(state, player.player_id, card, target, self.rng)
                removal_priority = self._removal_priority(state, card, target)
                affordable_cards.append((removal_priority, card.cost, index, target))
            except ValueError:
                continue
        if affordable_cards:
            # Generic mana rule: spend the largest affordable card first.
            _, _, index, target = max(affordable_cards, key=lambda item: (item[0], item[1]))
            return PlayCardAction(index, target)

        taunts = [
            index for index, minion in enumerate(state.opponent.board)
            if "taunt" in minion.statuses
        ]
        for index, minion in enumerate(player.board):
            if minion.attack > 0 and minion.can_attack and "frozen" not in minion.statuses:
                target = self._attack_target(state, minion.attack, index, taunts)
                return AttackAction(index, target)

        if (
            player.hero.attack > 0
            and not player.hero.hero_attack_used
            and "frozen" not in player.hero.statuses
            and not taunts
        ):
            return HeroAttackAction(self._hero_attack_target(state, taunts))

        definition = hero_power_for(player.player_class)
        if not player.hero.hero_power_used and player.mana >= definition.cost:
            target = self._hero_power_target(state, definition.target_rule)
            try:
                build_effects(state, player.player_id, target, self.rng)
                return HeroPowerAction(target)
            except ValueError:
                pass

        return EndTurnAction()

    def _attack_target(self, state, attack: int, attacker_index: int, taunts: list[int]) -> str:
        if taunts:
            return f"minion:{self._best_minion_target(state, attack, taunts)}"

        attacker = state.current_player.board[attacker_index]
        killable = [index for index, target in enumerate(state.opponent.board)
                    if attack >= target.hp]
        if killable:
            return f"minion:{self._highest_threat(state, killable)}"
        if state.opponent.board:
            return f"minion:{self._highest_threat(state, list(range(len(state.opponent.board))))}"
        return "hero"

    def _hero_attack_target(self, state, taunts: list[int]) -> str:
        if taunts:
            return f"minion:{self._best_minion_target(state, state.current_player.hero.attack, taunts)}"
        if state.opponent.board:
            return f"minion:{self._highest_threat(state, list(range(len(state.opponent.board))))}"
        return "hero"

    @staticmethod
    def _best_minion_target(state, attack: int, candidates: list[int]) -> int:
        killable = [index for index in candidates
                    if attack >= state.opponent.board[index].hp]
        return killable[0] if killable else candidates[0]

    @staticmethod
    def _highest_threat(state, candidates: list[int]) -> int:
        return max(candidates, key=lambda index: (
            state.opponent.board[index].attack,
            state.opponent.board[index].hp,
        ))

    def _removal_priority(self, state, card, target) -> int:
        card_id = card.definition.card_id
        if card_id in DAMAGE_BY_CARD and target is not None and target.kind.value == "minion":
            target_minion = next(m for m in state.opponent.board
                                 if m.instance_id == target.entity_id)
            return 300 if DAMAGE_BY_CARD[card_id] >= target_minion.hp else 180
        if card_id in AREA_CLEAR_CARDS and state.opponent.board:
            return 220
        if card_id in REMOVAL_WEAPONS and state.opponent.board:
            return 80
        if target is not None and target.kind.value == "minion" and target.player_id != state.current_player.player_id:
            return 100
        if card.definition.card_type == "MINION":
            return 50
        return 0

    def _card_target(self, state, hand_index):
        card = state.current_player.hand.cards[hand_index]
        rule = TargetRule(card.definition.target_rule)
        legal = self.targeting.legal_targets(state, state.current_player.player_id, rule)
        enemy_targets = [target for target in legal
                         if target.player_id != state.current_player.player_id]
        if enemy_targets:
            enemy_minions = [target for target in enemy_targets if target.kind.value == "minion"]
            if enemy_minions:
                damage = DAMAGE_BY_CARD.get(card.definition.card_id, 0)
                killable = [target for target in enemy_minions
                            if damage and damage >= next(
                                m for m in state.opponent.board
                                if m.instance_id == target.entity_id
                            ).hp]
                if killable:
                    return self._highest_target(state, killable)
                return max(
                    enemy_minions,
                    key=lambda target: (
                        next(m for m in state.opponent.board if m.instance_id == target.entity_id).attack,
                        next(m for m in state.opponent.board if m.instance_id == target.entity_id).hp,
                    ),
                )
            legal = enemy_targets
        return self.rng.choice(legal) if legal else None

    @staticmethod
    def _highest_target(state, targets):
        return max(
            targets,
            key=lambda target: next(
                m for m in state.opponent.board if m.instance_id == target.entity_id
            ).attack,
        )

    def _hero_power_target(self, state, rule):
        legal = self.targeting.legal_targets(state, state.current_player.player_id, rule)
        enemy_targets = [target for target in legal
                         if target.player_id != state.current_player.player_id]
        if enemy_targets:
            enemy_minions = [target for target in enemy_targets if target.kind.value == "minion"]
            power_damage = HERO_POWER_DAMAGE.get(hero_power_for(state.current_player.player_class).power_id, 0)
            if enemy_minions and power_damage:
                killable = [target for target in enemy_minions
                            if power_damage >= next(
                                m for m in state.opponent.board
                                if m.instance_id == target.entity_id
                            ).hp]
                return self._highest_target(state, killable or enemy_minions)
            legal = enemy_minions or enemy_targets
        return self.rng.choice(legal) if legal else None
