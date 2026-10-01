import random

from ..actions.action import AttackAction, EndTurnAction, PlayCardAction
from ..ai_agent import RuleBasedAgent
from ..cards.starter_decks import CLASSES
from ..actions.hero_attack import HeroAttackAction
from ..actions.hero_power import HeroPowerAction
from .game_mode import read_player2_control
from .input_handler import read_action, read_class
from .renderer import clear_screen, render
from ..engine.game_engine import InvalidAction
from ..session.game_session import new_game


def main() -> None:
    clear_screen()
    player1_class = read_class("Player 1")
    player2_is_ai = read_player2_control()
    if player2_is_ai:
        player2_class = random.choice(CLASSES)
        print(f"AI 職業已隨機選定：{player2_class}")
    else:
        player2_class = read_class("Player 2")
    input("職業選擇完成。按 Enter 開始遊戲...")
    state, engine = new_game(player_classes=(player1_class, player2_class))
    agent = RuleBasedAgent() if player2_is_ai else None
    first_player = state.player(state.current_player_id)
    second_player = state.player(1 - state.current_player_id)
    pending_logs = [
        f"遊戲開始！{first_player.name} 先手。",
        f"{second_player.name} 為後手，獲得一張幸運幣。",
    ]
    while not state.game_over:
        if player2_is_ai and state.current_player_id == 1:
            ai_logs = ["AI 回合開始。"]
            while not state.game_over and state.current_player_id == 1:
                action = agent.choose_action(state)
                target_text = describe_ai_target(state, action)
                try:
                    action_logs = engine.apply_action(state, action)
                    if target_text and action_logs:
                        action_logs[-1] += f"，目標：{target_text}"
                    ai_logs.extend(action_logs)
                except InvalidAction as error:
                    ai_logs.append(f"AI 行動失敗：{error}")
                    action = EndTurnAction()
                if isinstance(action, EndTurnAction):
                    break
            pending_logs.extend(ai_logs)
            continue

        clear_screen()
        print(render(state))
        print("\n".join(pending_logs))
        pending_logs = []
        try:
            action = read_action(state)
            pending_logs.extend(engine.apply_action(state, action))
        except InvalidAction as error:
            pending_logs = [f"無法執行：{error}"]
            input("按 Enter 繼續...")
            continue
        if state.game_over:
            break
        if isinstance(action, EndTurnAction) and not player2_is_ai:
            clear_screen()
            print(f"請把畫面交給 {state.current_player.name}。")
            input("確認後按 Enter...")

    clear_screen()
    print(render(state))
    print("\n".join(pending_logs))
    print(f"\n遊戲結束！勝利者：{state.player(state.winner_id).name}")


def describe_ai_target(state, action) -> str | None:
    if isinstance(action, PlayCardAction):
        if action.target is None:
            return None
        return describe_target_ref(state, action.target)
    if isinstance(action, HeroPowerAction):
        return describe_target_ref(state, action.target) if action.target else None
    if isinstance(action, (AttackAction, HeroAttackAction)):
        if action.target == "hero":
            return f"{state.opponent.name} Hero"
        try:
            index = int(action.target.split(":", 1)[1])
            return f"{state.opponent.name} {state.opponent.board[index].name}"
        except (ValueError, IndexError):
            return "未知目標"
    return None


def describe_target_ref(state, target) -> str:
    player = state.player(target.player_id)
    if target.kind.value == "hero":
        return f"{player.name} Hero"
    minion = next((m for m in player.board if m.instance_id == target.entity_id), None)
    return f"{player.name} {minion.name}" if minion else "未知目標"


if __name__ == "__main__":
    main()
