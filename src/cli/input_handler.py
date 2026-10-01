from ..actions.action import AttackAction, EndTurnAction, PlayCardAction
from ..actions.hero_attack import HeroAttackAction
from ..actions.hero_power import HeroPowerAction
from ..cards.starter_decks import CLASSES
from ..heroes.hero_powers import hero_power_for
from ..targeting.target import TargetKind, TargetRef, TargetRule


def read_class(player_name: str) -> str:
    while True:
        print(f"{player_name} 請選擇職業：")
        for index, player_class in enumerate(CLASSES, start=1):
            print(f"  {index}. {player_class}")
        try:
            choice = int(input("職業編號：").strip())
            if 1 <= choice <= len(CLASSES):
                return CLASSES[choice - 1]
        except ValueError:
            pass
        print("請輸入有效的職業編號。\n")


def read_action(state):
    while True:
        choice = input("請選擇操作（1 出牌、2 手下攻擊、3 Hero 攻擊、4 英雄技能、5 結束回合）：").strip()
        if choice == "1":
            try:
                hand_index = int(input("手牌編號：").strip()) - 1
                if not 0 <= hand_index < len(state.current_player.hand.cards):
                    raise ValueError
                return PlayCardAction(hand_index, read_card_target(state, hand_index))
            except ValueError:
                print("請輸入有效的手牌編號。")
        elif choice == "2":
            try:
                attacker = int(input("你的手下編號：").strip()) - 1
                target_index = int(input("攻擊目標編號（0=敵方 Hero，1 以上=敵方手下）：").strip())
                target = "hero" if target_index == 0 else f"minion:{target_index - 1}"
                return AttackAction(attacker, target)
            except ValueError:
                print("目標格式錯誤。")
        elif choice == "3":
            try:
                target_index = int(input("Hero 攻擊目標編號（0=敵方 Hero，1 以上=敵方手下）：").strip())
                target = "hero" if target_index == 0 else f"minion:{target_index - 1}"
                return HeroAttackAction(target)
            except ValueError:
                print("目標格式錯誤。")
        elif choice == "4":
            return HeroPowerAction(read_hero_power_target(state))
        elif choice == "5":
            return EndTurnAction()
        else:
            print("請輸入 1、2、3、4 或 5。")


def read_hero_power_target(state):
    definition = hero_power_for(state.current_player.player_class)
    if definition.target_rule == TargetRule.NO_TARGET:
        return None

    player = state.current_player
    enemy = state.opponent
    print(f"目標（{definition.name}）：")
    if definition.target_rule == TargetRule.ANY_CHARACTER:
        choices = [TargetRef(TargetKind.HERO, player.player_id)]
        choices.extend(TargetRef(TargetKind.MINION, player.player_id, minion.instance_id)
                       for minion in player.board)
        choices.append(TargetRef(TargetKind.HERO, enemy.player_id))
        choices.extend(TargetRef(TargetKind.MINION, enemy.player_id, minion.instance_id)
                       for minion in enemy.board)
        for index, target in enumerate(choices):
            if target.kind == TargetKind.HERO:
                label = "自己的 Hero" if target.player_id == player.player_id else "敵方 Hero"
            else:
                minion = next(m for owner in state.players for m in owner.board
                              if m.instance_id == target.entity_id)
                label = f"{'自己的' if target.player_id == player.player_id else '敵方'} {minion.name}"
            print(f"  {index}. {label}")
        while True:
            try:
                choice = int(input("目標編號："))
                if 0 <= choice < len(choices):
                    return choices[choice]
            except ValueError:
                pass
            print("目標編號無效。")
    if definition.target_rule == TargetRule.FRIENDLY_CHARACTER:
        print("  0. 自己的 Hero")
        for index, minion in enumerate(player.board, start=1):
            print(f"  {index}. 自己的 {minion.name}")
        while True:
            try:
                choice = int(input("目標編號："))
                if choice == 0:
                    return TargetRef(TargetKind.HERO, player.player_id)
                if 1 <= choice <= len(player.board):
                    return TargetRef(TargetKind.MINION, player.player_id, player.board[choice - 1].instance_id)
            except ValueError:
                pass
            print("目標編號無效。")

    print("  0. 敵方 Hero")
    for index, minion in enumerate(enemy.board, start=1):
        print(f"  {index}. 敵方 {minion.name}")
    while True:
        try:
            choice = int(input("目標編號："))
            if choice == 0:
                return TargetRef(TargetKind.HERO, enemy.player_id)
            if 1 <= choice <= len(enemy.board):
                return TargetRef(TargetKind.MINION, enemy.player_id, enemy.board[choice - 1].instance_id)
        except ValueError:
            pass
        print("目標編號無效。")


def read_card_target(state, hand_index):
    card = state.current_player.hand.cards[hand_index]
    rule = TargetRule(card.definition.target_rule)
    if rule == TargetRule.NO_TARGET:
        return None
    player = state.current_player
    enemy = state.opponent
    choices = []
    if rule in (TargetRule.FRIENDLY_CHARACTER, TargetRule.ANY_CHARACTER):
        choices.append(TargetRef(TargetKind.HERO, player.player_id))
        choices.extend(TargetRef(TargetKind.MINION, player.player_id, minion.instance_id)
                       for minion in player.board)
    if rule in (TargetRule.ENEMY_CHARACTER, TargetRule.ANY_CHARACTER):
        choices.append(TargetRef(TargetKind.HERO, enemy.player_id))
        choices.extend(TargetRef(TargetKind.MINION, enemy.player_id, minion.instance_id)
                       for minion in enemy.board)
    print(f"目標（{card.name}）：")
    for index, target in enumerate(choices):
        owner = "自己的" if target.player_id == player.player_id else "敵方"
        if target.kind == TargetKind.HERO:
            label = f"{owner} Hero"
        else:
            minion = next(m for owner_state in state.players for m in owner_state.board
                          if m.instance_id == target.entity_id)
            label = f"{owner} {minion.name}"
        print(f"  {index}. {label}")
    while True:
        try:
            choice = int(input("目標編號："))
            if 0 <= choice < len(choices):
                return choices[choice]
        except ValueError:
            pass
        print("目標編號無效。")
