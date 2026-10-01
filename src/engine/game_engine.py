import random

from ..actions.action import Action, AttackAction, EndTurnAction, PlayCardAction
from ..actions.hero_attack import HeroAttackAction
from ..actions.hero_power import HeroPowerAction
from ..domain.game_state import GameState
from ..effects.effect import DamageEffect, DrawEffect, SummonEffect
from ..cards.card_effects import build_play_effects
from ..auras.aura import recalculate_auras
from ..heroes.hero_powers import build_effects, hero_power_for
from . import rules
from .resolver import EffectResolver, remove_dead_minions


class InvalidAction(ValueError):
    pass


class GameEngine:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.effect_resolver = EffectResolver()

    def start(self, state: GameState) -> list[str]:
        events: list[str] = []
        first_player_id = state.current_player_id
        second_player_id = 1 - first_player_id
        for player in state.players:
            # 先手起手 3 張，後手起手 4 張；幸運幣由 session 另外加入。
            starting_hand_size = rules.STARTING_HAND_SIZE
            if player.player_id == second_player_id:
                starting_hand_size += 1
            for _ in range(starting_hand_size):
                player.draw()
        events.extend(self._start_turn(state, first_player_id))
        return events

    def apply_action(self, state: GameState, action: Action) -> list[str]:
        if state.game_over:
            raise InvalidAction("遊戲已經結束")
        if isinstance(action, PlayCardAction):
            events = self._play_card(state, action)
        elif isinstance(action, AttackAction):
            events = self._attack(state, action)
        elif isinstance(action, HeroAttackAction):
            events = self._hero_attack(state, action)
        elif isinstance(action, HeroPowerAction):
            events = self._hero_power(state, action)
        elif isinstance(action, EndTurnAction):
            events = self._end_turn(state)
        else:
            raise InvalidAction("不支援的 Action")
        events.extend(remove_dead_minions(state))
        recalculate_auras(state)
        self._check_game_over(state)
        return events

    def _play_card(self, state: GameState, action: PlayCardAction) -> list[str]:
        player = state.current_player
        if not 0 <= action.hand_index < len(player.hand.cards):
            raise InvalidAction("手牌編號不存在")
        card = player.hand.cards[action.hand_index]
        if card.cost > player.mana:
            raise InvalidAction("Mana 不足")
        if card.definition.card_type == "MINION" and len(player.board) >= rules.MAX_BOARD_SIZE:
            raise InvalidAction("場上已經有 7 個手下")
        try:
            effects = build_play_effects(state, player.player_id, card, action.target, self.rng)
        except ValueError as error:
            raise InvalidAction(str(error)) from None
        player.hand.remove(action.hand_index)
        player.mana -= card.cost
        effect_events = self.effect_resolver.resolve(state, effects)
        if card.definition.card_type == "MINION":
            result = f"{player.name} 打出 {card.name} ({card.definition.attack}/{card.definition.health})"
        else:
            result = f"{player.name} 打出 {card.name}"
        logs = [result]
        for event in effect_events:
            if event.event_type == "card_drawn":
                logs.append(f"{state.player(event.target_player_id).name} 抽了一張牌")
        return logs

    def _attack(self, state: GameState, action: AttackAction) -> list[str]:
        player = state.current_player
        enemy = state.opponent
        if not 0 <= action.attacker_index < len(player.board):
            raise InvalidAction("攻擊者不存在")
        attacker = player.board[action.attacker_index]
        if attacker.attack <= 0:
            raise InvalidAction("攻擊力為 0，無法攻擊")
        if not attacker.can_attack:
            raise InvalidAction("這個手下本回合不能攻擊")
        if action.target == "hero":
            self._validate_taunt_target(enemy, None)
            self.effect_resolver.resolve(state, [DamageEffect(
                enemy.player_id,
                attacker.attack,
                target_kind="hero",
                source_player_id=player.player_id,
                source_id=attacker.instance_id,
            )])
            if "freeze_attack_target" in attacker.attack_trigger_ids:
                enemy.hero.statuses.add("frozen")
            events = [f"{attacker.name} 攻擊敵方英雄，造成 {attacker.attack} 點傷害"]
        elif action.target.startswith("minion:"):
            try:
                target_index = int(action.target.split(":", 1)[1])
                target = enemy.board[target_index]
            except (ValueError, IndexError):
                raise InvalidAction("目標手下不存在") from None
            self._validate_taunt_target(enemy, target)
            target_attack = target.attack
            self.effect_resolver.resolve(state, [
                DamageEffect(
                    enemy.player_id,
                    attacker.attack,
                    target_kind="minion",
                    target_id=target.instance_id,
                    source_player_id=player.player_id,
                    source_id=attacker.instance_id,
                ),
                DamageEffect(
                    player.player_id,
                    target_attack,
                    target_kind="minion",
                    target_id=attacker.instance_id,
                    source_player_id=enemy.player_id,
                    source_id=target.instance_id,
                ),
            ])
            if "freeze_attack_target" in attacker.attack_trigger_ids:
                target.statuses.add("frozen")
                target.can_attack = False
            events = [f"{attacker.name} 與 {target.name} 互相造成傷害"]
        else:
            raise InvalidAction("攻擊目標格式錯誤")
        attacker.attacks_remaining = max(0, attacker.attacks_remaining - 1)
        attacker.can_attack = attacker.attacks_remaining > 0
        return events

    def _end_turn(self, state: GameState) -> list[str]:
        ending_player = state.current_player
        ending_player.hero.temporary_attack = 0
        state.current_player_id = 1 - state.current_player_id
        state.turn_number += 1
        return self._start_turn(state, state.current_player_id)

    def _hero_attack(self, state: GameState, action: HeroAttackAction) -> list[str]:
        player = state.current_player
        enemy = state.opponent
        hero = player.hero
        if hero.attack <= 0:
            raise InvalidAction("Hero 沒有攻擊力，無法攻擊")
        if hero.hero_attack_used:
            raise InvalidAction("Hero 本回合已經攻擊過")
        if "frozen" in hero.statuses:
            raise InvalidAction("Hero 被凍結，無法攻擊")

        if action.target == "hero":
            self._validate_taunt_target(enemy, None)
            self.effect_resolver.resolve(state, [DamageEffect(
                enemy.player_id,
                hero.attack,
                target_kind="hero",
                source_player_id=player.player_id,
            )])
            events = [f"{player.name} 的 Hero 攻擊敵方 Hero，造成 {hero.attack} 點傷害"]
        elif action.target.startswith("minion:"):
            try:
                target_index = int(action.target.split(":", 1)[1])
                target = enemy.board[target_index]
            except (ValueError, IndexError):
                raise InvalidAction("目標手下不存在") from None
            self._validate_taunt_target(enemy, target)
            target_attack = target.attack
            self.effect_resolver.resolve(state, [
                DamageEffect(
                    enemy.player_id,
                    hero.attack,
                    target_kind="minion",
                    target_id=target.instance_id,
                    source_player_id=player.player_id,
                ),
                DamageEffect(
                    player.player_id,
                    target_attack,
                    target_kind="hero",
                    source_player_id=enemy.player_id,
                    source_id=target.instance_id,
                ),
            ])
            events = [f"{player.name} 的 Hero 攻擊 {target.name}，互相造成傷害"]
        else:
            raise InvalidAction("攻擊目標格式錯誤")

        hero.hero_attack_used = True
        if hero.weapon is not None:
            hero.weapon.lose_durability()
            if hero.weapon.destroyed:
                hero.weapon = None
        return events

    @staticmethod
    def _validate_taunt_target(enemy, target) -> None:
        taunts = [minion for minion in enemy.board if "taunt" in minion.statuses]
        if not taunts:
            return
        if target is None or "taunt" not in target.statuses:
            raise InvalidAction("敵方有嘲諷手下，只能攻擊嘲諷手下")

    def _start_turn(self, state: GameState, player_id: int) -> list[str]:
        player = state.player(player_id)
        for minion in player.board:
            if "corrupted" in minion.statuses:
                minion.hp = 0
        death_logs = remove_dead_minions(state)
        player.max_mana = min(rules.MAX_MANA, player.max_mana + 1)
        player.mana = player.max_mana
        player.hero.hero_power_used = False
        player.hero.hero_attack_used = False
        player.hero.temporary_attack = 0
        if "frozen" in player.hero.statuses:
            player.hero.statuses.remove("frozen")
            player.hero.hero_attack_used = True
        self.effect_resolver.resolve(state, [DrawEffect(player_id)])
        for minion in player.board:
            if "frozen" in minion.statuses:
                minion.statuses.remove("frozen")
                minion.can_attack = False
                minion.attacks_remaining = 0
            else:
                minion.can_attack = True
                minion.attacks_remaining = 2 if "windfury" in minion.statuses else 1
        return death_logs + [f"{player.name} 的回合開始：Mana {player.mana}/{player.max_mana}"]

    def _hero_power(self, state: GameState, action: HeroPowerAction) -> list[str]:
        player = state.current_player
        definition = hero_power_for(player.player_class)
        if player.hero.hero_power_used:
            raise InvalidAction("本回合已經使用過英雄技能")
        if player.mana < definition.cost:
            raise InvalidAction("Mana 不足")
        try:
            effects = build_effects(state, player.player_id, action.target, self.rng)
        except ValueError as error:
            raise InvalidAction(str(error)) from None
        player.mana -= definition.cost
        player.hero.hero_power_used = True
        self.effect_resolver.resolve(state, effects)
        return [f"{player.name} 使用英雄技能：{definition.name}"]

    def _check_game_over(self, state: GameState) -> None:
        for player in state.players:
            if not player.alive:
                state.winner_id = 1 - player.player_id
                state.phase = "GAME_OVER"
                return
