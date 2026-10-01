from ..domain.game_state import GameState
from ..heroes.hero_powers import hero_power_for


STATUS_NAMES_ZH = {
    "frozen": "凍結",
    "divine_shield": "聖盾",
    "taunt": "嘲諷",
    "windfury": "風怒",
}


def format_statuses(statuses) -> str:
    names = [STATUS_NAMES_ZH.get(status, status) for status in sorted(statuses)]
    return ", ".join(names) if names else "無"


def render(state: GameState) -> str:
    current = state.current_player
    enemy = state.opponent
    hero_power = hero_power_for(current.player_class)
    enemy_weapon = (
        f"{enemy.hero.weapon.name} {enemy.hero.weapon.attack}/{enemy.hero.weapon.durability}"
        if enemy.hero.weapon else "無"
    )
    lines = [
        "=" * 60,
        f"Turn {state.turn_number} | {current.name} ({current.player_class}) 的回合",
        f"你的職業: {current.player_class} | 英雄技能: {hero_power.name} ({hero_power.cost} Mana)",
        f"對手 {enemy.name} ({enemy.player_class}): Hero {enemy.hero.hp}/{enemy.hero.max_hp} | Armor: {enemy.hero.armor} | Attack: {enemy.hero.attack} | 武器: {enemy_weapon} | 狀態: {format_statuses(enemy.hero.statuses)} | 手牌 {len(enemy.hand)} | 牌庫 {len(enemy.deck)}",
        "-" * 60,
        f"你的 Hero: {current.hero.hp}/{current.hero.max_hp} | Armor: {current.hero.armor} | Attack: {current.hero.attack} | 狀態: {format_statuses(current.hero.statuses)}",
        f"武器: {current.hero.weapon.name + ' ' + str(current.hero.weapon.attack) + '/' + str(current.hero.weapon.durability) if current.hero.weapon else '無'}",
        f"Mana: {current.mana}/{current.max_mana} | Hero Power: {'已使用' if current.hero.hero_power_used else '可使用'}",
        f"你的牌庫: {len(current.deck)} 張 | 手牌: {len(current.hand)} 張 | 場上: {len(current.board)}/7",
        "",
        "手牌：",
    ]
    for index, card in enumerate(current.hand.cards, start=1):
        lines.append(f"  {index}. {card.name} | Cost {card.cost} | {card.definition.attack}/{card.definition.health}")
        lines.append(f"     {card.definition.description_zh}")
    if not current.hand.cards:
        lines.append("  （沒有手牌）")
    lines.extend(["", "你的場上："])
    for index, minion in enumerate(current.board, start=1):
        ready = "可攻擊" if minion.can_attack else "不可攻擊"
        status = format_statuses(minion.statuses)
        lines.append(f"  {index}. {minion.name} | {minion.attack}/{minion.hp} | {ready} | 狀態: {status}")
    if not current.board:
        lines.append("  （空）")
    lines.extend(["", "敵方場上："])
    for index, minion in enumerate(enemy.board, start=1):
        status = format_statuses(minion.statuses)
        lines.append(f"  {index}. {minion.name} | {minion.attack}/{minion.hp} | 狀態: {status}")
    if not enemy.board:
        lines.append("  （空）")
    lines.extend(["", "攻擊目標編號：0 = 敵方 Hero，1 以上 = 敵方手下"])
    lines.append("操作：1) 出牌  2) 手下攻擊  3) Hero 攻擊  4) 英雄技能  5) 結束回合")
    return "\n".join(lines)


def clear_screen() -> None:
    print("\033[2J\033[H", end="")
